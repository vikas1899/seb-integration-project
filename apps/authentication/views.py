from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import (
    TeacherRegistrationSerializer,
    TeacherLoginSerializer,
    TeacherProfileSerializer
)


@swagger_auto_schema(
    method='post',
    request_body=TeacherRegistrationSerializer,
    responses={
        201: openapi.Response('Teacher created successfully', TeacherProfileSerializer),
        400: 'Bad Request - Validation errors'
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new teacher account"""
    serializer = TeacherRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        teacher = serializer.save()
        refresh = RefreshToken.for_user(teacher)
        return Response({
            'message': 'Teacher registered successfully',
            'teacher': TeacherProfileSerializer(teacher).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    request_body=TeacherLoginSerializer,
    responses={
        200: openapi.Response(
            'Login successful',
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'teacher': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'tokens': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'access': openapi.Schema(type=openapi.TYPE_STRING),
                            'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                }
            )
        ),
        400: 'Bad Request - Invalid credentials'
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login teacher and return JWT tokens"""
    serializer = TeacherLoginSerializer(data=request.data)
    if serializer.is_valid():
        teacher = serializer.validated_data['teacher']
        refresh = RefreshToken.for_user(teacher)
        return Response({
            'message': 'Login successful',
            'teacher': TeacherProfileSerializer(teacher).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    responses={200: TeacherProfileSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Get teacher profile information"""
    serializer = TeacherProfileSerializer(request.user)
    return Response(serializer.data)


@swagger_auto_schema(
    method='put',
    request_body=TeacherProfileSerializer,
    responses={200: TeacherProfileSerializer}
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update teacher profile information"""
    serializer = TeacherProfileSerializer(
        request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
