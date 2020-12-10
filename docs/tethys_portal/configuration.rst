.. _tethys_configuration:

***************************
Tethys Portal Configuration
***************************

Beginning in Tethys Platform 3.0 the Tethys Portal is configured via a :file:`portal_config.yml` file in the :file:`$TETHYS_HOME/` directory. This instructions outline the various settings that can be added to the :file:`portal_config.yml` file.

Once you have installed Tethys you can generate a new :file:`portal_config.yml` file using the ``gen`` command. (See :ref:`tethys_gen_cmd` for more information).

::

  tethys gen portal_config

This will create a new :file:`portal_config.yml` file in your ``TETHYS_HOME`` directory that looks like this:

.. code-block:: yaml

    # Portal Level Config File

    # See tethys documentation for how to setup this file
    version: 1.0
    name: test
    apps:
    settings:
      SECRET_KEY: ...
    site_content:



You can now customize this file either by manually editing it, or by using the :ref:`tethys_settings_cmd`.

.. caution::

  The :ref:`tethys_settings_cmd` will rewrite the :file:`portal_config.yml` file each time it is run and will not preserve comments.

Portal Yaml Keys
----------------

The following is a list of keys that can be added to the :file:`portal_config.yml` file:

* **version**: the version of the :file:`portal_config.yml` file schema.
* **name**: the name of the :file:`portal_config.yml`.
* **apps**: settings for apps installed in this portal (see: :ref:`app_installation`).
* **settings**: the Tethys Portal settings. Note: do not edit the :file:`settings.py` directly, Instead set any Django setting in this section, even those not listed here.

  * **SECRET_KEY**: the Django `SECRET_KEY <https://docs.djangoproject.com/en/2.2/ref/settings/#secret-key>`_ setting. Automatically generated if not set, however setting it manually is recommended.
  * **DEBUG**: the Django `DEBUG <https://docs.djangoproject.com/en/2.2/ref/settings/#debug>`_ setting. Defaults to True.
  * **ALLOWED_HOSTS**: the Django `ALLOWED_HOSTS <https://docs.djangoproject.com/en/2.2/ref/settings/#allowed-hosts>`_ setting. Defaults to ``[]``.
  * **ADMINS**: the Django `ADMINS <https://docs.djangoproject.com/en/2.2/ref/settings/#admins>`_ setting.

  * **TETHYS_PORTAL_CONFIG**:

    * **BYPASS_TETHYS_HOME_PAGE**: the home page of Tethys Portal redirects to the Apps Library when ``True``. Defaults to ``False``.
    * **ENABLE_OPEN_SIGNUP**: anyone can create a Tethys Portal account using a "Sign Up" link on the home page when ``True``. Defaults to ``False``.
    * **ENABLE_OPEN_PORTAL**: no login required for Tethys Portal when ``True``. Defaults to ``False``. Controllers in apps need to use the ``login_required`` decorator from the Tethys SDK, rather than Django's ``login_required`` decorator.
    * **ENABLE_RESTRICTED_APP_ACCESS**: app access can be restricted based on user object permissions when ``True``. Defaults to ``False``. If ``ENABLE_OPEN_PORTAL`` is set to ``True`` this setting has no effect. That is, users will have unrestricted access to apps independently of the value of this setting.
    * **TETHYS_WORKSPACES_ROOT**: location to which app workspaces will be synced when ``tethys manage collectworkspaces`` is executed. Gathering all workspaces to one location is recommended for production deployments to allow for easier updating and backing up of app data. Defaults to :file:`<TETHYS_HOME>/workspaces`.
    * **STATIC_ROOT**: the Django `STATIC_ROOT <https://docs.djangoproject.com/en/2.2/ref/settings/#static-root>`_ setting. Defaults to :file:`<TETHYS_HOME>/static`.

  * **SESSION_CONFIG**:

    * **SESSION_EXPIRE_AT_BROWSER_CLOSE**: the Django `SESSION_EXPIRE_AT_BROWSER_CLOSE <https://docs.djangoproject.com/en/2.2/ref/settings/#session-expire-at-browser-close>`_ setting. Defaults to True.
    * **SESSION_SECURITY_WARN_AFTER**: the Django Session Security `WARN_AFTER <https://django-session-security.readthedocs.io/en/latest/full.html#module-session_security.settings>`_ setting. Defaults to 840 seconds.
    * **SESSION_SECURITY_EXPIRE_AFTER**: the Django Session Security `EXPIRE_AFTER <https://django-session-security.readthedocs.io/en/latest/full.html#module-session_security.settings>`_ setting. Defaults to 900 seconds.

  * **DATABASES**: the Django `DATABASES <https://docs.djangoproject.com/en/2.2/ref/settings/#databases>`_ setting.

    * **default**:

      * **NAME**: the Django default database `NAME <https://docs.djangoproject.com/en/2.2/ref/settings/#name>`_ setting.
      * **USER**: the Django default database `USER <https://docs.djangoproject.com/en/2.2/ref/settings/#user>`_ setting.
      * **PASSWORD**: the Django default database `PASSWORD <https://docs.djangoproject.com/en/2.2/ref/settings/#password>`_ setting.
      * **HOST**: the Django default database `HOST <https://docs.djangoproject.com/en/2.2/ref/settings/#host>`_ setting.
      * **PORT**: the Django default database `PORT <https://docs.djangoproject.com/en/2.2/ref/settings/#port>`_ setting.
      * **DIR**: name of psql directory for conda installation of PostgreSQL that ships with Tethys. This directory will be created in the ``TETHYS_HOME`` directory when ``tethys db create`` is executed. Defaults to "psql". If you are using an external database server then exclude this key or set it to `None`.

  * **LOGGING**:

    * **formatters**: override all of the default logging formatters.
    * **handlers**: override all of the default logging handlers.

    * **loggers**: define specific loggers or change the following default loggers:

      * **django**:

        * **handlers**: override the default handlers for the ``django`` logger. Defaults to ``['console_simple']``.
        * **level**: override the default level for the ``django`` logger. Defaults to ``'WARNING'`` unless the ``DJANGO_LOG_LEVEL`` environment variable is set.

      * **tethys**:
  
        * **handlers**: override the default handlers for the ``tethys`` logger. Defaults to ``['console_verbose']``.
        * **level**: override the default level for the ``tethys`` logger. Defaults to ``'INFO'``.

      * **tethys.apps**:
  
        * **handlers**: override the default handlers for the ``tethys.apps`` logger. Defaults to ``['console_verbose']``.
        * **level**:override the default level for the ``tethys.apps`` logger. Defaults to ``'INFO'``.

  * **INSTALLED_APPS**: the Django `INSTALLED_APPS <https://docs.djangoproject.com/en/2.2/ref/settings/#installed-apps>`_ setting. For convenience, any Django apps listed here will be appended to default list of Django apps required by Tethys. To override ``INSTALLED_APPS`` completely, use the ``INSTALLED_APPS_OVERRIDE`` setting.

  * **INSTALLED_APPS_OVERRIDE**: override for ``INSTALLED_APPS`` setting. CAUTION: improper use of this setting can break the Tethys Portal.

  * **MIDDLEWARE**: the Django `MIDDLEWARE <https://docs.djangoproject.com/en/2.2/ref/settings/#middleware>`_ setting. For convenience, any middleware listed here will be appended to default list of middleware required by Tethys. To override ``MIDDLEWARE`` completely, use the ``MIDDLEWARE_OVERRIDE`` setting.

  * **MIDDLEWARE_OVERRIDE**: override for ``MIDDLEWARE`` setting. CAUTION: improper use of this setting can break the Tethys Portal.

  * **AUTHENTICATION_BACKENDS**: the Django `AUTHENTICATION_BACKENDS <https://docs.djangoproject.com/en/2.2/ref/settings/#authentication-backends>`_ setting. For convenience, any authentication backends listed here will be appended to default list of authentication backends required by Tethys. To override ``AUTHENTICATION_BACKENDS`` completely, use the ``AUTHENTICATION_BACKENDS_OVERRIDE`` setting.

  * **AUTHENTICATION_BACKENDS_OVERRIDE**: override for ``AUTHENTICATION_BACKENDS`` setting. CAUTION: improper use of this setting can break the Tethys Portal.

  * **RESOURCE_QUOTA_HANDLERS**: a list of Tethys ``ResourceQuotaHandler`` classes to load (see: :ref:`sdk_quotas_api`). For convenience, any quota handlers listed here will be appended to the default list of quota handlerss. To override ``RESOURCE_QUOTA_HANDLERS`` completely, use the ``RESOURCE_QUOTA_HANDLERS_OVERRIDE`` setting.

  * **RESOURCE_QUOTA_HANDLERS_OVERRIDE**: override for ``RESOURCE_QUOTA_HANDLERS`` setting. CAUTION: improper use of this setting can break the Tethys Portal.

  * **CAPTCHA_CONFIG**:

    * **ENABLE_CAPTCHA**: Set to True to enable the simple captcha on the login screen. Defaults to False.
    * **RECAPTCHA_PRIVATE_KEY**: Private key for Google ReCaptcha. Required to enable ReCaptcha on the login screen. See `Django Recaptcha 2 Installation <https://github.com/kbytesys/django-recaptcha2#how-to-install>`_.
    * **RECAPTCHA_PUBLIC_KEY**: Public key for Google ReCaptcha. Required to enable ReCaptcha on the login screen. See `Django Recaptcha 2 Installation <https://github.com/kbytesys/django-recaptcha2#how-to-install>`_.
    * **RECAPTCHA_PROXY_HOST**: Proxy host for Google ReCaptcha. Optional. See `Django Recaptcha 2 Installation <https://github.com/kbytesys/django-recaptcha2#how-to-install>`_.

  * **OAUTH_CONFIG**:

    * **SSO_TENANT_ALIAS**: Alias to use for "Tenant" on the /accounts/tenant/ page. This page is only needed when using Multi-Tenant SSO features. Defaults to "Tenant".
    * **SSO_TENANT_REGEX**: A regular expression defining the characters allowed in the Tenant field on the /accounts/tenant/ page. This page is only needed when using Multi-Tenant SSO features. Defaults to "^[\w\s_-]+$".
    * **SOCIAL_AUTH_AZUREAD_OAUTH2_KEY**: Key for authenticating with Azure Active Directory using their OAuth2 service. See :ref:`social_auth_azuread` SSO Setup.
    * **SOCIAL_AUTH_AZUREAD_OAUTH2_SECRET**: Secret for authenticating with Azure Active Directory using their OAuth2 service. See :ref:`social_auth_azuread` SSO Setup.
    * **SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_KEY**: Key for authenticating with Azure Active Directory against a single Tenant/Active Directory using their OAuth2 service. See :ref:`social_auth_azuread` SSO Setup.
    * **SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET**: Secret for authenticating with Azure Active Directory against a single Tenant/Active Directory using their OAuth2 service. See :ref:`social_auth_azuread` SSO Setup.
    * **SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID**: The ID of the Tenant/Active Directory to authenticate against. See :ref:`social_auth_azuread` SSO Setup.
    * **SOCIAL_AUTH_AZUREAD_B2C_OAUTH2_KEY**: Key for authenticating with Azure Active Directory B2C using their OAuth2 service. See :ref:`social_auth_azuread` SSO Setup.
    * **SOCIAL_AUTH_AZUREAD_B2C_OAUTH2_SECRET**: Secret for authenticating with Azure Active Directory B2C using their OAuth2 service. See :ref:`social_auth_azuread` SSO Setup.
    * **SOCIAL_AUTH_AZUREAD_B2C_OAUTH2_TENANT_ID**: The ID of the Tenant/Active Directory to authenticate against in Azure Active Directory B2C. See :ref:`social_auth_azuread` SSO Setup.
    * **SOCIAL_AUTH_AZUREAD_B2C_OAUTH2_POLICY**: The user flow policy to use. Use `'b2c_'` unless you have created a custom user flow that you would like to use. See :ref:`social_auth_azuread` SSO Setup.
    * **SOCIAL_AUTH_ADFS_OIDC_KEY**: Client ID for authenticating with an AD FS services using its Open ID Connect interface. See :ref:`social_adfs` SSO Setup.
    * **SOCIAL_AUTH_ADFS_OIDC_SECRET**: Secret for authenticating with an AD FS service using its Open ID Connect interface. See :ref:`social_adfs` SSO Setup.
    * **SOCIAL_AUTH_ADFS_OIDC_DOMAIN**: Domain of the AD FS server. See :ref:`social_adfs` SSO Setup.
    * **SOCIAL_AUTH_FACEBOOK_KEY**: Key for authenticating with Facebook using their OAuth2 service. See :ref:`social_auth_facebook` SSO Setup.
    * **SOCIAL_AUTH_FACEBOOK_SECRET**: Secret for authenticating with Facebook using their OAuth2 service. See :ref:`social_auth_facebook` SSO Setup.
    * **SOCIAL_AUTH_FACEBOOK_SCOPE**: List of scopes for authenticating with Facebook using their OAuth2 service. See :ref:`social_auth_facebook` SSO Setup.
    * **SOCIAL_AUTH_GOOGLE_OAUTH2_KEY**: Key for authenticating with Google using their OAuth2 service. See :ref:`social_auth_google` SSO Setup.
    * **SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET**: Secret for authenticating with Google using their OAuth2 service. See :ref:`social_auth_google` SSO Setup.
    * **SOCIAL_AUTH_HYDROSHARE_KEY**: Key for authenticating with HydroShare using their OAuth2 service. See :ref:`social_auth_hydroshare` SSO Setup.
    * **SOCIAL_AUTH_HYDROSHARE_SECRET**: Secret for authentication with HydroShare using their OAuth2 service. See :ref:`social_auth_hydroshare` SSO Setup.
    * **SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY**: Key for authenticating with LinkedIn using their OAuth2 service. See :ref:`social_auth_linkedin` SSO Setup.
    * **SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET**: Secret for authenticating with LinkedIn using their OAuth2 service. See :ref:`social_auth_linkedin` SSO Setup.
    * **SOCIAL_AUTH_OKTA_OAUTH2_KEY**: Client ID for authenticating with Okta using their OAuth 2 interface. See :ref:`social_auth_okta` SSO Setup.
    * **SOCIAL_AUTH_OKTA_OAUTH2_SECRET**: Secret for authenticating with Okta using their OAuth 2 interface. See :ref:`social_auth_okta` SSO Setup.
    * **SOCIAL_AUTH_OKTA_OAUTH2_API_URL**: Your Okta Organization URL. See :ref:`social_auth_okta` SSO Setup.
    * **SOCIAL_AUTH_OKTA_OPENIDCONNECT_KEY**: Client ID for authenticating with Okta using their Open ID Connect interface. See :ref:`social_auth_okta` SSO Setup.
    * **SOCIAL_AUTH_OKTA_OPENIDCONNECT_SECRET**: Secret for authenticating with Okta using their Open ID Connect interface. See :ref:`social_auth_okta` SSO Setup.
    * **SOCIAL_AUTH_OKTA_OPENIDCONNECT_API_URL**: Your Okta Organization URL. See :ref:`social_auth_okta` SSO Setup.
    * **SOCIAL_AUTH_ONELOGIN_OIDC_KEY**: Client ID for authenticating with OneLogin using their Open ID Connect interface. See :ref:`social_auth_onelogin` SSO Setup.
    * **SOCIAL_AUTH_ONELOGIN_OIDC_SECRET**: Secret for authenticating with OneLogin using their Open ID Connect interface. See :ref:`social_auth_onelogin` SSO Setup.
    * **SOCIAL_AUTH_ONELOGIN_OIDC_SUBDOMAIN**: Your OneLogin Subdomain. See :ref:`social_auth_onelogin` SSO Setup.

  * **MFA_CONFIG**:

    * **MFA_REQUIRED**: Are users required to set up MFA to be able to use the Tethys portal. Defaults to ``False``.
    * **ADMIN_MFA_REQUIRED**: Are admin (staff) users required to set up MFA when MFA_REQUIRED is ``True``. Defaults to ``True``.
    * **SSO_MFA_REQUIRED**: Are users logged in with SSO required to set up MFA when MFA_REQUIRED is ``True``. Defaults to ``False``.
    * **MFA_RECHECK**: Allow random rechecking of the user.
    * **MFA_RECHECK_MIN**: Minimum recheck interval in seconds.
    * **MFA_RECHECK_MAX**: Maximum recheck interval in seconds.
    * **MFA_QUICKLOGIN**: Allow quick login for returning users by provide only their 2FA.
    * **TOKEN_ISSUER_NAME**: TOTP Issuer name to display in the app. Defaults to ``Tethys Portal``.
    * **MFA_UNALLOWED_METHODS**: A list of MFA methods to be disallowed. Valid methods are include ``U2F``, ``FIDO2``, ``Email``, ``Trusted_Devices``, and ``TOTP``. All but ``TOPT`` are disabled by default.

  * **ANALYTICS_CONFIG**: the Django Analytical configuration settings for enabling analytics services on the Tethys Portal (see: `Enabling Services - Django Analytical <https://django-analytical.readthedocs.io/en/latest/install.html#enabling-the-services>`_. The following is a list of settings for some of the supported services that can be enabled.

    * CLICKMAP_TRACKER_ID
    * CLICKY_SITE_ID
    * CRAZY_EGG_ACCOUNT_NUMBER
    * GAUGES_SITE_ID
    * GOOGLE_ANALYTICS_JS_PROPERTY_ID
    * GOSQUARED_SITE_TOKEN
    * HOTJAR_SITE_ID
    * HUBSPOT_PORTAL_ID
    * INTERCOM_APP_ID
    * KISSINSIGHTS_ACCOUNT_NUMBER
    * KISSINSIGHTS_SITE_CODE
    * KISS_METRICS_API_KEY
    * MIXPANEL_API_TOKEN
    * OLARK_SITE_ID
    * OPTIMIZELY_ACCOUNT_NUMBER
    * PERFORMABLE_API_KEY
    * PIWIK_DOMAIN_PATH
    * PIWIK_SITE_ID
    * RATING_MAILRU_COUNTER_ID
    * SNAPENGAGE_WIDGET_ID
    * SPRING_METRICS_TRACKING_ID
    * USERVOICE_WIDGET_KEY
    * WOOPRA_DOMAIN
    * YANDEX_METRICA_COUNTER_ID

  * **EMAIL_CONFIG**:

    * **EMAIL_BACKEND**: the Django `EMAIL_BACKEND <https://docs.djangoproject.com/en/2.2/ref/settings/#email-backend>`_ setting.
    * **EMAIL_HOST**: the Django `EMAIL_HOST <https://docs.djangoproject.com/en/2.2/ref/settings/#email-host>`_ setting.
    * **EMAIL_PORT**: the Django `EMAIL_PORT <https://docs.djangoproject.com/en/2.2/ref/settings/#email-port>`_ setting.
    * **EMAIL_HOST_USER**: the Django `EMAIL_HOST_USER <https://docs.djangoproject.com/en/2.2/ref/settings/#email-host-user>`_ setting.
    * **EMAIL_HOST_PASSWORD**: the Django `EMAIL_HOST_PASSWORD <https://docs.djangoproject.com/en/2.2/ref/settings/#email-host-password>`_ setting.
    * **EMAIL_USE_TLS**: the Django `EMAIL_USE_TLS <https://docs.djangoproject.com/en/2.2/ref/settings/#email-use-tls>`_ setting.
    * **DEFAULT_FROM_EMAIL**: the Django `DEFAULT_FROM_EMAIL <https://docs.djangoproject.com/en/2.2/ref/settings/#default-from-email>`_ setting.

  * **LOCKOUT_CONFIG**: the Django Axes configuration settings for enabling lockout capabilities on Tethys Portal (see: :ref:`advanced_config_lockout`). The following is a list of the Django Axes settings that are configured for the default lockout capabilities in Tethys Portal. For a full list of Django Axes settings, see: `Django Axes Configuration Documentation <https://django-axes.readthedocs.io/en/latest/4_configuration.html>`_.

    * **AXES_ENABLED**: Disabled when ``DEBUG`` is on, and enabled when ``DEBUG`` is off.
    * **AXES_FAILURE_LIMIT**: Number of failed login attempts to allow before locking. Default ``3``.
    * **AXES_COOLOFF_TIME**: Time to elapse before locked user is allowed to attempt logging in again. In the :file:`portal_config.yml` this setting accepts only integers or `ISO 8601 time duration formatted strings <https://en.wikipedia.org/wiki/ISO_8601#Durations>`_ (e.g.: ``"PT30M"``). Default is 30 minutes.
    * **AXES_ONLY_USER_FAILURES**: Only lock based on username and do not lock based on IP when True. Defaults to ``True``.
    * **AXES_ENABLE_ADMIN**: Enable the Django Axes admin interface. Defaults to ``True``.
    * **AXES_VERBOSE**: More logging for Axes when True. Defaults to ``True``.
    * **AXES_RESET_ON_SUCCESS**: Successful login (after the cooloff time has passed) will reset the number of failed logins when True. Defaults to ``True``.
    * **AXES_LOCKOUT_TEMPLATE**: Template to render when user is locked out. Defaults to ``'tethys_portal/accounts/lockout.html'``
    * **AXES_LOGGER**: The logger for Django Axes to use. Defaults to ``'tethys.watch_login'``.

  * **CHANNEL_LAYERS**: the Django Channels `CHANNEL_LAYERS <https://channels.readthedocs.io/en/latest/topics/channel_layers.html#channel-layers>`_ setting.

  * **AUTH_PASSWORD_VALIDATORS**: the Django `AUTH_PASSWORD_VALIDATORS <https://docs.djangoproject.com/en/2.2/topics/auth/passwords/#module-django.contrib.auth.password_validation>`_ setting.

    * **NAME**:

  * **GUARDIAN_RAISE_403**: the Django Guardian `GUARDIAN_RAISE_403 <https://django-guardian.readthedocs.io/en/stable/configuration.html#guardian-raise-403>`_ setting.
  * **GUARDIAN_RENDER_403**: the Django Guardian `GUARDIAN_RENDER_403 <https://django-guardian.readthedocs.io/en/stable/configuration.html#guardian-render-403>`_ setting.
  * **GUARDIAN_TEMPLATE_403**: the Django Guardian `GUARDIAN_TEMPLATE_403 <https://django-guardian.readthedocs.io/en/stable/configuration.html#guardian-template-403>`_ setting.
  * **ANONYMOUS_USER_NAME**: the Django Guardian `ANONYMOUS_USER_NAME <https://django-guardian.readthedocs.io/en/stable/configuration.html#anonymous-user-name>`_ setting.

* **site_content**: customize the look and feel of the Tethys Portal with these settings.

  * **TAB_TITLE**: title to display in the web browser tab.
  * **FAVICON**: icon to display in the web browser tab.
  * **TITLE**: title of the Tethys Portal.
  * **LOGO**: the logo/brand image of the Tethys Portal.
  * **LOGO_HEIGHT**: height of logo/brand image.
  * **LOGO_WIDTH**: width of logo/brand image.
  * **LOGO_PADDING**: padding around logo/brand image.
  * **LIBRARY_TITLE**: title of the Apps Library page.
  * **PRIMARY_COLOR**: primary color of the Tethys Portal.
  * **SECONDARY_COLOR**: secondary color of the Tethys Portal.
  * **BACKGROUND_COLOR**: background color of the Tethys Portal.
  * **TEXT_COLOR**: primary text color of the Tethys Portal.
  * **TEXT_HOVER_COLOR**: primary text color when hovered over.
  * **SECONDARY_TEXT_COLOR**: secondary text color of the Tethys Portal.
  * **SECONDARY_TEXT_HOVER_COLOR**: secondary text color when hovered over.
  * **FOOTER_COPYRIGHT**: the copyright text to display in the footer of the Tethys Portal.
  * **HERO_TEXT**: the hero text on the home page.
  * **BLURB_TEXT**: the blurb text on the home page.
  * **FEATURE1_HEADING**: the home page feature 1 heading.
  * **FEATURE1_BODY**: the home page feature 1 body text.
  * **FEATURE1_IMAGE**: the home page feature 1 image.
  * **FEATURE2_HEADING**: the home page feature 2 heading.
  * **FEATURE2_BODY**: the home page feature 2 body text.
  * **FEATURE2_IMAGE**: the home page feature 2 image.
  * **FEATURE3_HEADING**: the home page feature 3 heading.
  * **FEATURE3_BODY**: the home page feature 3 body text.
  * **FEATURE3_IMAGE**: the home page feature 3 image.
  * **ACTION_TEXT**: the action text on the home page.
  * **ACTION_BUTTON**: the action button text on the home page.

.. note::

    All of the settings groupings that end in ``_CONFIG`` are merely for convenience and organization, but are not necessary. Thus the following two examples are effectively the same:

    .. code-block:: yaml

        settings:
          TETHYS_PORTAL_CONFIG:
            BYPASS_TETHYS_HOME_PAGE: False

    .. code-block:: yaml

        settings:
          BYPASS_TETHYS_HOME_PAGE: False


.. note::

    You may define any Django Setting as a key under the ``settings`` key. Only the most common Django settings are listed above. For a complete reference of Django settings see: `Django Settings Reference <https://docs.djangoproject.com/en/2.2/ref/settings/>`_.

Example
-------

Sample portal_config.yml file:

.. code-block:: yaml

  # Portal Level Config File
  
  # See tethys documentation for how to setup this file
  version: 1.0
  name: test
  apps:
  settings:
    SECRET_KEY: ...
    DEBUG: True
    ALLOWED_HOSTS: []
    ADMINS: []

    TETHYS_PORTAL_CONFIG:
      BYPASS_TETHYS_HOME_PAGE: False
      ENABLE_OPEN_SIGNUP: False
      ENABLE_OPEN_PORTAL: False
      ENABLE_RESTRICTED_APP_ACCESS: False
      #  STATIC_ROOT: ''
      #  TETHYS_WORKSPACES_ROOT: ''
  
    SESSION_CONFIG:
      SESSION_EXPIRE_AT_BROWSER_CLOSE: True
      SESSION_SECURITY_WARN_AFTER: 840
      SESSION_SECURITY_EXPIRE_AFTER: 900
  
    DATABASES:
      default:
        NAME: tethys_platform
        USER: tethys_default
        PASSWORD: pass
        HOST: localhost
        PORT:  5436
        DIR: psql

    # LOGGING:
    #   formatters:
    #     verbose:
    #       format: '%(levelname)s:%(name)s:%(message)s'
    #     simple:
    #       format: '%(levelname)s %(message)s'
    #   handlers:
    #     console_simple:
    #       class: logging.StreamHandler
    #       formatter: simple
    #     console_verbose:
    #       class: logging.StreamHandler
    #       formatter: verbose
    #   loggers:
    #     django:
    #       handlers:
    #         - console_simple
    #       level: WARNING
    #     tethys:
    #       handlers:
    #         - console_verbose
    #       level: INFO
    #     tethys.apps:
    #       handlers:
    #         - console_verbose
    #       level: INFO


  
    #  INSTALLED_APPS_OVERRIDE: []
    INSTALLED_APPS: []
  
    #  MIDDLEWARE_OVERRIDE: []
    MIDDLEWARE: []
  
    #  AUTHENTICATION_BACKENDS_OVERRIDE: []
    AUTHENTICATION_BACKENDS: []
  
    #  RESOURCE_QUOTA_HANDLERS_OVERRIDE: []
    RESOURCE_QUOTA_HANDLERS: []
  
    CAPTCHA_CONFIG:
      ENABLE_CAPTCHA: False
      RECAPTCHA_PRIVATE_KEY: ''
      RECAPTCHA_PUBLIC_KEY: ''
      #  RECAPTCHA_PROXY_HOST: https://recaptcha.net
  
    #  OAUTH_CONFIG:
    #    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY: ''
    #    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET: ''
    #
    #    SOCIAL_AUTH_FACEBOOK_KEY: ''
    #    SOCIAL_AUTH_FACEBOOK_SECRET: ''
    #    SOCIAL_AUTH_FACEBOOK_SCOPE: ['email']
    #
    #    SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY: ''
    #    SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET: ''
    #
    #    SOCIAL_AUTH_HYDROSHARE_KEY: ''
    #    SOCIAL_AUTH_HYDROSHARE_SECRET: ''
  
    #  ANALYTICS_CONFIG:
    #    CLICKMAP_TRACKER_ID: False
    #    CLICKY_SITE_ID: False
    #    CRAZY_EGG_ACCOUNT_NUMBER: False
    #    GAUGES_SITE_ID: False
    #    GOOGLE_ANALYTICS_JS_PROPERTY_ID: False
    #    GOSQUARED_SITE_TOKEN: False
    #    HOTJAR_SITE_ID: False
    #    HUBSPOT_PORTAL_ID: False
    #    INTERCOM_APP_ID: False
    #    KISSINSIGHTS_ACCOUNT_NUMBER: False
    #    KISSINSIGHTS_SITE_CODE: False
    #    KISS_METRICS_API_KEY: False
    #    MIXPANEL_API_TOKEN: False
    #    OLARK_SITE_ID: False
    #    OPTIMIZELY_ACCOUNT_NUMBER: False
    #    PERFORMABLE_API_KEY: False
    #    PIWIK_DOMAIN_PATH: False
    #    PIWIK_SITE_ID: False
    #    RATING_MAILRU_COUNTER_ID: False
    #    SNAPENGAGE_WIDGET_ID: False
    #    SPRING_METRICS_TRACKING_ID: False
    #    USERVOICE_WIDGET_KEY: False
    #    WOOPRA_DOMAIN: False
    #    YANDEX_METRICA_COUNTER_ID: False
  
    #  EMAIL_CONFIG:
    #    EMAIL_BACKEND: 'django.core.mail.backends.smtp.EmailBackend'
    #    EMAIL_HOST: 'localhost'
    #    EMAIL_PORT: 25
    #    EMAIL_HOST_USER: ''
    #    EMAIL_HOST_PASSWORD: ''
    #    EMAIL_USE_TLS: False
    #    DEFAULT_FROM_EMAIL: 'Example <noreply@exmaple.com>'

    #  CHANNEL_LAYERS:
    #    default:
    #      BACKEND: channels.layers.InMemoryChannelLayer

    # Password validation
    # https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators
    #  AUTH_PASSWORD_VALIDATORS:
    #    - NAME: django.contrib.auth.password_validation.UserAttributeSimilarityValidator
    #    - NAME: django.contrib.auth.password_validation.MinimumLengthValidator
    #    - NAME: django.contrib.auth.password_validation.CommonPasswordValidator
    #    - NAME: django.contrib.auth.password_validation.NumericPasswordValidator

    # Django Guardian Settings
    #   GUARDIAN_RAISE_403: False  # Mutually exclusive with GUARDIAN_RENDER_403
    #   GUARDIAN_RENDER_403: False  # Mutually exclusive with GUARDIAN_RAISE_403
    #   GUARDIAN_TEMPLATE_403: ''
    #   ANONYMOUS_DEFAULT_USERNAME_VALUE: 'anonymous'
  
  site_content:
    TAB_TITLE:
    FAVICON:
    TITLE:
    LOGO:
    LOGO_HEIGHT:
    LOGO_WIDTH:
    LOGO_PADDING:
    LIBRARY_TITLE:
    PRIMARY_COLOR:
    SECONDARY_COLOR:
    BACKGROUND_COLOR:
    TEXT_COLOR:
    TEXT_HOVER_COLOR:
    SECONDARY_TEXT_COLOR:
    SECONDARY_TEXT_HOVER_COLOR:
    COPYRIGHT:
    HERO_TEXT:
    BLURB_TEXT:
    FEATURE1_HEADING:
    FEATURE1_BODY:
    FEATURE1_IMAGE:
    FEATURE2_HEADING:
    FEATURE2_BODY:
    FEATURE2_IMAGE:
    FEATURE3_HEADING:
    FEATURE3_BODY:
    FEATURE3_IMAGE:
    ACTION_TEXT:
    ACTION_BUTTON:
