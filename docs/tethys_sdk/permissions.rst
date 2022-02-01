.. _permissions_api:

***************
Permissions API
***************

**Last Updated:** May 28, 2016

Permissions allow you to restrict access to certain features or content of your app. We recommend creating permissions for specific tasks or features of your app (e.g.: "Can view the map" or "Can delete projects") and then define groups of permissions to create the roles for you app.

Create Permissions and Permission Groups
========================================

Declare the ``permissions`` method in the app class and have it return a list or tuple of ``Permission`` and/or ``PermissionGroup`` objects. Permissions are synced everytime you start or restart the development server (i.e.: ``tethys manage start``) or Apache server in production.

Once you have created permissions and permission groups for your app, they will be available for the Tethys Portal administrator to assign to users. See the :ref:`tethys_portal_permissions` documentation for more details.

.. automethod:: tethys_sdk.base.TethysAppBase.permissions

Permission and Permission Group Objects
---------------------------------------

.. autoclass:: tethys_sdk.permissions.Permission

.. autoclass:: tethys_sdk.permissions.PermissionGroup

Check Permission
================

Use the ``has_permission`` method to check whether the user of the current request has a permission.

.. automethod:: tethys_sdk.permissions.has_permission

Controller Decorator
====================

Use the ``permission_required`` decorator to enforce permissions for an entire controller.

.. automethod:: tethys_sdk.permissions.permission_required



