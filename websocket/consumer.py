import json

from channels.generic.websocket import AsyncWebsocketConsumer


class Consumer(AsyncWebsocketConsumer):
    async def websocket_connect(self, message):
        await self.accept()

    async def websocket_disconnect(self, message):
        print(message)

    async def websocket_receive(self, message):
        print(message)
