import re
from django.conf.urls import url
from channels.http import AsgiHandler

from tethys_apps.jupyterapp import consumers


class RoutingConfiguration(object):

    _websocket_urlpatterns = []

    _http_urlpatterns = [url(r'^asynchttp$', consumers.BasicHttpConsumer), url(r"", AsgiHandler),  # other sync urls go to sync handler
                        ]

    def __init__(self, applications_dict):

        for k, v in applications_dict.items():
            k = k.replace('/', '')
            self._add_new_routing(k, v)

    def get_websocket_urlpatterns(self):
        return self._websocket_urlpatterns

    def get_http_urlpatterns(self):
        return self._http_urlpatterns

    def _add_new_routing(self, app_name, app_context_obj):

        kwargs = {"application_context": app_context_obj, "bokeh_websocket_path": "/{}/ws".format(app_name)}

        # http
        url_str = app_name
        url_reg_str = r"^scripts/" + re.escape(url_str) + r"$"
        self._http_urlpatterns.insert(0, url(url_reg_str, consumers.BokehAppHTTPConsumer, kwargs=kwargs))

        # ws
        url_str = "{}/ws".format(app_name)
        url_reg_str = r"^scripts/" + re.escape(url_str) + r"$"
        self._websocket_urlpatterns.insert(0, url(url_reg_str, consumers.BokehAppWebsocketConsumer, kwargs=kwargs))
