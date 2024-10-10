.. _production_troubleshooting:

***************
Troubleshooting
***************

**Last Updated:** September 2022

This document provides a number of resources that can be used to troubleshoot your production installation of Tethys Portal.

.. _production_troubleshooting_logs:

Check the Logs
==============

Your first stop when troubleshooting should be to check the logs to determine if there are any errors occuring. There are several logs that may contain useful information related to any issues you are having.

Supervisor Logs
---------------

The supervisor logs are most helpful if you encounter errors while running one of the ``supervisorctl`` commands:

.. code-block:: bash

    /var/log/supervisor/supervisor.log

NGINX Logs
----------

The NGINX error log is useful for debugging issues related to configuration problems with NGINX or other errors related to NGINX.

.. code-block:: bash

    /var/log/nginx/error.log

The access log records all incoming web traffic and response from NGINX. This file is helpful for debugging problems connecting to Tethys Portal. For example, if NGINX is running and there are no new entries in the :file:`access.log` when you try to access Tethys Portal, then the connection is not making it to NGINX. This could be caused by network issues with your server or closed ports in your firewall.

.. code-block:: bash

    /var/log/nginx/access.log


Tethys Logs
-----------

The Tethys Portal log is useful for determining errors that are raised by Tethys Portal such as 500 errors.

.. code-block:: bash

    /var/log/tethys/tethys.log

Email Logs
----------

If you are having trouble with the Postfix email server, then you should check the :file:`syslog`. Look for entries with ``postfix`` in them.

.. code-block:: bash

    /var/log/syslog

.. note::

    A 250 status code means a send operation was successful.


Linux Commands
==============

Learning a few of the common Linux commands can help you become more proficient at debugging issues with production installations.

Tail Command
------------

The `tail <https://linux.die.net/man/1/tail>`_ command is often useful for checking logs. It allows you to view the last lines of a file, which is especially helpful for logs b/c they tend to get long:

.. code-block:: bash

    tail -n <number-of-lines> <path-to-file>

You can also have ``tail`` follow the logs, so you can see live print outs to the logs as you interact with the website. Just add the `-f` option to follow the log file:

.. code-block:: bash

    tail -f -n <number-of-lines> <path-to-file>

Grep Command
------------

The `grep <https://linux.die.net/man/1/grep>`_ command is another useful utility when inspecting logs. You can pipe the output from a tail command into a grep command to filter the output to only lines containing a query string or pattern. For example:

.. code-block:: bash

    tail -n 100 /var/log/syslog | grep "postfix"

Chown Command
-------------

The `chown <https://linux.die.net/man/1/chown>`_ command can be used to change the ownership of files and directories. For example, change the ownership of all files in a directory to a certain user:

.. code-block:: bash

    sudo chown -R <username> /path/to/dir

Chmod Command
-------------

The `chmod <https://linux.die.net/man/1/chmod>`_ command can be used to change permission levels of owners, groups, and everyone else on files and directories. For example to add execute permissions of the owners of the file you could run:

.. code-block:: bash

    sudo chmod +ux /path/to/file.ext

Review Configuration
====================

Many issues with a Tethys Portal production installation come down to a configuration issue. This is especially true if you are having issues starting NGINX or Daphne (ASGI). If the issue is not readily apparent in the logs, then a next step should be to review the configuration files.

You should verify the following:

    * Paths
    * Syntax errors
    * Spelling errors in variables
    * Other inconsistencies

Supervisor
----------

There are two Tethys specific configuration files for supervisor, one for NGINX and one for Daphne (ASGI).

.. code-block:: bash

    ~/.tethys/asgi_supervisord.conf

.. code-block:: bash

    ~/.tethys/nginx_supervisord.conf

Also verify that these files are correctly linked to the appropriate directory in :file:`/etc` (see :ref:`production_supervisor_config`). Listing the contents of the directory with the `-l` option will show you if the links are valid or not:

**Ubuntu**:

    .. code-block:: bash

        ls -l /etc/supervisor/conf.d/

