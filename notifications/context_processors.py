from .models import Notification


def unread_notifications(request):
    if request.user.is_authenticated:
        unread = Notification.objects.filter(recipient=request.user, is_read=False)
        # pending_submissions_count for teacher sidebar badge
        pending_submissions_count = 0
        if hasattr(request.user, 'is_teacher') and request.user.is_teacher:
            from submissions.models import Submission
            team_ids = request.user.supervised_teams.values_list('id', flat=True)
            pending_submissions_count = Submission.objects.filter(
                team_id__in=team_ids, status='pending'
            ).count()
        # tasks_pending for student sidebar badge
        tasks_pending = 0
        if hasattr(request.user, 'is_student') and request.user.is_student:
            team = request.user.current_team
            if team:
                tasks_pending = team.tasks.filter(
                    assigned_to=request.user, status='pending'
                ).count()
        return {
            'unread_notifications': unread[:10],
            'unread_count': unread.count(),
            'pending_submissions_count': pending_submissions_count,
            'tasks_pending': tasks_pending,
        }
    return {
        'unread_notifications': [],
        'unread_count': 0,
        'pending_submissions_count': 0,
        'tasks_pending': 0,
    }
