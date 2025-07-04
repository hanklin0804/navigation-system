# geouser/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D # Distance，用於 GeoDjango 查詢距離
from .models import UserLocation
import socket  
from django.db import transaction, IntegrityError  

# 使用者位置建立或更新
class UserLocationCreateView(APIView):
    def post(self, request):
        try:
            name = request.data.get('name')
            lat = request.data.get('lat')
            lng = request.data.get('lng')

            if not name or lat is None or lng is None:
                return Response({"error": "缺少資料"}, status=status.HTTP_400_BAD_REQUEST)

            point = Point(float(lng), float(lat)) 
            
            # 加入原子操作，防止 race condition
            # with transaction.atomic():
            obj, created = UserLocation.objects.update_or_create(
                name=name,
                defaults={"location": point}
            )

            return Response({
                "message": "已建立" if created else "已更新",
                "name": obj.name,
                "lat": obj.location.y, # y 是緯度
                "lng": obj.location.x, # x 是經度
                "served_by": socket.gethostname(),  #  顯示是哪個 instance 處理
            }, status=status.HTTP_200_OK)

        # 若發生資料競爭導致 IntegrityError，回傳 409 衝突
        except IntegrityError:
            return Response({"error": "此名稱已被其他 instance 同時註冊，請稍後重試"}, status=409)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 搜尋附近其他使用者
class NearbyUserSearchView(APIView):
    def get(self, request):
        name = request.query_params.get('name')
        radius = request.query_params.get('radius', 2)  # 預設 2 公里
        try:
            radius = float(radius)
        except (ValueError, TypeError):
            return Response({"error": "radius 必須為數字"}, status=400)

        try:
            user = UserLocation.objects.get(name=name)
        except UserLocation.DoesNotExist:
            return Response({"error": "找不到使用者"}, status=404)

        nearby_users = UserLocation.objects.filter(
            location__distance_lte=(user.location, D(km=radius))
        ).exclude(name=name)  # 排除自己

        result = [
            {
                "name": u.name,
                "lat": u.location.y,
                "lng": u.location.x
            }
            for u in nearby_users
        ]

        # 回傳包含：中心使用者位置、查詢半徑、附近使用者列表
        return Response({
            "center": {"lat": user.location.y, "lng": user.location.x},
            "radius_km": radius,
            "nearby": result
        })
