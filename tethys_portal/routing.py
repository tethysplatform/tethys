from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from tethys_apps.harvester import SingletonHarvester

harvester = SingletonHarvester()
app_ws_patterns = harvester.get_url_patterns()['ws_url_patterns']

ws_routing_patterns = []

for namespace, urls in app_ws_patterns.items():
    for url in urls:
        ws_routing_patterns.append(url)

application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            ws_routing_patterns
        )
    )
})
