from django.db import models
from django.utils import timezone
from apps.authentication.models import Teacher
import uuid
import os


def seb_config_upload_path(instance, filename):
    return f'seb_configs/{instance.teacher.id}/{instance.id}/{filename}'


class Exam(models.Model):
    COMPATIBILITY_CHOICES = [
        ('internet_speed', 'Internet Speed Check'),
        ('device_compatibility', 'Device Compatibility Check'),
        ('audio_check', 'Audio Check'),
        ('video_check', 'Video Check'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name='exams')
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    # Exam timing
    exam_date = models.DateField()
    exam_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField()
    launch_window_minutes = models.PositiveIntegerField(default=30)

    # SEB Configuration
    seb_config_file = models.FileField(
        upload_to=seb_config_upload_path,
        help_text="Upload .seb configuration file"
    )

    # Compatibility requirements
    required_checks = models.JSONField(
        default=list,
        help_text="List of required compatibility checks"
    )

    # Additional requirements
    additional_requirements = models.TextField(blank=True, null=True)

    # Exam link and status
    exam_link = models.CharField(max_length=200, unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'exams'
        ordering = ['-created_at']
        verbose_name = 'Exam'
        verbose_name_plural = 'Exams'

    def __str__(self):
        return f"{self.title} - {self.subject} ({self.exam_date})"

    @property
    def exam_datetime(self):
        return timezone.datetime.combine(self.exam_date, self.exam_time)

    @property
    def is_exam_time_active(self):
        """Check if current time is within the launch window"""
        now = timezone.now()
        exam_start = self.exam_datetime.replace(tzinfo=timezone.utc)
        launch_end = exam_start + \
            timezone.timedelta(minutes=self.launch_window_minutes)
        return exam_start <= now <= launch_end

    def save(self, *args, **kwargs):
        if not self.exam_link:
            self.exam_link = f"exam-{self.id}"
        super().save(*args, **kwargs)


class ExamAttempt(models.Model):
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, related_name='attempts')
    student_identifier = models.CharField(
        max_length=200)  # Could be email or student ID

    # Compatibility check results
    compatibility_results = models.JSONField(default=dict)
    all_checks_passed = models.BooleanField(default=False)

    # Attempt tracking
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='started')

    # Browser and system info
    user_agent = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        db_table = 'exam_attempts'
        ordering = ['-started_at']
        unique_together = ['exam', 'student_identifier']

    def __str__(self):
        return f"{self.exam.title} - {self.student_identifier} ({self.status})"
