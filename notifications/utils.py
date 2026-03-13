from .models import Notification


def notify(recipient, verb, description, icon='fa-bell', color='blue'):
    """Helper to create a notification."""
    Notification.objects.create(
        recipient=recipient,
        verb=verb,
        description=description,
        icon=icon,
        color=color,
    )
