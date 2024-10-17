from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from apps.realtime.routing import websocket_urlpatterns
from apps.realtime.consumers import TokenAuthMiddleware

TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))

application = ProtocolTypeRouter(
    {
        # Empty for now (http->django views is added by default)
        'websocket': TokenAuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)
