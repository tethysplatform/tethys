import os


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

    def files(self, absolute=False):
        """
        Return a list of files that are in the workspace.
        """

    def directories(self, absolute=False):
        """
        Return a list of directories that are in the workspace.
        """

    def clear(self, exclude=[]):
        """
        Clear all files and directories in the workspace.
        """