# chat/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<your_name>[^/]+)/(?P<target_name>[^/]+)/$', consumers.ChatConsumer.as_asgi())
]
