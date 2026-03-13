from django import forms
from .models import Team, Feedback


class TeamCreateForm(forms.ModelForm):
    class Meta:
        model  = Team
        fields = ['name', 'project_title', 'description', 'department', 'github_url', 'max_members']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'max_members': forms.NumberInput(attrs={'min': 2, 'max': 6}),
        }

    def clean_max_members(self):
        val = self.cleaned_data['max_members']
        if val < 2 or val > 6:
            raise forms.ValidationError('Teams must have between 2 and 6 members.')
        return val


class FeedbackForm(forms.ModelForm):
    class Meta:
        model  = Feedback
        fields = ['feedback_type', 'message', 'rating']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Write detailed feedback…'}),
            'rating':  forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }
