from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import socket_test.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'socket_test': AuthMiddlewareStack(
        URLRouter(
            socket_test.routing.websocket_urlpatterns
        )
    ),
})
