**************************************
Multi Factor Authentication (Optional)
**************************************

**Last Updated:** August 2020

Tethys allows you to enable/enforce the use of multifactor authentication through apps such as LastPass Authenticator or Google Authenticator. This capability is provided by `Django MFA2 <https://github.com/mkalioby/django-mfa2/>`_. This tutorial will show you how to enable that functionality.


Configuring Multi Factor Authentication
=======================================

Several options in your :file:`portal_config.yaml` file can be changed to customize the multi-factor authentication for your portal. See: the `Django MFA2 Documentation <https://pypi.org/project/django-mfa2/>`_ for more information about the different options. These are the default settings:

.. code-block:: yaml

    MFA_CONFIG:
      MFA_REQUIRED: false
      MFA_UNALLOWED_METHODS:
        - U2F
        - FIDO2
        - Email
        - Trusted_Devices
      MFA_RECHECK: true
      MFA_RECHECK_MIN: 10
      MFA_RECHECK_MAX: 30
      MFA_QUICKLOGIN: true
      TOKEN_ISSUER_NAME: 'Tethys Portal'

.. note::

    Multifactor authentication is on by default but is not required. However, you it can be required by setting ``MFA_REQUIRED`` to ``True``.

Email Configuration
===================

If you setup the Email option, users will be able to receive MFA codes through their email. Enabling this option for your multifactor authentication requires some extra setup.

1. Remove ``'Email'`` from the `MFA_UNALLOWED_METHODS` list in your portal config.

2. Setup emailing capabilities for your Tethys Portal. If you have a Gmail account you can use the free Gmail SMTP service as follows:

.. code-block:: yaml

  EMAIL_CONFIG:
    EMAIL_BACKEND: django.core.mail.backends.smtp.EmailBackend
    EMAIL_HOST: smtp.gmail.com
    EMAIL_PORT: 587
    EMAIL_HOST_USER: my.name@gmail.com
    EMAIL_HOST_PASSWORD: super-secret-password
    EMAIL_USE_TLS: true
    DEFAULT_FROM_EMAIL: my.name@gmail.com
    EMAIL_FROM: 'My Name'

Enable MFA on Your Account
==========================

Follow these steps to enable MFA on your account:

1. Log in to the Tethys Portal
2. Navigate to the settings for your account by selecting "User Settings" from the drop down menu next to your username.
3. Press the **Configure** button next to the **2-Step Verification** setting under the **Credentials** section.
4. Select the method you would like to enable from the **Add Method** menu.
5. Follow the on-screen instructions and enter the code to verify your method.
6. Log out and log back in to verify that you are prompted for the second factor.