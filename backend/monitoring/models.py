from django.db import models
from devices.models import Device


class SensorData(models.Model):
    """传感器数据模型"""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='sensor_data', verbose_name='设备')

    # 环境参数
    temperature = models.FloatField(null=True, blank=True, verbose_name='温度(℃)')
    humidity = models.FloatField(null=True, blank=True, verbose_name='湿度(%)')
    pressure = models.FloatField(null=True, blank=True, verbose_name='气压(hPa)')
    light_intensity = models.FloatField(null=True, blank=True, verbose_name='光照强度(lux)')
    uv_index = models.FloatField(null=True, blank=True, verbose_name='紫外线指数')
    pm25 = models.FloatField(null=True, blank=True, verbose_name='PM2.5(μg/m³)')
    pm10 = models.FloatField(null=True, blank=True, verbose_name='PM10(μg/m³)')
    co2 = models.FloatField(null=True, blank=True, verbose_name='CO2浓度(ppm)')
    voc = models.FloatField(null=True, blank=True, verbose_name='VOC浓度(ppb)')
    o3 = models.FloatField(null=True, blank=True, verbose_name='O3浓度(ppb)')
    noise_level = models.FloatField(null=True, blank=True, verbose_name='噪音水平(dB)')
    wind_speed = models.FloatField(null=True, blank=True, verbose_name='风速(m/s)')
    wind_direction = models.FloatField(null=True, blank=True, verbose_name='风向(度)')
    rainfall = models.FloatField(null=True, blank=True, verbose_name='降雨量(mm)')

    # 元数据
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='采集时间')
    is_valid = models.BooleanField(default=True, verbose_name='数据是否有效')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    battery_level = models.IntegerField(null=True, blank=True, verbose_name='电池电量(%)')
    signal_strength = models.IntegerField(null=True, blank=True, verbose_name='信号强度(dBm)')

    class Meta:
        db_table = 'sensor_data'
        verbose_name = '传感器数据'
        verbose_name_plural = '传感器数据'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', '-timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['is_valid']),
        ]

    def __str__(self):
        return f"{self.device.name} - {self.timestamp}"


class DataSummary(models.Model):
    """数据汇总模型（按小时/天汇总）"""
    SUMMARY_TYPE_CHOICES = [
        ('hour', '小时'),
        ('day', '天'),
        ('week', '周'),
        ('month', '月'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='data_summaries', verbose_name='设备')

    # 汇总类型：hour/day
    summary_type = models.CharField(max_length=10, choices=SUMMARY_TYPE_CHOICES, verbose_name='汇总类型')

    # 时间范围
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')

    # 温度统计
    temp_avg = models.FloatField(null=True, verbose_name='平均温度')
    temp_max = models.FloatField(null=True, verbose_name='最高温度')
    temp_min = models.FloatField(null=True, verbose_name='最低温度')

    # 湿度统计
    humidity_avg = models.FloatField(null=True, verbose_name='平均湿度')
    humidity_max = models.FloatField(null=True, verbose_name='最高湿度')
    humidity_min = models.FloatField(null=True, verbose_name='最低湿度')

    # PM2.5统计
    pm25_avg = models.FloatField(null=True, verbose_name='平均PM2.5')
    pm25_max = models.FloatField(null=True, verbose_name='最高PM2.5')

    # CO2统计
    co2_avg = models.FloatField(null=True, verbose_name='平均CO2')
    co2_max = models.FloatField(null=True, verbose_name='最高CO2')

    # 采集的数据点数量
    data_count = models.IntegerField(default=0, verbose_name='数据点数量')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'data_summaries'
        verbose_name = '数据汇总'
        verbose_name_plural = '数据汇总'
        unique_together = ['device', 'summary_type', 'start_time']
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['device', 'summary_type', '-start_time']),
        ]

    def __str__(self):
        return f"{self.device.name} - {self.summary_type} 汇总"


class DataExport(models.Model):
    """数据导出记录"""
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]

    EXPORT_TYPE_CHOICES = [
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name='用户')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='export_records', verbose_name='设备')
    export_type = models.CharField(max_length=10, choices=EXPORT_TYPE_CHOICES, verbose_name='导出类型')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    file_path = models.CharField(max_length=255, blank=True, verbose_name='文件路径')
    file_size = models.IntegerField(null=True, blank=True, verbose_name='文件大小(字节)')
    row_count = models.IntegerField(null=True, blank=True, verbose_name='数据行数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    error_message = models.TextField(blank=True, verbose_name='错误信息')

    class Meta:
        db_table = 'data_exports'
        verbose_name = '数据导出记录'
        verbose_name_plural = '数据导出记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.device.name} - {self.export_type}"
