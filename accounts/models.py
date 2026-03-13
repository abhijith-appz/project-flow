from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended user with role and department."""

    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        TEACHER = 'teacher', 'Teacher'
        ADMIN   = 'admin',   'Admin'

    DEPARTMENT_CHOICES = [
        ('cs',   'Computer Science'),
        ('it',   'Information Technology'),
        ('ece',  'Electronics & Communication'),
        ('mech', 'Mechanical Engineering'),
        ('civil','Civil Engineering'),
        ('other','Other'),
    ]

    role       = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    student_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    department = models.CharField(max_length=10, choices=DEPARTMENT_CHOICES, default='cs')
    bio        = models.TextField(blank=True)
    avatar     = models.ImageField(upload_to='avatars/', blank=True, null=True)

    # Track profile completeness
    phone      = models.CharField(max_length=20, blank=True)
    github_url = models.URLField(blank=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN

    @property
    def initials(self):
        name = self.get_full_name()
        if name:
            parts = name.split()
            return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][:2].upper()
        return self.username[:2].upper()

    @property
    def current_team(self):
        """Return the student's active team membership, if any."""
        membership = self.memberships.filter(is_active=True).select_related('team').first()
        return membership.team if membership else None
