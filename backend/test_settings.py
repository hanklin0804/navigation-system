# backend/test_settings.py
import os
from taxi_backend.settings import *

# 測試專用資料庫設定
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('POSTGRES_DB', 'test_db'),
        'USER': os.environ.get('POSTGRES_USER', 'test_user'), 
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'test_pass'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'TEST': {
            'NAME': 'test_navigation_db',
            'MIRROR': None,
        },
    }
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