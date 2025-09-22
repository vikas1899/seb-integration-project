from rest_framework import serializers
from .models import Exam, ExamAttempt


class ExamCreateSerializer(serializers.ModelSerializer):
    required_checks = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of required compatibility checks"
    )

    class Meta:
        model = Exam
        fields = [
            'title', 'subject', 'description', 'exam_date', 'exam_time',
            'duration_minutes', 'launch_window_minutes', 'seb_config_file',
            'required_checks', 'additional_requirements'
        ]

    def create(self, validated_data):
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)


class ExamListSerializer(serializers.ModelSerializer):
    exam_datetime = serializers.ReadOnlyField()
    is_exam_time_active = serializers.ReadOnlyField()
    attempts_count = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = [
            'id', 'title', 'subject', 'description', 'exam_date', 'exam_time',
            'duration_minutes', 'exam_datetime', 'is_exam_time_active',
            'exam_link', 'is_active', 'attempts_count', 'created_at', 'updated_at'
        ]

    def get_attempts_count(self, obj):
        return obj.attempts.count()


class ExamDetailSerializer(serializers.ModelSerializer):
    exam_datetime = serializers.ReadOnlyField()
    is_exam_time_active = serializers.ReadOnlyField()
    attempts = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = [
            'id', 'title', 'subject', 'description', 'exam_date', 'exam_time',
            'duration_minutes', 'launch_window_minutes', 'required_checks',
            'additional_requirements', 'exam_datetime', 'is_exam_time_active',
            'exam_link', 'is_active', 'attempts', 'created_at', 'updated_at'
        ]

    def get_attempts(self, obj):
        attempts = obj.attempts.all()[:10]  # Latest 10 attempts
        return ExamAttemptSerializer(attempts, many=True).data


class ExamUpdateSerializer(serializers.ModelSerializer):
    required_checks = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

    class Meta:
        model = Exam
        fields = [
            'title', 'subject', 'description', 'exam_date', 'exam_time',
            'duration_minutes', 'launch_window_minutes', 'required_checks',
            'additional_requirements', 'is_active'
        ]


class ExamAttemptSerializer(serializers.ModelSerializer):
    exam_title = serializers.CharField(source='exam.title', read_only=True)

    class Meta:
        model = ExamAttempt
        fields = [
            'id', 'exam_title', 'student_identifier', 'compatibility_results',
            'all_checks_passed', 'status', 'started_at', 'completed_at',
            'user_agent', 'ip_address'
        ]
