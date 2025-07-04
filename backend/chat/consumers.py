from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from geouser.models import UserLocation
from .models import Message
import json

class ChatConsumer(AsyncWebsocketConsumer):

    # 建立連線
    async def connect(self):
        # 取得連線 URL 中的 your_name 與 target_name
        self.user_name = self.scope["url_route"]["kwargs"]["your_name"]
        self.other_name = self.scope["url_route"]["kwargs"]["target_name"]

        # 為避免 A→B 和 B→A 產生不同房間，使用固定順序合成房名
        name_pair = sorted([self.user_name, self.other_name])
        self.room_name = f"chat_{name_pair[0]}_{name_pair[1]}"

        # channel_name WebSocket 連線的唯一 ID
        # 把目前這條 WebSocket 連線（self.channel_name）加入到某個「群組」房間（self.room_name）中
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        
        # 後端同意並正式建立 WebSocket 連線
        await self.accept()


    # 斷開連線
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    # 收到前端資料並再通個聊天室廣播出去(回傳到前端)
    async def receive(self, text_data):
        data = json.loads(text_data)
        msg = data.get('message')

        # 取得發送者與接收者（從資料庫查）
        sender = await self.get_user(self.user_name)
        recipient = await self.get_user(self.other_name)

        # 將訊息儲存到資料庫
        await self.save_message(sender, recipient, msg)

        # 廣播這則訊息給同一個房間的所有用戶
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message', # 呼叫 chat_message() 方法
                'sender_name': sender.name,
                'message': msg,
            }
        )

    async def chat_message(self, event):
        # 接收來自 group_send 的訊息事件，轉發給前端用戶
        await self.send(text_data=json.dumps({
            'sender_name': event['sender_name'],
            'message': event['message'],
        }))

    # 非同步從資料庫查詢使用者
    @database_sync_to_async
    def get_user(self, name):
        return UserLocation.objects.get(name=name)

    # 非同步地儲存一筆訊息
    @database_sync_to_async
    def save_message(self, sender, recipient, content):
        return Message.objects.create(sender=sender, recipient=recipient, content=content)
