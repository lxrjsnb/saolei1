from django.contrib import admin
from django.contrib.auth.models import User
from .models import UserProfile, UserActivityLog


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'organization', 'position', 'language', 'theme', 'is_active']
    list_filter = ['language', 'theme', 'is_active']
    search_fields = ['user__username', 'organization', 'position']


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'description', 'ip_address', 'created_at']
    list_filter = ['action_type', 'created_at']
    search_fields = ['user__username', 'description', 'ip_address']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
