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
app_url_patterns = normal_url_patterns['app_url_patterns']
ext_url_patterns = normal_url_patterns['ext_url_patterns']

# Add url patterns from apps, namespaced appropriately
for namespace, urls in app_url_patterns.items():
    root_pattern = r'^{0}/'.format(namespace.replace('_', '-'))
    urlpatterns.append(url(root_pattern, include((urls, namespace), namespace=namespace)))

# Collect url patterns for extension, namespaced appropriately
extension_urls = []
for namespace, urls in ext_url_patterns.items():
    root_pattern = r'^{0}/'.format(namespace.replace('_', '-'))
    extension_urls.append(url(root_pattern, include((urls, namespace), namespace=namespace)))

# Retriev generic websocket URL patterns
ws_url_patterns = normal_url_patterns['ws_url_patterns']

# Retrieve handler URL patterns
app_handler_patterns = harvester.get_handler_patterns()

# e.g.: bokeh handler_type => AutoloadJsConsumer
http_handler_patterns = app_handler_patterns['http_handler_patterns']

# e.g.: bokeh handler_type => WSConsumer
ws_handler_patterns = app_handler_patterns['ws_handler_patterns']

# Collect all app WebSocket URLs into one list
# TODO: These need to be namespaced per app
app_websocket_urls = []
app_websocket_urls.extend(
    list(
        itertools.chain.from_iterable(
            ws_url_patterns.values()
        )
    )
)
app_websocket_urls.extend(
    list(
        itertools.chain.from_iterable(
            ws_handler_patterns.values()
        )
    )
)

# Convert http_handler_patterns into a single list of URLs
app_http_handler_urls = list(
    itertools.chain.from_iterable(
        http_handler_patterns.values()
    )
)
