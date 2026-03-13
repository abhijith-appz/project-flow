from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ['username', 'email', 'first_name', 'last_name', 'role', 'department', 'is_active']
    list_filter   = ['role', 'department', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'student_id']
    ordering      = ['-date_joined']

    fieldsets = UserAdmin.fieldsets + (
        ('ProjectFlow', {'fields': ('role', 'student_id', 'department', 'bio', 'avatar', 'phone', 'github_url')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('ProjectFlow', {'fields': ('role', 'student_id', 'department')}),
    )
