.. _production_installation:

*****************************
Production Installation Guide
*****************************

**Last Updated:** December 2025

A **production installation**, sometimes called **deployment**, is an installation of Tethys Platform that is configured to for being hosted on a live server. This guide provides an explanation of the difference between Production and Development installations and provides several methods for installing Tethys Platform in production.

Production vs. Development
==========================

Here are the primary differences between the :ref:`development installation <development_installation>` you have been using to develop your apps  and a production installation:

* **Production Grade Servers**: The development server (``tethys manage start``) is not efficient nor capable of handling the traffic a production website receives. A combination of the either the `NGINX <https://nginx.org/en/>`_ or `Apache <https://httpd.apache.org/>`_ web server and `Daphne <https://github.com/django/daphne>`_ ASGI server are used for production installations.
* **Database Engine**: The default database engine used in development is SQLite. SQLite may not be a good fit for use in your production site (see `Appropriate Uses For SQLite <https://www.sqlite.org/whentouse.html>`_). Consider using an alternative database backend such as PostgreSQL.
* **Changes Are Not Automatically Loaded**: When changes are made to a production installation, such as installing new apps or changing settings, the Daphne server must be restarted manually to load them. It does not restart automatically like the development server.
* **Debug Disabled**: `Debug <https://docs.djangoproject.com/en/5.0/ref/settings/#debug>`_ mode is turned off to prevent sensitive information from being leaked through the detailed error messages produced by debug mode.
* **Secure Credentials**: The internet is a hostile place, so secure passwords and unique usernames are used for all admin and database accounts, instead of the default usernames and passwords used for development.
* **Static Files Collected**: The files in the :file:`public` and :file:`static` directories of apps are collected to one location to be served more efficiently by NGINX or Apache.
* **Workspaces Collected**: The files in the app workspaces are collected to one location so they can be more easily backed up.
* **Permissions**: NGINX or Apache must be given permission to access the static files and workspaces to be able to serve them.

Production Installation Methods
===============================

There are several approaches to installing Tethys Platform in a production environment that are listed below. Read through the brief description of each approach below to learn about their pros and cons.


Manual Installation
-------------------

Manual installation means installing Tethys Platform from scratch and performing all of the production configuration steps manually. The process can be time consuming and tedious and it requires familiarity with Linux command line. The major advantage of performing a manual installation is that it gives you the most control over how Tethys Platform is installed and configured.

If you have not performed a manual installation before, we recommend going through the process using a virtual machine on your computer first before attempting to do the installation on the production server. Even if you don't plan to use the manual installation method, performing a manual installation on a local virtual machine can be very informative and increase your understanding with what is going on behind the scenes in the other methods.

.. toctree::
    :maxdepth: 1

    production/manual


Docker Deployment
-----------------

This method involves using Docker to package and automate the deployment of a Tethys Portal that has your apps pre-installed. The advantage of this approach is that the process of installing Tethys Platform and your apps is automated in the Docker image. The other major advantage is portability, the Docker image can be deployed to any Linux server with Docker installed. The disadvantage is that there is a learning curve to get started using Docker for the first time. However, the investment of learning Docker is very much worth your time as most modern web applications are deployed using Docker or a similar container technology.

.. toctree::
    :maxdepth: 1

    production/docker

Advanced and Optional Capabilities
==================================

The following sections provide information on configuring advanced and optional capabilities for your production Tethys Platform installation.

* :doc:`Configure HTTPS <production/manual/configuration/advanced/https_config>`: For setting up a secured connection for your portal.
* :doc:`Customize Portal Theme <production/manual/configuration/advanced/customize>`: Customize the Tethys Portal to reflect your organization's branding.
* :doc:`Django Channels Layer <production/manual/configuration/advanced/django_channels_layer>`: For production installations that use the WebSockets and/or Bokeh Server functionality that comes with Tethys Platform.
* :doc:`Forgotten Password Recovery <production/manual/configuration/advanced/email_config>`: Set up email capabilities to allow users to recover forgotten passwords.
* :doc:`Lockout <production/manual/configuration/advanced/lockout>`: Prevent brute-force login attempts
* :doc:`Multi Factor Authentication <production/manual/configuration/advanced/multi_factor_auth>`: Enable and enforce multi-factor authentication through apps such as LastPass Authenticator or Google Authenticator.
* :doc:`Multi Tenancy <production/manual/configuration/advanced/multi_tenancy>`: Enable multiple tenants with a single portal deployment, and customize resources based on tenant.
* :doc:`Self Hosted Dependency Mode <production/manual/configuration/advanced/self_hosted_js_deps>`: Configure Tethys Portal to host JavaScript dependencies locally.
* :doc:`Single Sign On <production/manual/configuration/advanced/social_auth>`: Set up social authentication and single sign-on with providers including Google, Facebook, or LinkedIn.
* :doc:`Web Analytics <production/manual/configuration/advanced/webanalytics>`: Track how users interact with the Tethys portal and its applications using web-based analytical services.

References
==========

* `Deploying Django Channels <https://channels.readthedocs.io/en/stable/deploying.html>`_
* `Django Deployment Checklist <https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/>`_
* `Managing static files (e.g. images, JavaScript, CSS) <https://docs.djangoproject.com/en/5.0/howto/static-files/>`_
