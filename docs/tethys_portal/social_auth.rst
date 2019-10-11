*********************
Social Authentication
*********************

**Last Updated:** October 2019

Tethys Portal supports authenticating users with Google, Facebook, LinkedIn and HydroShare via the OAuth 2.0 method. The social authentication and authorization features have been implemented using the `Python Social Auth <http://psa.matiasaguirre.net/>`_ module and the social buttons provided by the `Social Buttons for Bootstrap <http://lipis.github.io/bootstrap-social/>`_. Social login is disabled by default, because enabling it requires registering your tethys portal instance with each provider.


Enable Social Login
===================

Use the following instructions to setup social login for the providers you desire.

.. caution::

    Beginning with Tethys Platform 3.0 you must configure the social auth settings in the :file:`portal_config.yml` file. See :ref:`tethys_configuration` for more details on how to create and configure this file. For instructions on how to configure social auth for previous versions of Tethys Platform please refer to the documentation specific to your version.

Google
------

1. Create a Google Developer Account

  Follow these instructions to register your project and create a client ID: `Setting Up OAuth 2.0 <https://support.google.com/googleapi/answer/6158849>`_. Provide the following as you setup OAuth2:


  a. Provide Authorized JavaScript Origins

    As a security precaution, Google will only accept authentication requests from the hosts listed in the ``Authorized JavaScript Origins`` box. Add the domain of your Tethys Portal to the list. Optionally, you may add a localhost domain to the list to be used during testing. For example, if the domain of your Tethys Portal is ``www.example.org``, you would add the following entries:

    ::

        https://www.example.org
        http://localhost:8000

  b. Provide Authorized Redirect URIs

    You also need to provide the callback URI for Google to call once it has authenticated the user. This follows the pattern ``http://<host>/oauth2/complete/google-oauth2/``. For a Tethys Portal at domain ``www.example.org``:

    ::

        https://www.example.org/oauth2/complete/google-oauth2/
        https://localhost:8000/oauth2/complete/google-oauth2/

  .. note::

      Some Google APIs are free to use up to a certain quota of hits. Be sure to familiarize yourself with the terms of use for each service.


4. Open  :file:`portal_config.yml` file located in :file:`${TETHYS_HOME}/portal_config.yml`


  Add the ``social_core.backends.google.GoogleOAuth2`` backend to the ``AUTHENTICATION_BACKENDS`` setting:

  ::

    AUTHENTICATION_BACKENDS:
      ...
      - social_core.backends.google.GoogleOAuth2

  Copy the ``Client ID`` and ``Client secret`` into the ``SOCIAL_AUTH_GOOGLE_OAUTH2_KEY`` and ``SOCIAL_AUTH_GOOGLE_AUTH2_SECRET`` settings, respectively:

  ::

    OAUTH_CONFIGS:
      SOCIAL_AUTH_GOOGLE_OAUTH2_KEY: '...'
      SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET: '...'

References
++++++++++

For more detailed information about using Google social authentication see the following articles:

* `Developer Console Help <https://developers.google.com/console/help/new/?hl=en_US#generatingoauth2>`_
* `Google Identity Platform <https://developers.google.com/identity/protocols/OAuth2>`_

Facebook
--------

1. Create a Facebook Developer Account

  You will need a Facebook developer account to register your Tethys Portal with Facebook. To create an account, visit `https://developers.facebook.com <https://developers.facebook.com/>`_ and sign in with a Facebook account.

2. Create a Facebook App

  a. Point to ``My Apps`` and select ``Create App``.
  b. Fill out the form and press ``Create App ID`` button.

3. Setup OAuth

  a. Scroll down and locate the tile titled Facebook Login.
  b. Press the ``Setup`` button on the tile (or ``Settings`` if setup previously).
  c. If your Tethys Portal were hosted at ``www.example.com``, you would enter the following for the Valid OAuth Redirect URIs field:

    ::

        https://www.example.org/oauth2/complete/facebook/

  .. note::

      Localhost domains are automatically enabled when the app is in development mode, so you don't need to add them for Facebook OAuth logins.

  d. Press the ``Save Changes`` button.

  c. Make the app public you wish by changing the toggle switch in the header from ``Off`` to ``On``.

  .. note::

      The Facebook app must be public to allow Facebook authentication to non-localhost Tethys Portals.

4. Expand the ``Settings`` menu on the left and select ``Basic``. Note the ``App ID`` and ``App Secret``.

5. Open  :file:`portal_config.yml` file located in :file:`${TETHYS_HOME}/portal_config.yml`


  Add the ``social_core.backends.facebook.FacebookOAuth2`` backend to the ``AUTHENTICATION_BACKENDS`` setting:

  ::

      AUTHENTICATION_BACKENDS:
        ...
        - social_core.backends.facebook.FacebookOAuth2

  Copy the ``App ID`` and ``App Secret`` to the ``SOCIAL_AUTH_FACEBOOK_KEY`` and ``SOCIAL_AUTH_FACEBOOK_SECRET`` settings, respectively:

  ::

    OAUTH_CONFIGS:
      ...
      SOCIAL_AUTH_FACEBOOK_KEY: '...'
      SOCIAL_AUTH_FACEBOOK_SECRET: '...'

