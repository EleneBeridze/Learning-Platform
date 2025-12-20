from rest_framework import serializers
from .models import Category, Course, Lesson, Enrollment, Progress
from users.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for course categories
    """
    courses_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'courses_count', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']

    def get_courses_count(self, obj):
        return obj.courses.filter(is_published=True).count()


class LessonSerializer(serializers.ModelSerializer):
    """
    Serializer for lessons
    """

    class Meta:
        model = Lesson
        fields = [
            'id', 'course', 'title', 'description', 'content_type',
            'content', 'video_url', 'file', 'order', 'duration',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        """Validate lesson content based on type"""
        content_type = attrs.get('content_type')

        if content_type == 'video':
            if not attrs.get('video_url') and not attrs.get('content'):
                raise serializers.ValidationError({
                    "video_url": "Video URL or embedded code is required for video lessons."
                })
        elif content_type == 'text':
            if not attrs.get('content'):
                raise serializers.ValidationError({
                    "content": "Content is required for text lessons."
                })
        elif content_type == 'file':
            if not attrs.get('file'):
                raise serializers.ValidationError({
                    "file": "File is required for file lessons."
                })

        return attrs

    def validate_order(self, value):
        """Ensure order is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Order must be a positive number.")
        return value


class LessonListSerializer(serializers.ModelSerializer):
    """
    Minimal lesson serializer for listing
    """

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content_type', 'order', 'duration']


class CourseSerializer(serializers.ModelSerializer):
    """
    Full course serializer with nested data
    """
    teacher = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    lessons = LessonListSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()
    enrolled_students_count = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'teacher',
            'category', 'category_id', 'thumbnail', 'difficulty',
            'price', 'duration', 'is_published', 'lessons',
            'lessons_count', 'enrolled_students_count', 'is_enrolled',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'teacher', 'created_at', 'updated_at']

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_enrolled_students_count(self, obj):
        return obj.enrollments.count()

    def get_is_enrolled(self, obj):
        """Check if current user is enrolled"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.enrollments.filter(student=request.user).exists()
        return False

    def validate_price(self, value):
        """Ensure price is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

    def validate(self, attrs):
        """Validate that user is a teacher"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if request.user.user_type != 'teacher':
                raise serializers.ValidationError(
                    "Only teachers can create/update courses."
                )
        return attrs


class CourseListSerializer(serializers.ModelSerializer):
    """
    Minimal course serializer for listing
    """
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    lessons_count = serializers.SerializerMethodField()
    enrolled_students_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'teacher_name',
            'category_name', 'thumbnail', 'difficulty', 'price',
            'duration', 'lessons_count', 'enrolled_students_count',
            'is_published', 'created_at'
        ]

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_enrolled_students_count(self, obj):
        return obj.enrollments.count()


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating courses
    """

    class Meta:
        model = Course
        fields = [
            'title', 'slug', 'description', 'category',
            'thumbnail', 'difficulty', 'price', 'duration',
            'is_published'
        ]
        extra_kwargs = {
            'slug': {'required': False}
        }

    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.user.user_type != 'teacher':
            raise serializers.ValidationError(
                "Only teachers can create/update courses."
            )
        return attrs


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Serializer for enrollments
    """
    student = UserSerializer(read_only=True)
    course = CourseListSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.filter(is_published=True),
        source='course',
        write_only=True
    )

    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'course', 'course_id',
            'enrolled_at', 'completed', 'completed_at',
            'progress_percentage'
        ]
        read_only_fields = [
            'id', 'student', 'enrolled_at', 'completed',
            'completed_at', 'progress_percentage'
        ]

    def validate(self, attrs):
        request = self.context.get('request')
        course = attrs.get('course')

        # Only students can enroll
        if request.user.user_type != 'student':
            raise serializers.ValidationError(
                "Only students can enroll in courses."
            )

        # Check if already enrolled
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            raise serializers.ValidationError(
                "You are already enrolled in this course."
            )

        # Check if course is published
        if not course.is_published:
            raise serializers.ValidationError(
                "This course is not published yet."
            )

        return attrs

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


class ProgressSerializer(serializers.ModelSerializer):
    """
    Serializer for lesson progress
    """
    lesson = LessonListSerializer(read_only=True)
    lesson_id = serializers.PrimaryKeyRelatedField(
        queryset=Lesson.objects.all(),
        source='lesson',
        write_only=True
    )

    class Meta:
        model = Progress
        fields = [
            'id', 'enrollment', 'lesson', 'lesson_id',
            'completed', 'completed_at'
        ]
        read_only_fields = ['id', 'enrollment', 'completed_at']


class EnrollmentDetailSerializer(serializers.ModelSerializer):
    """
    Detailed enrollment with progress
    """
    course = CourseSerializer(read_only=True)
    progress_records = ProgressSerializer(many=True, read_only=True)
    completed_lessons = serializers.SerializerMethodField()
    total_lessons = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = [
            'id', 'course', 'enrolled_at', 'completed',
            'completed_at', 'progress_percentage', 'progress_records',
            'completed_lessons', 'total_lessons'
        ]

    def get_completed_lessons(self, obj):
        return obj.progress_records.filter(completed=True).count()

    def get_total_lessons(self, obj):
        return obj.course.lessons.count()


class CourseStatsSerializer(serializers.Serializer):
    """
    Serializer for course statistics (teacher dashboard)
    """
    total_courses = serializers.IntegerField()
    published_courses = serializers.IntegerField()
    total_students = serializers.IntegerField()
    total_enrollments = serializers.IntegerField()