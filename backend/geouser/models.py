# geouser/models.py
from django.contrib.gis.db import models
from django.contrib.auth.models import User

class UserLocation(models.Model):
    # 直接使用 Django User 模型，一對一關係
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='location')

    # geography=True，表示WGS84 經緯度座標系統
    location = models.PointField(geography=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    # 當 print 或 admin 頁面顯示此物件時，使用以下格式呈現 
    def __str__(self):
        return f"{self.user.username} @ {self.location.y}, {self.location.x}"

