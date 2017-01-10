***************************************
Production Installation on Ubuntu 16.04
***************************************

**Last Updated:** January 5, 2017

This article will provide an overview of how to install Tethys Portal in a production setup ready to host apps. The recommended deployment platform for Python web projects is to use `WSGI <http://www.wsgi.org/>`_. The easiest and most stable way to deploy a WSGI application is with the `modwsgi <https://code.google.com/p/modwsgi/>`_ extension for the `Apache Server <http://httpd.apache.org/>`_. These instructions are optimized for Ubuntu 14.04 using Apache and modwsgi, though installation on other Linux distributions will be similar.

1. Install Tethys Portal
========================

Follow the default :doc:`../installation/ubuntu16` instructions to install Tethys Portal with the following considerations

* Make sure to checkout the correct branch. The master branch provides the latest stable release.
* Assign strong passwords to the database users.
* Create a new settings file, do not use the same file that you have been using in development.
* Optionally, Follow the :doc:`./distributed` instructions to install Docker and the components of the software suite on separate servers.

2. Install Nginx
================

Install Nginx to act as a proxy server for Tethys:

::

    sudo apt-get install -y nginx vim

.. note::

    The previous command also installs the command line text editor `vim`, which is used in the following instructions to edit various files. If you prefer a different editor then you can replace ``vim`` with your preferred editor.

.. _setup_email_capabilities:

3. Setup Email Capabilities
===========================

Tethys Platform provides a mechanism for resetting forgotten passwords that requires email capabilities, for which we recommend using Postfix. Install Postfix as follows:

::

    $ sudo apt-get install postfix

When prompted select "Internet Site". You will then be prompted to enter you Fully Qualified Domain Name (FQDN) for your server. This is the domain name of the server you are installing Tethys Platform on. For example:

::

    foo.example.org

Next, configure Postfix by opening its configuration file:

::

    $ sudo vim /etc/postfix/main.cf

Press :kbd:`i` to start editing, find the `myhostname` parameter, and change it to point at your FQDN:

::

    myhostname = foo.example.org

Find the `mynetworks` parameter and verify that it is set as follows:

::

    mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128

Press :kbd:`ESC` to exit ``INSERT`` mode and then press ``:x`` and :kbd:`ENTER` to save changes and exit. Finally, restart the Postfix service to apply the changes:

::

    $ sudo service postfix restart

Django must be configured to use the postfix server. The next section will describe the Django settings that must be configured for the email server to work. For an excellent guide on setting up Postfix on Ubuntu, refer to `How To Install and Setup Postfix on Ubuntu 14.04 <https://www.digitalocean.com/community/tutorials/how-to-install-and-setup-postfix-on-ubuntu-14-04>`_.

4. Set Secure Settings
======================

Several settings need to be modified in the :file:`settings.py` module to make the installation ready for a production environment. The internet is a hostile environment and you need to take every precaution to make sure your Tethys Platform installation is secure. Django provides a `Deployment Checklist <https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/>`_ that points out critical settings. You should review this checklist carefully before launching your site. As a minimum do the following:

Open the :file:`settings.py` module for editing using ``vim`` or another text editor:

::

    sudo vim /usr/lib/tethys/src/tethys_apps/settings.py

Press :kbd:`i` to start editing and change the following settings:

a. Create new secret key

  Create a new ``SECRET_KEY`` for the production installation of Tethys Platform. Do not use the same key you used during development and keep the key a secret. Take care not to store the :file:`settings.py` file with the production secret key in a repository. Django outlines several suggestions for making the secret key more secure in the `Deployment Checklist: SECRET_KEY <https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/#secret-key>`_ documentation.

b. Turn off debugging

  Turn off the debugging settings by changing ``DEBUG`` and ``TEMPLATE_DEBUG`` to ``False``. **You must never turn on debugging in a production environment.**

  ::

      DEBUG = False

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

d. Setup social authentication

  If you wish to enable social authentication capabilities in your Tethys Portal, follow the :doc:`../tethys_portal/social_auth` instructions.

e. Configure workspaces (optional)

  If you would like all of the app workspace directories to be aggregated to a central location, create the directory and then specify it using the ``TETHYS_WORKSPACES_ROOT`` setting.


Press :kbd:`ESC` to exit ``INSERT`` mode and then press ``:x`` and :kbd:`ENTER` to save changes and exit.

.. important::

    Review the `Deployment Checklist <https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/>`_ carefully.

5. Make Directories for Static Files, Workspaces, and TethysCluster
===================================================================

