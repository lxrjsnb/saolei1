from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """用户配置文件"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='用户')

    # 基本信息
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='手机号')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='头像')
    organization = models.CharField(max_length=200, null=True, blank=True, verbose_name='组织/公司')
    position = models.CharField(max_length=100, null=True, blank=True, verbose_name='职位')

    # 通知偏好
    email_notification = models.BooleanField(default=True, verbose_name='邮件通知')
    sms_notification = models.BooleanField(default=False, verbose_name='短信通知')
    webhook_notification = models.BooleanField(default=False, verbose_name='Webhook通知')

    # 界面设置
    language = models.CharField(max_length=10, default='zh-hans', verbose_name='语言')
    timezone = models.CharField(max_length=50, default='Asia/Shanghai', verbose_name='时区')
    theme = models.CharField(max_length=20, default='light', verbose_name='主题')
    items_per_page = models.IntegerField(default=20, verbose_name='每页显示数量')

    # 数据设置
    default_data_range = models.CharField(max_length=20, default='24h', verbose_name='默认数据范围')
    auto_refresh_interval = models.IntegerField(default=30, verbose_name='自动刷新间隔(秒)')

    # 安全设置
    two_factor_enabled = models.BooleanField(default=False, verbose_name='启用双因素认证')
    last_password_change = models.DateTimeField(null=True, blank=True, verbose_name='上次修改密码时间')
    login_notification = models.BooleanField(default=True, verbose_name='登录通知')

    # 状态
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'user_profiles'
        verbose_name = '用户配置'
        verbose_name_plural = '用户配置'

    def __str__(self):
        return f"{self.user.username} 的配置"


class UserActivityLog(models.Model):
    """用户活动日志"""
    ACTION_TYPE_CHOICES = [
        ('login', '登录'),
        ('logout', '登出'),
        ('create_device', '创建设备'),
        ('update_device', '更新设备'),
        ('delete_device', '删除设备'),
        ('create_alert', '创建报警规则'),
        ('acknowledge_alert', '确认报警'),
        ('resolve_alert', '解决报警'),
        ('export_data', '导出数据'),
        ('change_settings', '修改设置'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs', verbose_name='用户')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPE_CHOICES, verbose_name='操作类型')
    description = models.TextField(verbose_name='操作描述')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='用户代理')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'user_activity_logs'
        verbose_name = '用户活动日志'
        verbose_name_plural = '用户活动日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action_type', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.action_type} ({self.created_at})"
