*********************
Social Authentication
*********************

**Last Updated:** August 5, 2015

Tethys Portal supports authenticating users with Google, Facebook, LinkedIn and HydroShare via the OAuth 2.0 method. The social authentication and authorization features have been implemented using the `Python Social Auth <http://psa.matiasaguirre.net/>`_ module and the social buttons provided by the `Social Buttons for Bootstrap <http://lipis.github.io/bootstrap-social/>`_. Social login is disabled by default, because enabling it requires registering your tethys portal instance with each provider.


Enable Social Login
===================

Use the following instructions to setup social login for the providers you desire.

.. caution::

    These instructions assume that you have generated a new settings file after upgrading to **Tethys Platform 1.2.0** or later. If this is not the case, please review the :ref:`social_auth_settings` section.

Google
------

1. Create a Google Developer Account

  You will need a Google developer account to register your Tethys Portal with Google. To create an account, visit `https://developers.google.com <https://developers.google.com>`_ and sign in with a Google account.

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

3. Enable the Google+ API

  a. Use the navigation on the left to go to ``APIs & auth > APIs``.
  b. Search for ``Google+ API`` and select it from the results.
  c. Click on the ``Enable API`` button to enable it.

  .. note::

      Some Google APIs are free to use up to a certain quota of hits. Familiarize your self with the quotas for any APIs you use by selecting the API and viewing the ``Quota`` tab.


4. Open  ``settings.py`` script located in :file:`/usr/lib/tethys/src/tethys_apps/settings.py`


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

References
++++++++++

For more detailed information about using Google social authentication see the following articles:

* `Python Social Auth Supported Backends: Google <http://psa.matiasaguirre.net/docs/backends/google.html>`_
* `Developer Console Help <https://developers.google.com/console/help/new/?hl=en_US#generatingoauth2>`_
* `Google Identity Platform <https://developers.google.com/identity/protocols/OAuth2>`_

Facebook
--------

1. Create a Facebook Developer Account

  You will need a Facebook developer account to register your Tethys Portal with Facebook. To create an account, visit `https://developers.facebook.com <https://developers.facebook.com/>`_ and sign in with a Facebook account.

  Point to ``My Apps`` and select ``Become a Facebook Developer``. Click on ``Register Now`` and then accept the terms.

2. Create a Facebook App

  a. Point to ``My Apps`` and select ``Add a New App``.
  b. Select the ``Website`` option.
  c. Type the name of the new app in the text field and press the ``Create New Facebook App ID`` button from the drop down.
  d. Choose a category and press ``Create App ID``.
  e. View the Quick Start tutorial if you wish or press the ``Skip Quick Start`` button to skip.

3. Note the ``App ID`` and ``App Secret`` for Step 5.

4. Setup OAuth

  a. Select ``Settings`` from the left navigation menu and add a ``Contact Email`` address.
  b. Click on the ``Advanced`` tab and add the callback URIs to the Valid OAuth redirect URIs field. For example, if my Tethys Portal was located at ``www.example.org``:

    ::

        https://www.example.org/oauth2/complete/facebook/
        http://localhost:8000/oauth2/complete/facebook/

  c. Select ``Status & Review`` from the left navigation menu. Make the app public by changing the toggle switch to ``Yes``.

  .. note::

      The Facebook app must be public for you to allow anyone to authenticate using Facebook in your Tethys Portal. For testing, you can use the ``Roles`` menu item to add specific Facebook users that are allowed to authenticate when the app is in development mode.

5. Open  ``settings.py`` script located in :file:`/usr/lib/tethys/src/tethys_apps/settings.py`


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

References
++++++++++

For more detailed information about using Facebook social authentication see the following articles:

* `Python Social Auth Supported Backends: Facebook <http://psa.matiasaguirre.net/docs/backends/facebook.html>`_
* `Facebook Login <https://developers.facebook.com/docs/facebook-login/v2.4>`_
* `Facebook Login for the Web with the JavaScript SDK <https://developers.facebook.com/docs/facebook-login/login-flow-for-web/v2.4>`_

LinkedIn
--------

