"""
ASGI config for taxi_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taxi_backend.settings')
django.setup()



from channels.routing import ProtocolTypeRouter, URLRouter # Channels 所提供的 ASGI 路由系統
from django.core.asgi import get_asgi_application # ASGI HTTP 處理函式
from chat.routing import websocket_urlpatterns

# 定義 ASGI 應用的入口點
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(websocket_urlpatterns),  
})
