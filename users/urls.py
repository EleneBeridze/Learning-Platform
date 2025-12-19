from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    PasswordChangeView,
    GetRecoveryQuestionView,
    PasswordRecoveryView,
    TeacherListView,
    TeacherDetailView,
    current_user,
    health_check,
)

app_name = 'users'

urlpatterns = [
    # Health check
    path('health/', health_check, name='health'),

    # Authentication
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('me/', current_user, name='current-user'),

    # Password Management
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),
    path('password/recovery/question/', GetRecoveryQuestionView.as_view(), name='recovery-question'),
    path('password/recovery/', PasswordRecoveryView.as_view(), name='password-recovery'),

    # Teachers
    path('teachers/', TeacherListView.as_view(), name='teacher-list'),
    path('teachers/<str:username>/', TeacherDetailView.as_view(), name='teacher-detail'),
]