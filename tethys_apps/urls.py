"""
********************************************************************************
* Name: urls.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from django.conf.urls import url, include
from tethys_apps.harvester import SingletonHarvester
from tethys_apps.views import library, send_beta_feedback_email
import logging

tethys_log = logging.getLogger('tethys.' + __name__)

urlpatterns = [
    url(r'^$', library, name='app_library'),
    url(r'^send-beta-feedback/$', send_beta_feedback_email, name='send_beta_feedback'),
]

# Append the app urls urlpatterns
harvester = SingletonHarvester()
app_url_patterns = harvester.get_url_patterns()['app_url_patterns']
ext_url_patterns = harvester.get_url_patterns()['ext_url_patterns']

for namespace, urls in app_url_patterns.items():
    root_pattern = r'^{0}/'.format(namespace.replace('_', '-'))
    urlpatterns.append(url(root_pattern, include((urls, namespace), namespace=namespace)))

extension_urls = []

for namespace, urls in ext_url_patterns.items():
    root_pattern = r'^{0}/'.format(namespace.replace('_', '-'))
    extension_urls.append(url(root_pattern, include((urls, namespace), namespace=namespace)))
