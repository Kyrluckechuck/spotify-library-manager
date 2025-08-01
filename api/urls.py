"""
Minimal URL configuration for Django.
Since we're using GraphQL API, this is just a placeholder.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),
]

# Serve static files in development
if settings.DEBUG:
    # Serve admin static files at /admin/static/ (what Django admin expects)
    urlpatterns += static("/admin/static/", document_root=settings.STATIC_ROOT)
    # Also serve at /static/ for general static files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
