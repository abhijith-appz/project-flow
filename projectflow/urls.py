"""ProjectFlow URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from core import views as core_views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Public
    path('', core_views.HomeView.as_view(), name='home'),
    path('dashboard/', core_views.DashboardRedirectView.as_view(), name='dashboard'),

    # Dashboards
    path('dashboard/', include('core.urls')),

    # Apps
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('teams/', include('teams.urls', namespace='teams')),
    path('tasks/', include('tasks.urls', namespace='tasks')),
    path('submissions/', include('submissions.urls', namespace='submissions')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
    path('profile/', include('accounts.profile_urls', namespace='profile')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
