from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url

from . import consumers


application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter([
            url('ws/ids/', consumers.FlightConsumer),
        ])
    ),
})