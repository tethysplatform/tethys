.. _multi_factor_auth_config:

**************************************
Multi Factor Authentication (Optional)
**************************************

**Last Updated:** September 2020

.. important::

    These settings require the ``django-mfa2``, ``arrow``, and ``isodate`` libraries to be installed. Starting with Tethys 5.0 or if you are using ``micro-tethys-platform``, you will need to install these libraries using conda or pip as follows:

    .. code-block:: bash

        # conda: conda-forge channel strongly recommended
        conda install -c conda-forge django-mfa2 arrow isodate

        # pip
        pip install django-mfa2 arrow isodate


Tethys allows you to enable/enforce the use of multi factor authentication through apps such as LastPass Authenticator or Google Authenticator. This capability is provided by `Django MFA2 <https://github.com/mkalioby/django-mfa2/>`_. This tutorial will show you how to enable that functionality.


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

If you setup the Email option, users will be able to receive MFA codes through their email. Enabling this option for your multi factor authentication requires some extra setup.

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

Follow these steps to enable multi factor authentication on your account:

1. Log in to the Tethys Portal
2. Navigate to the settings for your account by selecting "User Settings" from the drop down menu next to your username.
3. Press the **Configure** button next to the **2-Step Verification** setting under the **Credentials** section.
4. Select the method you would like to enable from the **Add Method** menu.

  The MFA methods table will show a list of all enabled MFA methods. Use the **Add Method** button to add a new method.

  .. figure:: ./images/mfa_add_method_table.png
      :width: 800px

5. Follow the on-screen instructions and enter the code to verify your method.

  Example of adding an authenticator app. Scan the QR code using an authenticator app on your phone such as Google Authenticator or Lastpass Authenticator.

  .. figure:: ./images/mfa_add_auth_app.png
    :width: 800px

  Example of adding an email method. You will need to have set your email address on your profile to receive the codes through emails.

  .. figure:: ./images/mfa_add_email.png
    :width: 800px

  .. important::

       If you choose the Email MFA option, you must also provide an email in your profile.

6. Log out and log back in to verify that you are prompted for the second factor.

