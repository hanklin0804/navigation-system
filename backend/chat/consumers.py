from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from geouser.models import UserLocation
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_name = self.scope["url_route"]["kwargs"]["your_name"]
        self.other_name = self.scope["url_route"]["kwargs"]["target_name"]

        # 建立雙方固定順序的聊天室房名（不受順序影響）
        name_pair = sorted([self.user_name, self.other_name])
        self.room_name = f"chat_{name_pair[0]}_{name_pair[1]}"

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg = data.get('message')

        sender = await self.get_user(self.user_name)
        recipient = await self.get_user(self.other_name)

        await self.save_message(sender, recipient, msg)

        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'sender_name': sender.name,
                'message': msg,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'sender_name': event['sender_name'],
            'message': event['message'],
        }))

    @database_sync_to_async
    def get_user(self, name):
        return UserLocation.objects.get(name=name)

    @database_sync_to_async
    def save_message(self, sender, recipient, content):
        return Message.objects.create(sender=sender, recipient=recipient, content=content)
