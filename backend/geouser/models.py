# geouser/models.py
from django.contrib.gis.db import models

class UserLocation(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.PointField(geography=True)  # 經緯度
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} @ {self.location.y}, {self.location.x}"

