from django.urls import re_path
from tethys_portal.views.app_lifecycle import AppLifeCycleConsumer


websocket_urlpatterns = [
    re_path(r"ws/app-lifecycle/(?P<app_name>\w+)/", AppLifeCycleConsumer.as_asgi()),
]
