.. _production_preparation:

***********
Preparation
***********

**Last Updated:** May 2020

We recommend you take time before you start your Tethys Portal installation to collect the information that you will need throughout the installation process. This information includes usernames, passwords, SSL certificates, and server attributes. Planning for these ahead of time will make it more likely that you will setup the server securely, rather than using default values for things like passwords when you are prompted for them throughout the installation process.

Server Access
=============

* **Login Credentials**: You will most likely be using SSH to access the server so have your credentials handy. Obtain SSH keys from your server admin if those are required to log on to the server.
* **Sudo Access**: The account you use to install will need ``sudo`` access to be able to install the needed software.

Server Attributes
=================

* **SERVER_DOMAIN_NAME**: You will need to obtain a public domain name for the server. Contact your IT department or search the documentation for the hosting provider for how this is to be done.
* **SSL Certificate**: If you plan to setup SSL on your Tethys Portal installation, you will need to obtain an SSL certficate for your server's domain. An SSL certificate should be purchased from a Certificate Authority for a production installation. Some of the top certificate authorities include: `Digicert <https://www.digicert.com/>`_, `GeoTrust <https://www.geotrust.com/ssl/>`_, `Sectigo (formerly Comodo) <https://sectigo.com/>`_, `Thawte <https://www.thawte.com/>`_, `GoDaddy <https://www.godaddy.com/web-security/ssl-certificate>`_, and `Network Solutions <https://www.networksolutions.com/SSL-certificates/index.jsp>`_. If your instance of Tethys Portal is part of a larger organization, contact your IT department to determine if an agreement with one of these authorities already exists.

Important Directories
=====================

There are several directories that you will need to create and be aware of throughout the installation process. The following list describes each one along with the recommended locations for each.

* **TETHYS_HOME** (~/.tethys): Directory that stores configuration for Tethys Portal. To change this from the default value you need to permanently set the TETHYS_HOME environment variable.
* **STATIC_ROOT** (/var/www/tethys/static): Directory where all static files will be copied to to be hosted by NGINX.
* **TETHYS_WORKSPACES_ROOT** (/var/www/tethys/workspaces): Directory where all workspace directories will be copied to for easier backup and management of workspace files.
* **APP_SOURCES_ROOT** (/var/www/tethys/apps): Location where app source code should be stored on the server.

.. warning::

    Since files in the ``public`` / ``static`` directories of your app are copied to a different directory during a production installation, any changes to files in these directories at runtime will not be reflected in the ``STATIC_ROOT`` directory. You should not use the ``public`` / ``static`` directory for dynamic operations. Instead, use the workspaces directories for dynamic file storage.

Usernames and Passwords
=======================

Take time before you start your installation to decide on usernames and generate secure passwords for the various accounts that will be required during the installation. There are many secure password generation websites that make it easy to create more secure passwords: `Random Password Generator <https://www.random.org/passwords/>`_, `Last Pass Password Generator <https://www.lastpass.com/password-generator>`_, `Secure Password Generator <https://passwordsgenerator.net/>`_, `Pronounceable Password Generator <https://www.warpconduit.net/password-generator/>`_, or my favorite, `xkpass <https://xkpasswd.net/s/>`_.

In particular create the following usernames and passwords and store them in a secure place:

Tethys Portal Admin

* **PORTAL_SUPERUSER_USERNAME**: The username for the primary Tethys Portal administrator.
* **PORTAL_SUPERUSER_EMAIL**: Email address for the primary Tethys Portal administrator (likely your email address).
* **PORTAL_SUPERUSER_PASSWORD**: The password for the Tethys Portal administrator.

Postgres Password

* **POSTGRES_PASSWORD**: Password of the ``postgres`` user for your database. ``postgres`` is the default superuser for PostgreSQL databases, so make this a strong password.

Tethys Database User

* **TETHYS_DB_USERNAME**: Username for the Tethys database user. This user only has access to the Tethys Portal database.
* **TETHYS_DB_PASSWORD**: Password for the Tethys database user.

Tethys Database Superuser

* **TETHYS_DB_SUPER_USERNAME**: Username for the Tethys database superuser.
* **TETHYS_DB_SUPER_PASSWORD**: Password for the Tethys database superuser. This user is another superuser like ``postgres``, so make the password strong.

Email Support
=============

If you plan to enable the email capabilities to allow users to reset their forgotten passwords, you'll need to identify an email address to use as the "From" field. Users will be able to reply to these emails, so if your organization has a "noreply" email address, that would be ideal.

* **DEFAULT_FROM_EMAIL**: The "FROM" email address and name of sender that will be shown on forgotten password emails (e.g.: <My App Portal noreply@my.domain.com>).

Security Enhanced Linux (SELinux)
=================================

If you plan to enable SELinux on your CentOS server, read up on SELinux. Here are a few links to get you started: `Security-Enhanced Linux <https://en.wikipedia.org/wiki/Security-Enhanced_Linux>`_, `CentOS SELinux <https://wiki.centos.org/HowTos/SELinux>`_, `RedHat SELinux <https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/5/html/deployment_guide/ch-selinux>`_

Summary
=======

Copy this table into a text file or spreadsheet and fill in your values. The installation guide refers to these parameters where they are needed.

.. list-table::
    :widths: 2 3
    :header-rows: 1

    * - Parameter
      - Value
    * - SERVER_DOMAIN_NAME
      -
    * - TETHYS_HOME
      - ~/.tethys
    * - STATIC_ROOT
      - 
    * - TETHYS_WORKSPACES_ROOT
      -
    * - APP_SOURCES_ROOT
      -
    * - PORTAL_SUPERUSER_USERNAME
      -
    * - PORTAL_SUPERUSER_EMAIL
      -
    * - PORTAL_SUPERUSER_PASSWORD
      -
    * - POSTGRES_PASSWORD
      -
    * - TETHYS_DB_USERNAME
      -
    * - TETHYS_DB_PASSWORD
      -
    * - TETHYS_DB_SUPER_USERNAME
      -
    * - TETHYS_DB_SUPER_PASSWORD
      -
    * - DEFAULT_FROM_EMAIL
      -

.. caution::

    Keep the document with your table in a safe location and only share it with trusted individuals in your organization.


Tips
====

* **Read the Guide**: Read through the entire Production Installation Guide before attempting your install so you can anticipate everything you will need.
* **Plan Ahead**: Decide on usernames and passwords right now so you aren't tempted to use an insecure, default value.
* **Don't Rush It**: Set aside at least a full day to setup your production portal and an additional day for each app.
* **Avoid the Copy-Paste Temptation**: Be sure you understand what the commands do before you run them. Don't just run through the guide copying and pasting every code block you see.
* **Use the Internet**: Use your preferred search engine to look up problems when they occur and use the tips in our :ref:`production_troubleshooting` guide.
