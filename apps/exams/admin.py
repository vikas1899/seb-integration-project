from django.contrib import admin
from .models import Exam, ExamAttempt


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'teacher', 'exam_date', 'exam_time',
                    'duration_minutes', 'is_active', 'created_at')
    list_filter = ('subject', 'exam_date', 'is_active', 'created_at')
    search_fields = ('title', 'subject', 'teacher__email',
                     'teacher__first_name', 'teacher__last_name')
    readonly_fields = ('id', 'exam_link', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'teacher', 'title', 'subject', 'description')
        }),
        ('Exam Schedule', {
            'fields': ('exam_date', 'exam_time', 'duration_minutes', 'launch_window_minutes')
        }),
        ('Configuration', {
            'fields': ('seb_config_file', 'required_checks', 'additional_requirements')
        }),
        ('Access', {
            'fields': ('exam_link', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('exam', 'student_identifier', 'status', 'all_checks_passed',
                    'started_at', 'completed_at')
    list_filter = ('status', 'all_checks_passed',
                   'started_at', 'exam__subject')
    search_fields = ('student_identifier', 'exam__title', 'exam__subject')
    readonly_fields = ('id', 'started_at', 'ip_address', 'user_agent')
    ordering = ('-started_at',)
