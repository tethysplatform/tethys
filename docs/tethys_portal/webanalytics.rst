*************
Web-Analytics
*************

**Last Updated:** April 29, 2019

.. image:: ../images/software/webanalytics.png
   :width: 300px
   :align: right

Tethys portals are configured to allow portal administrators to track how users interact with their portal and applications using web based analytical services. 24 services, including common services like Google Analytical and Optimizely, can be configured using the `Django-Analytical <https://github.com/jazzband/django-analytical>`_ package.

Key Concepts
============
Web-Analytics generally work by adding an asynchronous script to the head of html pages that sends information about what the user does to another website where that data is processed and made available to the website administrator. The tracked website's information is associated with an ID number or character string that needs to be included in the tracking code. Django-Analytical is a python package that automates including the asynchronous scripts for 24 services.

Enabling Services
=================
After installing tethys in either a development or production environment, the tracking ID numbers or character strings can be specified in the Tethys portal's settings.py file found at ``tethys/src/tethys_portal/settings.py``. At the bottom of the file is a section containing a placeholder for the ID's for many of the services supported by Django-Anlytical.

::

    CLICKMAP_TRACKER_ID = False
    CLICKY_SITE_ID = False
    CRAZY_EGG_ACCOUNT_NUMBER = False
    GAUGES_SITE_ID = False
    GOOGLE_ANALYTICS_JS_PROPERTY_ID = False
    GOSQUARED_SITE_TOKEN = False
    HOTJAR_SITE_ID = False
    HUBSPOT_PORTAL_ID = False
    INTERCOM_APP_ID = False
    KISSINSIGHTS_ACCOUNT_NUMBER = False
    KISSINSIGHTS_SITE_CODE = False
    KISS_METRICS_API_KEY = False
    MIXPANEL_API_TOKEN = False
    OLARK_SITE_ID = False
    OPTIMIZELY_ACCOUNT_NUMBER = False
    PERFORMABLE_API_KEY = False
    PIWIK_DOMAIN_PATH = False
    PIWIK_SITE_ID = False
    RATING_MAILRU_COUNTER_ID = False
    SNAPENGAGE_WIDGET_ID = False
    SPRING_METRICS_TRACKING_ID = False
    USERVOICE_WIDGET_KEY = False
    WOOPRA_DOMAIN = False
    YANDEX_METRICA_COUNTER_ID = False

To start using one of these services to track your Tethys portal's usage, replace ``False`` with a string containing the tracking ID for that service. Be sure to follow the exact format for the ID provided by the service provider.

For example, Google Analytics generally requires a tracking ID in the format

::

    UA-123456789-1

You must include the dashes and capitalize the UA at the beginning. If you wanted to implement a Google Analytics tracking for your portal, you would replace

::

    GOOGLE_ANALYTICS_JS_PROPERTY_ID = False

With the correctly formatted user ID as a string such as

::

    GOOGLE_ANALYTICS_JS_PROPERTY_ID = 'UA-246813579-5'
