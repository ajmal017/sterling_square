from django.urls import path

from websocket import consumer

websocket_urlpatterns = [
    path('ws/', consumer.Consumer),
]
