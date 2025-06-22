# chat/models.py
from django.db import models
from geouser.models import UserLocation

class Message(models.Model):
    sender = models.ForeignKey(UserLocation, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(UserLocation, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['timestamp']
