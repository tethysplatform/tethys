"""
********************************************************************************
* Name: permissions.py
* Author: nswain
* Created On: May 09, 2016
* Copyright: (c) Aquaveo 2016
* License: 
********************************************************************************
"""


class Permission:
    """
    Defines an object that represents a permission for an app.

    Attributes:
        name (string): The code name for the permission. Only numbers, letters, and underscores allowed.
        description (string): Short description of the permission for the admin interface.
    """

    def __init__(self, name, description):
        """
        Constructor
        """
        self.name = name
        self.description = description

    def _repr(self):
        return '<Permission name="{0}" description="{1}">'.format(self.name, self.description)

    def __unicode__(self):
        return self._repr()

    def __repr__(self):
        return self._repr()


class PermissionGroup:
    """
    Defines an object that represents a permission group for an app.

    Attributes:
        name (string): The name for the group. Only numbers, letters, and underscores allowed.
        permissions (iterable): A list or tuple of Permission objects.
    """

    def __init__(self, name, permissions=[]):
        """
        Constructor
        """
        self.name = name
        self.permissions = permissions

    def _repr(self):
        return '<Group name="{0}">'.format(self.name)

    def __unicode__(self):
        return self._repr()

    def __repr__(self):
        return self._repr()
