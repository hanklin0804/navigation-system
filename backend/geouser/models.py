# geouser/models.py
from django.contrib.gis.db import models

class UserLocation(models.Model):
    name = models.CharField(max_length=100, unique=True)

    # geography=True，表示WGS84 經緯度座標系統
    location = models.PointField(geography=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    # 當 print 或 admin 頁面顯示此物件時，使用以下格式呈現 
    # 在 Django admin 介面或 shell 裡輸出會非常直觀（"Hank @ 25.03, 121.56"）
    def __str__(self):
        return f"{self.name} @ {self.location.y}, {self.location.x}"

