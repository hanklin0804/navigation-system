# # geouser/serializers.py
# from rest_framework import serializers
# from django.contrib.gis.geos import Point
# from .models import UserLocation

# class UserLocationSerializer(serializers.ModelSerializer):
#     lat = serializers.FloatField(write_only=True)
#     lng = serializers.FloatField(write_only=True)

#     class Meta:
#         model = UserLocation
#         fields = ['name', 'lat', 'lng']

#     def create(self, validated_data):
#         lat = validated_data.pop('lat')
#         lng = validated_data.pop('lng')
#         name = validated_data['name']
#         point = Point(lng, lat)  # 經緯度順序：X=lng, Y=lat
#         instance, _ = UserLocation.objects.update_or_create(
#             name=name,
#             defaults={'location': point}
#         )
#         return instance
