"""
********************************************************************************
* Name: permissions.py
* Author: nswain
* Created On: May 09, 2016
* Copyright: (c) Aquaveo 2016
* License: 
********************************************************************************
"""
# from tethys_apps.utilities import get_active_app


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


# def has_permission(request, perm):
#     """
#     Returns True if a user has the given permission for the app.
#
#     Args:
#         request (Request): The current request object.
#         perm (string): The name of the permission (e.g. 'create_things').
#     """
#     app = get_active_app(request)
#     user = request.user
#     namespaced_perm = 'tethys_apps.' + app.package + ':' + perm
#
#     # Check permission
#     if user.has_perm(namespaced_perm, app):
#         return True
#     return False
