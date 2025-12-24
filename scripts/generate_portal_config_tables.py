# flake8: noqa
DJANGO_VERSION = 5.2

d = {
    "": {
        "SECRET_KEY": f"the Django `SECRET_KEY <https://docs.djangoproject.com/en/{DJANGO_VERSION}/ref/settings/#secret-key>`_ setting. Automatically generated if not set, however setting it manually is recommended.",
        "DEBUG": f"the Django `DEBUG <https://docs.djangoproject.com/en/{DJANGO_VERSION}/ref/settings/#debug>`_ setting. Defaults to True.",
        "ALLOWED_HOSTS": f"the Django `ALLOWED_HOSTS <https://docs.djangoproject.com/en/{DJANGO_VERSION}/ref/settings/#allowed-hosts>`_ setting. Defaults to ``[]``.",
        "ADMINS": f"the Django `ADMINS <https://docs.djangoproject.com/en/{DJANGO_VERSION}/ref/settings/#admins>`_ setting.",
        "INSTALLED_APPS": f"the Django `INSTALLED_APPS <https://docs.djangoproject.com/en/{DJANGO_VERSION}/ref/settings/#installed-apps>`_ setting. For convenience, any Django apps listed here will be appended to default list of Django apps required by Tethys. To override ``INSTALLED_APPS`` completely, use the ``INSTALLED_APPS_OVERRIDE`` setting.",
        "INSTALLED_APPS_OVERRIDE": "override for ``INSTALLED_APPS`` setting. CAUTION: improper use of this setting can break the Tethys Portal.",
        "MIDDLEWARE": f"the Django `MIDDLEWARE <https://docs.djangoproject.com/en/{DJANGO_VERSION}/ref/settings/#middleware>`_ setting. For convenience, any middleware listed here will be appended to default list of middleware required by Tethys. To override ``MIDDLEWARE`` completely, use the ``MIDDLEWARE_OVERRIDE`` setting.",
        "MIDDLEWARE_OVERRIDE": "override for ``MIDDLEWARE`` setting. CAUTION: improper use of this setting can break the Tethys Portal.",
        "AUTHENTICATION_BACKENDS": f"the Django `AUTHENTICATION_BACKENDS <https://docs.djangoproject.com/en/{DJANGO_VERSION}/ref/settings/#authentication-backends>`_ setting. For convenience, any authentication backends listed here will be appended to default list of authentication backends required by Tethys. To override ``AUTHENTICATION_BACKENDS`` completely, use the ``AUTHENTICATION_BACKENDS_OVERRIDE`` setting.",
        "AUTHENTICATION_BACKENDS_OVERRIDE": "override for ``AUTHENTICATION_BACKENDS`` setting. CAUTION: improper use of this setting can break the Tethys Portal.",
        "RESOURCE_QUOTA_HANDLERS": "a list of Tethys ``ResourceQuotaHandler`` classes to load (see: :ref:`sdk_quotas_api`). For convenience, any quota handlers listed here will be appended to the default list of quota handlerss. To override ``RESOURCE_QUOTA_HANDLERS`` completely, use the ``RESOURCE_QUOTA_HANDLERS_OVERRIDE`` setting.",
        "RESOURCE_QUOTA_HANDLERS_OVERRIDE": "override for ``RESOURCE_QUOTA_HANDLERS`` setting. CAUTION: improper use of this setting can break the Tethys Portal.",
    },
    "TETHYS_PORTAL_CONFIG": {
        "ENABLE_OPEN_SIGNUP": 'anyone can create a Tethys Portal account using a "Sign Up" link on the home page when ``True``. Defaults to ``False``.',
        "REGISTER_CONTROLLER": "override the default registration page with a custom controller. The value should be the dot-path to the controller function/class (e.g. ``tethysext.my_extension.controllers.custom_registration``)",
        "ENABLE_OPEN_PORTAL": "no login required for Tethys Portal when ``True``. Defaults to ``False``. Controllers in apps need to use the ``controller`` decorator from the Tethys SDK, rather than Django's ``login_required`` decorator.",
        "ALLOW_JWT_BASIC_AUTHENTICATION": "allows users to get a JSON Web Token (JWT) using basic authentication when ``True``. Defaults to ``False``. If set to true, users can obtain a JWT by sending a POST request with their username and password to the ``/api/token/`` endpoint.",
        "ENABLE_RESTRICTED_APP_ACCESS": "app access can be restricted based on user object permissions when ``True``. Defaults to ``False``. A list can also be provided to restrict specific applications. If ``ENABLE_OPEN_PORTAL`` is set to ``True`` this setting has no effect. That is, users will have unrestricted access to apps independently of the value of this setting.",
        "TETHYS_WORKSPACES_ROOT": "location to which app workspaces will be synced when ``tethys manage collectworkspaces`` is executed. Gathering all workspaces to one location is recommended for production deployments to allow for easier updating and backing up of app data. Defaults to :file:`<TETHYS_HOME>/workspaces`.",
        "STATIC_ROOT": f"the Django `STATIC_ROOT <https://docs.djangoproject.com/en/{DJANGO_VERSION}/ref/settings/#static-root>`_ setting. Defaults to :file:`<TETHYS_HOME>/static`.",
        "STATICFILES_USE_NPM": "serves JavaScript dependencies through Tethys rather than using a content delivery network (CDN) when ``True``. Defaults to ``False``. When set to ``True`` then you must run ``tethys gen package_json`` to npm install the JS dependencies locally so they can be served by Tethys.",
    },
    "SESSION_CONFIG": {
        "SESSION_SECURITY_WARN_AFTER": "the Django Session Security `WARN_AFTER <https://django-session-security.readthedocs.io/en/latest/full.html#module-session_security.settings>`_ setting. Defaults to 840 seconds.",
        "SESSION_SECURITY_EXPIRE_AFTER": "the Django Session Security `EXPIRE_AFTER <https://django-session-security.readthedocs.io/en/latest/full.html#module-session_security.settings>`_ setting. Defaults to 900 seconds.",
    },
    "DATABASES": {
        "__description__": f"See the Django `DATABASES <https://docs.djangoproject.com/en/{DJANGO_VERSION}/ref/settings/#databases>`_ setting.",
        "default": {
            "ENGINE": "the Django default database `ENGINE <https://docs.djangoproject.com/en/{DJANGO_VERSION}/ref/settings/#engine>`_ setting. Default is ``django.db.backends.sqlite3``.",
            "NAME": "the Django default databases `NAME <https://docs.djangoproject.com/en/{DJANGO_VERSION}/ref/settings/#name>`_ setting. If using the ``sqlite3`` ``ENGINE`` (default) then the default value for name will be ``tethys_platform.sqlite`` and will be located in the ``TETHYS_HOME`` directory. If another ``ENGINE`` is used then the default value is ``tethys_platform``.",
            "USER": "the Django default database `USER <https://docs.djangoproject.com/en/{DJANGO_VERSION}/ref/settings/#user>`_ setting. Not used with SQLite.",
            "PASSWORD": "the Django default database `PASSWORD <https://docs.djangoproject.com/en/{DJANGO_VERSION}/ref/settings/#password>`_ setting. Not used with SQLite.",
            "HOST": "the Django default database `HOST <https://docs.djangoproject.com/en/{DJANGO_VERSION}/ref/settings/#host>`_ setting. Not used with SQLite.",
            "PORT": "the Django default database `PORT <https://docs.djangoproject.com/en/{DJANGO_VERSION}/ref/settings/#port>`_ setting. Not used with SQLite.",
            "DIR": "name of psql directory for conda installation of PostgreSQL that ships with Tethys (if using the ``django.db.backends.postgresql`` ``ENGINE``). This directory will be created relative to the ``TETHYS_HOME`` directory when ``tethys db create`` is executed, unless an absolute path is provided. Defaults to ``psql``. If you are using the ``sqlite3`` ``ENGINE`` or an external database server then exclude this key or set it to `None`.",
        },
    },
    "LOGGING": {
        "formatters": "override all of the default logging formatters.",
        "handlers": "override all of the default logging handlers.",
        "loggers": {
            "__description__": "define specific loggers or change the following default loggers:",
            "django": {
                "handlers": "override the default handlers for the ``django`` logger. Defaults to ``['console_simple']``.",
                "level": "override the default level for the ``django`` logger. Defaults to ``'WARNING'`` unless the ``DJANGO_LOG_LEVEL`` environment variable is set.",
            },
            "tethys": {
                "handlers": "override the default handlers for the ``tethys`` logger. Defaults to ``['console_verbose']``.",
                "level": "override the default level for the ``tethys`` logger. Defaults to ``'INFO'``.",
            },
            "tethysapp": {
                "handlers": "override the default handlers for the ``tethysapp`` logger. Defaults to ``['console_verbose']``.",
                "level": "override the default level for the ``tethysapp`` logger. Defaults to ``'INFO'``.",
            },
        },
    },
    "CAPTCHA_CONFIG": {
        "RECAPTCHA_PRIVATE_KEY": "Private key for Google ReCaptcha. Required to enable ReCaptcha on the login screen. See `Django Recaptcha 2 Installation <https://github.com/kbytesys/django-recaptcha2>`_.",
        "RECAPTCHA_PUBLIC_KEY": "Public key for Google ReCaptcha. Required to enable ReCaptcha on the login screen. See `Django Recaptcha 2 Installation <https://github.com/kbytesys/django-recaptcha2>`_.",
        "RECAPTCHA_PROXY_HOST": "Proxy host for Google ReCaptcha. Optional. See `Django Recaptcha 2 Installation <https://github.com/kbytesys/django-recaptcha2>`_.",
    },
    "OAUTH_CONFIG": {
        "SSO_TENANT_REGEX": 'A regular expression defining the characters allowed in the Tenant field on the /accounts/tenant/ page. This page is only needed when using Multi-Tenant SSO features. Defaults to "^[\\w\\s_-]+$".',
        "SOCIAL_AUTH_AZUREAD_OAUTH2_KEY": "Key for authenticating with Azure Active Directory using their OAuth2 service. See :ref:`social_auth_azuread` SSO Setup.",
        "SOCIAL_AUTH_AZUREAD_OAUTH2_SECRET": "Secret for authenticating with Azure Active Directory using their OAuth2 service. See :ref:`social_auth_azuread` SSO Setup.",
        "SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_MULTI_TENANT": "Define one or more sets of settings for multiple tenants, each indexed by a Tenant Key. See: :ref:`social_auth_azuread_multi` Setup.",
        "SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_KEY": "Key for authenticating with Azure Active Directory against a single Tenant/Active Directory using their OAuth2 service. See :ref:`social_auth_azuread` SSO Setup.",
        "SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET": "Secret for authenticating with Azure Active Directory against a single Tenant/Active Directory using their OAuth2 service. See :ref:`social_auth_azuread` SSO Setup.",
        "SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID": "The ID of the Tenant/Active Directory to authenticate against. See :ref:`social_auth_azuread` SSO Setup.",
        "SOCIAL_AUTH_AZUREAD_B2C_OAUTH2_MULTI_TENANT": "Define one or more sets of settings for multiple tenants, each indexed by a Tenant Key. See: :ref:`social_auth_azuread_multi` Setup.",
        "SOCIAL_AUTH_AZUREAD_B2C_OAUTH2_KEY": "Key for authenticating with Azure Active Directory B2C using their OAuth2 service. See :ref:`social_auth_azuread` SSO Setup.",
        "SOCIAL_AUTH_AZUREAD_B2C_OAUTH2_SECRET": "Secret for authenticating with Azure Active Directory B2C using their OAuth2 service. See :ref:`social_auth_azuread` SSO Setup.",
        "SOCIAL_AUTH_AZUREAD_B2C_OAUTH2_TENANT_ID": "The ID of the Tenant/Active Directory to authenticate against in Azure Active Directory B2C. See :ref:`social_auth_azuread` SSO Setup.",
        "SOCIAL_AUTH_AZUREAD_B2C_OAUTH2_POLICY": "The user flow policy to use. Use `'b2c_'` unless you have created a custom user flow that you would like to use. See :ref:`social_auth_azuread` SSO Setup.",
        "SOCIAL_AUTH_ADFS_OIDC_MULTI_TENANT": "Define one or more sets of settings for multiple tenants, each indexed by a Tenant Key. See: :ref:`social_adfs_multi` Setup.",
        "SOCIAL_AUTH_ADFS_OIDC_KEY": "Client ID for authenticating with an AD FS services using its Open ID Connect interface. See :ref:`social_adfs` SSO Setup.",
        "SOCIAL_AUTH_ADFS_OIDC_SECRET": "Secret for authenticating with an AD FS service using its Open ID Connect interface. See :ref:`social_adfs` SSO Setup.",
        "SOCIAL_AUTH_ADFS_OIDC_DOMAIN": "Domain of the AD FS server. See :ref:`social_adfs` SSO Setup.",
        "SOCIAL_AUTH_FACEBOOK_KEY": "Key for authenticating with Facebook using their OAuth2 service. See :ref:`social_auth_facebook` SSO Setup.",
        "SOCIAL_AUTH_FACEBOOK_SECRET": "Secret for authenticating with Facebook using their OAuth2 service. See :ref:`social_auth_facebook` SSO Setup.",
        "SOCIAL_AUTH_FACEBOOK_SCOPE": "List of scopes for authenticating with Facebook using their OAuth2 service. See :ref:`social_auth_facebook` SSO Setup.",
        "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY": "Key for authenticating with Google using their OAuth2 service. See :ref:`social_auth_google` SSO Setup.",
        "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET": "Secret for authenticating with Google using their OAuth2 service. See :ref:`social_auth_google` SSO Setup.",
        "SOCIAL_AUTH_HYDROSHARE_KEY": "Key for authenticating with HydroShare using their OAuth2 service. See :ref:`social_auth_hydroshare` SSO Setup.",
        "SOCIAL_AUTH_HYDROSHARE_SECRET": "Secret for authentication with HydroShare using their OAuth2 service. See :ref:`social_auth_hydroshare` SSO Setup.",
        "SOCIAL_AUTH_ARCGIS_KEY": "Key for authenticating with ArcGIS Online using their OAuth2 service. See :ref:`social_auth_arcgis` SSO Setup.",
        "SOCIAL_AUTH_ARCGIS_SECRET": "Secret for authentication with ArcGIS Online using their OAuth2 service. See :ref:`social_auth_arcgis` SSO Setup.",
        "SOCIAL_AUTH_ARCGIS_PORTAL_KEY": "Key for authenticating with an ArcGIS Enterprise Portal using their OAuth2 service. See :ref:`social_auth_arcgis` SSO Setup.",
        "SOCIAL_AUTH_ARCGIS_PORTAL_SECRET": "Secret for authentication with an ArcGIS Enterprise Portal using their OAuth2 service. See :ref:`social_auth_arcgis` SSO Setup.",
        "SOCIAL_AUTH_ARCGIS_PORTAL_URL": "Root URL of the ArcGIS Enterprise Portal that will provide their OAuth2 service. See :ref:`social_auth_arcgis` SSO Setup.",
        "SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY": "Key for authenticating with LinkedIn using their OAuth2 service. See :ref:`social_auth_linkedin` SSO Setup.",
        "SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET": "Secret for authenticating with LinkedIn using their OAuth2 service. See :ref:`social_auth_linkedin` SSO Setup.",
        "SOCIAL_AUTH_OKTA_OAUTH2_MULTI_TENANT": "Define one or more sets of settings for multiple tenants, each indexed by a Tenant Key. See: :ref:`social_auth_okta_multi` Setup.",
        "SOCIAL_AUTH_OKTA_OAUTH2_KEY": "Client ID for authenticating with Okta using their OAuth 2 interface. See :ref:`social_auth_okta` SSO Setup.",
        "SOCIAL_AUTH_OKTA_OAUTH2_SECRET": "Secret for authenticating with Okta using their OAuth 2 interface. See :ref:`social_auth_okta` SSO Setup.",
        "SOCIAL_AUTH_OKTA_OAUTH2_API_URL": "Your Okta Organization URL. See :ref:`social_auth_okta` SSO Setup.",
        "SOCIAL_AUTH_OKTA_OPENIDCONNECT_MULTI_TENANT": "Define one or more sets of settings for multiple tenants, each indexed by a Tenant Key. See: :ref:`social_auth_okta_multi` Setup.",
        "SOCIAL_AUTH_OKTA_OPENIDCONNECT_KEY": "Client ID for authenticating with Okta using their Open ID Connect interface. See :ref:`social_auth_okta` SSO Setup.",
        "SOCIAL_AUTH_OKTA_OPENIDCONNECT_SECRET": "Secret for authenticating with Okta using their Open ID Connect interface. See :ref:`social_auth_okta` SSO Setup.",
        "SOCIAL_AUTH_OKTA_OPENIDCONNECT_API_URL": "Your Okta Organization URL. See :ref:`social_auth_okta` SSO Setup.",
        "SOCIAL_AUTH_ONELOGIN_OIDC_MULTI_TENANT": "Define one or more sets of settings for multiple tenants, each indexed by a Tenant Key. See: :ref:`social_auth_onelogin_multi` Setup.",
        "SOCIAL_AUTH_ONELOGIN_OIDC_KEY": "Client ID for authenticating with OneLogin using their Open ID Connect interface. See :ref:`social_auth_onelogin` SSO Setup.",
        "SOCIAL_AUTH_ONELOGIN_OIDC_SECRET": "Secret for authenticating with OneLogin using their Open ID Connect interface. See :ref:`social_auth_onelogin` SSO Setup.",
        "SOCIAL_AUTH_ONELOGIN_OIDC_SUBDOMAIN": "Your OneLogin Subdomain. See :ref:`social_auth_onelogin` SSO Setup.",
        "SOCIAL_AUTH_ONELOGIN_OIDC_TOKEN_ENDPOINT_AUTH_METHOD": "The authentication method to use when requesting tokens from the token endpoint. See :ref:`social_auth_onelogin` SSO Setup.",
    },
    "MFA_CONFIG": {
        "ADMIN_MFA_REQUIRED": "Are admin (staff) users required to set up MFA when MFA_REQUIRED is ``True``. Defaults to ``True``.",
        "SSO_MFA_REQUIRED": "Are users logged in with SSO required to set up MFA when MFA_REQUIRED is ``True``. Defaults to ``False``.",
        "MFA_RECHECK": "Allow random rechecking of the user. Defaults to False.",
        "MFA_RECHECK_MIN": "Minimum recheck interval in seconds. Defaults to 600 seconds (10 minutes).",
        "MFA_RECHECK_MAX": "Maximum recheck interval in seconds. Defaults to 1800 seconds (30 minutes).",
        "MFA_QUICKLOGIN": "Allow quick login for returning users by provide only their 2FA. Defaults to False.",
        "TOKEN_ISSUER_NAME": "TOTP Issuer name to display in the app. Defaults to ``Tethys Portal``.",
        "MFA_UNALLOWED_METHODS": "A list of MFA methods to be disallowed. Valid methods are include ``U2F``, ``FIDO2``, ``Email``, ``Trusted_Devices``, and ``TOTP``. All but ``TOPT`` are disabled by default.",
    },
    "ANALYTICS_CONFIG": {
        "__description__": "the Django Analytical configuration settings for enabling analytics services on the Tethys Portal (see: `Enabling Services - Django Analytical <https://django-analytical.readthedocs.io/en/latest/install.html#enabling-the-services>`_. The following is a list of settings for some of the supported services that can be enabled.",
        "CLICKY_SITE_ID": "",
        "CRAZY_EGG_ACCOUNT_NUMBER": "",
        "GAUGES_SITE_ID": "",
        "GOOGLE_ANALYTICS_JS_PROPERTY_ID": "",
        "GOSQUARED_SITE_TOKEN": "",
        "HOTJAR_SITE_ID": "",
        "HUBSPOT_PORTAL_ID": "",
        "INTERCOM_APP_ID": "",
        "KISSINSIGHTS_ACCOUNT_NUMBER": "",
        "KISSINSIGHTS_SITE_CODE": "",
        "KISS_METRICS_API_KEY": "",
        "MIXPANEL_API_TOKEN": "",
        "OLARK_SITE_ID": "",
        "OPTIMIZELY_ACCOUNT_NUMBER": "",
        "PERFORMABLE_API_KEY": "",
        "PIWIK_DOMAIN_PATH": "",
        "PIWIK_SITE_ID": "",
        "RATING_MAILRU_COUNTER_ID": "",
        "SNAPENGAGE_WIDGET_ID": "",
        "SPRING_METRICS_TRACKING_ID": "",
        "USERVOICE_WIDGET_KEY": "",
        "WOOPRA_DOMAIN": "",
        "YANDEX_METRICA_COUNTER_ID": "",
    },
    "EMAIL_CONFIG": {
        "EMAIL_HOST": f"the Django `EMAIL_HOST <https://docs.djangoproject.com/en/{DJANGO_VERSION}/ref/settings/#email-host>`_ setting.",
        "EMAIL_PORT": f"the Django `EMAIL_PORT <https://docs.djangoproject.com/en/{DJANGO_VERSION}/ref/settings/#email-port>`_ setting.",
        "EMAIL_HOST_USER": f"the Django `EMAIL_HOST_USER <https://docs.djangoproject.com/en/{DJANGO_VERSION}/ref/settings/#email-host-user>`_ setting.",
        "EMAIL_HOST_PASSWORD": f"the Django `EMAIL_HOST_PASSWORD <https://docs.djangoproject.com/en/{DJANGO_VERSION}/ref/settings/#email-host-password>`_ setting.",
        "EMAIL_USE_TLS": f"the Django `EMAIL_USE_TLS <https://docs.djangoproject.com/en/{DJANGO_VERSION}/ref/settings/#email-use-tls>`_ setting.",
        "DEFAULT_FROM_EMAIL": f"the Django `DEFAULT_FROM_EMAIL <https://docs.djangoproject.com/en/{DJANGO_VERSION}/ref/settings/#default-from-email>`_ setting.",
        "EMAIL_FROM": "the email alias setting (e.g.: 'John Smith').",
    },
    "LOCKOUT_CONFIG": {
        "__description__": "the Django Axes configuration settings for enabling lockout capabilities on Tethys Portal (see: :ref:`advanced_config_lockout`). The following is a list of the Django Axes settings that are configured for the default lockout capabilities in Tethys Portal. For a full list of Django Axes settings, see: `Django Axes Configuration Documentation <https://django-axes.readthedocs.io/en/latest/4_configuration.html>`_.",
        "AXES_FAILURE_LIMIT": "Number of failed login attempts to allow before locking. Default ``3``.",
        "AXES_COOLOFF_TIME": 'Time to elapse before locked user is allowed to attempt logging in again. In the :file:`portal_config.yml` this setting accepts only integers or `ISO 8601 time duration formatted strings <https://en.wikipedia.org/wiki/ISO_8601#Durations>`_ (e.g.: ``"PT30M"``). Default is 30 minutes.',
        "AXES_ONLY_USER_FAILURES": "Only lock based on username and do not lock based on IP when True. Defaults to ``True``.",
        "AXES_ENABLE_ADMIN": "Enable the Django Axes admin interface. Defaults to ``True``.",
        "AXES_VERBOSE": "More logging for Axes when True. Defaults to ``True``.",
        "AXES_RESET_ON_SUCCESS": "Successful login (after the cooloff time has passed) will reset the number of failed logins when True. Defaults to ``True``.",
        "AXES_LOCKOUT_TEMPLATE": "Template to render when user is locked out. Defaults to ``'tethys_portal/accounts/lockout.html'``",
        "AXES_LOGGER": "The logger for Django Axes to use. Defaults to ``'tethys.watch_login'``.",
    },
    "Other Settings": {
        "CHANNEL_LAYERS": "the Django Channels `CHANNEL_LAYERS <https://channels.readthedocs.io/en/latest/topics/channel_layers.html#channel-layers>`_ setting.",
        "AUTH_PASSWORD_VALIDATORS": f"the Django `AUTH_PASSWORD_VALIDATORS <https://docs.djangoproject.com/en/{DJANGO_VERSION}/topics/auth/passwords/#module-django.contrib.auth.password_validation>`_ setting.",
        "GUARDIAN_RAISE_403": "the Django Guardian `GUARDIAN_RAISE_403 <https://django-guardian.readthedocs.io/en/stable/configuration.html#guardian-raise-403>`_ setting.",
        "GUARDIAN_RENDER_403": "the Django Guardian `GUARDIAN_RENDER_403 <https://django-guardian.readthedocs.io/en/stable/configuration.html#guardian-render-403>`_ setting.",
        "GUARDIAN_TEMPLATE_403": "the Django Guardian `GUARDIAN_TEMPLATE_403 <https://django-guardian.readthedocs.io/en/stable/configuration.html#guardian-template-403>`_ setting.",
        "ANONYMOUS_USER_NAME": "the Django Guardian `ANONYMOUS_USER_NAME <https://django-guardian.readthedocs.io/en/stable/configuration.html#anonymous-user-name>`_ setting.",
    },
}

