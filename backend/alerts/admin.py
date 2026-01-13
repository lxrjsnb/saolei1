from django.contrib import admin
from .models import AlertRule, AlertRecord, NotificationConfig, NotificationLog


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'device', 'sensor_type', 'condition', 'threshold', 'severity', 'cooldown_minutes', 'enabled', 'created_at']
    list_filter = ['sensor_type', 'condition', 'severity', 'enabled', 'created_at']
    search_fields = ['name', 'device__name', 'device__device_id']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('基本配置', {
            'fields': ('name', 'device', 'sensor_type', 'condition', 'threshold', 'threshold_min', 'threshold_max')
        }),
        ('高级配置', {
            'fields': ('severity', 'cooldown_minutes', 'repeat_alert', 'repeat_interval_minutes', 'enabled')
        }),
        ('其他', {
            'fields': ('description', 'created_by')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(AlertRecord)
class AlertRecordAdmin(admin.ModelAdmin):
    list_display = ['device', 'rule', 'status', 'severity', 'current_value', 'triggered_at', 'acknowledged_by', 'resolved_by']
    list_filter = ['status', 'severity', 'triggered_at']
    search_fields = ['device__name', 'message']
    readonly_fields = ['triggered_at', 'acknowledged_at', 'resolved_at']
    date_hierarchy = 'triggered_at'


@admin.register(NotificationConfig)
class NotificationConfigAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'enabled', 'min_severity', 'notify_24h', 'created_at']
    list_filter = ['notification_type', 'enabled', 'min_severity']
    search_fields = ['user__username']


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['alert_record', 'notification_config', 'recipient', 'status', 'sent_at', 'retry_count', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['recipient', 'content']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
