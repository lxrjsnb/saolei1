from rest_framework import serializers
from .models import SensorData, DataSummary


class SensorDataSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    device_id = serializers.CharField(source='device.device_id', read_only=True)

    class Meta:
        model = SensorData
        fields = ['id', 'device', 'device_name', 'device_id', 'temperature', 'humidity',
                  'light_intensity', 'pm25', 'co2', 'timestamp', 'is_valid', 'error_message']
        read_only_fields = ['timestamp']


class SensorDataCreateSerializer(serializers.ModelSerializer):
    """传感器数据创建序列化器（用于设备上报数据）"""
    class Meta:
        model = SensorData
        fields = ['device', 'temperature', 'humidity', 'light_intensity', 'pm25', 'co2']

    def validate(self, data):
        device = data.get('device')
        if device.status != 'online':
            raise serializers.ValidationError("设备不在线，无法上报数据")
        return data


class DataSummarySerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)

    class Meta:
        model = DataSummary
        fields = '__all__'


class DataQuerySerializer(serializers.Serializer):
    """数据查询序列化器"""
    device_id = serializers.IntegerField(required=True)
    start_time = serializers.DateTimeField(required=True)
    end_time = serializers.DateTimeField(required=True)
    data_type = serializers.CharField(required=False, default='all')
