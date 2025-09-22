from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.exams.models import Exam, ExamAttempt
from .models import CompatibilityCheck
from .serializers import (
    ExamAccessSerializer, CompatibilityCheckSerializer,
    CompatibilityCheckCreateSerializer, ExamLaunchSerializer,
    ExamAttemptCreateSerializer
)
from .utils import get_client_ip


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'exam_link',
            openapi.IN_PATH,
            description="Unique exam link",
            type=openapi.TYPE_STRING
        )
    ],
    responses={
        200: ExamAccessSerializer,
        404: 'Exam not found or inactive'
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def exam_access(request, exam_link):
    """Get exam information for students using exam link"""
    try:
        exam = Exam.objects.get(exam_link=exam_link, is_active=True)
        serializer = ExamAccessSerializer(exam)
        return Response(serializer.data)
    except Exam.DoesNotExist:
        return Response(
            {'error': 'Exam not found or no longer available'},
            status=status.HTTP_404_NOT_FOUND
        )


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('exam_link', openapi.IN_QUERY,
                          type=openapi.TYPE_STRING),
        openapi.Parameter('student_identifier',
                          openapi.IN_QUERY, type=openapi.TYPE_STRING)
    ],
    responses={200: CompatibilityCheckSerializer(many=True)}
)
@swagger_auto_schema(
    method='post',
    request_body=CompatibilityCheckCreateSerializer,
    responses={201: CompatibilityCheckSerializer}
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def compatibility_checks(request):
    """Handle compatibility checks for students"""
    if request.method == 'GET':
        exam_link = request.query_params.get('exam_link')
        student_identifier = request.query_params.get('student_identifier')

        if not exam_link or not student_identifier:
            return Response(
                {'error': 'exam_link and student_identifier are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            exam = Exam.objects.get(exam_link=exam_link, is_active=True)
            checks = CompatibilityCheck.objects.filter(
                exam=exam,
                student_identifier=student_identifier
            )
            serializer = CompatibilityCheckSerializer(checks, many=True)
            return Response(serializer.data)
        except Exam.DoesNotExist:
            return Response(
                {'error': 'Invalid exam link'},
                status=status.HTTP_404_NOT_FOUND
            )

    elif request.method == 'POST':
        serializer = CompatibilityCheckCreateSerializer(data=request.data)
        if serializer.is_valid():
            check = serializer.save()
            return Response(
                CompatibilityCheckSerializer(check).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    request_body=ExamLaunchSerializer,
    responses={
        200: openapi.Response(
            'Exam launch successful',
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'seb_config_url': openapi.Schema(type=openapi.TYPE_STRING),
                    'exam_attempt_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: 'Bad Request - Validation errors'
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def launch_exam(request):
    """Launch exam after all compatibility checks are passed"""
    serializer = ExamLaunchSerializer(data=request.data)
    if serializer.is_valid():
        exam = serializer.validated_data['exam']
        student_identifier = serializer.validated_data['student_identifier']

        # Create exam attempt
        attempt_serializer = ExamAttemptCreateSerializer(
            data={
                'exam_link': exam.exam_link,
                'student_identifier': student_identifier,
                'user_agent': request.META.get('HTTP_USER_AGENT', '')
            },
            context={'ip_address': get_client_ip(request)}
        )

        if attempt_serializer.is_valid():
            attempt = attempt_serializer.save()

            # Return SEB config download URL
            return Response({
                'success': True,
                'seb_config_url': f'/api/students/seb-config/{exam.exam_link}/?student={student_identifier}',
                'exam_attempt_id': str(attempt.id),
                'message': 'Exam launched successfully. Download the SEB configuration file.'
            })

        return Response(attempt_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'exam_link',
            openapi.IN_PATH,
            description="Unique exam link",
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'student',
            openapi.IN_QUERY,
            description="Student identifier",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response('SEB configuration file', schema=openapi.Schema(type=openapi.TYPE_FILE)),
        403: 'Access denied - compatibility checks not passed',
        404: 'Exam not found'
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def download_seb_config(request, exam_link):
    """Download SEB configuration file for the exam"""
    student_identifier = request.query_params.get('student')

    if not student_identifier:
        return Response(
            {'error': 'Student identifier is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        exam = Exam.objects.get(exam_link=exam_link, is_active=True)

        # Verify exam timing
        if not exam.is_exam_time_active:
            return Response(
                {'error': 'Exam is not available at this time'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Verify compatibility checks are passed
        if exam.required_checks:
            passed_checks = CompatibilityCheck.objects.filter(
                exam=exam,
                student_identifier=student_identifier,
                check_type__in=exam.required_checks,
                status='passed'
            ).count()

            if passed_checks != len(exam.required_checks):
                return Response(
                    {'error': 'All compatibility checks must be passed before launching the exam'},
                    status=status.HTTP_403_FORBIDDEN
                )

        # Serve the SEB config file
        if exam.seb_config_file:
            response = HttpResponse(
                exam.seb_config_file.read(),
                content_type='application/x-sebconfiguration'
            )
            response['Content-Disposition'] = f'attachment; filename="{exam.title}_config.seb"'
            return response
        else:
            return Response(
                {'error': 'SEB configuration file not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    except Exam.DoesNotExist:
        return Response(
            {'error': 'Invalid exam link'},
            status=status.HTTP_404_NOT_FOUND
        )


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'exam_link': openapi.Schema(type=openapi.TYPE_STRING),
            'student_identifier': openapi.Schema(type=openapi.TYPE_STRING),
            'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['completed', 'abandoned'])
        }
    ),
    responses={200: 'Exam attempt updated successfully'}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def complete_exam(request):
    """Mark exam attempt as completed"""
    exam_link = request.data.get('exam_link')
    student_identifier = request.data.get('student_identifier')
    attempt_status = request.data.get('status', 'completed')

    try:
        exam = Exam.objects.get(exam_link=exam_link, is_active=True)
        attempt = ExamAttempt.objects.get(
            exam=exam,
            student_identifier=student_identifier
        )

        attempt.status = attempt_status
        if attempt_status == 'completed':
            from django.utils import timezone
            attempt.completed_at = timezone.now()
        attempt.save()

        return Response({
            'success': True,
            'message': f'Exam attempt marked as {attempt_status}'
        })

    except (Exam.DoesNotExist, ExamAttempt.DoesNotExist):
        return Response(
            {'error': 'Exam or attempt not found'},
            status=status.HTTP_404_NOT_FOUND
        )
