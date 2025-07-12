from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.gis.geos import Point # 地理空間的點
from django.contrib.gis.measure import D # 地理距離單位
from .models import UserLocation
from .serializers import UserLocationSerializer, UserLocationCreateSerializer
import socket # 取得目前執行此程式的主機ID
from django.db import IntegrityError # 捕捉資料庫唯一性錯誤
from drf_spectacular.utils import extend_schema, OpenApiParameter # 自動產生 API 文件的標註工具

class UserLocationCreateView(APIView):
    """
    接收認證使用者的經緯度，建立或更新對應的地理位置。
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=UserLocationCreateSerializer,
        responses={200: UserLocationSerializer}
    )
    def post(self, request):
        # 使用序列化器來驗證輸入資料
        serializer = UserLocationCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        point = Point(data['lng'], data['lat']) # 建立 GEOS 點（經度在前，緯度在後）

        try:
            # 使用認證使用者建立或更新地理位置
            obj, created = UserLocation.objects.update_or_create(
                user=request.user,
                defaults={"location": point}
            )
            output = UserLocationSerializer(obj).data # 回傳序列化結果
            output['message'] = "已建立" if created else "已更新"
            output['served_by'] = socket.gethostname() # 加上是哪台機器處理的
            return Response(output, status=200)

        except IntegrityError:
            return Response({"error": "位置更新失敗"}, status=409)
        
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class NearbyUserSearchView(APIView):
    """
    根據認證使用者的位置與可選的查詢半徑，查找附近的其他使用者。
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='radius', required=False, type=float, description='查詢半徑（公里）'),
        ],
        responses={200: UserLocationSerializer(many=True)} # many=True，回傳多筆使用者資料
    )
    def get(self, request):
        radius = request.query_params.get('radius', 2)

        try:
            radius = float(radius)
        except ValueError:
            return Response({"error": "radius 必須為數字"}, status=400)

        try:
            # 取得認證使用者的位置
            user_location = UserLocation.objects.get(user=request.user)
        except UserLocation.DoesNotExist:
            return Response({"error": "請先設定您的位置"}, status=404)

        # 查詢距離在 radius 公里以內的其他使用者（排除自己）
        nearby_users = UserLocation.objects.filter(
            location__distance_lte=(user_location.location, D(km=radius))
        ).exclude(user=request.user)

        # 回傳中心點座標、查詢半徑、附近使用者列表
        return Response({
            "center": {"lat": user_location.location.y, "lng": user_location.location.x},
            "radius_km": radius,
            "nearby": UserLocationSerializer(nearby_users, many=True).data # 對多筆使用者序列化
        })
