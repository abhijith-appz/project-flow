from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification


@login_required
def notification_list_view(request):
    notifs = request.user.notifications.all()
    # Mark all as read when viewed
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications/list.html', {
        'notifications': notifs,
        'active_nav': 'notifications',
    })


@login_required
@require_POST
def mark_read_view(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    return redirect('notifications:list')


@login_required
@require_POST
def mark_all_read_view(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('notifications:list')
