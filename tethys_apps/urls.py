"""
********************************************************************************
* Name: urls.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from django.conf.urls import patterns, url, include

from tethys_apps.utilities import generate_app_url_patterns

urlpatterns = patterns('',
    url(r'^$', 'tethys_apps.views.library', name='app_library'),
    url(r'^send-beta-feedback/$', 'tethys_apps.views.send_beta_feedback_email', name='send_beta_feedback'),
)

# Append the app urls urlpatterns
app_url_patterns = generate_app_url_patterns()

for namespace, urls in app_url_patterns.iteritems():
    root_pattern = r'^{0}/'.format(namespace.replace('_', '-'))
    urlpatterns.append(url(root_pattern, include(urls, namespace=namespace)))