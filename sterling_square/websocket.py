# socket_test.py
from asgiref.sync import sync_to_async, async_to_sync

from socket_test.kiteSocket import kws


class Websocket_test(object):

    def __init__(self, scope, receive, send):
        kws.on_ticks = self.on_ticks
        kws.connect(threaded=True)
        self.scope = scope
        self.receive = receive
        self.send = send

    def on_ticks(self, ws, ticks):
        # Callback to receive ticks.
        print(ticks)
        # yield ticks

    async def websocket_application(self):
        while True:
            event = await self.receive()
            if event['type'] == 'websocket.connect':
                await self.send({
                    'type': 'websocket.accept',
                })
                await self.send({
                    'type': 'websocket.send',
                    'text': "success",
                })

            if event['type'] == 'websocket.disconnect':
                await self.send({
                    'type': 'websocket.send',
                    'text': 'closed'
                })
                break

            if event['type'] == 'websocket.receive':
                # if event['text'] == 'ping':
                    # kws.subscribe([5215745])
                await self.send({
                    'type': 'websocket.send',
                    'text': event['text']
                })
