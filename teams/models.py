from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Team(models.Model):
    """A student project team (5–6 members)."""

    STATUS_CHOICES = [
        ('forming',  'Forming'),
        ('active',   'Active'),
        ('at_risk',  'At Risk'),
        ('completed','Completed'),
        ('inactive', 'Inactive'),
    ]

    DEPARTMENT_CHOICES = [
        ('cs',   'Computer Science'),
        ('it',   'Information Technology'),
        ('ece',  'Electronics & Communication'),
        ('mech', 'Mechanical Engineering'),
        ('civil','Civil Engineering'),
        ('other','Other'),
    ]

    name        = models.CharField(max_length=100, unique=True)
    project_title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    department  = models.CharField(max_length=10, choices=DEPARTMENT_CHOICES, default='cs')
    teacher     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='supervised_teams',
        limit_choices_to={'role': 'teacher'}
    )
    leader      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='led_teams',
        limit_choices_to={'role': 'student'}
    )
    status       = models.CharField(max_length=12, choices=STATUS_CHOICES, default='forming')
    github_url   = models.URLField(blank=True)
    max_members  = models.PositiveSmallIntegerField(default=6)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.project_title}"

    @property
    def member_count(self):
        return self.memberships.filter(is_active=True).count()

    @property
    def is_full(self):
        return self.member_count >= self.max_members

    @property
    def progress_percent(self):
        tasks = self.tasks.all()
        total = tasks.count()
        if total == 0:
            return 0
        done = tasks.filter(status='completed').count()
        return round((done / total) * 100)

    @property
    def active_members(self):
        return self.memberships.filter(is_active=True).select_related('student')


class TeamMembership(models.Model):
    """Links a student to a team."""
    team      = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='memberships')
    student   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memberships',
        limit_choices_to={'role': 'student'}
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('team', 'student')
        ordering = ['joined_at']

    def __str__(self):
        return f"{self.student} → {self.team.name}"


class Feedback(models.Model):
    """Teacher feedback on a team."""

    FEEDBACK_TYPE_CHOICES = [
        ('general',   'General Feedback'),
        ('code',      'Code Review'),
        ('docs',      'Documentation Review'),
        ('slides',    'Presentation Feedback'),
    ]

    team        = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='feedback_list')
    teacher     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='given_feedback',
        limit_choices_to={'role': 'teacher'}
    )
    feedback_type = models.CharField(max_length=10, choices=FEEDBACK_TYPE_CHOICES, default='general')
    message     = models.TextField()
    rating      = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback by {self.teacher} on {self.team.name}"

    @property
    def star_range(self):
        return range(self.rating or 0)
