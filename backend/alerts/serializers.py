from rest_framework import serializers
from .models import AlertRule, AlertRecord, NotificationConfig


class AlertRuleSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = AlertRule
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class AlertRecordSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    rule_name = serializers.CharField(source='rule.name', read_only=True)
    acknowledged_by_name = serializers.CharField(source='acknowledged_by.username', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.username', read_only=True)

    class Meta:
        model = AlertRecord
        fields = '__all__'
        read_only_fields = ['triggered_at', 'acknowledged_at', 'resolved_at']


class AlertRecordUpdateSerializer(serializers.ModelSerializer):
    """报警记录更新序列化器"""
    class Meta:
        model = AlertRecord
        fields = ['status', 'notes']


class NotificationConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationConfig
        fields = '__all__'
