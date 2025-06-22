# geouser/urls.py
from django.urls import path
from .views import UserLocationCreateView, NearbyUserSearchView

urlpatterns = [
    path('users/', UserLocationCreateView.as_view(), name='user-create'),
    path('users/nearby/', NearbyUserSearchView.as_view(), name='user-nearby'),
]