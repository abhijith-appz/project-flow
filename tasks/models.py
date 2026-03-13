from django.db import models
from django.conf import settings
from django.utils import timezone


class Task(models.Model):
    """A project task assigned to a team member."""

    PRIORITY_CHOICES = [
        ('low',    'Low'),
        ('medium', 'Medium'),
        ('high',   'High'),
    ]
    STATUS_CHOICES = [
        ('pending',     'Pending'),
        ('in_progress', 'In Progress'),
        ('completed',   'Completed'),
        ('overdue',     'Overdue'),
    ]

    team        = models.ForeignKey(
        'teams.Team', on_delete=models.CASCADE, related_name='tasks'
    )
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_tasks'
    )
    created_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks'
    )
    priority    = models.CharField(max_length=6,  choices=PRIORITY_CHOICES, default='medium')
    status      = models.CharField(max_length=12, choices=STATUS_CHOICES,   default='pending')
    deadline    = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['deadline', '-priority']

    def __str__(self):
        return f"[{self.team.name}] {self.title}"

    @property
    def is_overdue(self):
        if self.deadline and self.status != 'completed':
            return self.deadline < timezone.now().date()
        return False

    def save(self, *args, **kwargs):
        # Auto-mark overdue
        if self.is_overdue and self.status == 'pending':
            self.status = 'overdue'
        super().save(*args, **kwargs)


class TaskComment(models.Model):
    """Comments on a task."""
    task       = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on '{self.task.title}'"
