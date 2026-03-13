from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path('',                      views.team_list_view,    name='list'),
    path('create/',               views.team_create_view,  name='create'),
    path('<int:pk>/',             views.team_detail_view,  name='detail'),
    path('<int:pk>/join/',        views.team_join_view,    name='join'),
    path('<int:pk>/leave/',       views.team_leave_view,   name='leave'),
    path('<int:team_pk>/feedback/', views.give_feedback_view, name='feedback'),
]
