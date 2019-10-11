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

    # see tethys documentation for how to setup this file
    version: 1.0
    name: test
    apps:
    settings:
      SECRETE_KEY: ...
    site_content:



You can now customize this file either by manually editing it, or by using the :ref:`tethys_settings_cmd`.

.. caution::

  The :ref:`tethys_settings_cmd` will rewrite the :file:`portal_config.yml` file each time it is run and will not preserve comments.

Portal Yaml Keys
----------------

The following is a list of keys that can be added to the :file:`portal_config.yml` file:

* ``version``: The version of the :file:`portal_config.yml` file schema
* ``name``:
* ``apps``:
* ``settings``:

  * ``SECRET_KEY``:
  * ``DEBUG``:
  * ``ALLOWED_HOSTS``:
  * ``ADMINS``:
  * ``TETHYS_PORTAL_CONFIG``:

    * ``BYPASS_TETHYS_HOME_PAGE``:
    * ``ENABLE_OPEN_SIGNUP``:
    * ``ENABLE_OPEN_PORTAL``:
    * ``STATIC_ROOT``:
    * ``TETHYS_WORKSPACES_ROOT``:

  * ``SESSION_CONFIG``:

    * ``EXPIRE_AT_BROWSER_CLOSE``:
    * ``SECURITY_WARN_AFTER``:
    * ``SECURITY_EXPIRE_AFTER``:

  * ``DATABASES``:

    * ``default``:

      * ``NAME``:
      * ``USER``:
      * ``PASSWORD``:
      * ``HOST``:
      * ``PORT``:
      * ``DIR``:

  * ``LOGGING_CONFIG``:

    * ``TETHYS_LOGGING``:

      * ``handlers``:
      * ``level``:

    * ``TETHYS_APPS_LOGGING``:

      * ``handlers``:
      * ``level``:

    * ``LOGGING_FORMATTERS``:
    * ``LOGGING_HANDLERS``:
    * ``LOGGERS``:

  * ``INSTALLED_APPS_OVERRIDE``:

  * ``INSTALLED_APPS``:

  * ``MIDDLEWARE_OVERRIDE``:

  * ``MIDDLEWARE``:

  * ``AUTHENTICATION_BACKENDS_OVERRIDE``:

  * ``AUTHENTICATION_BACKENDS``:

  * ``RESOURCE_QUOTA_HANDLERS_OVERRIDE``:

  * ``RESOURCE_QUOTA_HANDLERS``:

  * ``CAPTCHA_CONFIG``:

    * ``ENABLE_CAPTCHA``:
    * ``RECAPTCHA_PRIVATE_KEY``:
    * ``RECAPTCHA_PUBLIC_KEY``:
    * ``RECAPTCHA_PROXY_HOST``:

  * ``OAUTH_CONFIGS``:

    * ``SOCIAL_AUTH_GOOGLE_OAUTH2_KEY``:
    * ``SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET``:
    * ``SOCIAL_AUTH_FACEBOOK_KEY``:
    * ``SOCIAL_AUTH_FACEBOOK_SECRET``:
    * ``SOCIAL_AUTH_FACEBOOK_SCOPE``:
    * ``SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY``:
    * ``SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET``:
    * ``SOCIAL_AUTH_HYDROSHARE_KEY``:
    * ``SOCIAL_AUTH_HYDROSHARE_SECRET``:

  * ``ANALYTICS_CONFIGS``:

    * ``CLICKMAP_TRACKER_ID``:
    * ``CLICKY_SITE_ID``:
    * ``CRAZY_EGG_ACCOUNT_NUMBER``:
    * ``GAUGES_SITE_ID``:
    * ``GOOGLE_ANALYTICS_JS_PROPERTY_ID``:
    * ``GOSQUARED_SITE_TOKEN``:
    * ``HOTJAR_SITE_ID``:
    * ``HUBSPOT_PORTAL_ID``:
    * ``INTERCOM_APP_ID``:
    * ``KISSINSIGHTS_ACCOUNT_NUMBER``:
    * ``KISSINSIGHTS_SITE_CODE``:
    * ``KISS_METRICS_API_KEY``:
    * ``MIXPANEL_API_TOKEN``:
    * ``OLARK_SITE_ID``:
    * ``OPTIMIZELY_ACCOUNT_NUMBER``:
    * ``PERFORMABLE_API_KEY``:
    * ``PIWIK_DOMAIN_PATH``:
    * ``PIWIK_SITE_ID``:
    * ``RATING_MAILRU_COUNTER_ID``:
    * ``SNAPENGAGE_WIDGET_ID``:
    * ``SPRING_METRICS_TRACKING_ID``:
    * ``USERVOICE_WIDGET_KEY``:
    * ``WOOPRA_DOMAIN``:
    * ``YANDEX_METRICA_COUNTER_ID``:

  * ``EMAIL_CONFIG``:

    * ``EMAIL_BACKEND``:
    * ``EMAIL_HOST``:
    * ``EMAIL_PORT``:
    * ``EMAIL_HOST_USER``:
    * ``EMAIL_HOST_PASSWORD``:
    * ``EMAIL_USE_TLS``:
    * ``DEFAULT_FROM_EMAIL``:

  * ``CHANNEL_LAYERS``:

  * ``AUTH_PASSWORD_VALIDATORS``:

    * ``NAME``:

  * ``GUARDIAN_RAISE_403``:
  * ``GUARDIAN_RENDER_403``:
  * ``GUARDIAN_TEMPLATE_403``:
  * ``ANONYMOUS_DEFAULT_USERNAME_VALUE``:

