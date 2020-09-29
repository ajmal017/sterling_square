import json

from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from socket_test.kiteSocket import kws


class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.ws = kws
        kws.on_ticks = self.on_ticks
        kws.connect(threaded=True)

    def on_ticks(self, ws, ticks):
        # Callback to receive ticks.
        print(ticks)
        # logging.debug("WS: {}".format(ticks))
        self.send(text_data=json.dumps({
            'message': ticks
        }))

    # async def demo(self, data):
    #     print("data", data)


    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, byte_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print("messaggg:::::", message)
        kws.subscribe([int(i) for i in message])
        # Send message to room group
        await self.send(text_data=json.dumps({
            'message': message
        }))
        # await self.channel_layer.group_send(
        #     self.room_group_name,
        #     {
        #         'type': 'on_ticks',
        #         'message': message
        #     }
        # )

    # # Receive message from room group
    # async def chat_message(self, event):
    #     message = event['message']
    #
    #     # Send message to WebSocket
    #     await self.send(text_data=json.dumps({
    #         'message': message
    #     }))
