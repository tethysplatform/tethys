"""
********************************************************************************
* Name: paths.py
* Author: Scott Christensen
* Created On: April 2024
* Copyright: (c) Tethys Geospatial Foundation 2024
* License: BSD 2-Clause
********************************************************************************
"""

import os
import shutil
import logging
from pathlib import Path

from django.conf import settings
from django.utils.functional import wraps
from django.http import HttpRequest
from django.utils.functional import SimpleLazyObject

from tethys_quotas.utilities import passes_quota, _get_storage_units

from .workspace import (
    get_app_workspace_old,
    get_user_workspace_old,
    _get_user_workspace,
)

log = logging.getLogger(f"tethys.{__name__}")


class TethysPath:
    """
    Defines objects that represent paths (directories) for apps and users.

    Attributes:
      path(Path): The absolute path to the workspace directory. Cannot be overwritten.
    """

    def __init__(self, path, read_only=False):
        """
        Constructor
        """
        self._path = Path(path).resolve()
        assert not self._path.is_file()
        # Create the path if it doesn't already exist
        self._path.mkdir(parents=True, exist_ok=True)

        self._read_only = read_only

    def __repr__(self):
        """
        Rendering
        """
        return '<TethysPath path="{0}">'.format(self._path)

    @property
    def path(self):
        # Note that this is different from TethysWorkspace in that it now returns a python Path object
        return self._path

    @property
    def read_only(self):
        return self._read_only

    def files(self, names_only=False):
        """
        Return a list of files (as Path objects by default) that are in the workspace.

        Args:
          names_only(bool): Returns list of filenames as strings when True. Defaults to False.

        Returns:
          list: A list of files in the workspace.

        **Examples:**

        ::

            # List file names
            workspace.files()

            # List full path file names
            workspace.files(full_path=True)

        """
        path, dirs, files = next(os.walk(self.path))
        if names_only:
            return files
        return [self.path / f for f in files]

    def directories(self, names_only=False):
        """
        Return a list of directories (as Path objects by default) that are in the workspace.

        Args:
          names_only(bool): Returns list of directory names  as strings when True. Defaults to False.

        Returns:
          list: A list of directories in the workspace.

        **Examples:**

        ::

            # List directory names
            workspace.directories()

            # List full path directory names
            workspace.directories(full_path=True)

        """
        path, dirs, files = next(os.walk(self.path))
        if names_only:
            return dirs
        return [self.path / d for d in dirs]

    def clear(self, exclude=None, exclude_files=False, exclude_directories=False):
        """
        Remove all files and directories in the workspace.

        Args:
          exclude(iterable): A list or tuple of file and directory names to exclude from clearing operation.
          exclude_files(bool): Excludes all files from clearing operation when True. Defaults to False.
          exclude_directories(bool): Excludes all directories from clearing operation when True. Defaults to False.

        **Examples:**

        ::

            # Clear everything
            workspace.clear()

            # Clear directories only
            workspace.clear(exclude_files=True)

            # Clear files only
            workspace.clear(exclude_directories=True)

            # Clear all but specified files and directories
            workspace.clear(exclude=['file1.txt', '/full/path/to/directory1', 'directory2', '/full/path/to/file2.txt'])

        """
        if self.read_only:
            raise RuntimeError("Read only TethysPaths cannot be cleared")

        if exclude is None:
            exclude = list()

        files = self.files()

        if not exclude_files:
            for file in files:
                if file not in exclude and file.name not in exclude:
                    file.unlink()

        if not exclude_directories:
            directories = self.directories()
            for directory in directories:
                if directory not in exclude and directory.name not in exclude:
                    shutil.rmtree(directory)

    def remove(self, item):
        """
        Remove a file or directory from the workspace.

        Args:
          item(str): Name of the item to remove from the workspace.

        **Examples:**

        ::

            tethys_path.remove('file.txt')
            tethys_path.remove('/full/path/to/file.txt')
            tethys_path.remove('relative/path/to/file.txt')
            tethys_path.remove('directory')
            tethys_path.remove('/full/path/to/directory')
            tethys_path.remove('relative/path/to/directory')
            tethys_path.remove(path_object)

        **Note:** Though you can specify relative paths, the ``remove()`` method will not allow you to back into other directories using "../" or similar notation. Furthermore, absolute paths given must contain the path of the tethys_path to be valid.

        """  # noqa: E501
        if self.read_only:
            raise RuntimeError("Cannot remove files from read-only TethysPaths")
        item = Path(item).resolve()

        assert item.relative_to(
            self.path
        ), f'The item to remove ({item}) must be relative to "{self.path}".'

        if item.is_dir():
            shutil.rmtree(item)
        elif item.is_file():
            item.unlink()

    def get_size(self, units="b"):
        total_size = 0
        for file in self.files():
            total_size += os.path.getsize(file)

        if units.lower() == "b":
            conversion_factor = 1
        else:
            storage_units = _get_storage_units()
            conversion_factor = [
                item[0] for item in storage_units if units.upper() in item[1]
            ][0]

        return total_size / conversion_factor


