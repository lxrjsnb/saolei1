"""
Celery配置文件
"""
import os
from celery import Celery

# 设置默认的Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iot_monitor.settings')

app = Celery('iot_monitor')

# 使用Django的settings文件作为配置源
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现所有已安装应用的tasks.py
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
