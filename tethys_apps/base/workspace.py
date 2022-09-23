"""
********************************************************************************
* Name: workspace.py
* Author: Nathan Swain & Scott Christensen
* Created On: August 5, 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""

import os
import sys
import shutil
import logging
from django.utils.functional import wraps
from django.http import HttpRequest
from django.utils.functional import SimpleLazyObject

from tethys_quotas.utilities import passes_quota, _get_storage_units

log = logging.getLogger('tethys.' + __name__)


class TethysWorkspace:
    """
    Defines objects that represent file workspaces (directories) for apps and users.

    Attributes:
      path(str): The absolute path to the workspace directory. Cannot be overwritten.
    """

    def __init__(self, path):
        """
        Constructor
        """
        # Create the path if it doesn't already exist
        if not os.path.exists(path):
            os.makedirs(path)

        # Validate that the path is a directory
        self._path = path

    def __repr__(self):
        """
        Rendering
        """
        return '<TethysWorkspace path="{0}">'.format(self._path)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        """
        Don't allow overwriting the path property.
        """
        pass

    def files(self, full_path=False):
        """
        Return a list of files that are in the workspace.

        Args:
          full_path(bool): Returns list of files with full path names when True. Defaults to False.

        Returns:
          list: A list of files in the workspace.

        **Examples:**

        ::

            # List file names
            workspace.files()

            # List full path file names
            workspace.files(full_path=True)

        """
        if full_path:
            files = [os.path.join(self._path, f) for f in os.listdir(self._path) if
                     os.path.isfile(os.path.join(self._path, f))]
        else:
            files = [f for f in os.listdir(self._path) if os.path.isfile(os.path.join(self._path, f))]
        return files

    def directories(self, full_path=False):
        """
        Return a list of directories that are in the workspace.

        Args:
          full_path(bool): Returns list of directories with full path names when True. Defaults to False.

        Returns:
          list: A list of directories in the workspace.

        **Examples:**

        ::

            # List directory names
            workspace.directories()

            # List full path directory names
            workspace.directories(full_path=True)

        """
        if full_path:
            directories = [os.path.join(self._path, d) for d in os.listdir(self._path) if
                           os.path.isdir(os.path.join(self._path, d))]
        else:
            directories = [d for d in os.listdir(self._path) if os.path.isdir(os.path.join(self._path, d))]
        return directories

    def clear(self, exclude=[], exclude_files=False, exclude_directories=False):
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
        files = [f for f in os.listdir(self._path) if os.path.isfile(os.path.join(self._path, f))]
        directories = [d for d in os.listdir(self._path) if os.path.isdir(os.path.join(self._path, d))]

        if not exclude_files:
            for file in files:
                fullpath = os.path.join(self._path, file)
                if file not in exclude and fullpath not in exclude:
                    os.remove(fullpath)

        if not exclude_directories:
            for directory in directories:
                fullpath = os.path.join(self._path, directory)
                if directory not in exclude and fullpath not in exclude:
                    shutil.rmtree(fullpath)

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

        **Note:** Though you can specify relative paths, the ``remove()`` method will not allow you to back into other directories using "../" or similar notation. Futhermore, absolute paths given must contain the path of the workspace to be valid.

        """  # noqa: E501
        # Sanitize to prevent backing into other directories or entering the home directory
        full_path = item.replace('../', '').replace('./', '').replace('..\\', '').\
            replace('.\\', '').replace('~/', '').replace('~\\', '')

        if self._path not in full_path:
            full_path = os.path.join(self._path, full_path)

        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        elif os.path.isfile(full_path):
            os.remove(full_path)

    def get_size(self, units='b'):
        total_size = 0
        for file in self.files(True):
            total_size += os.path.getsize(file)

        if units.lower() == 'b':
            conversion_factor = 1
        else:
            storage_units = _get_storage_units()
            conversion_factor = [item[0] for item in storage_units if units.upper() in item[1]][0]

        return total_size / conversion_factor


def _get_user_workspace(app_class, user_or_request):
    """
    Get the file workspace (directory) for the given User.

    Args:
      app_class(TethysApp): tethys app
      user_or_request(User or HttpRequest): User or request object.

    Returns:
      tethys_apps.base.TethysWorkspace: An object representing the workspace.
    """
    username = ''

    from django.contrib.auth.models import User
    if isinstance(user_or_request, User) or isinstance(user_or_request, SimpleLazyObject):
        username = user_or_request.username
    elif isinstance(user_or_request, HttpRequest):
        username = user_or_request.user.username
    elif user_or_request is None:
        username = 'anonymous_user'
    else:
        raise ValueError("Invalid type for argument 'user': must be either an User or HttpRequest object.")

    project_directory = os.path.dirname(sys.modules[app_class.__module__].__file__)
    workspace_directory = os.path.join(project_directory, 'workspaces', 'user_workspaces', username)
    return TethysWorkspace(workspace_directory)


