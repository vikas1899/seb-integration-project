import uuid
import hashlib
from django.utils import timezone


def generate_exam_link(exam):
    """Generate a unique exam link based on exam details"""
    base_string = f"{exam.id}-{exam.title}-{exam.exam_date}-{exam.exam_time}"
    hash_object = hashlib.md5(base_string.encode())
    unique_hash = hash_object.hexdigest()[:8]
    return f"exam-{unique_hash}"


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
