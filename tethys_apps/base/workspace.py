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
from django.core.exceptions import PermissionDenied
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

    **Example:**

    ::

        import os
        from my_first_app.app import MyFirstApp as app

        def a_controller(request):
            \"""
            Example controller that uses get_user_workspace() method.
            \"""
            # Retrieve the workspace
            user_workspace = app.get_user_workspace(request.user)
            new_file_path = os.path.join(user_workspace.path, 'new_file.txt')

            with open(new_file_path, 'w') as a_file:
                a_file.write('...')

            context = {}

            return render(request, 'my_first_app/template.html', context)

    """
    username = ''

    from django.contrib.auth.models import User
    if isinstance(user_or_request, User) or isinstance(user_or_request, SimpleLazyObject):
        username = user_or_request.username
    elif isinstance(user_or_request, HttpRequest):
        username = user_or_request.user.username
    elif user_or_request is None:
        pass
    else:
        raise ValueError("Invalid type for argument 'user': must be either an User or HttpRequest object.")

    if not username:
        username = 'anonymous_user'

    project_directory = os.path.dirname(sys.modules[app_class.__module__].__file__)
    workspace_directory = os.path.join(project_directory, 'workspaces', 'user_workspaces', username)
    return TethysWorkspace(workspace_directory)


def user_workspace(controller):
    """
    **Decorator:** Get the file workspace (directory) for the given User.

    Returns:
      tethys_apps.base.TethysWorkspace: An object representing the workspace.

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

    """
    @wraps(controller)
    def wrapper(*args, **kwargs):
        from tethys_quotas.models import ResourceQuota
        from tethys_apps.utilities import get_active_app

        request = None
        for index, arg in enumerate(args):
            if isinstance(arg, HttpRequest):
                request = arg
                break

        if request is None:
            raise ValueError('No request given. The user_workspace decorator only works on controllers.')

        # Get user
        user = request.user

        try:
            codename = 'user_workspace_quota'
            rq = ResourceQuota.objects.get(codename=codename)

            if not passes_quota(user, codename):
                raise PermissionDenied(rq.help)

        except ResourceQuota.DoesNotExist:
            log.warning('ResourceQuota with codename {} does not exist.'.format(codename))

        # Get the active app
        app = get_active_app(request, get_class=True)

        the_workspace = _get_user_workspace(app, user)

        return controller(*args, the_workspace, **kwargs)
    return wrapper


def _get_app_workspace(app_class):
    """
    Get the file workspace (directory) for the app.

    Args:
      app_class(TethysApp): tethys app

    Returns:
      tethys_apps.base.TethysWorkspace: An object representing the workspace.

    **Example:**

    ::

        import os
        from my_first_app.app import MyFirstApp as app

        def a_controller(request):
            \"""
            Example controller that uses get_app_workspace() method.
            \"""
            # Retrieve the workspace
            app_workspace = app.get_app_workspace()
            new_file_path = os.path.join(app_workspace.path, 'new_file.txt')

            with open(new_file_path, 'w') as a_file:
                a_file.write('...')

            context = {}

            return render(request, 'my_first_app/template.html', context)

    """
    # Find the path to the app project directory
    # Hint: cls is a child class of this class.
    # Credits: http://stackoverflow.com/questions/4006102/ is-possible-to-know-the-_path-of-the-file-of-a-subclass-in-python  # noqa: E501
    project_directory = os.path.dirname(sys.modules[app_class.__module__].__file__)
    workspace_directory = os.path.join(project_directory, 'workspaces', 'app_workspace')
    return TethysWorkspace(workspace_directory)


def app_workspace(controller):
    """
    **Decorator:** Get the file workspace (directory) for the app.

    Returns:
      tethys_apps.base.TethysWorkspace: An object representing the workspace.

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

    """
    @wraps(controller)
    def wrapper(*args, **kwargs):
        from tethys_quotas.models import ResourceQuota
        from tethys_apps.utilities import get_active_app

        request = None
        for index, arg in enumerate(args):
            if isinstance(arg, HttpRequest):
                request = arg
                break

        if request is None:
            raise ValueError('No request given. The app_workspace decorator only works on controllers.')

        try:
            codename = 'app_workspace_quota'
            rq = ResourceQuota.objects.get(codename=codename)

        except ResourceQuota.DoesNotExist:
            log.warning('ResourceQuota with codename {} does not exist.'.format(codename))

        # Get the active app
        app = get_active_app(request, get_class=True)

        if not passes_quota(app, codename):
            raise PermissionDenied(rq.help)

        the_workspace = _get_app_workspace(app)

        return controller(*args, the_workspace, **kwargs)
    return wrapper
