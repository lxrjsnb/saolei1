from rest_framework import serializers
from .models import Device, DeviceConfig


class DeviceConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceConfig
        fields = '__all__'


class DeviceSerializer(serializers.ModelSerializer):
    config = DeviceConfigSerializer(read_only=True)
    owner_name = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Device
        fields = ['id', 'name', 'device_id', 'device_type', 'location', 'status',
                  'description', 'owner', 'owner_name', 'created_at', 'updated_at',
                  'last_active', 'config']
        read_only_fields = ['created_at', 'updated_at', 'last_active']

    def validate_device_id(self, value):
        """验证设备ID唯一性"""
        instance = self.instance
        if Device.objects.filter(device_id=value).exclude(id=instance.id if instance else None).exists():
            raise serializers.ValidationError("设备ID已存在")
        return value


class DeviceListSerializer(serializers.ModelSerializer):
    """设备列表序列化器（轻量级）"""
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    sensor_count = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = ['id', 'name', 'device_id', 'device_type', 'location', 'status',
                  'owner_name', 'last_active', 'sensor_count']

    def get_sensor_count(self, obj):
        return obj.sensor_data.count()


class DeviceCreateSerializer(serializers.ModelSerializer):
    """设备创建序列化器"""
    config = DeviceConfigSerializer(required=False)

    class Meta:
        model = Device
        fields = ['name', 'device_id', 'device_type', 'location', 'description', 'config']

    def create(self, validated_data):
        config_data = validated_data.pop('config', None)
        device = Device.objects.create(**validated_data)
        if config_data:
            DeviceConfig.objects.create(device=device, **config_data)
        else:
            DeviceConfig.objects.create(device=device)
        return device
