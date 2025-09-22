from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Exam, ExamAttempt
from .serializers import (
    ExamCreateSerializer, ExamListSerializer, ExamDetailSerializer,
    ExamUpdateSerializer, ExamAttemptSerializer
)
from .utils import generate_exam_link


@swagger_auto_schema(
    method='get',
    responses={200: ExamListSerializer(many=True)}
)
@swagger_auto_schema(
    method='post',
    request_body=ExamCreateSerializer,
    responses={201: ExamDetailSerializer}
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def exam_list_create(request):
    """List all exams for authenticated teacher or create a new exam"""
    if request.method == 'GET':
        exams = Exam.objects.filter(teacher=request.user)
        serializer = ExamListSerializer(exams, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ExamCreateSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            exam = serializer.save()
            return Response(
                ExamDetailSerializer(exam).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    responses={200: ExamDetailSerializer}
)
@swagger_auto_schema(
    method='put',
    request_body=ExamUpdateSerializer,
    responses={200: ExamDetailSerializer}
)
@swagger_auto_schema(
    method='delete',
    responses={204: 'Exam deleted successfully'}
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def exam_detail(request, exam_id):
    """Retrieve, update or delete an exam"""
    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)

    if request.method == 'GET':
        serializer = ExamDetailSerializer(exam)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ExamUpdateSerializer(
            exam, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(ExamDetailSerializer(exam).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        exam.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='post',
    request_body=ExamCreateSerializer,
    responses={201: ExamDetailSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def duplicate_exam(request, exam_id):
    """Duplicate an existing exam"""
    original_exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)

    # Create a copy of the exam
    exam_data = {
        'title': f"Copy of {original_exam.title}",
        'subject': original_exam.subject,
        'description': original_exam.description,
        'exam_date': request.data.get('exam_date', original_exam.exam_date),
        'exam_time': request.data.get('exam_time', original_exam.exam_time),
        'duration_minutes': original_exam.duration_minutes,
        'launch_window_minutes': original_exam.launch_window_minutes,
        'required_checks': original_exam.required_checks,
        'additional_requirements': original_exam.additional_requirements,
    }

    serializer = ExamCreateSerializer(
        data=exam_data, context={'request': request})
    if serializer.is_valid():
        new_exam = serializer.save()
        # Copy the SEB config file if it exists
        if original_exam.seb_config_file:
            # Note: In production, you'd want to copy the actual file
            new_exam.seb_config_file = original_exam.seb_config_file
            new_exam.save()

        return Response(
            ExamDetailSerializer(new_exam).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    responses={200: ExamAttemptSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exam_attempts(request, exam_id):
    """List all attempts for a specific exam"""
    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)
    attempts = ExamAttempt.objects.filter(exam=exam)
    serializer = ExamAttemptSerializer(attempts, many=True)
    return Response(serializer.data)
