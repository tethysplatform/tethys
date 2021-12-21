"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os
from tethys_portal.routing import application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tethys_portal.settings")

application = application
