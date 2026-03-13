from django.contrib import admin
from .models import Submission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display  = ['title', 'team', 'submitted_by', 'phase', 'status', 'version', 'submitted_at']
    list_filter   = ['phase', 'status']
    search_fields = ['title', 'team__name']
    readonly_fields = ['submitted_at', 'reviewed_at', 'version']
