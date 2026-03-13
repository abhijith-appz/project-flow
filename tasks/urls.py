from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('',                    views.task_list_view,          name='list'),
    path('create/',             views.task_create_view,        name='create'),
    path('<int:pk>/',           views.task_detail_view,        name='detail'),
    path('<int:pk>/edit/',      views.task_update_view,        name='update'),
    path('<int:pk>/complete/',  views.task_mark_complete_view, name='complete'),
    path('<int:pk>/delete/',    views.task_delete_view,        name='delete'),
]
