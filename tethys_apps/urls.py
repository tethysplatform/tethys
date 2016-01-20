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

from tethys_apps.utilities import generate_app_url_patterns
from tethys_apps.views import library, send_beta_feedback_email

urlpatterns = [
    url(r'^$', library, name='app_library'),
    url(r'^send-beta-feedback/$', send_beta_feedback_email, name='send_beta_feedback'),
]

# Append the app urls urlpatterns
app_url_patterns = generate_app_url_patterns()

for namespace, urls in app_url_patterns.iteritems():
    root_pattern = r'^{0}/'.format(namespace.replace('_', '-'))
    urlpatterns.append(url(root_pattern, include(urls, namespace=namespace)))