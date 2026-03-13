from django.urls import path
from accounts import views

app_name = 'profile'

urlpatterns = [
    path('',        views.profile_view,        name='detail'),
    path('edit/',   views.profile_update_view, name='edit'),
    path('password/', views.change_password_view, name='password'),
]
