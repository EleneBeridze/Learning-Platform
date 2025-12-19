from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    Handles password validation and user creation
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        label='Confirm Password',
        style={'input_type': 'password'}
    )

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'password', 'password2',
            'first_name', 'last_name', 'user_type', 'bio',
            'profile_picture', 'phone_number',
            'recovery_question', 'recovery_answer'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs

    def validate_email(self, value):
        """Check if email already exists"""
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def validate_recovery_answer(self, value):
        """Validate recovery answer length"""
        if value and len(value) < 3:
            raise serializers.ValidationError("Recovery answer must be at least 3 characters long.")
        return value

    def create(self, validated_data):
        """Create new user with hashed password"""
        validated_data.pop('password2')
        password = validated_data.pop('password')

        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        # Send welcome email
        try:
            send_mail(
                subject='Welcome to Courses Lab!',
                message=f'Hello {user.first_name},\n\nWelcome to Courses Lab! Your account has been created successfully.\n\nUsername: {user.username}\nUser Type: {user.get_user_type_display()}\n\nHappy Learning!',
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings,
                                                                  'DEFAULT_FROM_EMAIL') else 'noreply@courseslab.com',
                recipient_list=[user.email],
                fail_silently=True,
            )
        except:
            pass  # Email sending is optional

        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile display
    """
    full_name = serializers.SerializerMethodField()
    total_courses = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'user_type', 'bio', 'profile_picture',
            'phone_number', 'created_at', 'total_courses'
        ]
        read_only_fields = ['id', 'username', 'created_at']

    def get_full_name(self, obj):
        return obj.full_name

    def get_total_courses(self, obj):
        """Get total courses (taught or enrolled)"""
        if obj.is_teacher:
            return obj.taught_courses.count()
        elif obj.is_student:
            return obj.enrollments.count()
        return 0


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile
    """

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'bio',
            'profile_picture', 'phone_number'
        ]


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing password (authenticated users)
    """
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password2 = serializers.CharField(
        required=True,
        write_only=True,
        label='Confirm New Password',
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """Validate new passwords match"""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })
        return attrs

    def validate_old_password(self, value):
        """Verify old password is correct"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class GetRecoveryQuestionSerializer(serializers.Serializer):
    """
    Serializer to get user's recovery question
    """
    username = serializers.CharField(required=True)

    def validate_username(self, value):
        """Check if user exists"""
        try:
            user = CustomUser.objects.get(username=value)
            if not user.recovery_question:
                raise serializers.ValidationError(
                    "No recovery question set for this user. Please contact support."
                )
            self.context['user'] = user
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        return value


class PasswordRecoverySerializer(serializers.Serializer):
    """
    Serializer for password recovery using security question
    """
    username = serializers.CharField(required=True)
    recovery_answer = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password2 = serializers.CharField(
        required=True,
        write_only=True,
        label='Confirm New Password',
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """Validate passwords match and recovery answer is correct"""
        # Check passwords match
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })

        # Verify user and recovery answer
        try:
            user = CustomUser.objects.get(username=attrs['username'])

            if not user.recovery_answer:
                raise serializers.ValidationError({
                    "username": "No recovery question set for this user. Please contact support."
                })

            # Case-insensitive comparison
            if user.recovery_answer.lower().strip() != attrs['recovery_answer'].lower().strip():
                raise serializers.ValidationError({
                    "recovery_answer": "Recovery answer is incorrect."
                })

            attrs['user'] = user

        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({
                "username": "User not found."
            })

        return attrs

    def save(self):
        """Reset password and send confirmation email"""
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']

        # Set new password
        user.set_password(new_password)
        user.save()

        # Send confirmation email
        try:
            send_mail(
                subject='Password Reset Successful - Courses Lab',
                message=f'Hello {user.first_name},\n\nYour password has been reset successfully.\n\nIf you did not request this password reset, please contact support immediately.\n\nUsername: {user.username}\nReset Time: {user.updated_at}\n\nBest regards,\nCourses Lab Team',
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings,
                                                                  'DEFAULT_FROM_EMAIL') else 'noreply@courseslab.com',
                recipient_list=[user.email],
                fail_silently=True,
            )
        except:
            pass  # Email sending is optional

        return user


class TeacherSerializer(serializers.ModelSerializer):
    """
    Serializer for teacher profile with statistics
    """
    full_name = serializers.SerializerMethodField()
    total_courses = serializers.SerializerMethodField()
    total_students = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'bio', 'profile_picture', 'created_at',
            'total_courses', 'total_students'
        ]

    def get_full_name(self, obj):
        return obj.full_name

    def get_total_courses(self, obj):
        return obj.taught_courses.filter(is_published=True).count()

    def get_total_students(self, obj):
        from courses.models import Enrollment
        return Enrollment.objects.filter(
            course__teacher=obj
        ).values('student').distinct().count()