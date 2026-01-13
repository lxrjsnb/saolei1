from django.contrib import admin
from .models import SensorData, DataSummary, DataExport


@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ['device', 'temperature', 'humidity', 'pressure', 'pm25', 'co2', 'timestamp', 'is_valid']
    list_filter = ['device', 'is_valid', 'timestamp']
    search_fields = ['device__name', 'device__device_id']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(DataSummary)
class DataSummaryAdmin(admin.ModelAdmin):
    list_display = ['device', 'summary_type', 'start_time', 'end_time', 'temp_avg', 'humidity_avg', 'data_count']
    list_filter = ['summary_type', 'start_time']
    search_fields = ['device__name']
    readonly_fields = ['created_at']


@admin.register(DataExport)
class DataExportAdmin(admin.ModelAdmin):
    list_display = ['user', 'device', 'export_type', 'start_time', 'end_time', 'status', 'row_count', 'created_at']
    list_filter = ['export_type', 'status', 'created_at']
    search_fields = ['user__username', 'device__name']
    readonly_fields = ['created_at', 'completed_at']
