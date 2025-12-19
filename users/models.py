
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator


class CustomUser(AbstractUser):
    """
    Custom User model with role-based access (Teacher/Student)
    Extends Django's AbstractUser
    """
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )

    # Required fields
    email = models.EmailField(unique=True, help_text='User email address')
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='student',
        help_text='User role: Student or Teacher'
    )

    # Profile fields
    bio = models.TextField(
        blank=True,
        help_text='User biography/description'
    )
    profile_picture = models.ImageField(
        upload_to='profiles/%Y/%m/',
        blank=True,
        null=True,
        help_text='Profile picture'
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text='Contact phone number'
    )

    # Password Recovery
    recovery_question = models.CharField(
        max_length=255,
        blank=True,
        help_text='Security question for password recovery'
    )
    recovery_answer = models.CharField(
        max_length=255,
        blank=True,
        validators=[MinLengthValidator(3)],
        help_text='Answer to security question (min 3 characters)'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    @property
    def is_teacher(self):
        """Check if user is a teacher"""
        return self.user_type == 'teacher'

    @property
    def is_student(self):
        """Check if user is a student"""
        return self.user_type == 'student'

    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username

    # Override email to be required
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']