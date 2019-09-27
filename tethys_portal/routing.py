from django.conf.urls import url as django_url

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.http import AsgiHandler

from tethys_apps.harvester import SingletonHarvester

harvester = SingletonHarvester()
app_ws_patterns = harvester.get_url_patterns()['ws_url_patterns']

app_handler_patterns = harvester.get_handler_patterns()
app_http_handler_patterns = app_handler_patterns['http_handler_patterns']
app_ws_handler_patterns = app_handler_patterns['ws_handler_patterns']

ws_routing_patterns = []

for namespace, urls in app_ws_patterns.items():
    for url in urls:
        ws_routing_patterns.append(url)

http_routing_patterns = []

for namespace, urls in app_http_handler_patterns.items():
    for url in urls:
        http_routing_patterns.append(url)

for namespace, urls in app_ws_handler_patterns.items():
    for url in urls:
        ws_routing_patterns.append(url)

application = ProtocolTypeRouter({
    # 'http' -> django views are added automatically
    'websocket': AuthMiddlewareStack(
        URLRouter(
            ws_routing_patterns
        )
    )
})

if http_routing_patterns:
    http_routing_patterns.append(django_url(r'', AsgiHandler))
    application.application_mapping['http'] = AuthMiddlewareStack(
        URLRouter(
            http_routing_patterns
        )
    )
