# Define your handoff handlers here
# for more information, see:
# http://docs.tethysplatform.org/en/dev/tethys_sdk/handoff.html

import os
import requests


def csv(request, csv_url):
    """
    Test Handoff handler.
    """
    return 'test_app:home'
