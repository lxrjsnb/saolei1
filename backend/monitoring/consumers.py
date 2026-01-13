import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import SensorData
from devices.models import Device


class RealTimeDataConsumer(AsyncWebsocketConsumer):
    """实时数据推送消费者"""

    async def connect(self):
        self.device_id = self.scope['url_route']['kwargs']['device_id']
        self.room_group_name = f'device_{self.device_id}'

        # 验证设备权限
        device = await self.get_device()
        if not device:
            await self.close()
            return

        # 加入房间组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # 离开房间组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """接收WebSocket消息"""
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'subscribe':
            # 订阅确认
            await self.send(text_data=json.dumps({
                'type': 'subscription_confirmed',
                'device_id': self.device_id
            }))

    async def sensor_data_update(self, event):
        """发送传感器数据更新"""
        await self.send(text_data=json.dumps({
            'type': 'sensor_update',
            'data': event['data']
        }))

    @database_sync_to_async
    def get_device(self):
        """获取设备"""
        try:
            return Device.objects.get(id=self.device_id)
        except Device.DoesNotExist:
            return None