1. Create a LinkedIn Developer Account

  You will need a LinkedIn developer account to register your Tethys Portal with LinkedIn. To create an account, visit `https://developer.linkedin.com/my-apps <https://developer.linkedin.com/my-apps>`_ and sign in with a LinkedIn account.

2. Create a LinkedIn Application

  a. Navigate back to `https://developer.linkedin.com/my-apps <https://developer.linkedin.com/my-apps>`_, if necessary and press the ``Create Application`` button.
  b. Fill out the form and press ``Submit``.

3. Note the ``Client ID`` and ``Client Secret`` for Step 5.

4. Setup OAuth

  a. Add the call back URLs under the OAuth 2.0 section. For example, if my Tethys Portal was located at the domain ``www.example.org``:

    ::

        https://www.example.org/oauth2/complete/linkedin-oauth2/
        http://localhost:8000/oauth2/complete/linkedin-oauth2/

  b. Select ``Settings`` from the left navigation menu. Make the app public by selecting ``Live`` from the ``Application Status`` dropdown.

  .. note::

      The LinkedIn app must be public for you to allow anyone to authenticate using LinkedIn in your Tethys Portal. For testing, you can use the ``Roles`` menu item to add specific LinkedIn users that are allowed to authenticate when the app is in development mode.

5. Open  ``settings.py`` script located in :file:`/usr/lib/tethys/src/tethys_apps/settings.py`


  Add the ``social.backends.linkedin.LinkedinOAuth2`` backend to the ``AUTHENTICATION_BACKENDS`` setting:

  ::

      AUTHENTICATION_BACKENDS = (
          ...
          'social.backends.linkedin.LinkedinOAuth2',
          'django.contrib.auth.backends.ModelBackend',
      )

  Assign the ``Client ID`` and ``Client Secret`` to the ``SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY`` and ``SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET`` settings, respectively:

  ::

      SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY = '...'
      SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET = '...'

References
++++++++++

For more detailed information about using LinkedIn social authentication see the following articles:

* `Python Social Auth Supported Backends: LinkedIn <http://psa.matiasaguirre.net/docs/backends/linkedin.html>`_
* `LinkedIn: Authenticating with OAuth 2.0 <https://developer.linkedin.com/docs/oauth2>`_


HydroShare
----------

1. Create a HydroShare Account

  You will need a HydroShare account to register your Tethys Portal with HydroShare. To create an account, visit `https://www.hydroshare.org <https://www.hydroshare.org>`_.

2. Create and setup a HydroShare Application

  a. Navigate to `https://www.hydroshare.org/o/applications/register/ <https://www.hydroshare.org/o/applications/register/>`_.

  b. Name: Give this OAuth app a name. It is recommended to use the domain of your Tethys Portal instance as the name, like: www.my-tethys-portal.com

  c. Client id:  Leave unchanged. Note this value for step 3.

  d. Client secret: Leave unchanged. Note this value for step 3.

  e. Client type: Select "Confidential".

  f. Authorization grant type: Select "Authorzation code".

  g. Redirect uris: Add the call back URLs. The protocol (http or https) that matches your Tethys Portal settings should be included in this url. For example:

  ::

      if your Tethys Portal was located at the domain ``https://www.my-tethys-portal.com``:
          https://www.my-tethys-portal.com/oauth2/complete/hydroshare/

      if your Tethys Portal was on a local development machine:
          http://localhost:8000/oauth2/complete/hydroshare/
          or
          http://127.0.0.1:8000/oauth2/complete/hydroshare/

  h. Press the "Save" button.

3. Open  ``settings.py`` script located in :file:`/usr/lib/tethys/src/tethys_apps/settings.py`

  Add the ``social.backends.hydroshare.HydroShareOAuth2`` backend to the ``AUTHENTICATION_BACKENDS`` setting:

  ::

      AUTHENTICATION_BACKENDS = (
          'tethys_services.backends.hydroshare.HydroShareOAuth2',
          ...
          'django.contrib.auth.backends.ModelBackend',
      )

  Assign the ``Client ID`` and ``Client Secret`` to the ``SOCIAL_AUTH_HYDROSHARE_KEY`` and ``SOCIAL_AUTH_HYDROSHARE_SECRET`` settings, respectively:

  ::

      SOCIAL_AUTH_HYDROSHARE_KEY = '...'
      SOCIAL_AUTH_HYDROSHARE_SECRET = '...'

