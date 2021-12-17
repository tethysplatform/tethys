.. _azure_vm_cost:

**********************
Estimate Azure VM Cost
**********************

**Last Updated:** November 2021

The cost of a VM on Azure depends on what compute requirements your Tethys Platform installation needs. If your apps do a lot of on-server processing, then you may need more cores and memory, if your apps require a lot of storage, then you'll need more disk space. For a quick estimate of cost based on the VM series, see: `Linux Virtual Machines Prices | Microsoft Azure <https://azure.microsoft.com/en-us/pricing/details/virtual-machines/linux/>`_.

Azure also provides a pricing calculator that can be used to get a more accurate estimate of the cost. In this tutorial you will learn how to use the Azure Pricing Calculator to estimate the cost of running a single-node Tethys Platform VM on Azure.

1. Navigate to Azure Pricing Calculator
=======================================

The Azure Pricing Calculator is part of the Azure website (Figure 1). To access it, use a web browser to navigate to:

https://azure.microsoft.com/en-us/pricing/calculator/

.. figure:: images/cost--pricing-calculator.png
    :width: 800px
    :alt: Screenshot of Azure Pricing Calculator

    **Figure 1.** Screenshot of Azure Pricing Calculator.

2. Select Products
==================

To estimate the cost of a single VM installation of Tethys Platform, click on the **Virtual Machines** tile to add a virtual machine to the estimate (Figure 2).

.. figure:: images/cost--add-vm.png
    :width: 800px
    :alt: Screenshot of adding Virtual Machines to the estimate

    **Figure 2.** Screenshot of adding Virtual Machines to the estimate.

3. Configure Options
====================

Scroll down to the section titled "Your Estimate", where you should see an item called "Virtual Machine" has been added. You'll need to define the type and size of the VM using the options in the Virtual Machine section (Figure 2). Fill out the options as follows:

* **REGION**: Select the region that the Tethys server will be hosted in. Try to select a region that is closest to most of your users.
* **OPERATING SYSTEM**: Choose **Linux**.
* **TYPE**: Choose **Ubuntu**.
* **TIER**, **CATEGORY**, **INSTANCE SERIES**: Use these fields to filter the **INSTANCE** field to the types of VMs suited to the requirements of the apps you plan to install on the server. Here are some considerations for the different categories:

    * **General purpose**: Suitable for "viewer" type apps that do not run intense processing on the server and use externally hosted data services.
    * **Compute optimized**: Consider using one of these if at least one of the apps performs intense processing on the server.
    * **Memory optimized**: Consider using one of these if you plan to run a GeoServer and/or THREDDS server on the VM. Both GeoServer and THREDDS perform better with more memory.
    * **Storage optimized**: Consider using one of these if at least one of the apps requires a lot of file storage. Additional storage can be added to VMs, so using this instance category is not required for apps with high-storage needs.

* **INSTANCE**: The instance type defines the size of the virtual machine (i.e. number of processors/cores, memory, and storage). There are many different types of instance types organized into groups called series. For an explanation of the different VM series available, see `Virtual Machine series | Microsoft Azure <https://azure.microsoft.com/en-us/pricing/details/virtual-machines/series/>`_.
* **VIRTUAL MACHINES**: Set to the number of Tethys VMs you plan to have (usually 1).
* **Hours**: Time period you want the estimate to estimate cost over. The average number of hours in a month is 730.5 hours (365.25 days x 24 hours / 12 months).
* **Savings Options**: Select a Savings option to potentially save on the cost (see: `Azure Reserved Virtual Machine Instances | Microsoft Azure <https://azure.microsoft.com/en-us/pricing/reserved-vm-instances/>`_).
* **Managed Disks**: Use this section to add additional storage to the VM. Most VM instances don't come with much storage attached.

.. figure:: images/cost--configure-options.png
    :width: 800px
    :alt: Screenshot of *Your Estimate* form

    **Figure 3.** Screenshot of the Your Estimate form.

4. Export / Save
================

After specifying the VM configuration, your estimate will be complete. You can choose to export the estimate as an Excel file or save it if to your Azure account. Saved estimates are available on the **Saved Estimates** tab of the calculator page after logging in.

Scroll down to the bottom of the estimate form to see **Export** and **Save** buttons (Figure 4).

.. figure:: images/cost--export.png
    :width: 800px
    :alt: Screenshot of exporting the estimate.

    **Figure 4.** Screenshot of exporting the estimate.