When running Tethys Platform in development mode, the static files are automatically served by the development server. In a production environment the static files will need to be collected into one location and Nginx or another server will need to be configured to serve these files (see `Deployment Checklist: STATIC_ROOT <https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/#static-root-and-static-url>`_). Optionally, the app workspaces can also be collected into one location. Since Nginx will be serving Tethys Portal under the user (www-data) the TethysCluster home directory also needs to be created:

::

    sudo mkdir /var/www/.tethyscluster && sudo mkdir -p /var/www/tethys/static && sudo mkdir -p /var/www/tethys/workspaces
    sudo chown -R $USER /var/www/tethys/

.. note::
    The static and workspaces directories can be created at any location, however, if they are created at a different location than listed above the Nginx configuration file and the Tethys settings file will need to be updated to point at the correct location.


6. Update the Nginx Configuration File
======================================

Open the Tethys Nginx configuration file using ``vim`` or another text editor:

::

    vim /usr/lib/tethys/src/tethys_portal/tethys_nginx.conf

Press :kbd:`i` to start editing and update the following line with the IP address or fully qualified domain name of your server:

::

    server_name 127.0.0.1 localhost; # substitute your machine's IP address or FQDN

Press :kbd:`ESC` to exit ``INSERT`` mode and then press ``:x`` and :kbd:`ENTER` to save changes and exit.

7. Update the uWSGI Configuration File (Optional)
=================================================

Open the Tethys uWSGI configuration and customize to your liking. (See the `uWSGI documentation <http://uwsgi-docs.readthedocs.io/en/latest/index.html>`_ for more information about configuration):

::

    vim /usr/lib/tethys/src/tethys_portal/tethys_uwsgi.yml

8. Install Apps
===============

Download and install any apps that you want to host using this installation of Tethys Platform. It is recommended that you create a directory to store the source code for all of the apps that you install. The installation of each app may vary, but generally, an app can be installed as follows:

::

             $ sudo su
             $ . activate tethys
    (tethys) $ cd /path/to/tethysapp-my_first_app
    (tethys) $ python setup.py install
    (tethys) $ exit

.. note::

    If you get the following error when you try to activate the tethys environment::

        bash: activate: No such file or directory

    It probably means that miniconda is not in your path. You can add miniconda to your path by running::

        export PATH="/opt/miniconda/bin:$PATH"

9. Collect Static Files
=======================

The static files need to be collected into the directory that you created. Enter the following commands and enter "yes" if prompted:

::

             $ sudo su
             $ . activate tethys
    (tethys) $ tethys manage collectstatic
    (tethys) $ exit

10. Collect Workspaces (optional)
=================================

If you configured a workspaces directory with the ``TETHYS_WORKSPACES_ROOT`` setting, you will need to run the following command to collect all the workspaces to that directory:

::

             $ sudo su
             $ . /usr/lib/tethys/bin/activate
    (tethys) $ tethys manage collectworkspaces
    (tethys) $ exit

11. Setup the Persistent Stores for Apps
========================================

After all the apps have been successfully installed, you will need to initialize the persistent stores for the apps:

::

             $ . activate tethys
    (tethys) $ tethys syncstores all

12. Transfer Ownership to Nginx
===============================

When you are finished installing Tethys Portal, change the ownership of the source code, static files, and workspaces files to be the Nginx user (``www-data``):

::

    sudo chown -R www-data:www-data /usr/lib/tethys/src /var/www/tethys /var/www/.tethyscluster

13. Enable Site and Restart Server
==================================

Both the Tethys Nginx configuration and the Tethys uWSGI configuration need to be enabled:

a. Create a simlink to the `tethys_nginx.conf` file in the `/etc/nginx/sites-enabled/` directory:

::

    sudo ln -s /usr/lib/tethys/src/tethys_portal/tethys_nginx.conf /etc/nginx/sites-enabled/

b. Enable the Tethys uWSGI configuration as a system service and then start the service:

::

    sudo systemctl enable /usr/lib/tethys/src/tethys_portal/tethys.uwsgi.service
    sudo systemctl start tethys.uwsgi.service

c. Finally, restart Nginx:

::

    sudo systemctl restart nginx

.. tip::

    To install additional apps after the initial setup of Tethys, you will follow the following process:

    1. Change ownership of the ``src`` and ``static`` directories to your user using the patter in step 12 OR login as root user using ``sudo su``.
    2. Install apps, syncstores, collectstatic, and collectworkspaces as in steps 8-11.
    3. Transfer ownership of files to Apache user as in step 12.
    4. Reload the apache server using ``sudo systemctl restart nginx``.

    For more information see: :doc:`./app_installation`.

Troubleshooting
===============

Here we try to provide some guidance on some of the most commonly encountered issues. If you are experiencing problems and can't find a solution here then please post a question on the `Tethys Platform Forum <https://groups.google.com/forum/#!forum/tethysplatform>`_.

