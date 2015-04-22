***********************
Production Installation
***********************

**Last Updated:** November 25, 2014

This article will provide an overview of how to install Tethys Portal in a production setup ready to host apps. The recommended deployment platform for Python web projects is to use `WSGI <http://www.wsgi.org/>`_. The easiest and most stable way to deploy a WSGI application is with the `modwsgi <https://code.google.com/p/modwsgi/>`_ extension for the `Apache Server <http://httpd.apache.org/>`_. These instructions are optimized for Ubuntu 14.04 using Apache and modwsgi, though installation on other Linux distributions will be similar.

1. Install Tethys Portal
========================

Follow the default :doc:`../installation/linux` instructions to install Tethys Portal with the following considerations

* Assign strong passwords to the database users.
* Create a new settings file, do not use the same file that you have been using in development.
* Follow the :doc:`./distributed` instructions to install Docker and the software suite on separate servers.

When you are finished installing Tethys Portal, change the owner of the source code to be the Apache user (``www-data``):

::

    $ sudo chown -R www-data:www-data /usr/lib/tethys/src

2. Install Apache and Dependencies
==================================

Install Apache and the modwsgi module if they are not installed already. In this tutorial, ``vim`` is used to edit file, however, you are welcome to use any text editor you are comfortable with.

::

    $ sudo apt-get install apache2 libapache2-mod-wsgi vim

3. Make BASELINE Virtual Environment
====================================

An additional virtual environment needs to be created to use modwsgi in Apache. This virtual environment needs to be independent of the Tethys virtual environment and the system Python installation.

::

    $ sudo mkdir -p /usr/local/pythonenv
    $ sudo virtualenv --no-site-packages /usr/local/pythonenv/BASELINE

4. Set WSGI Python Home
=======================

Edit the Apache configuration to use the ``BASELINE`` environment as the home python for WSGI. Open :file:`apache2.conf` using ``vim`` or another text editor:

::

    $ sudo vim /etc/apache2/apache2.conf

To edit the file using ``vim``, you need to be in ``INSERT`` mode. Press :kbd:`i` to enter ``INSERT`` mode and addd this line to the bottom of the :file:`apache2.conf` file:

::

    WSGIPythonHome /usr/local/pythonenv/BASELINE

Press :kbd:`ESC` to exit ``INSERT`` mode and then press ``:x`` and :kbd:`ENTER` to save changes and exit.

5. Make Directory for Static Files
==================================

When running Tethys Platform in development mode, the static files are automatically served by the development server. In a production environment the static files will need to be collected into one location and Apache or another server will need to be configured to serve these files (see `Deployment Checklist: STATIC_ROOT <https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/#static-root-and-static-url>`_).

In these instructions, Apache will be used to serve the static files. Create a directory for the collected static files:

::

    $ sudo mkdir -p /var/www/tethys/static
    $ sudo chown `whoami` /var/www/tethys/static

6. Setup Email Capabilities
===========================

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

Django must be configured to use the postfix server. The next section will describe the Django settings that must be configured for the email server to work. For an excellent guide on setting up Postfix on Ubuntu, refer to `How To Install and Setup Postfix on Ubuntu 14.04 <https://www.digitalocean.com/community/tutorials/how-to-install-and-setup-postfix-on-ubuntu-14-04>`_.

7. Set Secure Settings
======================

Several settings need to be modified in the :file:`settings.py` module to make the installation ready for a production environment. The internet is a hostile environment and you need to take every precaution to make sure your Tethys Platform installation is secure. Django provides a `Deployment Checklist <https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/>`_ that points out critical settings. You should review this checklist carefully before launching your site. As a minimum do the following:

Open the :file:`settings.py` module for editing using ``vim`` or another text editor:

::

    $ sudo vim /usr/lib/tethys/src/tethys_apps/settings.py

Press :kbd:`i` to start editing and change the following settings:

a. Create new secret key

  Create a new ``SECRET_KEY`` for the production installation of Tethys Platform. Do not use the same key you used during development and keep the key a secret. Take care not to store the :file:`settings.py` file with the production secret key in a repository. Django outlines several suggestions for making the secret key more secure in the `Deployment Checklist: SECRET_KEY <https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/#secret-key>`_ documentation.

b. Turn off debugging

  Turn off the debugging settings by changing ``DEBUG`` and ``TEMPLATE_DEBUG`` to ``False``. **You must never turn on debugging in a production environment.**

  ::

      DEBUG = False
      TEMPLATE_DEBUG = False

