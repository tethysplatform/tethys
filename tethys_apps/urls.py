"""
********************************************************************************
* Name: urls.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
# from django.db.utils import ProgrammingError
# from django.core.exceptions import ObjectDoesNotExist
from django.conf.urls import url, include
from tethys_apps.harvester import SingletonHarvester
from tethys_apps.views import library, send_beta_feedback_email
import logging

tethys_log = logging.getLogger('tethys.' + __name__)

# Get the harvester
harvester = SingletonHarvester()

# Sync the tethys apps database
harvester.sync_tethys_db()

urlpatterns = [
    url(r'^$', library, name='app_library'),
    url(r'^send-beta-feedback/$', send_beta_feedback_email, name='send_beta_feedback'),
]

# Append the app urls urlpatterns
app_url_patterns, extension_url_patterns = harvester.get_url_patterns()

for namespace, urls in app_url_patterns.items():
    root_pattern = r'^{0}/'.format(namespace.replace('_', '-'))
    urlpatterns.append(url(root_pattern, include(urls, namespace=namespace)))

extension_urls = []

for namespace, urls in extension_url_patterns.items():
    root_pattern = r'^{0}/'.format(namespace.replace('_', '-'))
    extension_urls.append(url(root_pattern, include(urls, namespace=namespace)))

# # Register permissions here?
# try:
#     register_app_permissions()
# except (ProgrammingError, ObjectDoesNotExist) as e:
#     tethys_log.error(e)

