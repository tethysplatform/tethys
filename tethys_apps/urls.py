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

tethys_log = logging.getLogger('tethys.' + __name__)

urlpatterns = [
    re_path(r'^$', library, name='app_library'),
    re_path(r'^send-beta-feedback/$', send_beta_feedback_email, name='send_beta_feedback'),
]

# Append the app urls urlpatterns
harvester = SingletonHarvester()
normal_url_patterns = harvester.get_url_patterns()
handler_url_patterns = harvester.get_handler_patterns()

# configure handler HTTP routes
http_handler_patterns = []
for namespace, urls in handler_url_patterns['http_handler_patterns'].items():
    root_pattern = r'^apps/{0}/'.format(namespace.replace('_', '-'))
    http_handler_patterns.append(re_path(root_pattern, URLRouter(urls)))

# Add app url patterns to urlpatterns, namespaced per app appropriately
for namespace, urls in normal_url_patterns['app_url_patterns'].items():
    root_pattern = r'^{0}/'.format(namespace.replace('_', '-'))
    urlpatterns.append(re_path(root_pattern, include((urls, namespace), namespace=namespace)))

# Collect url patterns for extensions, namespaced per app appropriately
ext_url_patterns = normal_url_patterns['ext_url_patterns']
extension_urls = []
for namespace, urls in ext_url_patterns.items():
    root_pattern = r'^{0}/'.format(namespace.replace('_', '-'))
    extension_urls.append(re_path(root_pattern, include((urls, namespace), namespace=namespace)))

# Collect all app WebSocket URLs into one list and prepend with "apps/<root-url>"
app_websocket_url_patterns = normal_url_patterns['ws_url_patterns']
handler_websocket_url_patterns = handler_url_patterns['ws_handler_patterns']


def prepare_websocket_urls(app_websocket_url_patterns):
    prepared_urls = []
    for namespace, urls in app_websocket_url_patterns.items():
        root_url = namespace.replace('_', '-')
        for u in urls:
            url_str = str(u.pattern).replace("^", "")
            namespaced_url_str = f'^apps/{root_url}/{url_str}'
            namespaced_url = re_path(namespaced_url_str, u.callback, name=u.name)
            prepared_urls.append(namespaced_url)

    return prepared_urls


app_websocket_urls = prepare_websocket_urls(app_websocket_url_patterns)
app_websocket_urls += prepare_websocket_urls(handler_websocket_url_patterns)
