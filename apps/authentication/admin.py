from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name',
                    'institution', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'institution')
    search_fields = ('email', 'first_name', 'last_name', 'institution')
    ordering = ('-created_at',)

    fieldsets = UserAdmin.fieldsets + (('Additional Info', {'fields': ('institution',)}),
                                       )
