*********************
Social Authentication
*********************

**Last Updated:** August 4, 2015

Tethys Portal supports authenticating users with Google, Facebook, LinkedIn and HydroShare. The social authentication and authorization features have been implemented using the `Python Social Auth <http://psa.matiasaguirre.net/>`_ module and the social buttons provided by the `Social Buttons for Bootstrap <http://lipis.github.io/bootstrap-social/>`_.

Social login is disabled by default, because enabling it requires registering your tethys portal instance with each provider. To enable social authentication, follow the directions below for on or more of the providers.


Enable Social Login
===================

Enabling social login consists of 3 steps:

1. Register your Tethys Portal instance with the authentication provider
2. Add the appropriate backend to the AUTHENTICATION_BACKENDS setting in :file:`settings.py`
3. Add the client ID/key and client secret obtained from the provider on during registration to the :file:`settings.py` file

This process is slightly different for each provider, so detailed instructions are provided for each provider.

.. caution::

    These instructions assume that you have generated a new settings file after upgrading to 1.2. If this is not the case, please review the :ref:`social_auth_settings` section.

Google
------

1. Create a Google Developer Account

  You will need a Google developer account to register your Tethys Portal with Google. To create an account, visit `https://developers.google.com/ <https://developers.google.com/>`_ and sign in with a Google account.

2. Create a New Project

  Use the `Google Developer Console <https://console.developers.google.com/project/_/appengine/logs>`_ to create a new project.

3. Create a New Client ID

  After the project has been created, select the project and use the navigation on the left to go to ``APIs & auth > Credentials`` and press the ``Create new Client ID`` button in the OAuth section.

  a. Configure the Consent Screen

    In the window that appears, select ``Web Application`` and press ``Configure consent screen``. The consent screen is what the user sees when they log into Tethys using their Google account. You need to provide information like the name of your Tethys Portal and your logo.

  b. Provide Authorized Origins

    As a security precaution, Google will only accept authentication requests from the hosts listed in the ``Authorized JavaScript Origins`` box. Add the domain of your Tethys Portal to the list. Optionally, you may add a localhost domain to the list to be used during testing. For example, if the domain of your Tethys Portal is ``www.example.org``, you would add the following entries:

    ::

        https://www.example.org
        http://localhost:8000

  c. Provide Authorized Redirect URIs

    You also need to provide the callback URI for Google to call once it has authenticated the user. This follows the pattern ``http://<host>/oauth2/complete/google-oauth2/``. For a Tethys Portal at domain ``www.example.org``:

    ::

        https://www.example.org/oauth2/complete/google-oauth2/
        https://localhost:8000/oauth2/complete/google-oauth2/

  d. Press ``Create Client ID`` Button

    Take note the ``Client ID`` and ``Client secret`` that are assigned to your app for the next step.

4. Open ``settings.py`` file located in :file:`/usr/lib/tethys/src/tethys_apps/settings.py`


  Add the ``social.backends.google.GoogleOAuth2`` backend to the ``AUTHENTICATION_BACKENDS`` setting:

  ::

      AUTHENTICATION_BACKENDS = (
          ...
          'social.backends.google.GoogleOAuth2',
          'django.contrib.auth.backends.ModelBackend',
      )

  Assign the ``Client ID`` and ``Client secret`` to the ``SOCIAL_AUTH_GOOGLE_OAUTH2_KEY`` and ``SOCIAL_AUTH_GOOGLE_AUTH2_SECRET`` settings, respectively:

  ::

      SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '...'
      SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '...'

Facebook
--------

1. Create a Facebook Developer Account

  You will need a Facebook developer account to register your Tethys Portal with Facebook. To create an account, visit `https://developers.facebook.com// <https://developers.facebook.com/>`_ and sign in with a Facebook account.

  Point to ``My Apps`` and select ``Become a Facebook Developer``. Click on ``Register Now`` and then accept the terms.

2. Create a Facebook App

  a. Point to ``My Apps`` and select ``Add a New App``.
  b. Select the ``Website`` option.
  c. Type the name of the new app in the text field and press the ``Create New Facebook App ID`` button from the drop down.
  d. Choose a category and press ``Create App ID``.
  e. View the Quick Start tutorial if you wish or press the ``Skip Quick Start`` button to skip.
  f. Note the ``App ID`` and ``App Secret`` for later steps.

4. Setup OAuth

  a. Select ``Settings`` from the left navigation menu and add a ``Contact Email`` address.
  b. Click on the ``Advanced`` tab and add the callback URIs to the Valid OAuth redirect URIs field. For example, if my Tethys Portal was located at ``www.example.org``:

    ::

        https://www.example.org/oauth2/complete/facebook/
        http://localhost:8000/oauth2/complete/facebook/

  c. Select ``Status & Review`` from the left navigation menu. Make the app public by changing the toggle switch to ``Yes``.

  .. note::

      The Facebook app must be public for you to allow anyone to authenticate using Facebook in your Tethys Portal. For testing, you can use the ``Roles`` menu item to add specific Facebook users that are allowed to authenticate (like yourself or other developers).

4. Open ``settings.py`` file located in :file:`/usr/lib/tethys/src/tethys_apps/settings.py`


  Add the ``social.backends.facebook.FacebookOAuth2`` backend to the ``AUTHENTICATION_BACKENDS`` setting:

  ::

      AUTHENTICATION_BACKENDS = (
          ...
          'social.backends.facebook.FacebookOAuth2',
          'django.contrib.auth.backends.ModelBackend',
      )

  Assign the ``App ID`` and ``App secret`` to the ``SOCIAL_AUTH_FACEBOOK_KEY`` and ``SOCIAL_AUTH_FACEBOOK_SECRET`` settings, respectively:

  ::

      SOCIAL_AUTH_FACEBOOK_KEY = '...'
      SOCIAL_AUTH_FACEBOOK_SECRET = '...'


LinkedIn
--------


HydroShare
----------

.. note::

    Coming soon!


.. _social_auth_settings:

Social Auth Settings
====================







