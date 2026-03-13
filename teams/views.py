from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Team, TeamMembership, Feedback
from .forms import TeamCreateForm, FeedbackForm
from notifications.utils import notify


@login_required
def team_list_view(request):
    """List all teams — filtered for teachers; show own team + available for students."""
    user = request.user
    search = request.GET.get('q', '')
    dept   = request.GET.get('dept', '')
    status = request.GET.get('status', '')

    teams = Team.objects.prefetch_related('memberships__student').select_related('leader', 'teacher')

    if search:
        teams = teams.filter(Q(name__icontains=search) | Q(project_title__icontains=search))
    if dept:
        teams = teams.filter(department=dept)
    if status:
        teams = teams.filter(status=status)

    if user.is_student:
        my_team     = user.current_team
        other_teams = teams.exclude(id=my_team.id) if my_team else teams
        return render(request, 'teams/student_teams.html', {
            'my_team': my_team,
            'other_teams': other_teams,
            'search': search,
            'active_nav': 'teams',
        })
    else:
        return render(request, 'teams/teacher_teams.html', {
            'teams': teams,
            'search': search,
            'dept': dept,
            'status': status,
            'active_nav': 'teams',
        })


@login_required
def team_detail_view(request, pk):
    team = get_object_or_404(Team, pk=pk)
    user = request.user

    # Students can only view their own team's full detail
    if user.is_student and user.current_team != team:
        messages.warning(request, 'You can only view your own team details.')
        return redirect('teams:list')

    tasks     = team.tasks.order_by('deadline')
    feedback  = team.feedback_list.select_related('teacher').all()[:10]
    members   = team.memberships.filter(is_active=True).select_related('student')
    files     = team.submissions.order_by('-submitted_at')

    context = {
        'team': team,
        'tasks': tasks,
        'feedback': feedback,
        'members': members,
        'files': files,
        'is_leader': team.leader == user,
    }
    return render(request, 'teams/team_detail.html', context)


@login_required
def team_create_view(request):
    if not request.user.is_student:
        messages.error(request, 'Only students can create teams.')
        return redirect('teams:list')
    if request.user.current_team:
        messages.warning(request, 'You are already in a team. Leave it first to create a new one.')
        return redirect('teams:list')

    if request.method == 'POST':
        form = TeamCreateForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.leader = request.user
            team.save()
            # Add creator as first member
            TeamMembership.objects.create(team=team, student=request.user)
            messages.success(request, f'Team "{team.name}" created successfully!')
            notify(
                recipient=request.user,
                verb='created',
                description=f'You created team "{team.name}".',
                icon='fa-users',
                color='green',
            )
            return redirect('teams:detail', pk=team.pk)
    else:
        form = TeamCreateForm()
    return render(request, 'teams/team_form.html', {'form': form, 'action': 'Create'})


@login_required
@require_POST
def team_join_view(request, pk):
    team = get_object_or_404(Team, pk=pk)
    user = request.user

    if not user.is_student:
        messages.error(request, 'Only students can join teams.')
        return redirect('teams:list')
    if user.current_team:
        messages.warning(request, 'You must leave your current team first.')
        return redirect('teams:list')
    if team.is_full:
        messages.error(request, f'Team "{team.name}" is full (max {team.max_members} members).')
        return redirect('teams:list')

    TeamMembership.objects.create(team=team, student=user)
    messages.success(request, f'You joined "{team.name}"!')
    notify(
        recipient=user,
        verb='joined',
        description=f'You joined team "{team.name}".',
        icon='fa-user-plus',
        color='blue',
    )
    # Notify team leader
    if team.leader:
        notify(
            recipient=team.leader,
            verb='new member',
            description=f'{user.get_full_name()} joined your team.',
            icon='fa-user-plus',
            color='green',
        )
    return redirect('teams:detail', pk=team.pk)


@login_required
@require_POST
def team_leave_view(request, pk):
    team = get_object_or_404(Team, pk=pk)
    user = request.user

    membership = TeamMembership.objects.filter(team=team, student=user, is_active=True).first()
    if not membership:
        messages.error(request, 'You are not a member of this team.')
        return redirect('teams:list')

    membership.is_active = False
    membership.save()

    # If leader leaves, assign a new one
    if team.leader == user:
        next_member = team.memberships.filter(is_active=True).exclude(student=user).first()
        team.leader = next_member.student if next_member else None
        team.save()

    messages.info(request, f'You left team "{team.name}".')
    return redirect('teams:list')


@login_required
def give_feedback_view(request, team_pk):
    if not request.user.is_teacher:
        messages.error(request, 'Only teachers can give feedback.')
        return redirect('teams:list')

    team = get_object_or_404(Team, pk=team_pk)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            fb = form.save(commit=False)
            fb.team    = team
            fb.teacher = request.user
            fb.save()
            # Notify all team members
            for m in team.active_members:
                notify(
                    recipient=m.student,
                    verb='feedback',
                    description=f'New feedback from {request.user.get_full_name()} on your project.',
                    icon='fa-comment',
                    color='blue',
                )
            messages.success(request, f'Feedback sent to {team.name}.')
            return redirect('teams:detail', pk=team.pk)
    else:
        form = FeedbackForm()

    return render(request, 'teams/feedback_form.html', {'form': form, 'team': team})
