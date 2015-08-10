"""
********************************************************************************
* Name: wgsi.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************

WSGI config for tethys_portal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys
sys.path.append('/usr/lib/tethys/src')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tethys_apps.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
