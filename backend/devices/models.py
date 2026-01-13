from django.db import models
from django.contrib.auth.models import User


class Device(models.Model):
    """设备模型"""
    DEVICE_TYPE_CHOICES = [
        ('temperature', '温度传感器'),
        ('humidity', '湿度传感器'),
        ('light', '光照传感器'),
        ('pm25', 'PM2.5传感器'),
        ('co2', 'CO2传感器'),
        ('composite', '综合传感器'),
    ]

    STATUS_CHOICES = [
        ('online', '在线'),
        ('offline', '离线'),
        ('maintenance', '维护中'),
        ('error', '故障'),
    ]

    # 基本信息
    name = models.CharField(max_length=100, verbose_name='设备名称')
    device_id = models.CharField(max_length=50, unique=True, verbose_name='设备ID')
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE_CHOICES, verbose_name='设备类型')
    location = models.CharField(max_length=200, verbose_name='安装位置')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline', verbose_name='设备状态')
    description = models.TextField(blank=True, verbose_name='设备描述')

    # 设备硬件信息
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    mac_address = models.CharField(max_length=17, null=True, blank=True, verbose_name='MAC地址')
    firmware_version = models.CharField(max_length=50, null=True, blank=True, verbose_name='固件版本')
    manufacturer = models.CharField(max_length=100, null=True, blank=True, verbose_name='制造商')
    model = models.CharField(max_length=100, null=True, blank=True, verbose_name='型号')
    serial_number = models.CharField(max_length=100, null=True, blank=True, verbose_name='序列号')

    # 设备位置信息
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name='纬度')
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name='经度')
    altitude = models.FloatField(null=True, blank=True, verbose_name='海拔(米)')

    # 设备生命周期
    install_date = models.DateField(null=True, blank=True, verbose_name='安装日期')
    warranty_date = models.DateField(null=True, blank=True, verbose_name='保修期至')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='所属用户')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    last_active = models.DateTimeField(null=True, blank=True, verbose_name='最后活跃时间')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    class Meta:
        db_table = 'devices'
        verbose_name = '设备'
        verbose_name_plural = '设备'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['device_id']),
            models.Index(fields=['status']),
            models.Index(fields=['device_type']),
            models.Index(fields=['owner']),
        ]

    def __str__(self):
        return f"{self.name} ({self.device_id})"


class DeviceConfig(models.Model):
    """设备配置模型"""
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name='config', verbose_name='设备')
    collect_interval = models.IntegerField(default=60, verbose_name='采集间隔(秒)')
    enable_alert = models.BooleanField(default=True, verbose_name='启用报警')
    data_retention_days = models.IntegerField(default=90, verbose_name='数据保留天数')
    auto_cleanup = models.BooleanField(default=False, verbose_name='自动清理过期数据')
    extra_config = models.JSONField(default=dict, blank=True, verbose_name='额外配置')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'device_configs'
        verbose_name = '设备配置'
        verbose_name_plural = '设备配置'

    def __str__(self):
        return f"{self.device.name} 配置"


class DeviceMaintenance(models.Model):
    """设备维护记录"""
    MAINTENANCE_TYPE_CHOICES = [
        ('routine', '例行维护'),
        ('repair', '故障维修'),
        ('upgrade', '固件升级'),
        ('calibration', '校准'),
        ('replacement', '更换部件'),
    ]

    STATUS_CHOICES = [
        ('scheduled', '已计划'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='maintenance_records', verbose_name='设备')
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES, verbose_name='维护类型')
    description = models.TextField(verbose_name='维护描述')
    scheduled_date = models.DateTimeField(verbose_name='计划时间')
    completed_date = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name='状态')
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='技术人员')
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='费用')
    notes = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'device_maintenance'
        verbose_name = '设备维护记录'
        verbose_name_plural = '设备维护记录'
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.device.name} - {self.get_maintenance_type_display()} - {self.scheduled_date}"