**Rocky Linux**:

    .. code-block:: bash

        ls -l /etc/supervisord.d/

NGINX
-----

The Tethys-specific configuration file for NGINX is usually located at:

.. code-block:: bash

    ~/.tethys/tethys_nginx.conf

Also verify that this file is correctly linked to the appropriate directory in :file:`/etc` (see :ref:`production_nginx_config`). Listing the contents of the directory with the `-l` option will show you if the link is valid or not:

**Ubuntu**:

    .. code-block:: bash

        ls -l /etc/nginx/sites-enabled/

**Rocky Linux**:

    .. code-block:: bash

        ls -l /etc/nginx/conf.d/

Tethys
------

All Tethys and Django settings are configured using the :file:`portal_config.yml`.

.. code-block:: bash

    ~/.tethys/portal_config.yml

.. important::

    Any Django setting can be added to the ``settings`` section of the :file:`portal_config.yml`. **DO NOT EDIT THE settings.py FILE DIRECTLY**

SELinux
-------

If you suspect an issue with SELinux then inspecting the :file:`tethys-selinux.te` file may be worthwhile:

.. code-block:: bash

    ~/.tethys/tethys-selinux.te

If you make a change to the :file:`tethys-selinux.te` file, you will need to run the ``checkmodule`` and ``semodule_package`` commands again and then update the policy (see: :ref:`selinux_configuration`).

File Permissions
================

The production Tethys Portal server processes will be managed by the ``NGINX_USER``. If you encounter issues with file permissions (i.e. permission denied), you may need to grant the ``NGINX_USER`` access to additional directories.

The minimum directories that should be owned by the ``NGXINX_USER`` at runtime are the ``STATIC_ROOT`` and ``TETHYS_WORKSPACES_ROOT`` directories (see: :ref:`production_file_permissions_config`). Listing the contents of these directories is a good sanity check to ensure the contents are owned by the ``NGINX_USER``:

.. code-block:: bash

        sudo ln -l <STATIC_ROOT>
        sudo ln -l <TETHYS_WORKSPACES_ROOT>

You may also need to modify what level of access the ``NGINX_USER`` has. This can be done using the ``chmod`` command. For example, to set the owner to have read-only access to all files in a directory, you could run:

.. code-block:: bash

    sudo chmod -R =ur /path/to/dir

.. caution::

    Granting the ``NGINX_USER`` access to directories and files on your server should be done judiciously. Remember anything the ``NGINX_USER`` can access is potentially accessible to the internet at large and the internet is a hostile environment. When possible, you should also restrict access to read-only.

Internet Search
===============

Your first step in addressing an issue with your production installation is to do an internet search. As each production installation is different, it is likely that the issue you are encountering is specific to your setup. It is also likely that someone else has encountered this same issue and there is a solution to it on one of the many online forums.

The following tips can help you when searching for an issue:

    1. Include the software name somewhere in the search (i.e.: supervisor, nginx, Django)
    2. Include the error message from any traceback, but remove anything that is specific to your machine or instance
    3. Tethys Portal is built on Django, so adding Django to your search terms often yields helpful results.
    4. Recognize that many issues you may encounter won't be Tethys specific. If you can figure out where the error is coming from then you can narrow your search (see: :ref:`production_troubleshooting_logs`). For example, if the error is occurring in one of the NGINX logs, then adding "NGINX" to your search terms would be more helpful than adding "Tethys".

Tethys Platform GitHub Discussions
==================================

The `Tethys Platform GitHub Discussions <https://github.com/tethysplatform/tethys/discussions>`_ is an excellent place to search for Tethys-specific problems. Many members of the group respond to questions posted, including the primary developers of Tethys Platform.

Please search for your issue before posting a new question, as someone likely has already asked the question you want to ask. If you do post a question, please provide as much information as possible. At a minimum, include:

    1. Steps to reproduce the problem.
    2. A clear description of the problem with traceback if applicable.
    3. What the expected behavior should be.
    4. Helpful metadata such as the operating system and version of Tethys.
