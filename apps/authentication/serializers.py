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
        fields = ('email', 'username', 'first_name', 'last_name', 'institution',
                  'password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
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
