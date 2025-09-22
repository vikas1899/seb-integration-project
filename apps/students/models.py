from django.db import models
from apps.exams.models import Exam
import uuid


class CompatibilityCheck(models.Model):
    CHECK_TYPES = [
        ('internet_speed', 'Internet Speed'),
        ('device_compatibility', 'Device Compatibility'),
        ('audio_check', 'Audio Check'),
        ('video_check', 'Video Check'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, related_name='compatibility_checks')
    student_identifier = models.CharField(max_length=200)
    check_type = models.CharField(max_length=30, choices=CHECK_TYPES)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending')
    result_data = models.JSONField(default=dict, blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'compatibility_checks'
        unique_together = ['exam', 'student_identifier', 'check_type']
        ordering = ['-checked_at']

    def __str__(self):
        return f"{self.exam.title} - {self.student_identifier} - {self.check_type} ({self.status})"
