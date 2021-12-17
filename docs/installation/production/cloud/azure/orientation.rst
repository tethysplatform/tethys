.. _azure_vm_orientation:

***********************
Orientation to Azure VM
***********************

**Last Updated:** November 2021

This tutorial provides an orientation to the Tethys Azure virtual machine (VM). It includes instructions for connecting to the VM, user accounts to use, descriptions of what is installed, and important directories and files.

.. _azure_vm_orientation_ssh:

Connect with SSH
================

To connect to the Azure virtual machine via SSH, do the following:

1. Navigate to the overview page for the virtual machine resource.
2. If the virtual machine is not running, press the **Start** button.
3. Click on **Connect** from the tools at the top of the page and select SSH.
4. Follow the instructions to connect to the virtual machine via SSH.

.. figure:: images/connect--ssh-instructions.png
    :width: 800px
    :alt: Example connect SSH instructions

    **Figure 1.** Example connect SSH instructions.

.. _azure_vm_orientation_tethys_account:

Tethys User Account
===================

The Tethys Portal image for Azure includes a ``tethys`` user account for maintenance of the Tethys installation. You should always be logged in to this account to run any ``tethys`` commands or install apps.

Change Tethys User Password
---------------------------

Before switching to the ``tethys`` user account, you should change the password using the following command:

.. code-block::

    sudo passwd tethys

.. tip::

    Consider using a password generator to help you create strong passwords. For example, the `xkpasswd generator <https://xkpasswd.net/s/>`_ is a tool based on an `xkcd cartoon <https://xkcd.com/936/>`_ for creating secure passwords that are memorable.

Switch to Tethys User
---------------------

To switch to the Tethys user from another account, use the ``su`` command (switch user):

.. code-block::

    su - tethys

Enter the password for the ``tethys`` user when prompted.

.. important::

    Don't forget the dash (``-``)!

To exit the ``tethys`` user and return to your login user, run the ``exit`` command:

.. code-block::

    exit

Activate Conda Environment
==========================

Before running any ``tethys`` command in this or other tutorials, you'll need to activate the ``tethys`` Conda environment. After logging in as the ``tethys`` user, you'll notice that the ``base`` environment for Conda is automatically activated. Activate the ``tethys`` environment as normal:

.. code-block::

    conda activate tethys

Now you can run ``tethys`` commands:

.. code-block::

    tethys version

Tethys Home
===========

Tethys Home is the directory where the ``portal_config.yaml`` is located. Use the ``TETHYS_HOME`` environment variable to locate the Tethys Home directory:

.. code-block::

    echo $TETHYS_HOME

You can also use ``TETHYS_HOME`` to change into the directory:

.. code-block::

    cd $TETHYS_HOME

Contents
--------

List the contents of the TETHYS_HOME directory:

.. code-block::

    ls -l $TETHYS_HOME

.. figure:: images/connect--tethys-home-contents.png
    :width: 800px
    :alt: Contents of Tethys Home directory as given by ls command

    **Figure 2.** Contents of Tethys Home directory as given by ``ls`` command.

Here's a brief explanation of the important items in the Tethys Home directory:

* **apps**: Directory for storing app source code.
* **config**: Directory with configuration files used by the production installation.
* **data**: Directory for storing data for GeoServer, THREDDS, etc.
* **miniconda3**: Conda installation containing the ``tethys`` Conda environment.
* **portal_config.yml**: The primary configuration file for the Tethys Portal.
* **static**: Location where static files are collected and served by NGINX.
* **workspaces**: Location where workspaces for apps will be collected.

Database
========

Tethys Portal is configured to use a system-installed PostgreSQL database with the PostGIS extension installed.

psql
----

To connect to the database using ``psql``, run the ``su`` command, but this time specifying the ``postgres`` user and a command to run with the ``-c`` option:

.. code-block::

    sudo su - postgres -c psql

Version
-------

Using ``psql``, run the following query to get the version of the PostgreSQL database:

.. code-block::

    SELECT version();

Run the following query in ``psql`` to get the version of PostGIS installed:

.. code-block::

    SELECT * FROM pg_available_extensions WHERE pg_available_extensions.name LIKE 'postgis';

Database Users
--------------

Run the following in ``psql`` to get a list of the database users:

.. code-block::

    \du

.. important::

    The passwords of the database users should be changed from their default values. See :ref:`azure_vm_config` tutorial for how to do this.

Databases
---------

Run the following in ``psql`` to get a list of the databases:

.. code-block::

    \l

Quit psql
---------

To quit ``psql`` run:

.. code-block::

    \q

Docker
======

Docker is installed on the image but not running by default. This is to make it easy for you to install the services your apps need such as a THREDDS or GeoServer. The :ref:`azure_vm_config` tutorial describes the additional configuration that should be performed before using Docker.

Logs
====

In a production installation, you will need to examine logs to see errors when they occur. All logs for running processes on the server are located in the `/var/log` directory. Here's a list of the logs that are most helpful to use when debugging Tethys problems:

Daphne/Tethys Portal
--------------------

The Daphne logs capture all of the logged information from Tethys Platform:

* /var/log/tethys/access.log
* /var/log/tethys/error.log
* /var/log/tethys/out.log

NGINX
-----

The NGINX logs are helpful to review when you get 502 errors or when you are debugging connection issues:

* /var/log/nginx/access.log
* /var/log/nginx/error.log

PostgreSQL
----------

The PostgreSQL logs can be helpful when you encounter database errors, though these are rare for most Tethys applications:

* /var/log/postgresql/postgresql-12-main.log

.. _azure_vm_orientation_start_stop:

Start, Stop, Restart
====================

The Daphne, NGINX, and PostgreSQL services are all managed using the ``systemctl`` command. You'll need to restart any of these services any time you make changes to the configuration. Use the following commands to start/stop/restart these services.

Daphne/Tethys
-------------

.. code-block::

    sudo systemctl status tethys.service

.. code-block::

    sudo systemctl start tethys.service

.. code-block::

    sudo systemctl stop tethys.service

.. code-block::

    sudo systemctl restart tethys.service

NGINX
-----

.. code-block::

    sudo systemctl status nginx.service

.. code-block::

    sudo systemctl start nginx.service

.. code-block::

    sudo systemctl stop nginx.service

.. code-block::

    sudo systemctl restart nginx.service

PostgreSQL
----------

.. code-block::

    sudo systemctl status postgresql@12-main.service

.. code-block::

    sudo systemctl start postgresql@12-main.service

.. code-block::

    sudo systemctl stop postgresql@12-main.service

.. code-block::

    sudo systemctl restart postgresql@12-main.service

Additional Resources
====================

* `Su Command in Linux (Switch User) <https://linuxize.com/post/su-command-in-linux/>`_
* `Psql Command Documentation <https://www.postgresql.org/docs/12/app-psql.html>`_
* `PostgreSQL Primer for Busy People <https://zaiste.net/posts/postgresql-primer-for-busy-people/>`_
* `Understanding and Using Systemd <https://www.linux.com/training-tutorials/understanding-and-using-systemd/>`_
* `xkpasswd <https://xkpasswd.net/s/>`_

What's Next?
============

Now that you know how to connect to the VM and have a basic understanding of what is installed, you are ready to configure and customize the Tethys Portal. Don't skip out on this important next step!

