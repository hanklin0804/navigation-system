# geouser/urls.py
from django.urls import path
from .views import UserLocationCreateView, NearbyUserSearchView

urlpatterns = [
    path('users/', UserLocationCreateView.as_view()),
    path('users/nearby/', NearbyUserSearchView.as_view()),
]