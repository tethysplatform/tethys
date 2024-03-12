"""
********************************************************************************
* Name: urls.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

from django.urls import re_path, include
from tethys_services import views as tethys_services_views

service_urls = [
    re_path(r"^$", tethys_services_views.wps_service, name="wps_service"),
    re_path(
        r"^process/(?P<identifier>[\w._-]+)/$",
        tethys_services_views.wps_process,
        name="wps_process",
    ),
]

urlpatterns = [
    re_path(r"^datasets/$", tethys_services_views.datasets_home, name="datasets_home"),
    re_path(r"^wps/$", tethys_services_views.wps_home, name="wps_home"),
    re_path(r"^wps/(?P<service>[\w._-]+)/", include(service_urls)),
]
