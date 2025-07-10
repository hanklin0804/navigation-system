from rest_framework import serializers
from .models import UserLocation

# 回傳並轉換 model 資料給前端
class UserLocationSerializer(serializers.ModelSerializer):
    # 從 Model: UserLocation的 PointField 拆出經緯度）
    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()

    class Meta:
        model = UserLocation # 對應的模型
        fields = ['name', 'lat', 'lng', 'created_at'] # 要輸出的欄位

    # get_<欄位名稱>，SerializerMethodField 自動呼叫的約定命名。
    def get_lat(self, obj):
        return obj.location.y

    def get_lng(self, obj):
        return obj.location.x

# 驗證前端輸入的資料格式
class UserLocationCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    lat = serializers.FloatField()
    lng = serializers.FloatField()
