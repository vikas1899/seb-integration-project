from django.contrib import admin
from .models import CompatibilityCheck


@admin.register(CompatibilityCheck)
class CompatibilityCheckAdmin(admin.ModelAdmin):
    list_display = ('exam', 'student_identifier',
                    'check_type', 'status', 'checked_at')
    list_filter = ('check_type', 'status', 'checked_at', 'exam__subject')
    search_fields = ('student_identifier', 'exam__title', 'exam__subject')
    readonly_fields = ('id', 'checked_at')
    ordering = ('-checked_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('exam', 'exam__teacher')
