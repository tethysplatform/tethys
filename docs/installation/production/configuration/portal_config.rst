.. _production_portal_config:

********************
Portal Configuration
********************

**Last Updated:** May 2020

3) Create :file:`portal_config.yml`:

    Generate the portal configuration file with the following command:

    .. code-block::

        tethys gen portal_config

    .. note::

        This file is generated in your ``TETHYS_HOME`` directory. It can be edited directly or using the ``tethys settings`` command. See: :ref:`tethys_configuration` and :ref:`tethys_settings_cmd`.

4) Note the Location of ``TETHYS_HOME``

    The directory where the :file:`portal_config.yml` is generated is the ``TETHYS_HOME`` directory for your installation.

    The default location of ``TETHYS_HOME`` is :file:`~/.tethys/` if your environment is named Tethys, otherwise it is :file:`~/.tethys/<env_name>/`.

    **Note this location and use it in the following steps where you see ``<TETHYS_HOME>``.**

5) Configure Settings for Production:

    Use the ``tethys settings`` command to set the following settings (see :ref:`tethys_settings_cmd`). **DO NOT EDIT settings.py DIRECTLY IN TETHYS 3+**.

    * Set Allowed Hosts:

        .. code-block::

            tethys settings --set ALLOWED_HOSTS "['my.example.host', 'localhost']"

        .. note::

            The first entry in ``ALLOWED_HOSTS`` will be used to set the server name in the nginx configuration file.

    * Disable Debug:

        .. code-block::

            tethys settings --set DEBUG False

2. Review the Django Deployment Checklist
=========================================

.. important::

    Review the `Django Deployment Checklist <https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/>`_ carefully. Remember, do not edit the settings.py file directly, instead use the ``tethys settings`` command or edit the ``settings`` section of the :file:`portal_config.yml` to change Django settings.

Generate Tethys Configuration
=============================

Required Settings
=================

* ALLOWED_HOSTS
* DEBUG