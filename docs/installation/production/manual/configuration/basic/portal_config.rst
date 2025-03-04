.. _production_portal_config:

********************
Portal Configuration
********************

**Last Updated:** September 2024

The :file:`portal_config.yml` is the primary configuration file for Tethys Portal. As of version 3.0, you should not edit the :file:`settings.py` file directly. Instead add any Django settings that you need to the ``settings`` section of the :file:`portal_config.yml`. This can be done by manually editing the file, or you can use the ``tethys settings`` command to add settings to it.

This part of the installation guide will show you how to create the :file:`portal_config.yml` and highlights a few of the settings that you should configure when setting up Tethys Portal for production. The following sections of the production installation guide will walk you through other important settings as well.

1. Prepare the ``TETHYS_HOME`` Directory
========================================

The ``TETHYS_HOME`` directory is the directory where the :file:`portal_config.yml` file is generated. This directory is also used to store other configuration files and logs for Tethys Portal. The default location of the ``TETHYS_HOME`` directory is :file:`~/.tethys/` or :file:`/home/<username>/.tethys/` if your environment is named Tethys, otherwise it is :file:`~/.tethys/<env_name>/`.

In a production environment, it is better to define the location of ``TETHYS_HOME`` to be outside of a user's home directory. The ``TETHYS_HOME`` directory should be on a disk with plenty of space and should be backed up regularly.

1. Decide where to store the ``TETHYS_HOME`` directory and create that directory:

    .. code-block:: bash

        sudo mkdir -p <TETHYS_HOME>
        sudo chown -R $USER <TETHYS_HOME>

2. Create a new ``tethys.sh`` script in ``/etc/profile.d`` to set the ``TETHYS_HOME`` environment variable for all users:

    .. code-block:: bash

        sudo touch /etc/profile.d/tethys.sh
        sudo chmod +x /etc/profile.d/tethys.sh
        sudo echo "export TETHYS_HOME=<TETHYS_HOME>" > /etc/profile.d/tethys.sh

.. note::

    Replace ``<TETHYS_HOME>`` with the path to the directory where you would like to store the Tethys configuration files.

2. Generate Tethys Configuration
================================

Generate the portal configuration file with the following command:

    .. code-block::

            tethys gen portal_config

    .. note::

        This file is generated in your ``TETHYS_HOME`` directory. It can be edited directly or using the ``tethys settings`` command. See: :ref:`tethys_configuration` and :ref:`tethys_settings_cmd`.

3. Set Required Production Settings
===================================

The following settings should be set for a production installation of Tethys Portal.

ALLOWED_HOSTS
-------------

The `ALLOWED_HOSTS <https://docs.djangoproject.com/en/5.0/ref/settings/#allowed-hosts>`_ setting is used to specify a list of host/domain names that this Django site can serve. If a request comes in with a host/domain name that is not listed here, it will be rejected. You should set this to the domain(s) of your server. For example, you can set this setting using the ``tethys settings`` command as follows:

    .. code-block:: bash

        tethys settings --set ALLOWED_HOSTS "['<SERVER_DOMAIN_NAME>']"

    .. note::

        Replace ``<SERVER_DOMAIN_NAME>`` with the domain name you identified during the :ref:`production_preparation` step.

    .. important::

        The first entry in ``ALLOWED_HOSTS`` will be used to set the server name in the NGINX configuration file in one of the following sections of this guide.


CSRF_TRUSTED_ORIGINS
--------------------

The `CSRF_TRUSTED_ORIGINS <https://docs.djangoproject.com/en/5.0/ref/settings/#csrf-trusted-origins>`_ setting is used to specify a list of trusted origins for unsafe requests (e.g. POST). Beginning with Django 4.0 the list of origins must be fully qualified domain names (e.g. https://example.com). You should set this to the domain(s) of your server. For example, you can set this setting using the ``tethys settings`` command as follows:

    .. code-block:: bash

        tethys settings --set CSRF_TRUSTED_ORIGINS "['<SCHEME><SERVER_DOMAIN_NAME>']"

    .. note::

        Replace ``<SCHEME>`` with ``http://`` or ``https://`` as appropriate for your deployment.
        Replace ``<SERVER_DOMAIN_NAME>`` with the domain name you identified during the :ref:`production_preparation` step.

DEBUG
-----

The `DEBUG <https://docs.djangoproject.com/en/5.0/ref/settings/#debug>`_ settings is used to enable debug mode. You should never deploy a site into production with ``DEBUG`` turned on. You should set this setting to ``False`` as follows:

    .. code-block:: bash

        tethys settings --set DEBUG False

4. Review the Django Deployment Checklist
=========================================

Review the `Django Deployment Checklist <https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/>`_ carefully.

    .. important::

        Remember, do not edit the settings.py file directly, instead use the ``tethys settings`` command or edit the ``settings`` section of the :file:`portal_config.yml` to change Django settings.
