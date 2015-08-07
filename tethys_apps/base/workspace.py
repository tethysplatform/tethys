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
import shutil


class TethysWorkspace(object):
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
            files = [os.path.join(self._path, f) for f in os.listdir(self._path) if os.path.isfile(os.path.join(self._path, f))]
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
            directories = [os.path.join(self._path, d) for d in os.listdir(self._path) if os.path.isdir(os.path.join(self._path, d))]
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

        """
        # Sanitize to prevent backing into other directories or entering the home directory
        full_path = item.replace('../', '').replace('./', '').\
                         replace('..\\', '').replace('.\\', '').\
                         replace('~/', '').replace('~\\', '')

        if self._path not in full_path:
            full_path = os.path.join(self._path, full_path)

        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        elif os.path.isfile(full_path):
            os.remove(full_path)