* ``site_content``:

  * ``TAB_TITLE``:
  * ``FAVICON``:
  * ``TITLE``:
  * ``LOGO``:
  * ``LOGO_HEIGHT``:
  * ``LOGO_WIDTH``:
  * ``LOGO_PADDING``:
  * ``LIBRARY_TITLE``:
  * ``PRIMARY_COLOR``:
  * ``SECONDARY_COLOR``:
  * ``BACKGROUND_COLOR``:
  * ``TEXT_COLOR``:
  * ``TEXT_HOVER_COLOR``:
  * ``SECONDARY_TEXT_COLOR``:
  * ``SECONDARY_TEXT_HOVER_COLOR``:
  * ``COPYRIGHT``:
  * ``HERO_TEXT``:
  * ``BLURB_TEXT``:
  * ``FEATURE1_HEADING``:
  * ``FEATURE1_BODY``:
  * ``FEATURE1_IMAGE``:
  * ``FEATURE2_HEADING``:
  * ``FEATURE2_BODY``:
  * ``FEATURE2_IMAGE``:
  * ``FEATURE3_HEADING``:
  * ``FEATURE3_BODY``:
  * ``FEATURE3_IMAGE``:
  * ``ACTION_TEXT``:
  * ``ACTION_BUTTON``:



Sample portal_config.yml file:

.. code-block:: yaml

  # Portal Level Config File
  
  # see tethys documentation for how to setup this file
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
      #  STATIC_ROOT: ''
      #  TETHYS_WORKSPACES_ROOT: ''
  
    SESSION_CONFIG:
      EXPIRE_AT_BROWSER_CLOSE: True
      SECURITY_WARN_AFTER: 840
      SECURITY_EXPIRE_AFTER: 900
  
    DATABASES:
      default:
        NAME: tethys_platform
        USER: tethys_default
        PASSWORD: pass
        HOST: localhost
        PORT:  5436
        DIR: psql
  
    LOGGING_CONFIG:
      TETHYS_LOGGING:
        handlers:
          - console_verbose
        level: INFO
      TETHYS_APPS_LOGGING:
        handlers:
          - console_verbose
        level: INFO
      LOGGING_FORMATTERS: {}
      LOGGING_HANDLERS: {}
      LOGGERS: {}
  
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
  
    #  OAUTH_CONFIGS:
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
  
    #  ANALYTICS_CONFIGS:
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
