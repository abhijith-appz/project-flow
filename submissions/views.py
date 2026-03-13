from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import FileResponse, Http404
from .models import Submission
from .forms import SubmissionForm, ReviewForm
from notifications.utils import notify


@login_required
def submission_list_view(request):
    user = request.user

    if user.is_student:
        team = user.current_team
        if not team:
            messages.info(request, 'Join a team to see submissions.')
            return redirect('teams:list')
        submissions = team.submissions.select_related('submitted_by', 'reviewed_by')
    else:
        team_ids    = user.supervised_teams.values_list('id', flat=True)
        submissions = Submission.objects.filter(team_id__in=team_ids)\
                                        .select_related('team', 'submitted_by', 'reviewed_by')
        team = None

    pending_count = submissions.filter(status='pending').count()

    context = {
        'submissions': submissions,
        'team': team,
        'pending_count': pending_count,
        'active_nav': 'submissions',
    }
    return render(request, 'submissions/submission_list.html', context)


@login_required
def submission_create_view(request):
    user = request.user
    if not user.is_student:
        messages.error(request, 'Only students can submit files.')
        return redirect('submissions:list')

    team = user.current_team
    if not team:
        messages.error(request, 'You must be in a team to submit.')
        return redirect('teams:list')

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.team         = team
            sub.submitted_by = user
            # Auto-increment version for same phase
            existing = Submission.objects.filter(team=team, phase=sub.phase).count()
            sub.version = existing + 1
            sub.save()

            # Notify teacher
            if team.teacher:
                notify(
                    recipient=team.teacher,
                    verb='new submission',
                    description=f'{team.name} submitted "{sub.title}" ({sub.get_phase_display()}).',
                    icon='fa-upload',
                    color='amber',
                )
            messages.success(request, f'Submission "{sub.title}" uploaded successfully.')
            return redirect('submissions:list')
    else:
        form = SubmissionForm()

    return render(request, 'submissions/submission_form.html', {'form': form, 'team': team})


@login_required
def submission_detail_view(request, pk):
    sub  = get_object_or_404(Submission, pk=pk)
    user = request.user

    # Access control
    if user.is_student:
        if not user.current_team or user.current_team != sub.team:
            messages.error(request, 'Access denied.')
            return redirect('submissions:list')

    return render(request, 'submissions/submission_detail.html', {'sub': sub})


@login_required
def submission_review_view(request, pk):
    """Teacher reviews (approve/reject) a submission."""
    if not request.user.is_teacher:
        messages.error(request, 'Only teachers can review submissions.')
        return redirect('submissions:list')

    sub = get_object_or_404(Submission, pk=pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=sub)
        if form.is_valid():
            reviewed       = form.save(commit=False)
            reviewed.reviewed_by = request.user
            reviewed.reviewed_at = timezone.now()
            reviewed.save()

            # Notify team members
            for membership in sub.team.memberships.filter(is_active=True):
                notify(
                    recipient=membership.student,
                    verb='submission ' + reviewed.status,
                    description=f'Your submission "{sub.title}" was {reviewed.status} by {request.user.get_full_name()}.',
                    icon='fa-check-circle' if reviewed.status == 'approved' else 'fa-times-circle',
                    color='green' if reviewed.status == 'approved' else 'red',
                )
            messages.success(request, f'Submission marked as {reviewed.status}.')
            return redirect('submissions:list')
    else:
        form = ReviewForm(instance=sub)

    return render(request, 'submissions/submission_review.html', {'form': form, 'sub': sub})


@login_required
def submission_download_view(request, pk):
    sub = get_object_or_404(Submission, pk=pk)
    user = request.user

    # Students can only download their own team's files
    if user.is_student and (not user.current_team or user.current_team != sub.team):
        raise Http404

    try:
        response = FileResponse(sub.file.open('rb'), as_attachment=True, filename=sub.filename)
        return response
    except Exception:
        raise Http404('File not found on server.')
