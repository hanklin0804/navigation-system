# chat/models.py
from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    # 訊息的發送者，直接使用 Django User 模型
    # 每一個 Message 訊息，只能對應一個 User（即一對一）;
    # 反過來說，一個使用者可以對應到很多則 Message（一對多）
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,         # 使用者被刪除時，訊息也一併刪除
        related_name='sent_messages'
    )

    # 訊息的接收者
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['timestamp']
