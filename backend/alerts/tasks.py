from celery import shared_task
from django.utils import timezone
from .models import AlertRule, AlertRecord
from monitoring.models import SensorData


@shared_task
def check_alert_rules(sensor_data_id):
    """检查传感器数据是否触发报警规则"""
    try:
        sensor_data = SensorData.objects.get(id=sensor_data_id)
    except SensorData.DoesNotExist:
        return

    device = sensor_data.device

    # 获取该设备所有启用的报警规则
    alert_rules = AlertRule.objects.filter(
        device=device,
        enabled=True
    )

    for rule in alert_rules:
        # 获取传感器对应的值
        sensor_value = None
        if rule.sensor_type == 'temperature':
            sensor_value = sensor_data.temperature
        elif rule.sensor_type == 'humidity':
            sensor_value = sensor_data.humidity
        elif rule.sensor_type == 'light_intensity':
            sensor_value = sensor_data.light_intensity
        elif rule.sensor_type == 'pm25':
            sensor_value = sensor_data.pm25
        elif rule.sensor_type == 'co2':
            sensor_value = sensor_data.co2

        if sensor_value is None:
            continue

        # 检查是否触发报警
        triggered = False
        if rule.condition == 'greater_than' and sensor_value > rule.threshold:
            triggered = True
        elif rule.condition == 'less_than' and sensor_value < rule.threshold:
            triggered = True
        elif rule.condition == 'equal' and sensor_value == rule.threshold:
            triggered = True
        elif rule.condition == 'not_equal' and sensor_value != rule.threshold:
            triggered = True

        if triggered:
            # 检查是否已有未解决的相同报警
            existing_alert = AlertRecord.objects.filter(
                rule=rule,
                device=device,
                status='pending'
            ).first()

            if not existing_alert:
                # 创建报警记录
                AlertRecord.objects.create(
                    rule=rule,
                    device=device,
                    status='pending',
                    message=f"{rule.get_sensor_type_display()} {rule.get_condition_display()} {rule.threshold}，当前值：{sensor_value}",
                    current_value=sensor_value,
                    severity=rule.severity
                )

                # 发送通知
                send_alert_notifications.delay(rule.id, sensor_value)


@shared_task
def send_alert_notifications(alert_rule_id, current_value):
    """发送报警通知"""
    try:
        rule = AlertRule.objects.get(id=alert_rule_id)
    except AlertRule.DoesNotExist:
        return

    # 获取该用户的通知配置
    from .models import NotificationConfig
    notification_configs = NotificationConfig.objects.filter(
        user=rule.created_by,
        enabled=True
    )

    # 检查严重程度
    severity_order = ['low', 'medium', 'high', 'critical']
    if severity_order.index(rule.severity) < severity_order.index(notification_configs.first().min_severity):
        return

    for config in notification_configs:
        if config.notification_type == 'email':
            # 发送邮件通知（需要配置邮件服务器）
            pass
        elif config.notification_type == 'webhook':
            # 发送Webhook通知
            import requests
            try:
                requests.post(
                    config.config.get('url'),
                    json={
                        'rule': rule.name,
                        'device': rule.device.name,
                        'severity': rule.severity,
                        'current_value': current_value,
                        'threshold': rule.threshold,
                        'message': f"{rule.get_sensor_type_display()} {rule.get_condition_display()} {rule.threshold}"
                    },
                    timeout=5
                )
            except:
                pass


@shared_task
def cleanup_old_alerts():
    """清理旧的已解决报警记录"""
    from datetime import timedelta
    threshold = timezone.now() - timedelta(days=90)

    AlertRecord.objects.filter(
        status__in=['resolved', 'false_alarm'],
        resolved_at__lt=threshold
    ).delete()
