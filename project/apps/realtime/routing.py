# realtime/routing.py
from django.urls import path, include, re_path

from . import consumers

websocket_urlpatterns = [
    path('ws/auction/<int:auction_id>/', consumers.RealtimeConsumer),
    path('ws/login/<username>/', consumers.ConsumerLoginCheck),
]
