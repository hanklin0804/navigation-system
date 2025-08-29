# backend/tests/base.py
from django.test import TestCase
from django.contrib.gis.geos import Point
from .utils import TestCoordinates, create_test_user

class BaseTestCase(TestCase):
    """基礎測試類別，提供常用測試資料"""
    
    @classmethod
    def setUpTestData(cls):
        """建立所有測試共用的資料"""
        coords = TestCoordinates
        cls.alice = create_test_user("Alice", *coords.TAIPEI_MAIN_STATION)
        cls.bob = create_test_user("Bob", *coords.TAIPEI_101)
        cls.charlie = create_test_user("Charlie", *coords.SHILIN_NIGHT_MARKET)
    
    def assertPointEqual(self, point1, point2, places=7):
        """比較兩個地理座標點，允許精度誤差"""
        self.assertAlmostEqual(point1.x, point2.x, places=places)
        self.assertAlmostEqual(point1.y, point2.y, places=places)