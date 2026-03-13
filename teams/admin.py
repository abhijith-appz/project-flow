from django.contrib import admin
from .models import Team, TeamMembership, Feedback


class MembershipInline(admin.TabularInline):
    model = TeamMembership
    extra = 0
    fields = ['student', 'is_active', 'joined_at']
    readonly_fields = ['joined_at']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display  = ['name', 'project_title', 'leader', 'teacher', 'status', 'member_count', 'progress_percent']
    list_filter   = ['status', 'department']
    search_fields = ['name', 'project_title']
    inlines       = [MembershipInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['team', 'teacher', 'feedback_type', 'rating', 'created_at']
    list_filter  = ['feedback_type', 'rating']
