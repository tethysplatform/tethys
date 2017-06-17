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

.. _tethys_portal_permissions:

Manage Users and Permissions
============================

Permissions and users can be managed from the administrator dashboard using ``Users`` link under the ``Authentication and Authorization`` heading. Figure 4 shows an example of the user management page for a user named John.

.. figure:: ../images/tethys_portal/tethys_portal_user_management.png
    :width: 500px

**Figure 4.** User management for Tethys Portal.

Assign App Permission Groups
----------------------------

To assign an app permission group to a user, select the desired user and locate the ``Groups`` dialog under the ``Permissions`` heading of the ``Change User`` page. All app permission groups will appear in the ``Available Groups`` list box. Assigning the permission group is done by moving the permission group to the ``Chosen Groups`` list box. Although the permissions may also appear in the ``User Permissions`` list box below, they cannot be properly assigned in the ``Change User`` dialog.

Assign App Permissions
----------------------

To assign a singluar app permission to a user, return to the administrator dashboard and navigate to the ``Installed Apps`` link under the ``Tethys Apps`` heading. Select the link with the app name from the list. In the upper right corner of the ``Change Tethys App`` page click the ``Object Permissions`` button. On the ``Object Permissions`` page you can assign app specific permissions to a user by entering the username in the ``User Identification`` field and press the ``Manage user`` button. Incidentally, you can also manage the app permissions groups from the ``Object Permisions`` page, but changes will be overridden the next time the server restarts and permissions are synced from the app.

.. note::

	Since assigning the individual app permissions is so difficult, we highly recommend that you use the app permission groups to group app permissions and then assign the permission groups to the users using the ``Change User`` page.

Anonymous User
--------------

The ``AnonymousUser`` can be used to assign permissions and permission groups to users who are not logged in. This means that you can define permissions for each feature of your app, but then assign them all to the ``AnonymousUser`` if you want the app to be publicly accessible.

Manage Tethys Services
======================

The administrator pages provide a simple mechanism for linking to the other services of Tethys Platform. Use the ``Spatial Dataset Services`` link to connect your Tethys Portal to GeoServer, the ``Dataset Services`` link to connect to CKAN instances or HydroShare, or the ``Web Processing Services`` link to connect to WPS instances. For detailed instructions on how to perform each of these tasks, refer to the :doc:`../tethys_sdk/tethys_services/spatial_dataset_services`, :doc:`../tethys_sdk/tethys_services/dataset_services`, and :doc:`../tethys_sdk/tethys_services/web_processing_services` documentation, respectively.

.. _tethys_portal_terms_and_conditions:

Manage Terms and Conditions
===========================

Portal administrators can manage and enforce portal wide terms and conditions and other legal documents via the administrator pages.

Use the ``Terms and Conditions`` link to create new legal documents (see Figure 5). To issue an update to a particular document, create a new entry with the same slug (e.g. 'site-terms'), but a different version number (e.g.: 1.10). This allows you to track multiple versions of the legal document and which users have accepted each. The document will not become active until the ``Date active`` field has been set and the date has past.

.. figure:: ../images/tethys_portal/tethys_portal_toc_new.png
    :width: 500px

**Figure 5.** Creating a new legal document using the terms and conditions feature.

When a new document becomes active, users will be presented with a modal prompting them to review and accept the new terms and conditions (see Figure 6). The modal can be dismissed, but will reappear each time a page is refreshed until the user accepts the new versions of the legal documents.

.. figure:: ../images/tethys_portal/tethys_portal_toc_modal.png
    :width: 500px

**Figure 6.** Terms and conditions modal.

Manage Computing Resources
==========================

Computing resources can be managed using the ``Tethys Compute`` admin pages. Powered, by TethysCluster <http://www.tethysplatform.org/TethysCluster/>`_, these pages allow Tethys Portal administrators to spin up clusters of computing resources on either the Amazon or Microsoft Azure commercial clouds, and link local computing clusters that are managed with HTCondor. These computational These computational resources are accessed in apps through the :doc:`../tethys_sdk/jobs` and the :doc:`../tethys_sdk/compute`. For more detailed documentation refer to the links below.

.. toctree::
   :maxdepth: 2

   tethys_compute_admin_pages

