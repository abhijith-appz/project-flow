from django import forms
from .models import Task, TaskComment


class TaskForm(forms.ModelForm):
    class Meta:
        model  = Task
        fields = ['title', 'description', 'assigned_to', 'priority', 'deadline']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'deadline':    forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, team=None, **kwargs):
        super().__init__(*args, **kwargs)
        if team:
            # Only show current active team members in the dropdown
            member_ids = team.memberships.filter(is_active=True).values_list('student_id', flat=True)
            from accounts.models import User
            self.fields['assigned_to'].queryset = User.objects.filter(id__in=member_ids)


class TaskStatusForm(forms.ModelForm):
    class Meta:
        model  = Task
        fields = ['status']


class TaskCommentForm(forms.ModelForm):
    class Meta:
        model  = TaskComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Add a comment…'}),
        }