import re


def get_description(d):
    desc = d.pop("__description__", "")
    if desc:
        desc = f"\n{desc}\n"
    return desc


def make_table_label(label, d):
    desc = get_description(d)
    output = f'{label}\n{"+" * len(label)}\n{desc}\n'
    return output


def make_simple_table(label, d):
    output = make_table_label(label, d) if label else ""
    col1_len = 50
    col2_len = 80

    table_sep = f'{"=" * col1_len} {"=" * col2_len}'

    output += f'{table_sep}\n{"Setting":<{col1_len}} {"Description":<{col2_len}}\n{table_sep}\n'

    for k, v in d.items():
        output += f"{k:<{col1_len}} {v:<{col2_len}}\n"
    output += f"{table_sep}\n\n"
    return output


def make_grid_table(label, d):
    output = make_table_label(label, d)
    indent = 0
    keys, vals = flatten_dict(d)
    col1_len = max([len(k) for k in keys])
    col2_len = max([len(v) for v in vals])
    col_lens = [col1_len, col2_len]
    col_positions = [col1_len, col1_len + col2_len + 1]
    table_lines = [
        make_row_line(col_positions),
        make_row_content(col_lens, (" Setting", " Description")),
        make_row_line(col_positions, "="),
    ]
    prev_positions = []
    for k, v in zip(keys, vals):
        line_col_lens = col_lens
        positions = [m.start() for m in re.finditer("\|", k)]
        positions.extend(col_positions)
        if prev_positions:
            merged_col_pos = sorted(set(positions).union(set(prev_positions)))
            table_lines.append(make_row_line(merged_col_pos))
        prev_positions = positions
        table_lines.append(make_row_content(col_lens, (k, v)))
    table_lines.append(make_row_line(positions))
    return output + "\n".join(table_lines) + "\n\n"


def make_row_line(pos, char="-"):
    line = [char] * (pos[-1] + 1)
    for p in pos:
        line[p] = "+"
    return "+" + "".join(line)


def make_row_content(col_lens, content):
    assert len(col_lens) == len(content)
    row = [f"{c:<{l}}" for c, l in zip(content, col_lens)]
    return f'|{"|".join(row)}|'


def flatten_dict(d, indent=""):
    desc = d.pop("__description__", "")
    keys = list()
    vals = list()
    for k, v in d.items():
        keys.append(f"{indent} {k} ")
        if isinstance(v, dict):
            vals.append(desc)
            sub_keys, sub_vals = flatten_dict(v, indent + "  |")
            keys.extend(sub_keys)
            vals.extend(sub_vals)
        else:
            vals.append(f" {v} ")
    return keys, vals


if __name__ == "__main__":
    output = ""
    for k, v in d.items():
        if k in ["DATABASES", "LOGGING"]:
            output += make_grid_table(k, v)
        else:
            output += make_simple_table(k, v)

    print(output)
