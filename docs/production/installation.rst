***************************************
Production Installation on Ubuntu 16.04
***************************************

**Last Updated:** January 5, 2017

This article will provide an overview of how to install Tethys Portal in a production setup ready to host apps. The recommended deployment platform for Python web projects is to use `WSGI <http://www.wsgi.org/>`_. The easiest way to deploy a WSGI application with conda is with `uWSGI <https://uwsgi-docs.readthedocs.io/en/latest/>`_ and Nginx. These instructions are optimized for Ubuntu 16.04 using Nginx and uWSGI, though installation on other Linux distributions will be similar.

1. Install Tethys Portal
========================

Follow the default :doc:`../installation/linux_and_mac` instructions to install Tethys Portal with the following considerations

* Make sure to checkout the correct branch. The master branch provides the latest stable release.
* Assign strong passwords to the database users.
* Create a new settings file, do not use the same file that you have been using in development.
* Optionally, Follow the :doc:`./distributed` instructions to install Docker and the components of the software suite on separate servers.

2. Install Nginx and uWSGI
==========================

For compatibility with the conda environment it is recommended that uWSGI be used to serve Tethys as a WSGI application. Nginx is then used a a proxy server.

First, install uwsgi with conda::

    $ t
    (tethys) $ conda install -c conda-forge uwsgi

Next, install Nginx to act as a proxy server for Tethys:

.. code-block:: bash

    sudo apt-get install -y nginx vim

.. note::

    The previous command also installs the command line text editor `vim`, which is used in the following instructions to edit various files. If you prefer a different editor then you can replace ``vim`` with your preferred editor.

3. Generate Production Settings
===============================

A new :file:`settings.py` file should be generated specifically for a production environment. Ensure that the following options are specified when generating a production settings file::

    (tethys) $ tethys gen settings --production -d "${TETHYS_HOME}/src/tethys_apps" --allowed-host <ALLOWED_HOST_OPT> --db-username <TETHYS_DB_USERNAME> --db-password <TETHYS_DB_PASSWORD> --db-port <TETHYS_DB_PORT>

.. note::

    The parameters indicated with angle brackets `<>` should be replaced with appropriate values for your production server.

The internet is a hostile environment and you need to take every precaution to make sure your Tethys Platform installation is secure. Django provides a `Deployment Checklist <https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/>`_ that points out critical settings. You should review this checklist carefully before launching your site.

Open the :file:`settings.py` module for editing using ``vim`` or another text editor:

::

    sudo vim $TETHYS_HOME/src/tethys_apps/settings.py

Press :kbd:`i` to start editing and change settings as necessary for your production environment. Some settings you may want to customize include:

a. Secret Key

  Create a new ``SECRET_KEY`` for the production installation of Tethys Platform. Do not use the same key you used during development and keep the key a secret. Take care not to store the :file:`settings.py` file with the production secret key in a repository. Django outlines several suggestions for making the secret key more secure in the `Deployment Checklist: SECRET_KEY <https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/#secret-key>`_ documentation.

b. Social authentication settings

  If you wish to enable social authentication capabilities in your Tethys Portal, follow the :doc:`../tethys_portal/social_auth` instructions.

c. Email settings

    If you would like to enable resetting passwords then an email server needs to be configured. See the next section for details.

Press :kbd:`ESC` to exit ``INSERT`` mode and then press ``:x`` and :kbd:`ENTER` to save changes and exit.

.. important::

    Review the `Deployment Checklist <https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/>`_ carefully.

.. _setup_email_capabilities:

4. Setup Email Capabilities
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


5. Make Directories for Static Files and Workspaces
===================================================

When running Tethys Platform in development mode, the static files are automatically served by the development server. In a production environment the static files will need to be collected into one location and Nginx or another server will need to be configured to serve these files (see `Deployment Checklist: STATIC_ROOT <https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/#static-root-and-static-url>`_). Optionally, the app workspaces can also be collected into one location::

    sudo mkdir -p $TETHYS_HOME/static && sudo mkdir -p $TETHYS_HOME/workspaces

.. note::
    The static and workspaces directories can be created at any location, however, if they are created at a different location than listed above the Nginx configuration file and the Tethys settings file will need to be updated to point at the correct location.


6. Generate the Nginx and uWSGI Configuration Files
===================================================

.. note::

    Values from the :file:`settings.py` file are used when generating these server configuration files. Be sure that the following values are properly configured before generating the configuration files:

    * `ALLOWED_HOSTS`
    * `STATIC_ROOT`
    * `TETHYS_WORKSPACES_ROOT`

::

    (tethys) $ cd $TETHYS_HOME/src/tethys_portal
    (tethys) $ tethys gen nginx
    (tethys) $ tethys gen uwsgi_settings
    (tethys) $ tethys gen uwsgi_service

7. Update the uWSGI Configuration File (Optional)
=================================================

Open the Tethys uWSGI configuration and customize to your liking. (See the `uWSGI documentation <http://uwsgi-docs.readthedocs.io/en/latest/index.html>`_ for more information about configuration):

::

    vim $TETHYS_HOME/src/tethys_portal/tethys_uwsgi.yml

8. Install Apps
===============

Download and install any apps that you want to host using this installation of Tethys Platform. It is recommended that you create a directory to store the source code for all of the apps that you install. The installation of each app may vary, but generally, an app can be installed as follows:

::

             $ sudo su
             $ . activate tethys
    (tethys) $ cd /path/to/tethysapp-my_first_app
    (tethys) $ python setup.py install
    (tethys) $ exit

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
             $ . $TETHYS_HOME/bin/activate
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

    sudo chown -R www-data:www-data $TETHYS_HOME/src $TETHYS_HOME/static $TETHYS_HOME/workspaces

13. Enable Site and Restart Server
==================================

Both the Tethys Nginx configuration and the Tethys uWSGI configuration need to be enabled:

a. Create a simlink to the `tethys_nginx.conf` file in the `/etc/nginx/sites-enabled/` directory:

::

    sudo ln -s $TETHYS_HOME/src/tethys_portal/tethys_nginx.conf /etc/nginx/sites-enabled/

b. Enable the Tethys uWSGI configuration as a system service and then start the service:

::

    sudo systemctl enable $TETHYS_HOME/src/tethys_portal/tethys.uwsgi.service
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

