# socket_test.py
async def websocket_application(scope, receive, send):
    while True:
        event = await receive()

        if event['type'] == 'socket_test.connect':
            await send({
                'type': 'socket_test.accept'
            })

        if event['type'] == 'socket_test.disconnect':
            break

        if event['type'] == 'socket_test.receive':
            if event['text'] == 'ping':
                await send({
                    'type': 'socket_test.send',
                    'text': 'pong!'
                })
