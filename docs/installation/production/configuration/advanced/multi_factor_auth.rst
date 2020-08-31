**************************************
Multi Factor Authentication (Optional)
**************************************

**Last Updated:** August 2020

Tethys allows you to enable/enforce the use of multi factor authentication through apps such as LastPass or Google Authenticate. This tutorial will show you how to enable that functionality.

Key Concepts
============
Multi factor authentication is available by default but can be enforced. Several other settings can also be changed to customize your multi factor authentication.

Configuring Multi Factor Authentication
=======================================
Several options your portal configuration file can be changed to customize the multi factor authentication for your portal.

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

Changing any one of these options will customize the way multi factor authentication works in your portal.

Email Configuration
===================
Setting up email configuration for your multi factor authentication requires some extra setup. To enable email support for Multi factor authentication you must configure email for your portal, and remove 'Email' from the MFA_UNALLOWED_METHODS list in your portal config. Here is an example of using the free google email service.

.. code-block:: yaml
  EMAIL_CONFIG:
    EMAIL_BACKEND: django.core.mail.backends.smtp.EmailBackend
    EMAIL_HOST: smtp.gmail.com
    EMAIL_PORT: 587
    EMAIL_HOST_USER: test_account@my-domain.com
    EMAIL_HOST_PASSWORD: super-secret-password
    EMAIL_USE_TLS: true
    DEFAULT_FROM_EMAIL: test_account@my-domain.com
    EMAIL_FROM: 'My Name'

configuring your email and removing 'Email' from the unallowed list will allow your portal to use email addresses for multi factor authentication.