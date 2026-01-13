from django.contrib import admin
from .models import Device, DeviceConfig, DeviceMaintenance


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'device_id', 'device_type', 'location', 'status', 'ip_address', 'owner', 'last_active', 'created_at']
    list_filter = ['device_type', 'status', 'created_at']
    search_fields = ['name', 'device_id', 'location', 'manufacturer', 'model']
    readonly_fields = ['created_at', 'updated_at', 'last_active']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'device_id', 'device_type', 'location', 'status', 'description')
        }),
        ('硬件信息', {
            'fields': ('ip_address', 'mac_address', 'firmware_version', 'manufacturer', 'model', 'serial_number')
        }),
        ('位置信息', {
            'fields': ('latitude', 'longitude', 'altitude')
        }),
        ('生命周期', {
            'fields': ('install_date', 'warranty_date', 'owner', 'is_active')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at', 'last_active')
        }),
    )


@admin.register(DeviceConfig)
class DeviceConfigAdmin(admin.ModelAdmin):
    list_display = ['device', 'collect_interval', 'enable_alert', 'data_retention_days', 'auto_cleanup', 'created_at', 'updated_at']
    list_filter = ['enable_alert', 'auto_cleanup', 'created_at']
    search_fields = ['device__name', 'device__device_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DeviceMaintenance)
class DeviceMaintenanceAdmin(admin.ModelAdmin):
    list_display = ['device', 'maintenance_type', 'scheduled_date', 'completed_date', 'status', 'technician', 'cost']
    list_filter = ['maintenance_type', 'status', 'scheduled_date']
    search_fields = ['device__name', 'description']
    date_hierarchy = 'scheduled_date'
