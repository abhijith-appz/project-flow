from django.db import models
from django.conf import settings


class Notification(models.Model):
    """In-app notification for a user."""

    COLOR_CHOICES = [
        ('blue',  'Blue'),
        ('green', 'Green'),
        ('amber', 'Amber'),
        ('red',   'Red'),
        ('gray',  'Gray'),
    ]

    recipient   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    verb        = models.CharField(max_length=50)   # e.g. "task assigned"
    description = models.TextField()
    icon        = models.CharField(max_length=40, default='fa-bell')  # FontAwesome class
    color       = models.CharField(max_length=6, choices=COLOR_CHOICES, default='blue')
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notif → {self.recipient}: {self.verb}"
