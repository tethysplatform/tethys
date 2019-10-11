**************
Workspaces API
**************

**Last Updated:** August 6, 2014

The Workspaces API makes it easy for you to create directories for storing files that your app operates on. This can be a tricky task for a web application, because of the multi-user, simultaneous-connection environment of the web. The Workspaces API provides a simple mechanism for creating and managing a global workspace for your app and individual workspaces for each user of your app to prevent unwanted overwrites and file lock conflicts.

Get a Workspace
===============

The Workspaces API adds two decorators, that can be used to retrieve with the global app workspace and the user workspaces, respectively. To use the Workspace API methods, import the appropriate method from `tethys_sdk.workspaces`. Explanations of the decorators and example usage follows.

.. _app_workspace:

@app_workspace
-----------------

.. automethod:: tethys_apps.base.workspace.app_workspace

.. _user_workspace:

@user_workspace
------------------

.. automethod:: tethys_apps.base.workspace.user_workspace


Working with Workspaces
=======================

The two methods described above return a ``TethysWorkspace`` object that contains the path to the workspace and several convenience methods for working with the workspace. An explanation of the ``TethysWorkspace`` object and examples of it's usage is provided below.

TethysWorkspace Objects
-----------------------

.. autoclass:: tethys_apps.base.TethysWorkspace
    :members: files, directories, remove, clear

Centralize Workspaces
=====================

The Workspaces API includes a command, ``collectworkspaces``, for moving all workspaces to a central location and symbolically linking them back to the app project directories. This is especially useful for production where the administrator may want to locate workspace content on a mounted drive to optimize storage. A brief explanation of how to use this command will follow. Refer to the :doc:`../tethys_cli` documentation for details about the ``collectworkspaces`` command.

Setting
-------

To enable centralized workspaces create a directory for the workspaces and specify its path in the :file:`portal_config.yml` file using the ``TETHYS_WORKSPACES_ROOT`` setting.

::

    TETHYS_WORKSPACES_ROOT: /var/www/tethys/workspaces

Command
-------

Run the ``collectworkspaces`` command to automatically move all of the workspace directories to the ``TETHYS_WORKSPACES_ROOT`` directory and symbolically link them back. You will need to run this command each time you install new apps.

::

    $ tethys manage collectworkspaces

.. tip::

    A convenience command is provided called ``collectall`` that can be used to run both the ``collectstatic`` and the ``collectworkspaces`` commands:

    ::

        $ tethys manage collectall

.. _tethys_quotas_workspace_manage:

Handling Workspace Clearing
===========================

Users and portal administrators are able to clear their user and app workspaces through pages in the Tethys Portal. The app class provides methods to allow the app developer to customize how the app handles clearing user/app workspaces. Override these methods in your app class to handle workspaces clearing appropriately in your app. When a workspace is cleared through the portal admin pages or user profile pages, the appropriate 'pre-delete' method is called, the workspace is cleared, and then the appropriate 'post-delete' method is called.

.. automethod:: tethys_apps.base.app_base.TethysAppBase.pre_delete_app_workspace
    :noindex:

.. automethod:: tethys_apps.base.app_base.TethysAppBase.post_delete_app_workspace
    :noindex:

.. automethod:: tethys_apps.base.app_base.TethysAppBase.pre_delete_user_workspace
    :noindex:

.. automethod:: tethys_apps.base.app_base.TethysAppBase.post_delete_user_workspace
    :noindex:
