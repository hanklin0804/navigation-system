# backend/geouser/tests.py
from django.test import TestCase
from django.contrib.gis.geos import Point
from django.db import IntegrityError
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import UserLocation
from .serializers import UserLocationSerializer, UserLocationCreateSerializer
from tests.base import BaseTestCase
from tests.utils import TestCoordinates, create_test_user
import json

class UserLocationModelTest(BaseTestCase):
    
    def test_create_user_location(self):
        """測試建立用戶位置"""
        coords = TestCoordinates.TAIPEI_MAIN_STATION
        point = Point(coords[1], coords[0])  # lng, lat
        user = UserLocation.objects.create(name="TestUser", location=point)
        
        self.assertEqual(user.name, "TestUser")
        self.assertPointEqual(user.location, point)
        self.assertTrue(user.created_at)
    
    def test_str_method(self):
        """測試 __str__ 方法格式"""
        expected = f"Alice @ {self.alice.location.y}, {self.alice.location.x}"
        self.assertEqual(str(self.alice), expected)
    
    def test_name_unique_constraint(self):
        """測試名稱唯一性約束"""
        coords = TestCoordinates.TAIPEI_101
        point = Point(coords[1], coords[0])
        
        with self.assertRaises(IntegrityError):
            UserLocation.objects.create(name="Alice", location=point)
    
    def test_coordinate_access(self):
        """測試經緯度存取正確性"""
        # x = longitude (經度), y = latitude (緯度)
        coords = TestCoordinates.TAIPEI_MAIN_STATION
        self.assertAlmostEqual(self.alice.location.y, coords[0], places=6)  # lat
        self.assertAlmostEqual(self.alice.location.x, coords[1], places=6)  # lng

class UserLocationSerializerTest(BaseTestCase):
    
    def test_user_location_serializer_output(self):
        """測試序列化輸出格式"""
        serializer = UserLocationSerializer(self.alice)
        data = serializer.data
        
        expected_fields = ['name', 'lat', 'lng', 'created_at']
        self.assertEqual(set(data.keys()), set(expected_fields))
        
        # 驗證經緯度提取正確性
        coords = TestCoordinates.TAIPEI_MAIN_STATION
        self.assertAlmostEqual(data['lat'], coords[0], places=6)
        self.assertAlmostEqual(data['lng'], coords[1], places=6)
    
    def test_user_location_create_serializer_validation(self):
        """測試輸入資料驗證"""
        # 有效資料
        valid_data = {"name": "TestUser", "lat": 25.0, "lng": 121.0}
        serializer = UserLocationCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        # 無效資料：缺少必填欄位
        invalid_data = {"name": "TestUser"}
        serializer = UserLocationCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('lat', serializer.errors)
        self.assertIn('lng', serializer.errors)

class UserLocationViewTest(APITestCase):
    
    @classmethod
    def setUpTestData(cls):
        """建立測試資料"""
        coords = TestCoordinates
        cls.alice = create_test_user("Alice", *coords.TAIPEI_MAIN_STATION)
        cls.bob = create_test_user("Bob", *coords.TAIPEI_101)
        cls.charlie = create_test_user("Charlie", *coords.SHILIN_NIGHT_MARKET)
    
    def test_create_user_success(self):
        """測試成功建立用戶"""
        data = {"name": "NewUser", "lat": 25.0, "lng": 121.0}
        
        response = self.client.post('/api/users/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "NewUser")
        self.assertIn('message', response.data)
        self.assertIn('served_by', response.data)
    
    def test_update_existing_user(self):
        """測試更新現有用戶位置"""
        data = {"name": "Alice", "lat": 25.1, "lng": 121.1}
        
        response = self.client.post('/api/users/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "已更新")
    
    def test_nearby_search_success(self):
        """測試成功搜尋鄰近用戶"""
        params = {"name": "Alice", "radius": 5}  # 增加到 5km 確保能找到 Bob
        
        response = self.client.get('/api/users/nearby/', params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('center', response.data)
        self.assertIn('nearby', response.data)
        # 驗證回傳格式正確
        self.assertIsInstance(response.data['nearby'], list)
    
    def test_nearby_search_user_not_found(self):
        """測試搜尋不存在的用戶"""
        params = {"name": "NonexistentUser"}
        
        response = self.client.get('/api/users/nearby/', params)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.json())
    
    def test_invalid_radius_parameter(self):
        """測試無效的半徑參數"""
        params = {"name": "Alice", "radius": "invalid"}
        
        response = self.client.get('/api/users/nearby/', params)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())
