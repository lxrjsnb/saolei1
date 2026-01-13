from django.db import models
from django.contrib.auth.models import User
from devices.models import Device


class AlertRule(models.Model):
    """报警规则模型"""
    CONDITION_CHOICES = [
        ('greater_than', '大于'),
        ('less_than', '小于'),
        ('equal', '等于'),
        ('not_equal', '不等于'),
        ('between', '介于之间'),
        ('outside', '超出范围'),
    ]

    SENSOR_TYPE_CHOICES = [
        ('temperature', '温度'),
        ('humidity', '湿度'),
        ('pressure', '气压'),
        ('light_intensity', '光照强度'),
        ('pm25', 'PM2.5'),
        ('pm10', 'PM10'),
        ('co2', 'CO2'),
        ('voc', 'VOC'),
        ('o3', 'O3'),
        ('noise_level', '噪音'),
        ('battery_level', '电池电量'),
        ('signal_strength', '信号强度'),
    ]

    SEVERITY_CHOICES = [
        ('info', '信息'),
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('critical', '严重'),
    ]

    name = models.CharField(max_length=100, verbose_name='规则名称')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='alert_rules', verbose_name='设备')
    sensor_type = models.CharField(max_length=20, choices=SENSOR_TYPE_CHOICES, verbose_name='传感器类型')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, verbose_name='条件')
    threshold_min = models.FloatField(null=True, blank=True, verbose_name='最小阈值')
    threshold_max = models.FloatField(null=True, blank=True, verbose_name='最大阈值')
    threshold = models.FloatField(null=True, blank=True, verbose_name='阈值')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium', verbose_name='严重程度')
    enabled = models.BooleanField(default=True, verbose_name='是否启用')
    description = models.TextField(blank=True, verbose_name='描述')

    # 高级配置
    cooldown_minutes = models.IntegerField(default=5, verbose_name='冷却时间(分钟)')
    repeat_alert = models.BooleanField(default=False, verbose_name='重复报警')
    repeat_interval_minutes = models.IntegerField(default=30, verbose_name='重复间隔(分钟)')

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'alert_rules'
        verbose_name = '报警规则'
        verbose_name_plural = '报警规则'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['device', 'enabled']),
        ]

    def __str__(self):
        return f"{self.name} - {self.get_sensor_type_display()} {self.get_condition_display()}"


class AlertRecord(models.Model):
    """报警记录模型"""
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('acknowledged', '已确认'),
        ('resolved', '已解决'),
        ('false_alarm', '误报'),
        ('auto_resolved', '自动解决'),
    ]

    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, related_name='records', verbose_name='报警规则')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='alert_records', verbose_name='设备')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    message = models.TextField(verbose_name='报警消息')
    current_value = models.FloatField(verbose_name='当前值')
    severity = models.CharField(max_length=20, verbose_name='严重程度')
    triggered_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='触发时间')
    acknowledged_at = models.DateTimeField(null=True, blank=True, verbose_name='确认时间')
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='acknowledged_alerts', verbose_name='确认人')
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name='解决时间')
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='resolved_alerts', verbose_name='解决人')
    notes = models.TextField(blank=True, verbose_name='备注')

    # 扩展信息
    recovery_value = models.FloatField(null=True, blank=True, verbose_name='恢复值')
    recovery_time = models.DurationField(null=True, blank=True, verbose_name='恢复耗时')
    notification_sent = models.BooleanField(default=False, verbose_name='通知已发送')
    notification_count = models.IntegerField(default=0, verbose_name='通知次数')

    class Meta:
        db_table = 'alert_records'
        verbose_name = '报警记录'
        verbose_name_plural = '报警记录'
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['device', '-triggered_at']),
            models.Index(fields=['status', '-triggered_at']),
            models.Index(fields=['severity', '-triggered_at']),
        ]

    def __str__(self):
        return f"{self.device.name} - {self.message} ({self.triggered_at})"


class NotificationConfig(models.Model):
    """通知配置模型"""
    NOTIFICATION_TYPE_CHOICES = [
        ('email', '邮件'),
        ('sms', '短信'),
        ('webhook', 'Webhook'),
        ('wechat', '微信'),
        ('dingtalk', '钉钉'),
        ('feishu', '飞书'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_configs', verbose_name='用户')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, verbose_name='通知类型')
    enabled = models.BooleanField(default=True, verbose_name='是否启用')
    config = models.JSONField(default=dict, verbose_name='配置信息')
    min_severity = models.CharField(max_length=20, default='medium',
                                     choices=AlertRule.SEVERITY_CHOICES, verbose_name='最低严重程度')

    # 通知时间配置
    notify_24h = models.BooleanField(default=True, verbose_name='24小时通知')
    quiet_hours_start = models.TimeField(null=True, blank=True, verbose_name='免打扰开始时间')
    quiet_hours_end = models.TimeField(null=True, blank=True, verbose_name='免打扰结束时间')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'notification_configs'
        verbose_name = '通知配置'
        verbose_name_plural = '通知配置'

    def __str__(self):
        return f"{self.user.username} - {self.get_notification_type_display()}"


class NotificationLog(models.Model):
    """通知发送日志"""
    STATUS_CHOICES = [
        ('pending', '待发送'),
        ('sent', '已发送'),
        ('failed', '发送失败'),
        ('retrying', '重试中'),
    ]

    alert_record = models.ForeignKey(AlertRecord, on_delete=models.CASCADE, related_name='notification_logs', verbose_name='报警记录')
    notification_config = models.ForeignKey(NotificationConfig, on_delete=models.CASCADE, related_name='logs', verbose_name='通知配置')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    recipient = models.CharField(max_length=255, verbose_name='接收人')
    content = models.TextField(verbose_name='通知内容')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='发送时间')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    retry_count = models.IntegerField(default=0, verbose_name='重试次数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'notification_logs'
        verbose_name = '通知日志'
        verbose_name_plural = '通知日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['alert_record', 'status']),
            models.Index(fields=['notification_config', '-created_at']),
        ]

    def __str__(self):
        return f"{self.recipient} - {self.status} ({self.created_at})"
