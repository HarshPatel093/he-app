"""
URL Configuration for the Holiday Explorers System.

This module defines the root URL routing for the entire Django project.
It connects the main application (`users`) and Django’s built-in admin panel.
Media files (e.g., feedback photos) are also served during development.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Root URL patterns
urlpatterns = [
    # Include all URL routes defined in the 'users' application.
    path('', include('users.urls')),
    path('admin/', admin.site.urls),
]

# Media File Routing (Development Mode)
# When DEBUG = True, Django serves uploaded media files (like photos)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)