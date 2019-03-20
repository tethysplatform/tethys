from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from tethys_apps.jupyterapp.routing import RoutingConfiguration
from tethys_apps.harvester import SingletonHarvester

harvester = SingletonHarvester()
applications = harvester.get_jupyter_applications()

routing_config = RoutingConfiguration(applications)

application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            routing_config.get_websocket_urlpatterns()
        )
    ),
    'http': AuthMiddlewareStack(
        URLRouter(
            routing_config.get_http_urlpatterns()
        )
    ),
})
