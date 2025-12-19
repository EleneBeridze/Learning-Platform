from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify


class Category(models.Model):
    """
    Course categories (e.g., Programming, Design, Business)
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(models.Model):
    """
    Main Course model
    Teachers create courses, students enroll in them
    """
    DIFFICULTY_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )

    # Basic Info
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    description = models.TextField()

    # Relationships
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='taught_courses',
        limit_choices_to={'user_type': 'teacher'}
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses'
    )

    # Media
    thumbnail = models.ImageField(
        upload_to='courses/%Y/%m/',
        blank=True,
        null=True,
        help_text='Course thumbnail image'
    )

    # Course Details
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='beginner'
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text='Course price (0 for free courses)'
    )
    duration = models.PositiveIntegerField(
        default=0,
        help_text='Total course duration in hours'
    )

    # Status
    is_published = models.BooleanField(
        default=False,
        help_text='Course visibility status'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def is_free(self):
        """Check if course is free"""
        return self.price == 0


class Lesson(models.Model):
    """
    Individual lessons within a course
    """
    CONTENT_TYPE_CHOICES = (
        ('video', 'Video'),
        ('text', 'Text'),
        ('file', 'File'),
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Content
    content_type = models.CharField(
        max_length=10,
        choices=CONTENT_TYPE_CHOICES,
        default='text'
    )
    content = models.TextField(
        blank=True,
        help_text='Text content or video embed code'
    )
    video_url = models.URLField(
        blank=True,
        help_text='YouTube or Vimeo URL'
    )
    file = models.FileField(
        upload_to='lessons/%Y/%m/',
        blank=True,
        null=True,
        help_text='Downloadable file (PDF, etc.)'
    )

    # Ordering
    order = models.PositiveIntegerField(
        default=0,
        help_text='Lesson order in course'
    )
    duration = models.PositiveIntegerField(
        default=0,
        help_text='Lesson duration in minutes'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['course', 'order']
        unique_together = ['course', 'order']
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Enrollment(models.Model):
    """
    Student enrollment in courses
    Links students to courses they're enrolled in
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'user_type': 'student'}
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    # Status
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Progress
    progress_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
        help_text='Course completion percentage'
    )

    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"

    def update_progress(self):
        """
        Calculate and update progress percentage
        Based on completed lessons
        """
        total_lessons = self.course.lessons.count()
        if total_lessons == 0:
            self.progress_percentage = 0
        else:
            completed_lessons = self.progress_records.filter(completed=True).count()
            self.progress_percentage = int((completed_lessons / total_lessons) * 100)

        # Mark as completed if 100%
        if self.progress_percentage == 100 and not self.completed:
            from django.utils import timezone
            self.completed = True
            self.completed_at = timezone.now()

        self.save()


class Progress(models.Model):
    """
    Track individual lesson completion
    """
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='progress_records'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE
    )

    # Status
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['enrollment', 'lesson']
        verbose_name = 'Progress'
        verbose_name_plural = 'Progress Records'
        ordering = ['lesson__order']

    def __str__(self):
        status = "✓" if self.completed else "○"
        return f"{status} {self.enrollment.student.username} - {self.lesson.title}"

    def save(self, *args, **kwargs):
        # Set completed_at when marking as complete
        if self.completed and not self.completed_at:
            from django.utils import timezone
            self.completed_at = timezone.now()

        super().save(*args, **kwargs)

        # Update enrollment progress
        self.enrollment.update_progress()