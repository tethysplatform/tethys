*************
Tethys Portal
*************

**Last Updated:** May 23, 2015

Tethys Portal is the Django web site provided by Tethys Platform that acts as the runtime environment for apps. It leverages the capabilities of Django to provide the core website functionality that is often taken for granted in modern web applications. A description of the primary capabilities of Tethys Portal is provided in this article.


Administrator Pages
===================

Tethys Portal includes administration pages that can be used to manage the website (see Figure 1). The administration dashboard is only available to administrator users. You should have created a default administrator user when you installed Tethys Platform. If you are logged in as an administrator, you will be able to access the administrator dashboard by selecting the "Site Admin" option from the user drop down menu in the top right-hand corner of the page.

.. figure:: images/site_admin/home.png
    :width: 500px

**Figure 1.** Administrator dashboard for Tethys Portal.

.. note::

    If you did not create an administrator user during installation, run the following command in the terminal:

    ::

        $ python /usr/lib/tethys/src/manage.py createsuperuser

Manage Users and Permissions
============================

Permissions and users can be managed from the administrator dashboard using the ``Groups`` and ``Users`` links under the Authentication and Authorization heading. Figure 4 shows an example of the user management page for a user named John. Permissions can be assigned to each user individually or users can be assigned to groups and they will be given the permissions of that group.

.. figure:: images/tethys_portal/tethys_portal_user_management.png
    :width: 500px

**Figure 4.** User management for Tethys Portal.

Customize
=========

The content of Tethys Portal can be customized or rebranded to reflect your organization. To access these settings, login to Tethys Portal using an administrator account and select the  ``Site Settings`` link under the ``Tethys Portal`` heading. Sitewide settings can be changed using the ``General Settings`` link (Figure 2) and the content on the home page can be modified by using the ``Home Page`` link. The general settings that are available include the following:

* Site Title: the title of the web page that appears in browser tabs and bookmarks of the site.
* Favicon: the path to the image that is used in browser tabs and bookmarks.
* Brand Text: the title that appears in the header.
* Brand Image: the logo or image that appears next to the title in the header.
* Apps Library Title: the title of the page that displays app icons.
* Primary Color: color that is used as the primary theme color  (e.g.: #ff0000 or rgb(255,0,0)).
* Secondary Color: color that is used as the secondary theme color (e.g.: #ff0000 or rgb(255,0,0)).
* Footer Copyright: The copyright text that appears in the footer.

.. figure:: images/tethys_portal/tethys_portal_general_settings.png
    :width: 500px

**Figure 2.** General settings for Tethys Portal.


Figure 3 shows a screenshot of the home page settings that are available. The settings that can be modified on the home page include:

* Hero Text
* Blurb Text
* Feature 1 Heading
* Feature 1 Body
* Feature 1 Image
* Feature 2 Heading
* Feature 2 Body
* Feature 2 Image
* Feature 3 Heading
* Feature 3 Body
* Feature 3 Image
* Call to Action
* Call to Action Button

.. figure:: images/tethys_portal/tethys_portal_home_page_settings.png
    :width: 500px

**Figure 3.** Home page settings for Tethys Portal.

Tethys Portal can also be configured to bypass the home page. When this setting is applied, the root url will always redirect to the apps library page. This setting is modified in the ``settings.py`` script. Simply set the ``BYPASS_TETHYS_HOME_PAGE`` setting to ``True`` like so:

::

    BYPASS_TETHYS_HOME_PAGE = True

Developer Tools
===============

Tethys provides a Developer Tools page that is accessible when you run Tethys in developer mode. Developer Tools contain documentation, code examples, and live demos of the features of various features of Tethys. Use it to learn how to add a map or a plot to your web app using Gizmos or browse the available geoprocessing capabilities and formulate geoprocessing requests interactively.

.. figure:: images/features/developer_tools.png
    :width: 500px


**Figure 4. ** Use the Developer Tools page to assist you in development.

Manage Tethys Services
======================

The administrator pages provide a simple mechanism for linking to the other services of Tethys Platform. Use the ``Spatial Dataset Services`` link to connect your Tethys Portal to GeoServer, the ``Dataset Services`` link to connect to CKAN instances or HydroShare, or the ``Web Processing Services`` link to connect to WPS instances. For detailed instructions on how to perform each of these tasks, refer to the :doc:`./tethys_sdk/spatial_publishing`, :doc:`./tethys_sdk/dataset_services`, and :doc:`./tethys_sdk/geoprocessing` documentation, respectively.

Manage Computing Resources
==========================

Manage the computing resources of Tethys Portal using the ``Tethys Compute`` admin pages. Powered, by TethysCluster, these pages allow Tethys Portal administrators to spin up clusters of computing resources on either the Amazon or Microsoft Azure commercial clouds. These computational nodes will be made available to apps that are installed in your Tethys Portal. For more detailed information on the computing capabilities of Tethys Platform, refer to the :doc:`./tethys_sdk/cloud_computing` documentaiton.



