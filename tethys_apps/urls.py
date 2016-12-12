"""
********************************************************************************
* Name: urls.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from django.db.utils import ProgrammingError
from django.core.exceptions import ObjectDoesNotExist
from django.conf.urls import url, include
from tethys_apps.utilities import generate_app_url_patterns, sync_tethys_app_db, register_app_permissions
from tethys_apps.views import library, send_beta_feedback_email
from tethys_apps import tethys_log

# Sync the tethys apps database
sync_tethys_app_db()

urlpatterns = [
    url(r'^$', library, name='app_library'),
    url(r'^send-beta-feedback/$', send_beta_feedback_email, name='send_beta_feedback'),
]

# Append the app urls urlpatterns
app_url_patterns = generate_app_url_patterns()

for namespace, urls in app_url_patterns.iteritems():
    root_pattern = r'^{0}/'.format(namespace.replace('_', '-'))
    urlpatterns.append(url(root_pattern, include(urls, namespace=namespace)))

# Register permissions here?
try:
    register_app_permissions()
except (ProgrammingError, ObjectDoesNotExist) as e:
    tethys_log.error(e)

