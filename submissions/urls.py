from django.urls import path
from . import views

app_name = 'submissions'

urlpatterns = [
    path('',                    views.submission_list_view,     name='list'),
    path('new/',                views.submission_create_view,   name='create'),
    path('<int:pk>/',           views.submission_detail_view,   name='detail'),
    path('<int:pk>/review/',    views.submission_review_view,   name='review'),
    path('<int:pk>/download/',  views.submission_download_view, name='download'),
]
