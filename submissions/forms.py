from django import forms
from .models import Submission


class SubmissionForm(forms.ModelForm):
    class Meta:
        model  = Submission
        fields = ['title', 'description', 'phase', 'file', 'github_url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'github_url':  forms.URLInput(attrs={'placeholder': 'https://github.com/…'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model  = Submission
        fields = ['status', 'teacher_note']
        widgets = {
            'teacher_note': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Add review notes…'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show teacher-actionable statuses
        self.fields['status'].choices = [
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('reviewed', 'Reviewed'),
        ]
