# backend/tests/utils.py
from django.contrib.gis.geos import Point
from geouser.models import UserLocation
from chat.models import Message

# 測試座標常數
class TestCoordinates:
    TAIPEI_MAIN_STATION = (25.0478, 121.5170)  # lat, lng
    TAIPEI_101 = (25.0340, 121.5645)
    SHILIN_NIGHT_MARKET = (25.0875, 121.5240)

# 測試資料建立輔助函數
def create_test_user(name, lat, lng):
    """建立測試用戶"""
    point = Point(lng, lat)  # Point(lng, lat) 順序很重要
    return UserLocation.objects.create(name=name, location=point)

def create_test_message(sender, recipient, content="Test message"):
    """建立測試訊息"""
    return Message.objects.create(
        sender=sender, 
        recipient=recipient, 
        content=content
    )