from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Task, TaskComment
from .forms import TaskForm, TaskCommentForm
from teams.models import Team
from notifications.utils import notify


def _get_team_or_403(user):
    """Return user's active team, or None with an error message."""
    team = user.current_team
    return team


@login_required
def task_list_view(request):
    user   = request.user
    status = request.GET.get('status', '')
    search = request.GET.get('q', '')

    if user.is_student:
        team = _get_team_or_403(user)
        if not team:
            messages.info(request, 'You need to join a team to see tasks.')
            return redirect('teams:list')
        tasks = team.tasks.select_related('assigned_to', 'created_by')
    else:
        # Teacher sees all tasks for their supervised teams
        team_ids = user.supervised_teams.values_list('id', flat=True)
        tasks    = Task.objects.filter(team_id__in=team_ids).select_related('team', 'assigned_to')
        team     = None

    if status:
        tasks = tasks.filter(status=status)
    if search:
        tasks = tasks.filter(title__icontains=search)

    # Stats
    all_tasks    = tasks if user.is_teacher else team.tasks.all() if team else Task.objects.none()
    total        = all_tasks.count()
    completed    = all_tasks.filter(status='completed').count()
    pending      = all_tasks.filter(status='pending').count()
    in_progress  = all_tasks.filter(status='in_progress').count()
    overdue      = all_tasks.filter(status='overdue').count()

    context = {
        'tasks': tasks,
        'team':  team,
        'total': total, 'completed': completed, 'pending': pending,
        'in_progress': in_progress, 'overdue': overdue,
        'status_filter': status,
        'search': search,
        'active_nav': 'tasks',
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_create_view(request):
    user = request.user
    team = _get_team_or_403(user)

    if not team:
        messages.error(request, 'You must be in a team to create tasks.')
        return redirect('teams:list')

    # Only team leader or teacher can create tasks
    if user.is_student and team.leader != user:
        messages.error(request, 'Only the team leader can create tasks.')
        return redirect('tasks:list')

    if request.method == 'POST':
        form = TaskForm(request.POST, team=team)
        if form.is_valid():
            task = form.save(commit=False)
            task.team       = team
            task.created_by = user
            task.save()
            # Notify the assigned member
            if task.assigned_to and task.assigned_to != user:
                notify(
                    recipient=task.assigned_to,
                    verb='task assigned',
                    description=f'You were assigned task "{task.title}" in {team.name}.',
                    icon='fa-tasks',
                    color='blue',
                )
            messages.success(request, f'Task "{task.title}" created.')
            return redirect('tasks:list')
    else:
        form = TaskForm(team=team)

    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Create', 'team': team})


@login_required
def task_detail_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    user = request.user

    # Access control
    if user.is_student:
        team = user.current_team
        if not team or task.team != team:
            messages.error(request, 'You do not have access to this task.')
            return redirect('tasks:list')

    comments    = task.comments.select_related('author').all()
    comment_form = TaskCommentForm()

    if request.method == 'POST':
        comment_form = TaskCommentForm(request.POST)
        if comment_form.is_valid():
            c = comment_form.save(commit=False)
            c.task   = task
            c.author = user
            c.save()
            messages.success(request, 'Comment added.')
            return redirect('tasks:detail', pk=pk)

    context = {
        'task': task,
        'comments': comments,
        'comment_form': comment_form,
        'can_edit': user == task.assigned_to or user == task.team.leader or user.is_teacher,
    }
    return render(request, 'tasks/task_detail.html', context)


@login_required
def task_update_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    user = request.user

    if user.is_student and task.team.leader != user and task.assigned_to != user:
        messages.error(request, 'You are not allowed to edit this task.')
        return redirect('tasks:list')

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, team=task.team)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated.')
            return redirect('tasks:detail', pk=pk)
    else:
        form = TaskForm(instance=task, team=task.team)

    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Update', 'task': task})


@login_required
@require_POST
def task_mark_complete_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    user = request.user

    if user.is_student and task.assigned_to != user and task.team.leader != user:
        return JsonResponse({'error': 'Not allowed'}, status=403)

    task.status       = 'completed'
    task.completed_at = timezone.now()
    task.save()

    # Notify leader
    if task.team.leader and task.team.leader != user:
        notify(
            recipient=task.team.leader,
            verb='task completed',
            description=f'{user.get_full_name()} completed task "{task.title}".',
            icon='fa-check-circle',
            color='green',
        )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'completed', 'progress': task.team.progress_percent})

    messages.success(request, f'Task "{task.title}" marked as complete.')
    return redirect('tasks:list')


@login_required
@require_POST
def task_delete_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    user = request.user

    if user.is_student and task.team.leader != user:
        messages.error(request, 'Only the team leader can delete tasks.')
        return redirect('tasks:list')

    name = task.title
    task.delete()
    messages.success(request, f'Task "{name}" deleted.')
    return redirect('tasks:list')
