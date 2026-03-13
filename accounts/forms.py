from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class StudentRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name  = forms.CharField(max_length=50, required=True)
    email      = forms.EmailField(required=True)
    student_id = forms.CharField(max_length=20, required=True)
    department = forms.ChoiceField(choices=User.DEPARTMENT_CHOICES)

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'username', 'email',
                  'student_id', 'department', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role  = User.Role.STUDENT
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class TeacherRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name  = forms.CharField(max_length=50, required=True)
    email      = forms.EmailField(required=True)
    department = forms.ChoiceField(choices=User.DEPARTMENT_CHOICES)

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'username', 'email',
                  'department', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role  = User.Role.TEACHER
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Email / Username', widget=forms.TextInput(
        attrs={'placeholder': 'you@university.edu', 'autofocus': True}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': '••••••••'}
    ))
    role = forms.ChoiceField(
        choices=[('student', 'Student'), ('teacher', 'Teacher'), ('admin', 'Admin')],
        required=False
    )


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email', 'department',
                  'bio', 'phone', 'github_url', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }
