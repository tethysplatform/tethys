.. _advanced_config_lockout:

******************
Lockout (Optional)
******************

**Last Updated:** May 2020

.. important::

    This feature requires the ``django-axes`` library to be installed. Starting with Tethys 5.0 or if you are using ``micro-tethys-platform``, you will need to install ``django-axes`` using conda or pip as follows:

    .. code-block:: bash

        # conda: conda-forge channel strongly recommended
        conda install -c conda-forge django-axes

        # pip
        pip install django-axes

Tethys Portal includes lockout capabilities to prevent brute-force login attempts. This capability is provided by the `Django Axes <https://django-axes.readthedocs.io/en/latest/>`_ add-on for Django. This document describes the different configuration options that are available for lockout capabilities in Tethys Portal.

.. image:: ./images/locked_out.png
   :width: 800px
   :align: left

Default Configuration
=====================

By default, the lockout functionality is disabled when the ``DEBUG`` setting is set to ``True`` and enabled when ``DEBUG`` is ``False``. When lockout is enabled the default behavior is to automatically disable logging in after 3 failed attempts for a given username with a cool off period of 30 minutes. For more details on the default lockout settings see ``LOCKOUT_CONFIG`` in the :ref:`tethys_configuration` documentation.

Configuration
=============

The default behavior can be overridden with settings in your :file:`portal_config.yaml` file. For example:

.. code-block:: yaml

  LOCKOUT_CONFIG:
    AXES_ENABLED: True
    AXES_FAILURE_LIMIT: 10
    AXES_COOLOFF_TIME: 1
    AXES_LOCK_OUT_BY_USER_OR_IP: True
    AXES_RESET_ON_SUCCESS: True

For a full list of options for configuring lockout in Tethys Portal, please refer to the `Django Axes Configuration Documentation <https://django-axes.readthedocs.io/en/latest/4_configuration.html>`_

