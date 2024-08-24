.. _tethys_workspaces_api:

***************************
Workspaces API (DEPRECATED)
***************************

**Last Updated:** May 2024

.. warning::

    The Workspaces API has been replaced by the Paths API and is now deprecated. It will be removed in Tethys v5.0. Please see :ref:`tethys_paths_api` to start using the Paths API.

.. _transition_to_paths_guide:

Guide to transitioning to the Paths API
=======================================

Use the following guide to transition apps that have been using the Workspaces API to use the new Paths API.

In Tethys v4.3 a temporary setting (``USE_OLD_WORKSPACES_API``) was introduces to ensure that apps will not break with the introduction of the Paths API. To begin using the Paths API set the value of ``USE_OLD_WORKSPACES_API`` to ``False``.

    .. code-block:: shell

        tethys settings -s USE_OLD_WORKSPACES_API False

The primary difference with transitioning to the Paths API is that rather than returning ``TethysWorkspace`` objects Paths API calls will return a ``TethysPath`` object. The ``TethysPath`` object has the same interface as the ``TethysWorkspace`` with the exception that it will return Python ``pathlib.Path`` objects to represent files and directories rather than strings. For example when using the Workspaces API you might do something along these lines:

.. code-block:: python

    import os
    ...

    @controller(
        app_workspace=True
    )
    def my_controller(request, app_workspace):
        my_path = os.path.join(app_workspace.path, 'my_dir')
        ...

When using the Paths API it would look something like this:

.. code-block:: python

    ...

    @controller(
        app_workspace=True
    )
    def my_controller(request, app_workspace):
        my_path = app_workspace.path / 'my_dir'
        ...

.. note:: if you are unfamiliar with Python's ``pathlib`` module then see the `pathlib documentation <https://docs.python.org/3/library/pathlib.html>`_

If you are using workspaces with the :ref:`handler-decorator` then note that the ``with_workspaces`` argument should be replaced with ``with_paths``:

.. code-block:: python

    from tethys_sdk.routing import handler

    @handler(
        with_paths=True
    )
    def my_handler(doc):
        my_dir = doc.app_workspace.path / 'my_dir'

Functions and decorators that were imported from ``tethys_sdk.workspaces`` should now be imported from ``tethys_sdk.paths``.

.. code-block:: python

    from tethys_sdk.paths import (
        get_app_workspace,
        get_user_workspace,
        app_workspace,
        user_workspace,
    )

Note that the Paths API has additional functions and decorators. For more information the :ref:`tethys_paths_api` documentation.


Workspaces Overview
===================

The Workspaces API makes it easy for you to create directories for storing files that your app operates on. This can be a tricky task for a web application, because of the multi-user, simultaneous-connection environment of the web. The Workspaces API provides a simple mechanism for creating and managing a global workspace for your app and individual workspaces for each user of your app to prevent unwanted overwrites and file lock conflicts.

Getting Workspaces
==================

There are four methods for obtaining the workspaces that are supported in Tethys Platform. In order of recommended use, the workspace methods are:

* Controller Decorator
* Workspaces Decorators
* App Class Methods
* Workspace Functions

Controller Decorator
--------------------

The recommended method for obtaining workspaces in controllers is to use the ``app_workspace`` and ``user_workspace`` arguments of the ``controller`` decorator:

.. code-block:: python

    from tethys_sdk.routing import controller

    @controller(app_workspace=True)
    def my_controller(request, app_workspace):
       ...

    @controller(user_workspace=True)
    def my_controller(request, user_workspace):
       ...

    @controller(app_workspace=True, user_workspace=True)
    def my_controller(request, app_workspace, user_workspace):
       ...

To learn more about the ``controller`` decorator, see: :ref:`controller-decorator`

Workspace Decorators
--------------------

The Workspaces API includes two decorators, that can be used to retrieve the app workspace and the user workspaces, respectively. To use these decorators, import them from ``tethys_sdk.workspaces``. Explanations of the decorators and example usage follows.

.. _workspace_app_workspace:

@app_workspace
++++++++++++++

.. automethod:: tethys_apps.base.workspace.app_workspace

.. _workspace_user_workspace:

@user_workspace
+++++++++++++++

.. automethod:: tethys_apps.base.workspace.user_workspace

App Class Methods
-----------------

In cases where it is not possible to use one of the decorators, the :term:`app class` provides methods for getting the workspaces:

.. code-block:: python

    from .app import App
    from django.contrib.auth.models import User

    user = User.objects.get(id=1)
    app_workspace = App.get_app_workspace()
    user_workspace = App.get_user_workspace(user)
    ...

For more details see :ref:`app_base_class_api`

Workspace Functions
-------------------

In the rare cases where you need to use a workspace where it is not convenient or not possible to use one of the decorators OR the :term:`app class` methods, the Workspaces API provides function versions of the getters. Import them from ``tethys_sdk.workspaces``:

.. _workspace_get_app_workspace_func:

.. automethod:: tethys_apps.base.paths.get_app_workspace
    :no-index:

.. _workspace_get_user_workspace_func:

.. automethod:: tethys_apps.base.paths.get_user_workspace
    :no-index:


Working with Workspaces
=======================

All of the methods described above return a ``TethysWorkspace`` object that contains the path to the workspace and several convenience methods for working with the workspace directory. An explanation of the ``TethysWorkspace`` object and examples of it's usage are provided below.

TethysWorkspace Objects
-----------------------

.. autoclass:: tethys_apps.base.TethysWorkspace
    :members: files, directories, remove, clear

Centralize Workspaces
=====================

The Workspaces API provides a :ref:`tethys_cli` command, ``collectworkspaces``, for moving all workspaces to a central location and symbolically linking them back to the app project directories. This command is intended for use in production installations where the administrator may want to locate workspace content on a mounted drive to optimize storage and make it easier to backup app data. A brief explanation of how to use this command will follow. Refer to the :ref:`tethys_cli` documentation for details about the ``collectworkspaces`` command.

Setting
-------

To enable centralized workspaces create a directory for the workspaces and specify its path in the :file:`portal_config.yml` file using the ``TETHYS_WORKSPACES_ROOT`` setting.

::

    TETHYS_WORKSPACES_ROOT: /var/www/tethys/workspaces

Command
-------

Run the ``collectworkspaces`` command to automatically move all of the workspace directories to the ``TETHYS_WORKSPACES_ROOT`` directory and symbolically link them back. You will need to run this command each time you install new apps.

::

    tethys manage collectworkspaces

.. tip::

    A convenience command is provided called ``collectall`` that can be used to run both the ``collectstatic`` and the ``collectworkspaces`` commands:

    ::

        tethys manage collectall

.. _workspace_tethys_quotas_workspace_manage:

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
