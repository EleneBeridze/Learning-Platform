from django.contrib import admin
from .models import Category, Course, Lesson, Enrollment, Progress


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'content_type', 'order', 'duration']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'category', 'difficulty', 'price', 'is_published', 'created_at']
    list_filter = ['is_published', 'difficulty', 'category', 'created_at']
    search_fields = ['title', 'description', 'teacher__username']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(teacher=request.user)
        return qs


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'content_type', 'order', 'duration']
    list_filter = ['content_type', 'course']
    search_fields = ['title', 'course__title']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'progress_percentage', 'completed', 'enrolled_at']
    list_filter = ['completed', 'enrolled_at']
    search_fields = ['student__username', 'course__title']
    readonly_fields = ['progress_percentage', 'completed_at', 'enrolled_at']


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'lesson', 'completed', 'completed_at']
    list_filter = ['completed']
    search_fields = ['enrollment__student__username', 'lesson__title']