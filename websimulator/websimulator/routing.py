from channels.routing import ProtocolTypeRouter, ChannelNameRouter, URLRouter
from django.conf.urls import url

from connections import consumers

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    "websocket": URLRouter([
        url("^$", consumers.WsConnectionConsumer),
    ]),
    "channel": ChannelNameRouter({
        "simulator": consumers.SimulateConsumer,
    })
})
