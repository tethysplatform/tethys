.. _optional_features:

*****************
Optional Features
*****************

With the release of ``micro-tethys-platform`` and starting with Tethys v5.0 many features of Tethys Platform will become optional and require additional dependencies to be installed. This is done to limit the size of the environment and allow Tethys Portal administrators more flexibility in deciding what features are needed in their deployment. The following list of features are optional and will require the listed dependencies to be installed for that feature to be enabled:

Security Features
=================

Session Security
----------------

Session security enables setting timeouts for user sessions and automatically logging them out.

**dependencies**
 - ``django-session-security``


Track Failed Login Attempts
---------------------------

Tracking failed logins allows Tethys to lock user accounts after a certain number of failed attempts, and alerts users of the number of failed attempts when they login.

**dependencies**
    - ``django-axes``


Add CORS Headers
----------------

Adds CORS headers to enable Tethys resources to be accessed on other domains.

**dependencies**
 - ``django-cors-headers``

Login/Accounts
==============

Gravatar
--------

Gravatar provides a user avatar image in the user's profile.

**dependencies**
    - ``django-gravatar2``

Captcha
-------

Captcha requires users to type the code from an image during login.

**dependencies**
    - ``django-simple-captcha``

ReCaptcha
---------

ReCaptcha uses a Google provided service to verify that the user logging in is human.

**dependencies**
    - ``django-recaptcha2``

Multi-Factor Authentication
---------------------------

Allows users to enable multi-factor authentication for their Tethys Portal account.

**dependencies**
    - ``django-mfa2``
    - ``arrow``
    - ``isodate``

Multi Tenancy
-------------

Enable multiple tenants with a single portal deployment and customize resources based on tenant.

**dependencies**
    - ``django-tenants``

Single Sign On with Social Accounts
-----------------------------------

Allow users to login to Tethys using 3rd party accounts (e.g. GitHub, Google, Facebook, etc.).

**dependencies**
    - ``social-auth-app-django``

SSO with HydroShare
+++++++++++++++++++

Allows configuration of HydroShare as an SSO

**dependencies**
    - ``hs_restclient``

SSO with OneLogin
+++++++++++++++++

Allows configuration of OneLogin as an SSO

**dependencies**
    - ``python-jose``

OAuth2 Provider
---------------

Enables a Tethys Portal to be a provider of OAuth2 authentication.

**dependencies**
    - ``django-oauth-toolkit``

See :ref:`oauth2_provider_settings`

Portal Enhancements
===================

Terms and Conditions
--------------------

Enables portal administrators to define terms and conditions that users must accept to use the portal.

**dependencies**
    - ``django-termsandconditions``

Cookie Consent
--------------

Allows users to opt in or out of the cookies used by Tethys Portal and its installed apps.

**dependencies**
    - ``django-cookie-consent``

See :ref:`cookie_consent` for usage.

Web Analytics Tracking
----------------------

Gathers web analytics statistics from portal usage.

**dependencies**
    - ``django-analytical``

JSON Widget
-----------

Enables a JSON widget in the admin pages for app settings.

**dependencies**
    - ``django-json-widget``

RESTful Framework
-----------------

Provides a framework for defining REST APIs.

**dependencies**
    - ``djangorestframework``

Mapping
=======

May Layout Shapefile Support
----------------------------

Enables converting geojson to shapefile.


**dependencies**
    - ``PyShp``

Command Line Interface
======================

Docker
------

Enables the ``docker`` command on the ``tethys`` CLI.

**dependencies**
    - ``docker-py``

Conda Installer
---------------

Enables the `tethys install`` commands to install conda packages.

**dependencies**
    - ``conda``
    - ``conda-libmamba-solver``

Databases
=========

PostgreSQL
----------

Enables ``tethys db`` commands to setup local or remote PostgreSQL databases.

**dependencies**
    - ``postgresql``
    - ``psycopg2``

Persistent Stores
-----------------

Enables apps to define and use persistent stores.

**dependencies**
    - ``sqlalchemy<2``
    - ``psycopg2`` (or other DB driver for Persistent Store type)

Spatial Persistent Stores
-------------------------

Enables apps to define spatial persistent stores.

**dependencies**
    - ``sqlalchemy<2``
    - ``geoalchemy2``

Gizmos
======

Bokeh Plots
-----------

Enables the Bokeh plotting gizmo.

**dependencies**
    - ``bokeh``

Plotly Plots
------------

Enables the Plotly plotting gizmo.

**dependencies**
    - ``plotly``

Tethys Compute
==============

Dask Job Type
-------------

Enables the Dask job type.

**dependencies**
    - ``dask``
    - ``tethys_dask_scheduler``

HTCondor Job Types
------------------

Enables the HTCondor job and workflow types

**dependencies**
    - ``condorpy``

External Services
=================

Dataset Services
----------------

Enables the :term:`dataset services` APIs for CKAN and GeoServer.

**dependencies**
    - ``tethys_dataset_services``

THREDDS Spatial Dataset Service
-------------------------------

Enables using THREDDS as a spatial dataset service.

**dependencies**
    - ``siphon``


Web Processing Services (WPS)
-----------------------------

Enables apps to define WPS endpoints.

**dependencies**
    - ``owslib``


