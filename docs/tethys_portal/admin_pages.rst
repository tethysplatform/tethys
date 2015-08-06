*******************
Administrator Pages
*******************

**Last Updated:** August 4, 2015

Tethys Portal includes administration pages that can be used to manage the website (see Figure 1). The administration dashboard is only available to administrator users. You should have created a default administrator user when you installed Tethys Platform. If you are logged in as an administrator, you will be able to access the administrator dashboard by selecting the "Site Admin" option from the user drop down menu in the top right-hand corner of the page.

.. figure:: ../images/site_admin/home.png
    :width: 500px

**Figure 1.** Administrator dashboard for Tethys Portal.

.. note::

    If you did not create an administrator user during installation, run the following command in the terminal:

    ::

        $ python /usr/lib/tethys/src/manage.py createsuperuser

Manage Users and Permissions
============================

Permissions and users can be managed from the administrator dashboard using the ``Groups`` and ``Users`` links under the Authentication and Authorization heading. Figure 4 shows an example of the user management page for a user named John. Permissions can be assigned to each user individually or users can be assigned to groups and they will be given the permissions of that group.

.. figure:: ../images/tethys_portal/tethys_portal_user_management.png
    :width: 500px

**Figure 4.** User management for Tethys Portal.

Manage Tethys Services
======================

The administrator pages provide a simple mechanism for linking to the other services of Tethys Platform. Use the ``Spatial Dataset Services`` link to connect your Tethys Portal to GeoServer, the ``Dataset Services`` link to connect to CKAN instances or HydroShare, or the ``Web Processing Services`` link to connect to WPS instances. For detailed instructions on how to perform each of these tasks, refer to the :doc:`../tethys_sdk/spatial_dataset_services`, :doc:`../tethys_sdk/dataset_services`, and :doc:`../tethys_sdk/geoprocessing` documentation, respectively.

Manage Computing Resources
==========================

Manage the computing resources of Tethys Portal using the ``Tethys Compute`` admin pages. Powered, by TethysCluster, these pages allow Tethys Portal administrators to spin up clusters of computing resources on either the Amazon or Microsoft Azure commercial clouds. These computational nodes will be made available to apps that are installed in your Tethys Portal. For more detailed information on the computing capabilities of Tethys Platform, refer to the :doc:`../tethys_sdk/cloud_computing` documentation.