def _resolve_app_class(app_class_or_request):
    """
    Returns and app class
    """
    from tethys_apps.base.app_base import TethysAppBase
    from tethys_apps.models import TethysApp
    from tethys_apps.utilities import get_active_app, get_app_class

    # Get app
    if isinstance(app_class_or_request, TethysAppBase) or (
        isinstance(app_class_or_request, type)
        and issubclass(app_class_or_request, TethysAppBase)
    ):
        app = app_class_or_request
    elif isinstance(app_class_or_request, HttpRequest):
        app = get_active_app(app_class_or_request, get_class=True)
    elif isinstance(app_class_or_request, TethysApp):
        app = get_app_class(app_class_or_request)
    else:
        raise ValueError(
            f'Argument "app_class_or_request" must be of type TethysAppBase or HttpRequest: '
            f'"{type(app_class_or_request)}" given.'
        )

    return app


def _resolve_username(user_or_request, bypass_quota=False):
    """
    Gets the username from user or request object
    (Also check quotas?)
    """
    from django.contrib.auth.models import User

    # Get user
    if isinstance(user_or_request, User) or isinstance(
        user_or_request, SimpleLazyObject
    ):
        user = user_or_request
    elif isinstance(user_or_request, HttpRequest):
        user = user_or_request.user
    else:
        raise ValueError(
            f'Argument "user_or_request" must be of type HttpRequest or User: '
            f'"{type(user_or_request)}" given.'
        )

    if not bypass_quota:
        assert passes_quota(user, "user_workspace_quota")

    return user.username


def _get_app_workspace_root(app):
    return Path(settings.TETHYS_WORKSPACES_ROOT) / app.package


def get_app_workspace(app_or_request) -> TethysPath:
    app = _resolve_app_class(app_or_request)

    if settings.USE_OLD_WORKSPACES_API:
        return get_app_workspace_old(app)

    return TethysPath(_get_app_workspace_root(app) / "app_workspace")


def get_user_workspace(
    app_class_or_request, user_or_request, bypass_quota=False
) -> TethysPath:
    app = _resolve_app_class(app_class_or_request)
    username = _resolve_username(user_or_request, bypass_quota=bypass_quota)

    if settings.USE_OLD_WORKSPACES_API:
        if bypass_quota:
            return _get_user_workspace(app, username)
        return get_user_workspace_old(app, user_or_request)

    return TethysPath(_get_app_workspace_root(app) / "user_workspaces" / username)


def _get_app_media_root(app):
    return Path(settings.MEDIA_ROOT) / app.package


def get_app_media(app_or_request):
    """
    Gets the root media directory for an app. Uses MEDIA_ROOT setting.
    """
    app = _resolve_app_class(app_or_request)
    return TethysPath(_get_app_media_root(app) / "app_media")


def get_user_media(app_or_request, username_or_request, bypass_quota=False):
    app = _resolve_app_class(app_or_request)
    username = _resolve_username(username_or_request, bypass_quota=bypass_quota)
    return TethysPath(_get_app_media_root(app) / "user_media" / username)


def get_app_resources(app_or_request):
    """
    Gets the resources directory of an app or extension as a read-only TethysPath
    """
    app = _resolve_app_class(app_or_request)
    return app.resources_path


def get_app_public(app_or_request):
    """
    Gets the public directory of an app or extension as a read-only TethysPath
    """
    app = _resolve_app_class(app_or_request)
    return app.public_path


def _add_path_decorator(argument_name):
    """Creates a decorator that adds the TethysPath for `argument_name`.

    Args:
        argument_name (str): The name of the argument to add to the controller that represents a TethysPath.
            Must be one of (app_workspace, user_workspace, app_media, user_media, app_public, app_resources).

    Returns: A decorator for a controller function.

    """

    def decorator(controller):
        @wraps(controller)
        def wrapper(*args, **kwargs):
            request = None
            for _, arg in enumerate(args):
                if isinstance(arg, HttpRequest):
                    request = arg
                    break

            if request is None:
                raise ValueError(
                    f"No request given. The {argument_name} decorator only works on controllers."
                )

            func_args = [request]
            if "user" in argument_name:
                func_args.append(request.user)

            func = globals()[f"get_{argument_name}"]
            the_path = func(*func_args)

            return controller(*args, **{argument_name: the_path}, **kwargs)

        return wrapper

    return decorator


