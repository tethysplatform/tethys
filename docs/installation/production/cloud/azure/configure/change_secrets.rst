.. _azure_vm_config_change_secrets:

***************************************
Change Secrets and Passwords (Required)
***************************************

**Last Updated:** November 2021

The default secret key and passwords should be changed to secure the VM immediately after provisioning it.

Change Secret Key
=================

The :file:`portal_config.yml` has been configured with a default ``SECRET_KEY`` that should be changed. Use a tool like `RandomKeygen <https://randomkeygen.com/>`_ to generate a new key (e.g.: CodeIgniter Encryption Key or 256-bit WEP Key). Update the ``SECRET_KEY`` value as follows:

.. code-block::

    tethys settings --set SECRET_KEY <new_key>

Restart the Tethys service afterward:

.. code-block::

    sudo systemctl restart tethys

Change Passwords
================

All user accounts have default passwords that should be changed to secure passwords soon after creating the VM. Use a password generator like `xkpasswd <https://xkpasswd.net/s/>`_ or similar to create strong and unique passwords for the following accounts:

* Tethys User Account
* Tethys Portal Admin User
* Database Users (postgres, tethys_default, tethys_super)

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

.. figure:: ../images/configure--delete-admin.png
    :width: 800px
    :alt: Delete the default admin user account

    **Figure 1.** Delete the default admin user account.