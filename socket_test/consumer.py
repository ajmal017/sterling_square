import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer

from socket_test.kiteSocket import kws


def event_triger(data, group_name):
    print("called")
    ChatConsumer().send_chat_message(data)
    # channel_layer = get_channel_layer()
    # async_to_sync(channel_layer.group_send)(
    #     group_name,
    #     {
    #         'type': 'chat_message',
    #         'message': data
    #     }
    # )


class ChatConsumer(AsyncWebsocketConsumer):
    local_ticks = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.ws = kws
        kws.on_ticks = self.on_ticks
        kws.connect(threaded=True)

    def on_ticks(self, ws, ticks):
        # Callback to receive ticks.
        print("WS: {}".format(ticks))
        self.demo(ticks)

    def demo(self, message):
        print("called")
        async_to_sync(self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        ))

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        # counter = 1
        await self.send(text_data=json.dumps({
            'message': "handshake success"
        }))

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
        kws.subscribe([int(message)])
        # Send message to room group
        # await self.send(text_data=json.dumps({
        #     'message': message
        # }))
        # await self.demo(message)
        await self.send_chat_message(message)

    async def send_chat_message(self, message):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        print("mess", message)
        # Send message to WebSocket
        print(__class__.local_ticks)
        await self.send(text_data=json.dumps({
            'message': message
        }))
#
