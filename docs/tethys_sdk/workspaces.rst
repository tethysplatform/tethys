**************
Workspaces API
**************

**Last Updated:** August 6, 2014

The Workspaces API makes it easy for you to create directories for storing files that your app operates on. This can be a tricky task for a web application, because of the multi-user, simultaneous-connection environment of the web. The Workspaces API provides a simple mechanism for creating and managing a global workspace for your app and individual workspaces for each user of your app to prevent unwanted overwrites and file lock conflicts.

Get a Workspace
===============

The Workspaces API adds two methods to your :term:`app class`, ``get_app_workspace()`` and ``get_user_workspace()``, that can be used to retrieve with the global app workspace and the user workspaces, respectively. To use the Workspace API methods, import your :term:`app class` from the :term:`app configuration file` (:file:`app.py`) and call the appropriate method on that class. Explanations of the methods and example usage follows.

get_app_workspace
-----------------

.. automethod:: tethys_apps.base.TethysAppBase.get_app_workspace

get_user_workspace
------------------

.. automethod:: tethys_apps.base.TethysAppBase.get_user_workspace


Working with Workspaces
=======================

The two methods described above return a ``TethysWorkspace`` object that contains the path to the workspace and several convenience methods for working with the workspace. An explanation of the ``TethysWorkspace`` object and examples of it's usage is provided below.

TethysWorkspace Objects
-----------------------

.. autoclass:: tethys_apps.base.TethysWorkspace
    :members: files, directories, remove, clear
