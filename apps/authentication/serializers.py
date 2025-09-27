# apps/authentication/serializers.py

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import Teacher


class TeacherRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = Teacher
        # Remove 'username' from the fields the client needs to provide
        fields = ('email', 'first_name', 'last_name', 'institution',
                  'password', 'password_confirm')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        # Check if passwords match
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."})

        # Check if email already exists
        if Teacher.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError(
                {"email": "A user with that email already exists."})

        return attrs

    def create(self, validated_data):
        # Remove the confirmation password from the data
        validated_data.pop('password_confirm')

        # Automatically set the username to be the same as the email
        validated_data['username'] = validated_data['email']

        # Create the new teacher user
        teacher = Teacher.objects.create_user(**validated_data)
        return teacher


class TeacherLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            teacher = authenticate(username=email, password=password)
            if not teacher:
                raise serializers.ValidationError('Invalid credentials')
            if not teacher.is_active:
                raise serializers.ValidationError('Account is deactivated')
            attrs['teacher'] = teacher
        return attrs


class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'institution', 'created_at')
        read_only_fields = ('id', 'email', 'created_at')
