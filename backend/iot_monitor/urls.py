"""
URL configuration for iot_monitor project.

The `urlpatterns` list routes URLs to views. For more information please see:
https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("admin/", admin.site.urls),
    # API endpoints
    path("api/devices/", include("devices.urls")),
    path("api/monitoring/", include("monitoring.urls")),
    path("api/alerts/", include("alerts.urls")),
    path("api/auth/", include("users.urls")),
]

# 开发环境下提供静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
