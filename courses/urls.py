from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    CourseViewSet,
    LessonViewSet,
    EnrollmentViewSet,
    MyCoursesView,
    TeacherCoursesView,
    TeacherStatsView,
    health_check,
)

app_name = 'courses'

# Router for ViewSets
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')

urlpatterns = [
    # Health check
    path('health/', health_check, name='health'),

    # Router URLs (includes all ViewSet routes)
    path('', include(router.urls)),

    # Custom endpoints
    path('my-courses/', MyCoursesView.as_view(), name='my-courses'),
    path('teacher-courses/', TeacherCoursesView.as_view(), name='teacher-courses'),
    path('teacher-stats/', TeacherStatsView.as_view(), name='teacher-stats'),
]