import os
import shutil


class TethysWorkspace(object):
    """
    Definition of objects representing file workspaces (directories) for apps.


    """

    def __init__(self, path):
        """
        Constructor
        """
        # Create the path if it doesn't already exist
        if not os.path.exists(path):
            os.makedirs(path)

        # Validate that the path is a directory
        self.path = path

    def __repr__(self):
        """
        Rendering
        """
        return '<TethysWorkspace path="{0}">'.format(self.path)

    def files(self, fullpath=False):
        """
        Return a list of files that are in the workspace.

        Args:
          fullpath(bool): Returns list of files with full path names when True. Defaults to False.

        Returns:
          list: A list of files in the workspace.

        Example:

        ::

            workspace.files()
            workspace.files(fullpath=True)

        """
        if fullpath:
            files = [os.path.join(self.path, f) for f in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, f))]
        else:
            files = [f for f in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, f))]
        return files

    def directories(self, fullpath=False):
        """
        Return a list of directories that are in the workspace.

        Args:
          fullpath(bool): Returns list of directories with full path names when True. Defaults to False.

        Returns:
          list: A list of directories in the workspace.

        Example:

        ::

            workspace.directories()
            workspace.directories(fullpath=True)

        """
        if fullpath:
            directories = [os.path.join(self.path, d) for d in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, d))]
        else:
            directories = [d for d in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, d))]
        return directories

    def clear(self, exclude=[], exclude_files=False, exclude_directories=False):
        """
        Remove all files and directories in the workspace.

        Args:
          exclude(iterable): A list or tuple of file and directory names to exclude from clearing.
          exclude_files(bool): Excludes files from clearing when True. Defaults to False.
          exclude_directories(bool): Excludes directories from clearing when True. Defaults to False.

        Example:

        ::

            workspace.clear()
            workspace.clear(exclude_files=True)
            workspace.clear(exclude_directories=True)
            workspace.clear(exclude=['file1.txt', '/full/path/to/directory1', 'directory2', '/full/path/to/file2.txt'])

        """
        files = [f for f in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, f))]
        directories = [d for d in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, d))]

        if not exclude_files:
            for file in files:
                fullpath = os.path.join(self.path, file)
                if file not in exclude and fullpath not in exclude:
                    os.remove(fullpath)

        if not exclude_directories:
            for directory in directories:
                fullpath = os.path.join(self.path, directory)
                if directory not in exclude and fullpath not in exclude:
                    shutil.rmtree(fullpath)

    def remove(self, item):
        """
        Remove a file or directory from the workspace.

        Args:
          item(str): Name of the item to remove from the workspace.

        Examples:

        ::

            workspace.remove('file.txt')
            workspace.remove('/full/path/to/file.txt')
            workspace.remove('directory')
            workspace.remove('/full/path/to/directory')

        """
        fullpath = item

        if self.path not in fullpath:
            fullpath = os.path.join(self.path, item)

        if os.path.isdir(fullpath):
            shutil.rmtree(fullpath)
        elif os.path.isfile(fullpath):
            os.remove(fullpath)