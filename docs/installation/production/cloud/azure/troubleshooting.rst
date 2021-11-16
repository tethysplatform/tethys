.. _azure_vm_troubleshooting:

***************
Troubleshooting
***************

**Last Updated:** Nov 2021

Error after running `tethys manage start`
=========================================

Don't use `tethys manage start` in a production server! That starts the development server. To start/stop/restart Tethys in the Azure VM, use the ``systemctl`` command. See: :ref:`azure_vm_orientation_start_stop`.

Tethys Looking for Database on Port 5436
========================================

This means that Tethys isn't able to find the :file:`portal_config.yml` and is using the default value for the port: 5436. Log in as the ``tethys`` user so that the ``TETHYS_HOME`` variable is set correctly. See :ref:`azure_vm_orientation_tethys_account`.

.. important::

    DO NOT RUN ``tethys db confgure`` to set up a database. The database created by ``tethys db configure`` is not suitable for production.
