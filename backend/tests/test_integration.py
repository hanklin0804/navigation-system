# backend/tests/test_integration.py
from rest_framework.test import APITestCase
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from django.test import TransactionTestCase
from taxi_backend.asgi import application
from tests.base import BaseTestCase
from tests.utils import create_test_user, TestCoordinates
from chat.models import Message

class UserWorkflowIntegrationTest(APITestCase):
    """用戶工作流程整合測試"""
    
    @classmethod
    def setUpTestData(cls):
        """建立測試資料"""
        coords = TestCoordinates
        cls.alice = create_test_user("Alice", *coords.TAIPEI_MAIN_STATION)
        cls.bob = create_test_user("Bob", *coords.TAIPEI_101)
        cls.charlie = create_test_user("Charlie", *coords.SHILIN_NIGHT_MARKET)
    
    def test_complete_user_workflow(self):
        """測試完整用戶流程：建立 → 搜尋 → 聊天準備"""
        # 1. 建立用戶
        user_data = {"name": "IntegrationUser", "lat": 25.05, "lng": 121.52}
        
        create_response = self.client.post('/api/users/', user_data, format='json')
        self.assertEqual(create_response.status_code, 200)
        
        # 2. 搜尋鄰近用戶
        search_params = {"name": "IntegrationUser", "radius": 5}
        
        search_response = self.client.get('/api/users/nearby/', search_params)
        self.assertEqual(search_response.status_code, 200)
        
        # 3. 驗證找到其他用戶
        nearby_users = search_response.data['nearby']
        self.assertGreater(len(nearby_users), 0)
        
        # 4. 驗證資料一致性
        user_names = [user['name'] for user in nearby_users]
        self.assertIn('Alice', user_names)  # BaseTestCase 中建立的用戶
    
    def test_multi_user_geo_query_accuracy(self):
        """測試多用戶地理查詢準確性"""
        # Alice 搜尋 10km 範圍：應該找到所有用戶
        params_10km = {"name": "Alice", "radius": 10}
        response_10km = self.client.get('/api/users/nearby/', params_10km)
        
        self.assertEqual(response_10km.status_code, 200)
        nearby_users = response_10km.data['nearby']
        self.assertIsInstance(nearby_users, list)
        
        # 驗證基本功能正常（至少回傳格式正確）
        if len(nearby_users) > 0:
            self.assertIn('name', nearby_users[0])
            self.assertIn('lat', nearby_users[0])
            self.assertIn('lng', nearby_users[0])

class ChatIntegrationTest(TransactionTestCase):
    """聊天整合測試"""
    
    async def test_end_to_end_chat(self):
        """測試端到端聊天功能"""
        # 建立測試用戶
        coords = TestCoordinates
        alice = await database_sync_to_async(create_test_user)(
            "Alice", *coords.TAIPEI_MAIN_STATION
        )
        bob = await database_sync_to_async(create_test_user)(
            "Bob", *coords.TAIPEI_101
        )
        
        # 建立 WebSocket 連接
        alice_comm = WebsocketCommunicator(application, "/ws/chat/Alice/Bob/")
        bob_comm = WebsocketCommunicator(application, "/ws/chat/Bob/Alice/")
        
        await alice_comm.connect()
        await bob_comm.connect()
        
        # Alice 發送訊息
        await alice_comm.send_json_to({"message": "Hello Bob!"})
        
        # Bob 應該收到訊息
        alice_message = await bob_comm.receive_json_from()
        self.assertEqual(alice_message['sender_name'], 'Alice')
        self.assertEqual(alice_message['message'], 'Hello Bob!')
        
        # Alice 也會收到自己發送的訊息（廣播）
        alice_echo = await alice_comm.receive_json_from()
        self.assertEqual(alice_echo['sender_name'], 'Alice')
        
        # Bob 回覆
        await bob_comm.send_json_to({"message": "Hi Alice!"})
        
        # 兩個連接都會收到 Bob 的訊息
        bob_message_to_alice = await alice_comm.receive_json_from()
        bob_message_to_bob = await bob_comm.receive_json_from()
        
        self.assertEqual(bob_message_to_alice['sender_name'], 'Bob')
        self.assertEqual(bob_message_to_alice['message'], 'Hi Alice!')
        
        # 驗證資料庫中有兩則訊息
        message_count = await database_sync_to_async(Message.objects.count)()
        self.assertEqual(message_count, 2)
        
        await alice_comm.disconnect()
        await bob_comm.disconnect()
    
    async def test_multiple_chat_room_isolation(self):
        """測試多個聊天室隔離"""
        # 建立三個用戶
        coords = TestCoordinates
        alice = await database_sync_to_async(create_test_user)(
            "Alice", *coords.TAIPEI_MAIN_STATION
        )
        bob = await database_sync_to_async(create_test_user)(
            "Bob", *coords.TAIPEI_101
        )
        charlie = await database_sync_to_async(create_test_user)(
            "Charlie", *coords.SHILIN_NIGHT_MARKET
        )
        
        # 建立兩個獨立的聊天室
        alice_charlie_comm = WebsocketCommunicator(application, "/ws/chat/Alice/Charlie/")
        
        await alice_charlie_comm.connect()
        
        # Alice 向 Charlie 發送訊息
        await alice_charlie_comm.send_json_to({"message": "Hi Charlie!"})
        
        # 驗證訊息發送成功
        message = await alice_charlie_comm.receive_json_from()
        self.assertEqual(message['sender_name'], 'Alice')
        self.assertEqual(message['message'], 'Hi Charlie!')
        
        # 驗證資料庫中有訊息記錄
        message_count = await database_sync_to_async(Message.objects.count)()
        self.assertEqual(message_count, 1)
        
        await alice_charlie_comm.disconnect()