References
++++++++++

For more detailed information about using Facebook social authentication see the following articles:

* `Facebook Login <https://developers.facebook.com/docs/facebook-login/v2.4>`_
* `Facebook Login for the Web with the JavaScript SDK <https://developers.facebook.com/docs/facebook-login/login-flow-for-web/v2.4>`_

LinkedIn
--------

1. Create a LinkedIn Developer Account

  You will need a LinkedIn developer account to register your Tethys Portal with LinkedIn. To create an account, visit `https://developer.linkedin.com/my-apps <https://developer.linkedin.com/my-apps>`_ and sign in with a LinkedIn account.

2. Create a LinkedIn Application

  a. Navigate back to `https://www.linkedin.com/developers/apps <https://www.linkedin.com/developers/apps>`_, if necessary and press the ``Create App`` button.
  b. Fill out the form and press ``Create App``.

3. Open the **Auth** tab and note the ``Client ID`` and ``Client Secret`` for Step 5.

4. Setup OAuth

  a. Add the call back URLs under the **OAuth 2.0 settings** section. For example, if your Tethys Portal is hosted at the domain ``www.example.org``:

    ::

        https://www.example.org/oauth2/complete/linkedin-oauth2/
        http://localhost:8000/oauth2/complete/linkedin-oauth2/

5. Open  the :file:`portal_config.yml` file located in :file:`${TETHYS_HOME}/portal_config.yml`


  Add the ``social_core.backends.linkedin.LinkedinOAuth2`` backend to the ``AUTHENTICATION_BACKENDS`` setting:

  ::

      AUTHENTICATION_BACKENDS:
        ...
        - social_core.backends.linkedin.LinkedinOAuth2

  Copy the ``Client ID`` and ``Client Secret`` to the ``SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY`` and ``SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET`` settings, respectively:

  ::

    OAUTH_CONFIGS:
      ...
      - SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY: '...'
      - SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET: '...'

References
++++++++++

For more detailed information about using LinkedIn social authentication see the following articles:

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

3. Open  :file:`portal_config.yml` file located in :file:`${TETHYS_HOME}/portal_config.yml`

  Add the ``tethys_services.backends.hydroshare.HydroShareOAuth2`` backend to the ``AUTHENTICATION_BACKENDS`` setting:

  ::

      AUTHENTICATION_BACKENDS:
        - tethys_services.backends.hydroshare.HydroShareOAuth2
        ...

  Assign the ``Client id`` and ``Client secret`` to the ``SOCIAL_AUTH_HYDROSHARE_KEY`` and ``SOCIAL_AUTH_HYDROSHARE_SECRET`` settings, respectively:

  ::

    OAUTH_CONFIGS:
      ...
      - SOCIAL_AUTH_HYDROSHARE_KEY: '...'
      - SOCIAL_AUTH_HYDROSHARE_SECRET: '...'

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

    .. note::

        To prevent any unexpected behavior in section (4), a Tethys account SHOULD NOT be associated with multiple HydroShare social accounts.

References
++++++++++

For more detailed information about using HydroShare social authentication see the following articles:

* `https://github.com/hydroshare/hydroshare/wiki/HydroShare-REST-API#oauth-20-support <https://github.com/hydroshare/hydroshare/wiki/HydroShare-REST-API#oauth-20-support>`_

.. _social_auth_settings:

Social Auth Settings
====================


Beginning with Tethys Platform 3.0.0 the social auth settings are configured in the :file:`portal_config.yml` file. The following is a summary of all the settings that would need to be added for the various supported social auth backends.

.. caution::

  Social authentication requires Tethys Platform 1.2.0 or later. For instructions on how to configure social auth for previous versions of Tethys Platform please refer to the documentation specific to your version.


::

  AUTHENTICATION_BACKENDS:
    - social.backends.google.GoogleOAuth2
    - social.backends.facebook.FacebookOAuth2
    - social.backends.linkedin.LinkedinOAuth2
    - tethys_services.backends.hydroshare.HydroShareOAuth2

  OAUTH_CONFIGS:
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY: ''
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET: ''

    SOCIAL_AUTH_FACEBOOK_KEY: ''
    SOCIAL_AUTH_FACEBOOK_SECRET: ''
    SOCIAL_AUTH_FACEBOOK_SCOPE: ['email']

    SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY: ''
    SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET: ''

    SOCIAL_AUTH_HYDROSHARE_KEY: ''
    SOCIAL_AUTH_HYDROSHARE_SECRET: ''

