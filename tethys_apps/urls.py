"""
********************************************************************************
* Name: urls.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
import itertools
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

# Retrieve WebSocket URL patterns
app_websocket_url_patterns = normal_url_patterns['ws_url_patterns']
handler_websocket_url_patterns = handler_url_patterns['ws_handler_patterns']

# Collect all app WebSocket URLs into one list
app_websocket_urls = []
app_websocket_urls.extend(
    list(
        itertools.chain.from_iterable(
            app_websocket_url_patterns.values()
        )
    )
)
app_websocket_urls.extend(
    list(
        itertools.chain.from_iterable(
            handler_websocket_url_patterns.values()
        )
    )
)
