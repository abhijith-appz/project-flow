"""
These URL patterns are included by projectflow/urls.py.
We add the named dashboard URLs here so all apps can reverse them.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('student/',  views.StudentDashboardView.as_view(), name='student_dashboard'),
    path('teacher/',  views.TeacherDashboardView.as_view(), name='teacher_dashboard'),
]
