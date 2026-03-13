import os
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


def submission_upload_path(instance, filename):
    return f'submissions/team_{instance.team.id}/{filename}'


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    allowed = getattr(settings, 'ALLOWED_UPLOAD_EXTENSIONS',
                      ['.pdf', '.zip', '.docx', '.pptx', '.ppt', '.doc', '.txt'])
    if ext not in allowed:
        raise ValidationError(f'Unsupported file type "{ext}". Allowed: {", ".join(allowed)}')


class Submission(models.Model):
    """A project file submission by a student team."""

    PHASE_CHOICES = [
        ('phase1', 'Phase 1 — Project Proposal'),
        ('phase2', 'Phase 2 — Mid-term Review'),
        ('phase3', 'Phase 3 — Final Submission'),
    ]
    STATUS_CHOICES = [
        ('pending',  'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('reviewed', 'Reviewed'),
    ]

    team         = models.ForeignKey(
        'teams.Team', on_delete=models.CASCADE, related_name='submissions'
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True,
        related_name='submissions'
    )
    title        = models.CharField(max_length=200)
    description  = models.TextField(blank=True)
    phase        = models.CharField(max_length=6, choices=PHASE_CHOICES, default='phase1')
    file         = models.FileField(
        upload_to=submission_upload_path,
        validators=[validate_file_extension]
    )
    github_url   = models.URLField(blank=True)
    status       = models.CharField(max_length=8, choices=STATUS_CHOICES, default='pending')
    teacher_note = models.TextField(blank=True, help_text='Teacher review note')
    reviewed_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reviewed_submissions',
        limit_choices_to={'role': 'teacher'}
    )
    reviewed_at  = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    version      = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.team.name} | {self.get_phase_display()} | {self.title}"

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    @property
    def file_extension(self):
        return os.path.splitext(self.file.name)[1].lower().lstrip('.')

    @property
    def file_size_mb(self):
        try:
            return round(self.file.size / (1024 * 1024), 1)
        except Exception:
            return 0
