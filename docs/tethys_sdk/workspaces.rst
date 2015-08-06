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

Centralize Workspaces
=====================

The Workspaces API includes a command, ``collectworkspaces``, for moving all workspaces to a central location and symbolically linking them back to the app project directories. This is especially useful for production where the administrator may want to locate workspace content on a mounted drive to optimize storage. A brief explanation of how to use this command will follow. Refer to the :doc:`./tethys_cli` documentation for details about the ``collectworkspaces`` command.

Setting
-------

To enable centralized workspaces create a directory for the workspaces and specify its path in the ``settings.py`` file using the ``TETHYS_WORKSPACES_ROOT`` setting.

::

    TETHYS_WORKSPACES_ROOT = '/var/www/tethys/workspaces'

Command
-------

Run the ``collectworkspaces`` command to automatically move all of the workspace directories to the ``TETHYS_WORKSPACES_ROOT`` directory and symbolically link them back. You will need to run this command each time you install new apps.

::

    $ tethys manage collectworkspaces

.. tip::

    A convenience command is provided called ``collectall`` that can be used to run both the ``collectstatic`` and the ``collectworkspaces`` commands:

    ::

        $ tethys manage collectall