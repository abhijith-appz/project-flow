from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/',            views.login_view,            name='login'),
    path('logout/',           views.logout_view,           name='logout'),
    path('register/',         views.register_student_view, name='register'),
    path('register/teacher/', views.register_teacher_view, name='register_teacher'),
]
