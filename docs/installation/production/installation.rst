***********************
Production Installation
***********************

**Last Updated:** June, 2017

This article will provide an overview of how to install Tethys Portal in a production setup ready to host apps. Currently production installation of Tethys is only supported on Linux. Some parts of these instructions are optimized for Ubuntu 16.04, though installation on other Linux distributions will be similar.

1. Install Tethys Portal
========================

Follow the default :doc:`../linux_and_mac` instructions to install Tethys Portal with the following considerations

* Make sure to checkout the correct branch. The master branch provides the latest stable release.
* Assign strong passwords to the database users.
* A new settings file with production specific settings will be generated and will overwrite an existing settings file. If you want to preserve existing settings make sure to rename or move the existing :file:`settings.py` file.
* Optionally, Follow the :doc:`./distributed` instructions to install Docker and the components of the software suite on separate servers.

For a production installation the installation script should be run with all of the following settings::

    $ bash install_tethys.sh -allowed-host <YOUR_SERVERS_HOSTNAME> --db-username <SECURE_DB_USERNAME> --db-password <SECURE_DB_PASSWORD> --db-port <PORT_FOR_YOUR_DB_SERVER> --superuser <PORTAL_ADMIN_USERNAME> --superuser-email <PORTAL_ADMIN_EMAIL> --superuser-pass <PORTAL_ADMIN_PASSWORD> --production

.. note::

    The parameters indicated with angle brackets `<>` should be replaced with appropriate values for your production server.

2. Customize Production Settings
================================

A new :file:`settings.py` file will have been generated during the production installation specifically for a production environment. Notwithstanding, the internet is a hostile environment and you need to take every precaution to make sure your Tethys Platform installation is secure. Django provides a `Deployment Checklist <https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/>`_ that points out critical settings. You should review this checklist carefully before launching your site. Follow the process described below to review and edit settings. Only a few examples are included here, but be sure to review and update any settings that are needed to provide a secure production server environment.

Open the :file:`settings.py` module for editing using ``vim`` or another text editor:

::

    sudo vim $TETHYS_HOME/src/tethys_apps/settings.py

Press :kbd:`i` to start editing and change settings as necessary for your production environment. Some settings you may want to customize include:

a. Social authentication settings

  If you wish to enable social authentication capabilities in your Tethys Portal, follow the :doc:`../../tethys_portal/social_auth` instructions.

b. Email settings

    If you would like to enable resetting passwords then an email server needs to be configured. See the next section for details.

Press :kbd:`ESC` to exit ``INSERT`` mode and then press ``:x`` and :kbd:`ENTER` to save changes and exit.

.. important::

    Review the `Deployment Checklist <https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/>`_ carefully.

.. _setup_email_capabilities:

3. Setup Email Capabilities (optional)
======================================

Tethys Platform provides a mechanism for resetting forgotten passwords that requires email capabilities, for which we recommend using Postfix. Install Postfix as follows:

::

    sudo apt-get install postfix

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

Several email settings need to be configured for the forget password functionality to work properly. The following exampled illustrates how to setup email in the :file:`settings.py` file.

  ::

      EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
      EMAIL_HOST = 'localhost'
      EMAIL_PORT = 25
      EMAIL_HOST_USER = ''
      EMAIL_HOST_PASSWORD = ''
      EMAIL_USE_TLS = False
      DEFAULT_FROM_EMAIL = 'Example <noreply@exmaple.com>'

For more information about setting up email capabilities for Tethys Platform, refer to the `Sending email <https://docs.djangoproject.com/en/1.8/topics/email/>`_ documentation.

For an excellent guide on setting up Postfix on Ubuntu, refer to `How To Install and Setup Postfix on Ubuntu 14.04 <https://www.digitalocean.com/community/tutorials/how-to-install-and-setup-postfix-on-ubuntu-14-04>`_.


4. Install Apps
===============

Download and install any apps that you want to host using this installation of Tethys Platform. For more information see: :doc:`./app_installation`.


.. todo::

    **Troubleshooting**: Here we try to provide some guidance on some of the most commonly encountered issues. If you are experiencing problems and can't find a solution here then please post a question on the `Tethys Platform Forum <https://groups.google.com/forum/#!forum/tethysplatform>`_.
