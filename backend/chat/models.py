# chat/models.py
from django.db import models
# 匯入 geouser app 中的 UserLocation 模型，用來建立發送者與接收者的關聯
from geouser.models import UserLocation

class Message(models.Model):
    # 訊息的發送者，與 UserLocation 是多對一關係（可從使用者查出他送出的所有訊息）
    # 每一個 Message 訊息，只能對應一個 UserLocation 使用者（即一對一）;
    # 反過來說，一個使用者可以對應到很多則 Message（一對多）
    sender = models.ForeignKey(
        UserLocation,
        on_delete=models.CASCADE,          # 使用者被刪除時，訊息也一併刪除
        related_name='sent_messages',      # 反向關聯名稱，讓 UserLocation 可以透過 user.sent_messages 查詢所有收到的訊息
        related_query_name='sent_message',
    )

    # 訊息的接收者
    recipient = models.ForeignKey(
        UserLocation,
        on_delete=models.CASCADE,
        related_name='received_messages',  
    )
    
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['timestamp']
