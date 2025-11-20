.. _tethys_paths_api:

*********
Paths API
*********

**Last Updated:** September 2024

.. tip::

    If you are transitioning from using the Workspaces API then refer to the :ref:`transition_to_paths_guide`.


The Paths API makes it easy for you to retrieve the proper directories for accessing resource files in your app or writing files at runtime. This can be a tricky task for a web application, because of the multi-user, simultaneous-connection environment of the web. The Paths API provides a simple mechanism for creating and managing global, writable directories for your app and individual directories for each user of your app to prevent unwanted overwrites and file lock conflicts. It also provides a simple way to retrieve read-only file resources that are version controlled with the app source code.

Path Types
==========

The Paths API provides access to the following types of Paths:

Read/Write
----------

* **App Workspace**: A location were the app can write files at runtime
* **App Media**: A location were the app can store uploaded (publicly accessible) information
* **User Workspace**: A location were the app can write user files at runtime
* **User Media**: A location were the app can store user uploaded (publicly accessible) information

Read-Only
---------

* **App Public**: The location of the app's public directory (i.e. were static files like css and JavaScrip are stored)
* **App Resources**: The location where version-controlled app resource files (e.g. configuration files) are stored


Getting Paths
=============

There are several methods for obtaining the paths that are supported in Tethys Platform as follows:

* `Routing Decorators`_
    * `Controller Decorator`_
    * `Consumer Decorator`_
    * `Handler Decorator`_
* `App Class Methods and Properties`_
* `Path Functions`_

Routing Decorators
------------------

The Tethys paths can easily be accessed in controllers, consumers, and handlers by specifying arguments to the various routing decorators. The arguments for each routing decorator is described below:

Controller Decorator
++++++++++++++++++++

The method for obtaining Tethys paths in controllers is to use the following arguments in ``controller`` decorator:

* ``app_workspace``
* ``user_workspace``
* ``app_media``
* ``user_media``
* ``app_public``
* ``app_resources``

When you specify the argument in the ``controller`` decorator you must also specify the argument in the controller function itself as this is how the path will be passed to the controller function:

.. code-block:: python

    from tethys_sdk.routing import controller

    @controller(app_workspace=True)
    def my_controller(request, app_workspace):
       ...

    @controller(user_workspace=True)
    def my_controller(request, user_workspace):
       ...

    @controller(app_media=True)
    def my_controller(request, app_media):
       ...

    @controller(user_media=True)
    def my_controller(request, user_media):
       ...

    @controller(app_public=True)
    def my_controller(request, app_public):
       ...

    @controller(app_resources=True)
    def my_controller(request, app_resources):
       ...

    @controller(
        app_workspace=True,
        user_workspace=True,
        app_media=True,
        user_media=True,
        app_public=True,
        app_resources=True,
    )
    def my_controller(request, app_workspace, user_workspace, app_media, user_media, app_public, app_resources):
       ...

Note that the argument name in the controller function must match the argument to the ``controller`` decorator since the paths are passed to the controller function as key-word arguments.

To learn more about the ``controller`` decorator, see: :ref:`controller-decorator`

Consumer Decorator
++++++++++++++++++

To access Tethys paths in consumers, the ``with_paths`` argument to the ``consumer`` decorator should be set to ``True``. The paths will then be accessible as attributes on the class object.

.. code-block:: python

    from channels.generic.websocket import AsyncWebsocketConsumer
    from tethys_sdk.routing import consumer

    @consumer(
        with_paths=True,
        login_required=True,
    )
    class MyConsumer(AsyncWebsocketConsumer):

        async def authorized_connect(self):
            self.app_workspace
            self.user_workspace
            self.app_media
            self.user_media
            self.app_public
            self.app_resources

Handler Decorator
+++++++++++++++++

To access Tethys paths in handlers, the ``with_paths`` argument to the ``handler`` decorator should be set to ``True``. The paths will then be accessible on the ``document`` object that is passed to the handler.

.. code-block:: python

    from tethys_sdk.routing import handler

    @handler(
        with_paths=True
    )
    def my_app_handler(document):
        # attributes available when using "with_paths" argument
        request = document.request
        user_workspace = document.user_workspace
        user_media = document.user_media
        app_workspace = document.app_workspace
        app_media = document.app_media
        app_public = document.app_public
        app_resources = document.app_resources
        ...


App Class Methods and Properties
--------------------------------

In some cases, it may be necessary (or more convenient) to use the :term:`app class` to access the Tethys paths:

.. code-block:: python

    from .app import App
    from django.contrib.auth.models import User

    user = User.objects.get(id=1)
    app_workspace = App.get_app_workspace()
    user_workspace = App.get_user_workspace(user)
    app_media = App.get_app_media()
    user_media = App.get_user_media(user)
    app_public = App().public_path
    app_resources App().resources_path
    ...

