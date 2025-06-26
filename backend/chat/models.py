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
        related_name='sent_messages',     # 讓view.py可以寫 user.sent_messages.all()，查這個使用者傳送的所有訊息
        on_delete=models.CASCADE          # 使用者被刪除時，訊息也一併刪除
    )

    # 訊息的接收者
    recipient = models.ForeignKey(
        UserLocation,
        related_name='received_messages', # user.received_messages.all()
        on_delete=models.CASCADE
    )
    
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['timestamp']
