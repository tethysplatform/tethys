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

    **Example:**

    ::

        from tethys_sdk.permissions import Permission

        create_projects = Permission(
            name='create_projects',
            description='Create projects'
        )

    """

    def __init__(self, name, description):
        """
        Constructor
        """
        self.name = name
        self.description = description

    def _repr(self):
        return '<Permission name="{0}" description="{1}">'.format(self.name, self.description)

    def __str__(self):
        return self._repr()

    def __repr__(self):
        return self._repr()


class PermissionGroup:
    """
    Defines an object that represents a permission group for an app.

    Attributes:
        name (string): The name for the group. Only numbers, letters, and underscores allowed.
        permissions (iterable): A list or tuple of Permission objects.

    **Example:**

    ::

        from tethys_sdk.permissions import Permission, PermissionGroup

        create_projects = Permission(
            name='create_projects',
            description='Create projects'
        )

        delete_projects = Permission(
            name='delete_projects',
            description='Delete projects'
        )

        admin = PermissionGroup(
            name='admin',
            permissions=(create_projects, delete_projects)
        )

    """

    def __init__(self, name, permissions=[]):
        """
        Constructor
        """
        self.name = name
        self.permissions = permissions

    def _repr(self):
        return '<Group name="{0}">'.format(self.name)

    def __str__(self):
        return self._repr()

    def __repr__(self):
        return self._repr()


def has_permission(request, perm, user=None):
    """
    Returns True if the user of the given request has the given permission for the app. If a user object is provided, it is tested instead of the request user. The Request object is still required to derive the app context of the permission check.

    Args:
        request (Request): The current request object.
        perm (string): The name of the permission (e.g. 'create_things').
        user (django.contrib.auth.models.User): A user object to test instead of the user provided in the request.

    **Example:**

    ::

        from tethys_sdk.permissions import has_permission

        def my_controller(request):
            \"""
            Example controller
            \"""

            can_create_projects = has_permission(request, 'create_projects')

            if can_create_projects:
                ...

    """  # noqa: E501
    from tethys_apps.utilities import get_active_app

    app = get_active_app(request)

    if user is None:
        user = request.user

    namespaced_perm = 'tethys_apps.' + app.package + ':' + perm

    # Check permission
    if user.has_perm(namespaced_perm, app):
        return True
    return False