c. Set the allowed hosts

  Allowed hosts must be set to a suitable value, usually a list of the names and aliases of the server that you are hosting Tethys Portal on (e.g.: "www.example.com"). Django will not work without a value set for the ``ALLOWED_HOSTS`` parameter when debugging is turned of. See the `Deployment Checklist: ALLOWED_HOSTS <https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/#allowed-hosts>`_ for more information.

  ::

      ALLOWED_HOSTS = ['www.example.com']

d. Set the static root directory

  You must set the ``STATIC_ROOT`` settings to tell Django where to collect all of the static files. Set this setting to the directory that was created in the previous step (:file:`/var/www/tethys/static`). See the `Deployment Checklist: STATIC_ROOT <https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/#static-root-and-static-url>`_ for more details.

  ::

      STATIC_ROOT = '/var/www/tethys/static'

e. Set email settings

  Several email settings need to be configured for the forget password functionality to work properly. The following exampled illustrates how to setup email using the Postfix installation from above:

  ::

      EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
      EMAIL_HOST = 'localhost'
      EMAIL_PORT = 25
      EMAIL_HOST_USER = ''
      EMAIL_HOST_PASSWORD = ''
      EMAIL_USE_TLS = False
      DEFAULT_FROM_EMAIL = 'Example <noreply@exmaple.com>'

For more information about setting up email capabilities for Tethys Platform, refer to the `Sending email <https://docs.djangoproject.com/en/1.8/topics/email/>`_ documentation.


Press :kbd:`ESC` to exit ``INSERT`` mode and then press ``:x`` and :kbd:`ENTER` to save changes and exit.

.. important::

    Review the `Deployment Checklist <https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/>`_ carefully.



8. Create Apache Site Configuration File
========================================

Create an Apache configuration for your Tethys Platform using the :command:`gen` command and open the :file:`tethys-default.conf` file that was generated using ``vim``:

::

             $ . /usr/lib/tethys/bin/activate
    (tethys) $ tethys gen apache -d /etc/apache2/sites-available
    (tethys) $ sudo vim /etc/apache2/sites-available/tethys-default.conf

Press :kbd:`i` to enter ``INSERT`` mode and edit the file. Copy and paste the following changing the ``ServerName`` and ``ServerAlias`` appropriately. The :file:`tethys-default.conf` will look similar to this when you are done:

::

    <VirtualHost 0.0.0.0:80>
        ServerName example.net
        ServerAlias www.example.net

        Alias /static/ /var/www/tethys/static/

        <Directory /var/www/tethys/static/>
            Require all granted
        </Directory>

        WSGIScriptAlias / /usr/lib/tethys/src/tethys_portal/wsgi.py

        <Directory /usr/lib/tethys/src/tethys_portal>
            <Files wsgi.py>
                Require all granted
            </Files>
        </Directory>

        # Daemon config
        WSGIDaemonProcess tethys_default \
         python-path=/usr/lib/tethys/src/tethys_portal:/usr/lib/tethys/lib/python2.7/site-packages
        WSGIProcessGroup tethys_default

        # Logs
        ErrorLog /var/log/apache2/tethys_default.error.log
        CustomLog /var/log/apache2/tethys_default.custom.log combined
    </VirtualHost>


There is a lot going on in this file, for more information about Django and WSGI review Django's `How to deploy with WSGI <https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/>`_ documentation.

9. Install Apps
================

Download and install any apps that you want to host using this installation of Tethys Platform. It is recommended that you create a directory to store the source code for all of the apps that you install. The installation of each app may vary, but generally, an app can be installed as follows:

::

    (tethys) $ cd /path/to/tethysapp-my_first_app
    (tethys) $ python setup.py install

10. Setup the Persistent Stores for Apps
========================================

After all the apps have been successfully installed, you will need to initialize the persistent stores for the apps:

::

    (tethys) $ tethys syncstores all

11. Run Collect Static
======================

The static files need to be collected into the directory that you created. Enter the following commands and enter "yes" if prompted:

::

             $ sudo su
             $ . /usr/lib/tethys/bin/activate
    (tethys) $ cd /usr/lib/tethys/src
    (tethys) $ python manage.py collectstatic
    (tethys) $ chown -R www-data:www-data /var/www/tethys
    (tethys) $ exit


12. Enable Site and Restart Apache
==================================

Finally, you need to disable the default apache site, enable the Tethys Portal site, and reload Apache:

::

    $ sudo a2dissite 000-default.conf
    $ sudo a2ensite tethys-default.conf
    $ sudo service apache2 reload

.. note::

    Whenever you install new apps you will need to run through steps 11-14 again.

