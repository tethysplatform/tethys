"""
********************************************************************************
* Name: urls.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

import logging
from django.urls import include, re_path
from channels.routing import URLRouter
from tethys_apps.harvester import SingletonHarvester
from tethys_apps.views import library, send_beta_feedback_email
from tethys_apps.utilities import get_configured_standalone_app
from django.conf import settings
from django.views.generic.base import RedirectView

tethys_log = logging.getLogger("tethys." + __name__)
prefix_url = f"{settings.PREFIX_URL}"

urlpatterns = [
    re_path(
        r"^send-beta-feedback/$", send_beta_feedback_email, name="send_beta_feedback"
    ),
]

url_namespaces = None
if settings.MULTIPLE_APP_MODE:
    urlpatterns.append(re_path(r"^$", library, name="app_library"))
else:
    standalone_app = get_configured_standalone_app()
    if standalone_app:
        url_namespaces = [standalone_app.url_namespace]
    else:
        urlpatterns.append(
            re_path(
                r"^$", RedirectView.as_view(pattern_name="user:profile"), name="home"
            )
        )

# Append the app urls urlpatterns
harvester = SingletonHarvester()
normal_url_patterns = harvester.get_url_patterns(url_namespaces=url_namespaces)
handler_url_patterns = harvester.get_handler_patterns(url_namespaces=url_namespaces)

# configure handler HTTP routes
http_handler_patterns = []
for namespace, urls in handler_url_patterns["http_handler_patterns"].items():
    if settings.MULTIPLE_APP_MODE:
        root_pattern = f'apps/{namespace.replace("_", "-")}/'
    else:
        root_pattern = ""

    if prefix_url is not None and prefix_url != "/":
        root_pattern = f"{prefix_url}/{root_pattern}"
    root_pattern = rf"^{root_pattern}"

    http_handler_patterns.append(re_path(root_pattern, URLRouter(urls)))

# Add app url patterns to urlpatterns, namespaced per app appropriately
for namespace, urls in normal_url_patterns["app_url_patterns"].items():
    if settings.MULTIPLE_APP_MODE:
        root_pattern = r"^{0}/".format(namespace.replace("_", "-"))
    else:
        root_pattern = ""

    urlpatterns.append(
        re_path(root_pattern, include((urls, namespace), namespace=namespace))
    )

# Collect url patterns for extensions, namespaced per app appropriately
ext_url_patterns = normal_url_patterns["ext_url_patterns"]
extension_urls = []
for namespace, urls in ext_url_patterns.items():
    if settings.MULTIPLE_APP_MODE:
        root_pattern = r"^{0}/".format(namespace.replace("_", "-"))
    else:
        root_pattern = r"^"

    extension_urls.append(
        re_path(root_pattern, include((urls, namespace), namespace=namespace))
    )

# Collect all app WebSocket URLs into one list and prepend with "apps/<root-url>"
app_websocket_url_patterns = normal_url_patterns["ws_url_patterns"]
handler_websocket_url_patterns = handler_url_patterns["ws_handler_patterns"]


def prepare_websocket_urls(app_websocket_url_patterns):
    prepared_urls = []
    for namespace, urls in app_websocket_url_patterns.items():
        if settings.MULTIPLE_APP_MODE:
            root_url = f'apps/{namespace.replace("_", "-")}/'
        else:
            root_url = ""

        for u in urls:
            url_str = str(u.pattern).replace("^", "")
            namespaced_url_str = rf"^{root_url}{url_str}"
            if prefix_url is not None and prefix_url != "/":
                namespaced_url_str = rf"^{prefix_url}/{root_url}{url_str}"
            namespaced_url = re_path(namespaced_url_str, u.callback, name=u.name)
            prepared_urls.append(namespaced_url)

    return prepared_urls


app_websocket_urls = prepare_websocket_urls(app_websocket_url_patterns)
app_websocket_urls += prepare_websocket_urls(handler_websocket_url_patterns)
