from rest_framework import permissions


class IsTeacher(permissions.BasePermission):
    """
    Permission to check if user is a teacher
    """
    message = 'Only teachers can perform this action.'

    def has_permission(self, request, view):
        return (
                request.user and
                request.user.is_authenticated and
                request.user.user_type == 'teacher'
        )


class IsStudent(permissions.BasePermission):
    """
    Permission to check if user is a student
    """
    message = 'Only students can perform this action.'

    def has_permission(self, request, view):
        return (
                request.user and
                request.user.is_authenticated and
                request.user.user_type == 'student'
        )


class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Permission to allow read-only access to everyone,
    but write access only to teachers
    """

    def has_permission(self, request, view):
        # Read permissions (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for teachers
        return (
                request.user and
                request.user.is_authenticated and
                request.user.user_type == 'teacher'
        )

    def has_object_permission(self, request, view, obj):
        # Read permissions
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for course owner (teacher)
        if hasattr(obj, 'teacher'):
            return obj.teacher == request.user

        return False


class IsCourseOwner(permissions.BasePermission):
    """
    Permission to check if user is the course owner/teacher
    """
    message = 'You can only modify your own courses.'

    def has_object_permission(self, request, view, obj):
        # For Course model
        if hasattr(obj, 'teacher'):
            return obj.teacher == request.user

        # For Lesson model
        if hasattr(obj, 'course'):
            return obj.course.teacher == request.user

        return False


class IsEnrolledStudent(permissions.BasePermission):
    """
    Permission to check if student is enrolled in the course
    """
    message = 'You must be enrolled in this course.'

    def has_object_permission(self, request, view, obj):
        from .models import Enrollment

        # For Course model
        if hasattr(obj, 'enrollments'):
            return Enrollment.objects.filter(
                student=request.user,
                course=obj
            ).exists()

        # For Lesson model
        if hasattr(obj, 'course'):
            return Enrollment.objects.filter(
                student=request.user,
                course=obj.course
            ).exists()

        # For Enrollment model
        if hasattr(obj, 'student'):
            return obj.student == request.user

        return False


class IsEnrolledOrTeacher(permissions.BasePermission):
    """
    Permission for enrolled students or course teacher
    """

    def has_object_permission(self, request, view, obj):
        from .models import Enrollment

        # If user is the teacher
        if hasattr(obj, 'teacher') and obj.teacher == request.user:
            return True

        if hasattr(obj, 'course'):
            # If user is the course teacher
            if obj.course.teacher == request.user:
                return True

            # If user is enrolled in the course
            return Enrollment.objects.filter(
                student=request.user,
                course=obj.course
            ).exists()

        return False