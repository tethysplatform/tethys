*************
Tethys Portal
*************

**Last Updated:** February 6, 2015

Tethys Portal is the is the web site provided by Tethys Platform that you use to host and access Tethys apps. In development the Tethys Portal includes the Developer Tools page and provides debugging information. In an app-hosting or production mode, Tethys Portal is used to manage users and can be customized to reflect your organization.

The following article provides an overview of the features of Tethys Portal.

Administrator
=============

Tethys Portal provides a set of administration pages that can be used to manage the website (see Figure 1). The administration dashboard is only available to administrator users. You should have created a default administrator user when you installed Tethys Platform. If you are logged in as an administrator, you will be able to access the administrator dashboard by selecting the "Site Admin" option from the user drop down menu in the top right-hand corner of the page.

.. figure:: images/site_admin/home.png
    :width: 650px

    **Figure 1.** Administrator dashboard for Tethys Portal.

.. note::

    If you did not create an administrator user during installation, run the following command in the terminal:

    ::

        $ python /usr/lib/tethys/src/manage.py createsuperuser



Customize
=========

The content of Tethys Portal can be customized or rebranded to reflect your organization. To access these settings, login to Tethys Portal using an administrator account and select the  ``Site Settings`` link under the ``Tethys Portal`` heading. Sitewide settings can be changed by following the ``General Settings`` link and the content on the home page can be modified by following the ``Home Page`` link. Figure 2 shows a screenshot of the general settings available.

.. figure:: images/tethys_portal/tethys_portal_general_settings.png
    :width: 650px

    **Figure 2.** General settings for Tethys Portal.

The general settings that are available include the following:

* Site Title
* Favicon
* Brand Text
* Brand Image
* Primary Color
* Secondary Color
* Footer Copyright

Figure 3 shows a screenshot of the home page settings that are available.

.. figure:: images/tethys_portal/tethys_portal_home_page_settings.png
    :width: 650px

    **Figure 3.** Home page settings for Tethys Portal.

The settings that can be modified on the home page include:

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

Manage Users and Permissions
============================

Permissions and users can be managed from the administrator dashboard using the ``Groups`` and ``Users`` links under the Authentication and Authorization heading. Figure 4 shows an example of the user management page for a user named John. Permissions can be assigned to each user individually or users can be assigned to groups and they will be given the permissions of that group.

.. figure:: images/tethys_portal/tethys_portal_user_management.png
    :width: 650px

    **Figure 4.** User management for Tethys Portal.