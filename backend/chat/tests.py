# backend/chat/tests.py
from django.test import TestCase, TransactionTestCase
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from .models import Message
from tests.base import BaseTestCase
from tests.utils import create_test_message, create_test_user, TestCoordinates
from taxi_backend.asgi import application

class MessageModelTest(BaseTestCase):
    
    def test_create_message(self):
        """測試建立訊息"""
        message = create_test_message(
            sender=self.alice, 
            recipient=self.bob, 
            content="Hello Bob!"
        )
        
        self.assertEqual(message.sender, self.alice)
        self.assertEqual(message.recipient, self.bob)
        self.assertEqual(message.content, "Hello Bob!")
        self.assertTrue(message.timestamp)
    
    def test_message_ordering(self):
        """測試訊息排序"""
        msg1 = create_test_message(self.alice, self.bob, "First")
        msg2 = create_test_message(self.bob, self.alice, "Second")
        
        messages = Message.objects.all()
        self.assertEqual(messages[0], msg1)
        self.assertEqual(messages[1], msg2)
    
    def test_related_names(self):
        """測試關聯關係"""
        create_test_message(self.alice, self.bob, "Sent by Alice")
        create_test_message(self.charlie, self.alice, "Received by Alice")
        
        # 測試反向關聯
        self.assertEqual(self.alice.sent_messages.count(), 1)
        self.assertEqual(self.alice.received_messages.count(), 1)
        
        # 測試級聯刪除
        alice_sent_count = self.alice.sent_messages.count()
        alice_received_count = self.alice.received_messages.count()
        self.alice.delete()
        
        # Alice 相關的所有訊息都應該被刪除
        self.assertEqual(Message.objects.count(), 0)

class ChatConsumerTest(TransactionTestCase):
    """WebSocket 測試需要使用 TransactionTestCase"""
    
    @database_sync_to_async
    def create_test_users(self):
        """非同步建立測試用戶"""
        coords = TestCoordinates
        alice = create_test_user("Alice", *coords.TAIPEI_MAIN_STATION)
        bob = create_test_user("Bob", *coords.TAIPEI_101)
        return alice, bob
    
    async def test_websocket_connection(self):
        """測試 WebSocket 連接建立"""
        await self.create_test_users()
        
        communicator = WebsocketCommunicator(
            application, "/ws/chat/Alice/Bob/"
        )
        connected, _ = await communicator.connect()
        
        self.assertTrue(connected)
        await communicator.disconnect()
    
    async def test_room_naming_logic(self):
        """測試聊天室命名邏輯 (字母順序)"""
        await self.create_test_users()
        
        # Alice 連接到 Bob
        comm1 = WebsocketCommunicator(application, "/ws/chat/Alice/Bob/")
        await comm1.connect()
        
        # Bob 連接到 Alice (應該是同一個房間)
        comm2 = WebsocketCommunicator(application, "/ws/chat/Bob/Alice/")
        await comm2.connect()
        
        # 發送訊息測試房間共享
        await comm1.send_json_to({"message": "Hello from Alice"})
        response = await comm2.receive_json_from()
        
        self.assertEqual(response['sender_name'], 'Alice')
        self.assertEqual(response['message'], 'Hello from Alice')
        
        await comm1.disconnect()
        await comm2.disconnect()
    
    async def test_message_persistence(self):
        """測試訊息持久化到資料庫"""
        await self.create_test_users()
        
        communicator = WebsocketCommunicator(application, "/ws/chat/Alice/Bob/")
        await communicator.connect()
        
        await communicator.send_json_to({"message": "Persistent message"})
        await communicator.receive_json_from()
        
        # 檢查資料庫中是否有訊息
        message_count = await database_sync_to_async(Message.objects.count)()
        self.assertEqual(message_count, 1)
        
        message = await database_sync_to_async(Message.objects.first)()
        self.assertEqual(message.content, "Persistent message")
        
        await communicator.disconnect()
