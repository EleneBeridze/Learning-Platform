from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from .models import Category, Course, Lesson, Enrollment, Progress
from .serializers import (
    CategorySerializer,
    CourseSerializer,
    CourseListSerializer,
    CourseCreateUpdateSerializer,
    LessonSerializer,
    LessonListSerializer,
    EnrollmentSerializer,
    EnrollmentDetailSerializer,
    ProgressSerializer,
    CourseStatsSerializer,
)
from .permissions import (
    IsTeacher,
    IsStudent,
    IsTeacherOrReadOnly,
    IsCourseOwner,
    IsEnrolledStudent,
    IsEnrolledOrTeacher,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for category CRUD operations
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    @action(detail=True, methods=['get'])
    def courses(self, request, slug=None):
        """Get all published courses in this category"""
        category = self.get_object()
        courses = Course.objects.filter(
            category=category,
            is_published=True
        )
        serializer = CourseListSerializer(courses, many=True)
        return Response(serializer.data)


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for course CRUD operations
    """
    queryset = Course.objects.all()
    permission_classes = [IsTeacherOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'teacher__username']
    ordering_fields = ['created_at', 'price', 'title']

    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CourseCreateUpdateSerializer
        return CourseSerializer

    def get_queryset(self):
        queryset = Course.objects.select_related('teacher', 'category').prefetch_related('lessons')

        # Filter by published status for non-teachers
        user = self.request.user
        if not (user.is_authenticated and user.user_type == 'teacher'):
            queryset = queryset.filter(is_published=True)

        # Filter by teacher's own courses
        if user.is_authenticated and user.user_type == 'teacher':
            my_courses = self.request.query_params.get('my_courses')
            if my_courses:
                queryset = queryset.filter(teacher=user)

        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        # Filter free courses
        free_only = self.request.query_params.get('free')
        if free_only:
            queryset = queryset.filter(price=0)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        """Set the teacher to current user"""
        serializer.save(teacher=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly])
    def lessons(self, request, slug=None):
        """Get all lessons for this course"""
        course = self.get_object()

        # Check if user has access to all lessons
        has_full_access = False
        if request.user.is_authenticated:
            # Teacher has full access
            if course.teacher == request.user:
                has_full_access = True
            # Enrolled student has full access
            elif Enrollment.objects.filter(student=request.user, course=course).exists():
                has_full_access = True

        if has_full_access:
            lessons = course.lessons.all()
        else:
            # Only show basic info for non-enrolled users
            lessons = course.lessons.all()

        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsStudent])
    def enroll(self, request, slug=None):
        """Enroll in a course"""
        course = self.get_object()

        if not course.is_published:
            return Response({
                'error': 'This course is not published yet'
            }, status=status.HTTP_400_BAD_REQUEST)

        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course
        )

        if created:
            return Response({
                'message': 'Enrolled successfully',
                'enrollment': EnrollmentSerializer(enrollment).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Already enrolled in this course',
                'enrollment': EnrollmentSerializer(enrollment).data
            }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def enrollment_status(self, request, slug=None):
        """Check if user is enrolled in this course"""
        course = self.get_object()

        try:
            enrollment = Enrollment.objects.get(
                student=request.user,
                course=course
            )
            return Response({
                'enrolled': True,
                'enrollment': EnrollmentDetailSerializer(enrollment).data
            })
        except Enrollment.DoesNotExist:
            return Response({
                'enrolled': False
            })


class LessonViewSet(viewsets.ModelViewSet):
    """
    ViewSet for lesson CRUD operations
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Lesson.objects.select_related('course')

        # Filter by course
        course_slug = self.request.query_params.get('course')
        if course_slug:
            queryset = queryset.filter(course__slug=course_slug)

        # Teachers see all their course lessons
        user = self.request.user
        if user.is_authenticated and user.user_type == 'teacher':
            queryset = queryset.filter(course__teacher=user)

        return queryset

    def perform_create(self, serializer):
        """Only course teacher can add lessons"""
        course = serializer.validated_data['course']
        if course.teacher != self.request.user:
            raise PermissionError("You can only add lessons to your own courses")
        serializer.save()

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsTeacher(), IsCourseOwner()]
        return [IsAuthenticatedOrReadOnly()]


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for enrollment operations
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.user_type == 'teacher':
            # Teachers see enrollments in their courses
            return Enrollment.objects.filter(
                course__teacher=user
            ).select_related('student', 'course')
        else:
            # Students see their own enrollments
            return Enrollment.objects.filter(
                student=user
            ).select_related('course', 'course__teacher')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EnrollmentDetailSerializer
        return EnrollmentSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Get progress for an enrollment"""
        enrollment = self.get_object()
        progress_records = enrollment.progress_records.all()
        serializer = ProgressSerializer(progress_records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete_lesson(self, request, pk=None):
        """Mark a lesson as complete"""
        enrollment = self.get_object()
        lesson_id = request.data.get('lesson_id')

        if not lesson_id:
            return Response({
                'error': 'lesson_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            lesson = Lesson.objects.get(id=lesson_id, course=enrollment.course)
        except Lesson.DoesNotExist:
            return Response({
                'error': 'Lesson not found in this course'
            }, status=status.HTTP_404_NOT_FOUND)

        progress, created = Progress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )

        if not progress.completed:
            progress.completed = True
            progress.save()
            message = 'Lesson marked as complete'
        else:
            message = 'Lesson already completed'

        return Response({
            'message': message,
            'progress': ProgressSerializer(progress).data,
            'enrollment_progress': enrollment.progress_percentage
        }, status=status.HTTP_200_OK)


class MyCoursesView(generics.ListAPIView):
    """
    API endpoint for student's enrolled courses
    GET /api/my-courses/
    """
    serializer_class = EnrollmentDetailSerializer
    permission_classes = [IsAuthenticated, IsStudent]

    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user
        ).select_related('course', 'course__teacher', 'course__category')


class TeacherCoursesView(generics.ListAPIView):
    """
    API endpoint for teacher's created courses
    GET /api/teacher-courses/
    """
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_queryset(self):
        return Course.objects.filter(
            teacher=self.request.user
        ).select_related('category').prefetch_related('lessons')


class TeacherStatsView(generics.GenericAPIView):
    """
    API endpoint for teacher statistics
    GET /api/teacher-stats/
    """
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = CourseStatsSerializer

    def get(self, request):
        teacher = request.user

        stats = {
            'total_courses': Course.objects.filter(teacher=teacher).count(),
            'published_courses': Course.objects.filter(teacher=teacher, is_published=True).count(),
            'total_students': Enrollment.objects.filter(
                course__teacher=teacher
            ).values('student').distinct().count(),
            'total_enrollments': Enrollment.objects.filter(
                course__teacher=teacher
            ).count(),
        }

        serializer = self.get_serializer(stats)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    API health check endpoint
    GET /api/courses/health/
    """
    return Response({
        'status': 'healthy',
        'message': 'Courses API is running'
    })