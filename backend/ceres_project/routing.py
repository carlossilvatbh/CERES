# WebSocket routing for CERES alerts
from django.urls import re_path
from core.alerts import AlertConsumer

websocket_urlpatterns = [
    re_path(r'ws/alerts/$', AlertConsumer.as_asgi()),
]

