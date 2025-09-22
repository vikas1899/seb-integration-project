def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def validate_compatibility_check_data(check_type, result_data):
    """Validate compatibility check result data based on check type"""
    if check_type == 'internet_speed':
        required_fields = ['download_speed', 'upload_speed', 'ping']
        return all(field in result_data for field in required_fields)

    elif check_type == 'device_compatibility':
        required_fields = ['os', 'browser', 'browser_version']
        return all(field in result_data for field in required_fields)

    elif check_type in ['audio_check', 'video_check']:
        return 'device_available' in result_data and 'test_passed' in result_data

    return True
