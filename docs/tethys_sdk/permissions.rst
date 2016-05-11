***********
Permissions
***********

**Last Updated:** May 11, 2016

This section will discuss the permissions features of apps...


Create Permissions and Permission Groups
========================================

Declare the ``permissions`` method in the app class and have it return a list or tuple of ``Permission`` or ``PermissionGroup`` objects. Permissions are synced everytime you start or restart the development server (i.e.: ``tethys manage start``).

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



