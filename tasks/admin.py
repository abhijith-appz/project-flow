from django.contrib import admin
from .models import Task, TaskComment


class CommentInline(admin.TabularInline):
    model  = TaskComment
    extra  = 0
    fields = ['author', 'content', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display  = ['title', 'team', 'assigned_to', 'priority', 'status', 'deadline', 'is_overdue']
    list_filter   = ['status', 'priority', 'team']
    search_fields = ['title', 'team__name', 'assigned_to__username']
    inlines       = [CommentInline]
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
