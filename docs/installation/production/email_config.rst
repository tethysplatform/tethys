.. _setup_email_capabilities:

***********************************
Setup Email Capabilities (optional)
***********************************

**Last Updated:** January 2020


Tethys Platform provides a mechanism for resetting forgotten passwords that requires email capabilities, for which we recommend using Postfix. These instructions are for Debian or Ubuntu systems. For other Linux distributions refer to the `Postfix Documentation <http://www.postfix.org/>`_ or search for a guide for installing on your distribution.


1. Install Postfix:
-------------------

::

    sudo apt-get install postfix

2. Configure Postfix
--------------------

When prompted select "Internet Site". You will then be prompted to enter you Fully Qualified Domain Name (FQDN) for your server. This is the domain name of the server you are installing Tethys Platform on. For example:

::

    foo.example.org

Next, configure Postfix by opening its configuration file:

::

    sudo vim /etc/postfix/main.cf

Press :kbd:`i` to start editing, find the `myhostname` parameter, and change it to point at your FQDN:

::

    myhostname = foo.example.org

Find the `mynetworks` parameter and verify that it is set as follows:

::

    mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128

Press :kbd:`ESC` to exit ``INSERT`` mode and then press ``:x`` and :kbd:`ENTER` to save changes and exit. Finally, restart the Postfix service to apply the changes:

::

    sudo service postfix restart

Several email settings need to be configured for the forget password functionality to work properly. The following exampled illustrates how to setup email in the :file:`portal_config.yml` file.

  ::

      EMAIL_BACKEND: django.core.mail.backends.smtp.EmailBackend
      EMAIL_HOST: localhost
      EMAIL_PORT: 25
      EMAIL_HOST_USER: ''
      EMAIL_HOST_PASSWORD: ''
      EMAIL_USE_TLS: False
      DEFAULT_FROM_EMAIL: Example <noreply@exmaple.com>

For more information about setting up email capabilities for Tethys Platform, refer to the `Sending email <https://docs.djangoproject.com/en/2.2/topics/email/>`_ documentation.