.. note::

    While the workspace and media directories are accessed through methods on the app class, ``public_path`` and ``resources_path`` are properties of the ``App`` class.

For more details see :ref:`app_base_class_api`


Path Functions
--------------

In the rare cases where you need to use a Tethys path where it is not convenient or not possible to use one of the decorators OR the :term:`app class` methods, the Paths API provides function versions of the getters. Import them from ``tethys_sdk.paths``:

.. _get_app_workspace_func:

.. automethod:: tethys_apps.base.paths.get_app_workspace

.. _get_user_workspace_func:

.. automethod:: tethys_apps.base.paths.get_user_workspace

.. _get_app_media_func:

.. automethod:: tethys_apps.base.paths.get_app_media

.. _get_user_media_func:

.. automethod:: tethys_apps.base.paths.get_user_media

.. _get_app_public_func:

.. automethod:: tethys_apps.base.paths.get_app_public

.. _get_app_resources_func:

.. automethod:: tethys_apps.base.paths.get_app_resources


Working with Tethys Paths
=========================

All of the methods described above return a ``TethysPath`` object that contains the location to the Tethys path and several convenience methods for working with the Tethys path directory. An explanation of the ``TethysPath`` object and examples of its usage are provided below.

TethysPath Objects
------------------

.. autoclass:: tethys_apps.base.TethysPath
    :members: files, directories, remove, clear

Centralized Paths
=================

For the ``workspace`` and ``media`` paths the location of the paths from all apps is centralized based on the ``TETHYS_WORKSPACES_ROOT`` and ``MEDIA_ROOT`` settings. By default these paths will be in the ``TETHYS_HOME`` directory, but they can be specified in the :file:`portal_config.yml` file.

.. code-block:: yaml

    TETHYS_WORKSPACES_ROOT: /var/www/tethys/workspaces
    MEDIA_ROOT: /var/www/tethys/media

.. note::

    The ``public`` and the ``resources`` directories are relative to the source code of the app (i.e. not centralized). Even when the ``collectstatic`` command is used to copy all static files to a central location the :ref:`tethys_paths_api` will return the the public directory that is relative to the app source code.

.. _tethys_paths_cli:

Command Line Interface
==========================
The Paths API can be accessed through the command line interface (CLI) using the ``paths`` command. This command provides a way to list paths for specific apps or users and add files to those destinations.

Examples
--------

**Command:**

.. code-block:: bash

    tethys paths get -t app_workspace -a my_app

**Output:**

.. code-block:: console

    App Workspace for app 'my_app':
    /home/user/.tethys/tethys/workspaces/my_app/app_workspace

**Command:**

.. code-block:: bash

    tethys paths get -t user_workspace -a my_app -u my_user

**Output:**

.. code-block:: console

    User Workspace for user 'my_user' and app 'my_app':
    /home/user/.tethys/tethys/workspaces/my_app/user_workspaces/my_user

**Command:**

.. code-block:: bash

    tethys paths add -t user_media -a my_app -u my_user -f /path/to/file.txt

**Output:**

.. code-block:: console

    File 'file.txt' has been added to the User Media at '/home/user/.tethys/tethys/media/my_app/user/my_user/file.txt'

**Command:**

.. code-block:: bash

    tethys paths add -t app_media -a my_app -f /path/to/file.txt

**Output:**

.. code-block:: console

    File 'file.txt' has been added to the App Media at '/home/user/.tethys/tethys/media/my_app/app/file.txt'`

.. _tethys_quotas_workspace_manage:

Handling Workspace/Media Clearing
=================================

Users and portal administrators are able to clear their user and app workspaces through pages in the Tethys Portal. The app class provides methods to allow the app developer to customize how the app handles clearing user/app workspaces and media directories. Override these methods in your app class to handle clearing workspaces and media directories appropriately in your app. When a workspace/media directory is cleared through the portal admin pages or user profile pages, the appropriate 'pre-delete' method is called, the workspace or media directory is cleared, and then the appropriate 'post-delete' method is called.

.. automethod:: tethys_sdk.base.TethysAppBase.pre_delete_app_workspace
    :noindex:

.. automethod:: tethys_sdk.base.TethysAppBase.post_delete_app_workspace
    :noindex:

.. automethod:: tethys_sdk.base.TethysAppBase.pre_delete_user_workspace
    :noindex:

.. automethod:: tethys_sdk.base.TethysAppBase.post_delete_user_workspace
    :noindex:

.. automethod:: tethys_sdk.base.TethysAppBase.pre_delete_app_media
    :noindex:

.. automethod:: tethys_sdk.base.TethysAppBase.post_delete_app_media
    :noindex:

.. automethod:: tethys_sdk.base.TethysAppBase.pre_delete_user_media
    :noindex:

.. automethod:: tethys_sdk.base.TethysAppBase.post_delete_user_media
    :noindex:
