.. _azure_vm_troubleshooting:

***************
Troubleshooting
***************

**Last Updated:** November 2021

Unable to Connect after the VM Starts
=====================================

The most common cause of this issue is that the HTTP/HTTPS ports have not been opened on the Virtual Machine. Step 2 of the :ref:`azure_vm_config_https` tutorial describes how to configure ports for an Azure virtual machine. The process is the same for the HTTP port, just select HTTP instead of HTTPS for the **Service** and name it HTTP.

Error after running `tethys manage start`
=========================================

Don't use `tethys manage start` in a production server! That starts the development server. To start/stop/restart Tethys in the Azure VM, use the ``systemctl`` command. See: :ref:`azure_vm_orientation_start_stop`.

Tethys Looking for Database on Port 5436
========================================

This means that Tethys isn't able to find the :file:`portal_config.yml` and is using the default value for the port: 5436. Log in as the ``tethys`` user so that the ``TETHYS_HOME`` variable is set correctly. See :ref:`azure_vm_orientation_tethys_account`.

.. important::

    DO NOT RUN ``tethys db confgure`` to set up a database. The database created by ``tethys db configure`` is not suitable for production.
