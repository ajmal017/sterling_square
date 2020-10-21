import os

from django.core.asgi import get_asgi_application

from sterling_square.websocket import Websocket_test

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'websocket_app.settings')

django_application = get_asgi_application()


async def application(scope, receive, send):
    if scope['type'] == 'http':
        await django_application(scope, receive, send)
    elif scope['type'] == 'websocket':
        await Websocket_test(scope, receive, send).websocket_application()
    else:
        raise NotImplementedError(f"Unknown scope type {scope['type']}")
