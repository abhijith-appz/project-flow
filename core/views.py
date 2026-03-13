from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().get(request, *args, **kwargs)


class DashboardRedirectView(LoginRequiredMixin, View):
    """Route users to their role-specific dashboard."""

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_student:
            return redirect('student_dashboard')
        elif user.is_teacher:
            return redirect('teacher_dashboard')
        else:
            return redirect('/admin/')


class StudentDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/student_dashboard.html'

    def get_context_data(self, **kwargs):
        ctx  = super().get_context_data(**kwargs)
        user = self.request.user
        team = user.current_team

        ctx['team'] = team
        ctx['active_nav'] = 'dashboard'
        if team:
            tasks        = team.tasks.all()
            ctx['tasks_total']     = tasks.count()
            ctx['tasks_done']      = tasks.filter(status='completed').count()
            ctx['tasks_pending']   = tasks.filter(status='pending').count()
            ctx['tasks_overdue']   = tasks.filter(status='overdue').count()
            ctx['my_tasks']        = tasks.filter(assigned_to=user).order_by('deadline')[:5]
            ctx['recent_feedback'] = team.feedback_list.select_related('teacher').all()[:3]
            ctx['submissions']     = team.submissions.all()[:5]
            ctx['progress']        = team.progress_percent
        return ctx


class TeacherDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/teacher_dashboard.html'

    def get_context_data(self, **kwargs):
        ctx  = super().get_context_data(**kwargs)
        user = self.request.user

        from teams.models import Team
        from submissions.models import Submission
        from accounts.models import User as UserModel

        teams     = Team.objects.filter(teacher=user).prefetch_related('memberships')
        ctx['teams']            = teams
        ctx['teams_count']      = teams.count()
        ctx['active_nav']       = 'dashboard'
        ctx['students_count']   = UserModel.objects.filter(
            memberships__team__in=teams, memberships__is_active=True
        ).distinct().count()

        pending_subs = Submission.objects.filter(team__in=teams, status='pending')
        ctx['pending_submissions']       = pending_subs[:5]
        ctx['pending_submissions_count'] = pending_subs.count()

        all_subs = Submission.objects.filter(team__in=teams)
        ctx['submissions_count'] = all_subs.count()
        return ctx
