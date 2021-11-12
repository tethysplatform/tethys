.. _azure_vm_config:

******************
Configure Azure VM
******************

**Last Updated:** Nov 2021

This tutorial will guide you through the configuration you **must** do after first creating the virtual machine to ensure your Tethys server secure. It also contains suggestions for additional configuration you may want to do such as set up SSL, link with a domain name, and customize the look and feel of your Tethys Portal.

Change Passwords
================

All user accounts have default passwords that should be changed to secure passwords soon after creating the Virtual Machine image. Use a password generator like `xkpasswd <https://xkpasswd.net/s/>`_ or similar to create strong and unique passwords for the following accounts:

* Tethys User Account
* Database Users
    * postgres
    * tethys_default
    * tethys_super
* Portal Admin User

.. warning::

    Failure to change the passwords on your Tethys Portal server will make it vulnerable to attack! Do not keep the default passwords!

Tethys User
-----------

If you did not change the password of the ``tethys`` user in the :ref:`azure_vm_orientation` tutorial, do so now:

.. code-block::

    sudo passwd tethys

Database Users
--------------

Change the passwords for the database users as follows:

1. Start ``psql`` as the ``postgres`` user:

    .. code-block::

        sudo su - postgres -c psql

2. Use ``ALTER USER`` queries to change the passwords:

    .. code-block::

        ALTER USER <user_name> WITH PASSWORD '<new_password>';

3. Quit ``psql``:

    .. code-block::

        \q

4. Update Tethys ``portal_config.yml``:

    .. code-block::

        tethys settings --set DATABASES.default.PASSWORD <tethys_default_password>

5. Restart the `tethys` service to apply the changes to ``portal_config.yml``:

    .. code-block::

        sudo systemctl restart tethys.service

Tethys Portal Admin
-------------------

Create a new portal admin account and delete the default account as follows:

1. Run the ``createsuperuser`` command:

    .. code-block::

        tethys db createsuperuser --pn <username> --pe <email> --pp <password>

2. Log in to the Tethys Portal with the new admin account.

3. Select **Site Admin** from the dropdown menu at the top-right.

4. Click on the **Users** link under the **AUTHENTICATION AND AUTHORIZATION** section.

5. Check the box next to the **admin** user and

6. Select **Delete selected users** from the **Actions** dropdown and press the **Go** button.

.. figure:: ../../../../images/production/azure/configure--delete-admin.png
    :width: 800px
    :alt: Delete the default admin user account

    **Figure 1.** Delete the default admin user account.

Customize Tethys Portal
=======================

Customize the theme and content of the Tethys Portal to reflect your organization brand and theme guidelines. Follow the :ref:`Customize Portal Theme <production_customize_theme>` configuration guide to learn how to do this.

Custom images, CSS, and JavaScript should be added to a new directory in the :file:`$TETHYS_HOME/static` directory (e.g.: :file:`$TETHYS_HOME/static/custom_theme`. These can then be referenced in the settings via the name of the new directory (e.g.: :file:`custom_theme/images/custom_logo.png`.

.. figure:: ../../../../images/production/azure/configure--custom-theme.png
    :width: 800px
    :alt: Tethys Portal with a custom theme.

    **Figure 2.** Tethys Portal with a custom theme.

Custom Domain
=============

Configure a cloudapp.azure.com domain
Map a custom domain https://docs.microsoft.com/en-us/azure/virtual-machines/custom-domain

Configure HTTPS
===============

HTTPS is the secure way of serving websites that won't compromise the data of the website or your user's data. Most web browsers will warn users when they are using a site that is not secured with HTTPS. Follow the :ref:`Configure HTTPS <https_config>` tutorial to learn how to configure your Azure portal for HTTPS.

Setup Forgotten Password Recovery
=================================

To use Tethys Portal's forgotten password recovery feature, it needs to be configured with an email service. Follow the :ref:`Forgotten Password Recovery <setup_email_capabilities>` tutorial to enable this feature.


Enable Docker (optional)
========================

Start it
Enable it
Add user to docker group

THREDDS
-------

tethys docker init -c thredds
bind data directory to $TETHYS_HOME/data
Add endpoint to NGINX
Create Tethys Service


GeoServer
---------

tethys docker init -c thredds
bind data directory to $TETHYS_HOME/data
Add endpoint to NGINX
Create Tethys Service