def app_workspace(controller):
    """
    **Decorator:** Get the app resources directory for the app. Add an argument named "app_workspace" to your controller. The TethysPath object representing the app workspace directory will be passed to via this argument.

    Args:
        controller (callable): A controller function to add the TethysPath to.

    Returns: A decorated controller function.

    **Example:**

    ::
        from .app import App
        from tethys_sdk.paths import app_workspace

        @app_workspace
        def a_controller(request, app_workspace):
            \"""
            Example controller that uses @app_workspace() decorator.
            \"""
            new_file_path = app_workspace.path / 'new_file.txt'

            with new_file_path.open('w') as a_file:
                a_file.write('...')

            context = {}

            return App.render(request, 'template.html', context)

    """  # noqa:E501
    argument_name = app_workspace.__name__
    return _add_path_decorator(argument_name)(controller)


def user_workspace(controller):
    """
    **Decorator:** Get the app resources directory for the app. Add an argument named "user_workspace" to your controller. The TethysPath object representing the user workspace directory will be passed to via this argument.

    Args:
        controller (callable): A controller function to add the TethysPath to.

    Returns: A decorated controller function.

    **Example:**

    ::
        from .app import App
        from tethys_sdk.paths import user_workspace

        @user_workspace
        def a_controller(request, user_workspace):
            \"""
            Example controller that uses @user_workspace() decorator.
            \"""
            new_file_path = user_workspace.path / 'new_file.txt'

            with new_file_path.open('w') as a_file:
                a_file.write('...')

            context = {}

            return App.render(request, 'template.html', context)

    """  # noqa:E501
    argument_name = user_workspace.__name__
    return _add_path_decorator(argument_name)(controller)


def app_media(controller):
    """
    **Decorator:** Get the app resources directory for the app. Add an argument named "app_media" to your controller. The TethysPath object representing the app media directory will be passed to via this argument.

    Args:
        controller (callable): A controller function to add the TethysPath to.

    Returns: A decorated controller function.

    **Example:**

    ::
        from .app import App
        from tethys_sdk.paths import app_media

        @app_media
        def a_controller(request, app_media):
            \"""
            Example controller that uses @app_media() decorator.
            \"""
            new_file_path = app_media.path / 'new_file.txt'

            with new_file_path.open('w') as a_file:
                a_file.write('...')

            context = {}

            return App.render(request, 'template.html', context)

    """  # noqa:E501
    argument_name = app_media.__name__
    return _add_path_decorator(argument_name)(controller)


def user_media(controller):
    """
    **Decorator:** Get the app resources directory for the app. Add an argument named "user_media" to your controller. The TethysPath object representing the user media directory will be passed to via this argument.

    Args:
        controller (callable): A controller function to add the TethysPath to.

    Returns: A decorated controller function.

    **Example:**

    ::
        from .app import App
        from tethys_sdk.paths import user_media

        @user_media
        def a_controller(request, user_media):
            \"""
            Example controller that uses @user_media() decorator.
            \"""
            new_file_path = user_media.path / 'new_file.txt'

            with new_file_path.open('w') as a_file:
                a_file.write('...')

            context = {}

            return App.render(request, 'template.html', context)

    """  # noqa:E501
    argument_name = user_media.__name__
    return _add_path_decorator(argument_name)(controller)


def app_public(controller):
    """
    **Decorator:** Get the app resources directory for the app. Add an argument named "app_public" to your controller. The TethysPath object representing the app public directory will be passed to via this argument.

    Args:
        controller (callable): A controller function to add the TethysPath to.

    Returns: A decorated controller function.

    **Example:**

    ::
        from .app import App
        from tethys_sdk.paths import app_public

        @app_public
        def a_controller(request, app_public):
            \"""
            Example controller that uses @app_public() decorator.
            \"""
            static_file_path = app_public.path / 'static_file.css'

            context = {}

            return App.render(request, 'template.html', context)

    """  # noqa:E501
    argument_name = app_public.__name__
    return _add_path_decorator(argument_name)(controller)


def app_resources(controller):
    """
    **Decorator:** Get the app resources directory for the app. Add an argument named "app_resources" to your controller. The TethysPath object representing the app resources directory will be passed to via this argument.

    Args:
        controller (callable): A controller function to add the TethysPath to.

    Returns: A decorated controller function.

    **Example:**

    ::
        from .app import App
        from tethys_sdk.paths import app_resources

        @app_resources
        def a_controller(request, app_resources):
            \"""
            Example controller that uses @app_resources() decorator.
            \"""
            new_file_path = app_resources.path / 'new_file.txt'

            with new_file_path.open('w') as a_file:
                a_file.write('...')

            context = {}

            return App.render(request, 'template.html', context)

    """  # noqa:E501
    argument_name = app_resources.__name__
    return _add_path_decorator(argument_name)(controller)
