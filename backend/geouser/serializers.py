from rest_framework import serializers
from .models import UserLocation

# 回傳並轉換 model 資料給前端
class UserLocationSerializer(serializers.ModelSerializer):
    # 從 Model: UserLocation的 PointField 拆出經緯度
    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = UserLocation
        fields = ['username', 'lat', 'lng', 'created_at']

    def get_lat(self, obj):
        return obj.location.y

    def get_lng(self, obj):
        return obj.location.x
    
    def get_username(self, obj):
        return obj.user.username

# 驗證前端輸入的資料格式 - 只需要經緯度，user 從認證取得
class UserLocationCreateSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()
