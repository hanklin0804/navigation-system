# backend/test_settings.py
from taxi_backend.settings import *

# 測試專用設定
DATABASES['default']['TEST'] = {
    'NAME': 'test_navigation_db',
    'MIRROR': None,
}

# 禁用 logging 減少測試輸出
LOGGING_CONFIG = None

# 測試時使用記憶體快取
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# 測試時使用內存通道層
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}