def get_user_workspace(app_class_or_request, user_or_request) -> TethysWorkspace:
    """
    Get the dedicated user workspace for the given app. If an HttpRequest is given, the workspace of the logged-in user will be returned (i.e. request.user).

    Args:
        app_class_or_request (TethysAppBase or HttpRequest): The Tethys app class that is defined in app.py or HttpRequest to app endpoint.
        user_or_request (User or HttpRequest): Either an HttpRequest with active user session or Django User object.

    Raises:
        ValueError: if app_class_or_request or user_or_request are not correct types.
        AssertionError: if quota for the user workspace has been exceeded.

    Returns:
        TethysWorkspace: workspace object bound to the user's workspace directory.

    ::

        import os
        from tethys_sdk.workspaces import get_user_workspace
        from .app import MyFirstApp as app

        def some_function(user):
            user_workspace = get_user_workspace(app, user)
            ...
    """  # noqa: E501
    from tethys_apps.base.app_base import TethysAppBase
    from tethys_apps.utilities import get_active_app
    from django.contrib.auth.models import User

    # Get app
    if isinstance(app_class_or_request, TethysAppBase) or \
       (isinstance(app_class_or_request, type) and issubclass(app_class_or_request, TethysAppBase)):
        app = app_class_or_request
    elif isinstance(app_class_or_request, HttpRequest):
        app = get_active_app(app_class_or_request, get_class=True)
    else:
        raise ValueError(f'Argument "app_class_or_request" must be of type TethysAppBase or HttpRequest: '
                         f'"{type(app_class_or_request)}" given.')

    # Get user
    if isinstance(user_or_request, User) or isinstance(user_or_request, SimpleLazyObject):
        user = user_or_request
    elif isinstance(user_or_request, HttpRequest):
        user = user_or_request.user
    else:
        raise ValueError(f'Argument "user_or_request" must be of type HttpRequest or User: '
                         f'"{type(user_or_request)}" given.')

    assert passes_quota(user, 'user_workspace_quota')

    return _get_user_workspace(app, user)


def user_workspace(controller):
    """
    **Decorator:** Get the file workspace (directory) for the given User. Add an argument named "user_workspace" to your controller. The TethysWorkspace will be passed to via this argument.

    Returns:
      TethysWorkspace: An object representing the workspace.

    **Example:**

    ::

        import os
        from my_first_app.app import MyFirstApp as app
        from tethys_sdk.workspaces import user_workspace

        @user_workspace
        def a_controller(request, user_workspace):
            \"""
            Example controller that uses @user_workspace() decorator.
            \"""
            new_file_path = os.path.join(user_workspace.path, 'new_file.txt')

            with open(new_file_path, 'w') as a_file:
                a_file.write('...')

            context = {}

            return render(request, 'my_first_app/template.html', context)

    """  # noqa:E501
    @wraps(controller)
    def wrapper(*args, **kwargs):
        request = None
        for _, arg in enumerate(args):
            if isinstance(arg, HttpRequest):
                request = arg
                break

        if request is None:
            raise ValueError('No request given. The user_workspace decorator only works on controllers.')

        the_workspace = get_user_workspace(request, request.user)

        return controller(*args, user_workspace=the_workspace, **kwargs)
    return wrapper


def _get_app_workspace(app_class):
    """
    Get the file workspace (directory) for the app.

    Args:
      app_class(TethysAppBase): The Tethys app class that is defined in app.py.

    Returns:
      tethys_apps.base.TethysWorkspace: An object representing the workspace.
    """
    project_directory = os.path.dirname(sys.modules[app_class.__module__].__file__)
    workspace_directory = os.path.join(project_directory, 'workspaces', 'app_workspace')
    return TethysWorkspace(workspace_directory)


def get_app_workspace(app_or_request) -> TethysWorkspace:
    """
    Get the app workspace for the active app of the given HttpRequest or the given Tethys App class.

    Args:
        app_or_request (TethysAppBase | HttpRequest): The Tethys App class or an HttpRequest to an app endpoint.

    Raises:
        ValueError: if object of type other than HttpRequest or TethysAppBase given.
        AssertionError: if quota for the app workspace has been exceeded.

    Returns:
        TethysWorkspace: workspace object bound to the app workspace.

    **Example:**

    ::

        import os
        from tethys_sdk.workspaces import get_app_workspace
        from .app import MyFirstApp as app

        def some_function():
            app_workspace = get_app_workspace(app)
            ...
    """
    from tethys_apps.base.app_base import TethysAppBase
    from tethys_apps.utilities import get_active_app

    # Get the active app
    if isinstance(app_or_request, HttpRequest):
        app = get_active_app(app_or_request, get_class=True)
    elif isinstance(app_or_request, TethysAppBase) or \
            (isinstance(app_or_request, type) and issubclass(app_or_request, TethysAppBase)):
        app = app_or_request
    else:
        raise ValueError(f'Argument "app_or_request" must be of type HttpRequest or TethysAppBase: '
                         f'"{type(app_or_request)}" given.')

    assert passes_quota(app, 'app_workspace_quota')

    return _get_app_workspace(app)


def app_workspace(controller):
    """
    **Decorator:** Get the file workspace (directory) for the app. Add an argument named "app_workspace" to your controller. The TethysWorkspace will be passed to via this argument.

    Returns:
      TethysWorkspace: An object representing the workspace.

    **Example:**

    ::

        import os
        from my_first_app.app import MyFirstApp as app
        from tethys_sdk.workspaces import app_workspace

        @app_workspace
        def a_controller(request, app_workspace):
            \"""
            Example controller that uses @app_workspace() decorator.
            \"""
            new_file_path = os.path.join(app_workspace.path, 'new_file.txt')

            with open(new_file_path, 'w') as a_file:
                a_file.write('...')

            context = {}

            return render(request, 'my_first_app/template.html', context)

    """  # noqa:E501
    @wraps(controller)
    def wrapper(*args, **kwargs):
        request = None
        for _, arg in enumerate(args):
            if isinstance(arg, HttpRequest):
                request = arg
                break

        if request is None:
            raise ValueError('No request given. The app_workspace decorator only works on controllers.')

        the_workspace = get_app_workspace(request)

        return controller(*args, app_workspace=the_workspace, **kwargs)
    return wrapper
