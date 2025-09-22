from rest_framework import serializers
from apps.exams.models import Exam, ExamAttempt
from .models import CompatibilityCheck


class ExamAccessSerializer(serializers.ModelSerializer):
    """Serializer for student exam access (limited information)"""
    exam_datetime = serializers.ReadOnlyField()
    is_exam_time_active = serializers.ReadOnlyField()
    required_checks = serializers.ReadOnlyField()

    class Meta:
        model = Exam
        fields = [
            'id', 'title', 'subject', 'description', 'exam_date', 'exam_time',
            'duration_minutes', 'launch_window_minutes', 'exam_datetime',
            'is_exam_time_active', 'required_checks', 'additional_requirements'
        ]


class CompatibilityCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompatibilityCheck
        fields = ['id', 'check_type', 'status', 'result_data', 'checked_at']


class CompatibilityCheckCreateSerializer(serializers.ModelSerializer):
    exam_link = serializers.CharField(write_only=True)
    student_identifier = serializers.CharField()

    class Meta:
        model = CompatibilityCheck
        fields = ['exam_link', 'student_identifier',
                  'check_type', 'result_data']

    def create(self, validated_data):
        exam_link = validated_data.pop('exam_link')
        try:
            exam = Exam.objects.get(exam_link=exam_link, is_active=True)
            validated_data['exam'] = exam
            # Determine status based on result_data
            result_data = validated_data.get('result_data', {})
            validated_data['status'] = 'passed' if result_data.get(
                'success', False) else 'failed'

            # Update or create compatibility check
            check, created = CompatibilityCheck.objects.update_or_create(
                exam=exam,
                student_identifier=validated_data['student_identifier'],
                check_type=validated_data['check_type'],
                defaults={
                    'status': validated_data['status'],
                    'result_data': validated_data['result_data']
                }
            )
            return check
        except Exam.DoesNotExist:
            raise serializers.ValidationError('Invalid exam link')


class ExamLaunchSerializer(serializers.Serializer):
    exam_link = serializers.CharField()
    student_identifier = serializers.CharField()

    def validate(self, attrs):
        exam_link = attrs.get('exam_link')
        student_identifier = attrs.get('student_identifier')

        try:
            exam = Exam.objects.get(exam_link=exam_link, is_active=True)
            attrs['exam'] = exam

            # Check if exam timing is valid
            if not exam.is_exam_time_active:
                raise serializers.ValidationError(
                    'Exam is not available at this time. Please check the exam schedule.'
                )

            # Check if all required compatibility checks are passed
            if exam.required_checks:
                checks = CompatibilityCheck.objects.filter(
                    exam=exam,
                    student_identifier=student_identifier,
                    check_type__in=exam.required_checks,
                    status='passed'
                )

                if checks.count() != len(exam.required_checks):
                    missing_checks = set(
                        exam.required_checks) - set(checks.values_list('check_type', flat=True))
                    raise serializers.ValidationError(
                        f'Please complete all required compatibility checks: {", ".join(missing_checks)}'
                    )

            return attrs

        except Exam.DoesNotExist:
            raise serializers.ValidationError(
                'Invalid exam link or exam not available')


class ExamAttemptCreateSerializer(serializers.ModelSerializer):
    exam_link = serializers.CharField(write_only=True)

    class Meta:
        model = ExamAttempt
        fields = ['exam_link', 'student_identifier', 'user_agent']

    def create(self, validated_data):
        exam_link = validated_data.pop('exam_link')
        try:
            exam = Exam.objects.get(exam_link=exam_link, is_active=True)
            validated_data['exam'] = exam
            validated_data['ip_address'] = self.context.get('ip_address')

            # Get or create exam attempt
            attempt, created = ExamAttempt.objects.get_or_create(
                exam=exam,
                student_identifier=validated_data['student_identifier'],
                defaults=validated_data
            )

            if not created:
                # Update existing attempt
                attempt.status = 'in_progress'
                attempt.user_agent = validated_data.get(
                    'user_agent', attempt.user_agent)
                attempt.ip_address = validated_data.get(
                    'ip_address', attempt.ip_address)
                attempt.save()

            return attempt
        except Exam.DoesNotExist:
            raise serializers.ValidationError('Invalid exam link')