4. Work with HydroShare in your app

  Once user has logged in Tethys through HydroShare OAuth, your app is ready to retrieve data from HydroShare on behalf of this HydroShare user using HydroShare REST API Client (hs_restclient).
  A helper function is provided to make this integration smoother.

  ::

      # import helper function
      from tethys_services.backends.hs_restclient_helper import get_oauth_hs

      # your controller function
      def home(request)

          # put codes in a 'try..except...' statement
          try:
              # pass in request object
              hs = get_oauth_hs(request)

              # your logic goes here. For example: list all HydroShare resources
              for resource in hs.getResourceList():
                  print(resource)

          except Exception as e:
              # handle exceptions
              pass

5. (Optional) Link to a testing HydroShare instance

    The production HydroShare is located at `https://www.hydroshare.org/ <https://www.hydroshare.org/>`_. In some cases you may want to link your Tethys Portal to a testing HydroShare instance, like `hydroshare-beta <https://beta.hydroshare.org/>`_.
    Tethys already provides OAuth backends for `hydroshare-beta <https://beta.hydroshare.org/>`_ and `hydroshare-playground <https://playground.hydroshare.org/>`_.
    To activate them, you need to go through steps 1-3 for each backend (replace www.hydroshare.org with the testing domain urls accordingly).

    At step 3:

    a. Append the following classes in ``AUTHENTICATION_BACKENDS`` settings:

        hydroshare-beta:
          ``tethys_services.backends.hydroshare_beta.HydroShareBetaOAuth2``
        hydroshare-playground:
          ``tethys_services.backends.hydroshare_playground.HydroSharePlaygroundOAuth2``

    b. Assign the ``Client ID`` and ``Client Secret`` to the following variables:

        hydroshare-beta:
          ``SOCIAL_AUTH_HYDROSHARE_BETA_KEY``

          ``SOCIAL_AUTH_HYDROSHARE_BETA_SECRET``

        hydroshare-playground:
          ``SOCIAL_AUTH_HYDROSHARE_PLAYGROUND_KEY``

          ``SOCIAL_AUTH_HYDROSHARE_PLAYGROUND_SECRET``

    Note: To prevent any unexpected behavior in section (4), a Tethys account SHOULD NOT be associated with multiple HydroShare social accounts.

References
++++++++++

For more detailed information about using HydroShare social authentication see the following articles:

* `https://github.com/hydroshare/hydroshare/wiki/HydroShare-REST-API#oauth-20-support <https://github.com/hydroshare/hydroshare/wiki/HydroShare-REST-API#oauth-20-support>`_

.. _social_auth_settings:

Social Auth Settings
====================

Social authentication requires Tethys Platform 1.2.0 or later. If you are using an older version of Tethys Platform, you will need to upgrade by following either the :doc:`../installation/update` instructions. The  ``settings.py`` script is unaffected by the upgrade. You will need to either generate a new  ``settings.py`` script using ``tethys gen settings`` or add the following settings to your existing ``settings.py`` script to support social login.


::

    INSTALLED_APPS = (
        ...
        'social.apps.django_app.default',
    )

    MIDDLEWARE_CLASSES = (
        ...
        'tethys_portal.middleware.TethysSocialAuthExceptionMiddleware',
    )

    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        'django.core.context_processors.request',
        'social.apps.django_app.context_processors.backends',
        'social.apps.django_app.context_processors.login_redirect',
    )

    # OAuth Settings
    SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']
    SOCIAL_AUTH_SLUGIFY_USERNAMES = True
    SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/apps/'
    SOCIAL_AUTH_LOGIN_ERROR_URL = '/accounts/login/'

    # OAuth Providers
    ## Google
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''

    ## Facebook
    SOCIAL_AUTH_FACEBOOK_KEY = ''
    SOCIAL_AUTH_FACEBOOK_SECRET = ''
    SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']

    ## LinkedIn
    SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY = ''
    SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET = ''

    ## HydroShare
    SOCIAL_AUTH_HYDROSHARE_KEY = ''
    SOCIAL_AUTH_HYDROSHARE_SECRET = ''
