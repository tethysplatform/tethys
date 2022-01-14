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
from django.conf.urls import url, include
from tethys_apps.harvester import SingletonHarvester
from tethys_apps.views import library, send_beta_feedback_email

tethys_log = logging.getLogger('tethys.' + __name__)

urlpatterns = [
    url(r'^$', library, name='app_library'),
    url(r'^send-beta-feedback/$', send_beta_feedback_email, name='send_beta_feedback'),
]

# Append the app urls urlpatterns
harvester = SingletonHarvester()
normal_url_patterns = harvester.get_url_patterns()
handler_url_patterns = harvester.get_handler_patterns()
app_url_patterns = normal_url_patterns['app_url_patterns']
http_handler_patterns = handler_url_patterns['http_handler_patterns']

# Combine normal and handler http url patterns from apps
combined_app_url_patterns = dict()
app_namespaces = set(app_url_patterns.keys())\
    .union(http_handler_patterns.keys())

for namespace in app_namespaces:
    normal_urls = app_url_patterns.get(namespace, [])
    handler_urls = http_handler_patterns.get(namespace, [])
    combined_urls = normal_urls + handler_urls
    combined_app_url_patterns[namespace] = combined_urls

# Add combined app url patterns to urlpatterns, namespaced per app appropriately
for namespace, urls in combined_app_url_patterns.items():
    root_pattern = r'^{0}/'.format(namespace.replace('_', '-'))
    urlpatterns.append(url(root_pattern, include((urls, namespace), namespace=namespace)))

# Collect url patterns for extensions, namespaced per app appropriately
ext_url_patterns = normal_url_patterns['ext_url_patterns']
extension_urls = []
for namespace, urls in ext_url_patterns.items():
    root_pattern = r'^{0}/'.format(namespace.replace('_', '-'))
    extension_urls.append(url(root_pattern, include((urls, namespace), namespace=namespace)))

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
            namespaced_url = url(namespaced_url_str, u.callback, name=u.name)
            prepared_urls.append(namespaced_url)

    return prepared_urls


app_websocket_urls = prepare_websocket_urls(app_websocket_url_patterns)
app_websocket_urls += prepare_websocket_urls(handler_websocket_url_patterns)
