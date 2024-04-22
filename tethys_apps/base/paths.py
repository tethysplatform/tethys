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

from .workspace import get_app_workspace_old, get_user_workspace_old

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

            workspace.remove('file.txt')
            workspace.remove('/full/path/to/file.txt')
            workspace.remove('relative/path/to/file.txt')
            workspace.remove('directory')
            workspace.remove('/full/path/to/directory')
            workspace.remove('relative/path/to/directory')
            workspace.remove(path_object)

        **Note:** Though you can specify relative paths, the ``remove()`` method will not allow you to back into other directories using "../" or similar notation. Futhermore, absolute paths given must contain the path of the workspace to be valid.

        """  # noqa: E501
        if self.read_only:
            raise RuntimeError("Cannot remove files from read-only TethysPaths")
        item = Path(item).resolve()

        assert item.relative_to(
            self.path
        )  # TODO add an if statement with a helpful error message

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


def _resolve_username(user_or_request):
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

    # TODO Need to add the user_media usage into the user_workspace_quota
    assert passes_quota(user, "user_workspace_quota")

    return user.username


def _get_app_workspace_root(app):
    return Path(settings.TETHYS_WORKSPACES_ROOT) / app.package


def get_app_workspace(app_or_request) -> TethysPath:
    app = _resolve_app_class(app_or_request)

    if settings.USE_OLD_WORKSPACES_API:
        return get_app_workspace_old(app)

    return TethysPath(_get_app_workspace_root(app) / "app_workspace")


def get_user_workspace(app_class_or_request, user_or_request) -> TethysPath:
    app = _resolve_app_class(app_class_or_request)
    username = _resolve_username(user_or_request)

    if settings.USE_OLD_WORKSPACES_API:
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


def get_user_media(app_or_request, username_or_request):
    app = _resolve_app_class(app_or_request)
    username = _resolve_username(username_or_request)
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


def _add_path_decorator(func, argument_name, pass_user=False):
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
                    "No request given. The adding paths only works on controllers."
                )

            args = [request]
            if pass_user:
                args.append(request.user)
            the_path = func(*args)

            return controller(*args, **{argument_name, the_path}, **kwargs)

        return wrapper

    return decorator
