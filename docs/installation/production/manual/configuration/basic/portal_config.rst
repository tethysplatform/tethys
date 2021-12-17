.. _production_portal_config:

********************
Portal Configuration
********************

**Last Updated:** May 2020

The :file:`portal_config.yml` is the primary configuration file for Tethys Portal. As of version 3.0, you should not edit the :file:`settings.py` file directly. Instead add any Django settings that you need to the ``settings`` section of the :file:`portal_config.yml`. This can be done by manually editing the file, or you can use the ``tethys settings`` command to add settings to it.

This part of the installation guide will show you how to create the :file:`portal_config.yml` and highlights a few of the settings that you should configure when setting up Tethys Portal for production. The following sections of the production installation guide will walk you through other important settings as well.

1. Generate Tethys Configuration
================================

Generate the portal configuration file with the following command:

    .. code-block::

            tethys gen portal_config

    .. note::

        This file is generated in your ``TETHYS_HOME`` directory. It can be edited directly or using the ``tethys settings`` command. See: :ref:`tethys_configuration` and :ref:`tethys_settings_cmd`.

2. Note the Location of ``TETHYS_HOME``
=======================================

The directory where the :file:`portal_config.yml` is generated is the ``TETHYS_HOME`` directory for your installation.

The default location of ``TETHYS_HOME`` is :file:`~/.tethys/` or :file:`/home/<username>/.tethys/` if your environment is named Tethys, otherwise it is :file:`~/.tethys/<env_name>/`.

**Note this location and use it anywhere you see** ``<TETHYS_HOME>``.

3. Set Required Production Settings
===================================

The following settings should be changed for a production installation of Tethys Portal.

ALLOWED_HOSTS
-------------

The `ALLOWED_HOSTS <https://docs.djangoproject.com/en/3.0/ref/settings/#allowed-hosts>`_ setting is used to specify a list of host/domain names that this Django site can serve. If a request comes in with a host/domain name that is not listed here, it will be rejected. You should set this to the domain(s) of your server. For example, you can set this setting using the ``tethys settings`` command as follows:

    .. code-block:: bash

        tethys settings --set ALLOWED_HOSTS "['<SERVER_DOMAIN_NAME>']"

    .. note::

        Replace ``<SERVER_DOMAIN_NAME>`` with the domain name you identified during the :ref:`production_preparation` step.

    .. important::

        The first entry in ``ALLOWED_HOSTS`` will be used to set the server name in the NGINX configuration file in one of the following sections of this guide.

DEBUG
-----

The `DEBUG <https://docs.djangoproject.com/en/3.0/ref/settings/#debug>`_ settings is used to enable debug mode. You should never deploy a site into production with ``DEBUG`` turned on. You should set this setting to ``False`` as follows:

    .. code-block:: bash

        tethys settings --set DEBUG False

4. Review the Django Deployment Checklist
=========================================

Review the `Django Deployment Checklist <https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/>`_ carefully.

    .. important::

        Remember, do not edit the settings.py file directly, instead use the ``tethys settings`` command or edit the ``settings`` section of the :file:`portal_config.yml` to change Django settings.
