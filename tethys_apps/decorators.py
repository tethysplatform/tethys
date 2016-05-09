"""
********************************************************************************
* Name: decorators.py
* Author: nswain
* Created On: May 09, 2016
* Copyright: (c) Aquaveo 2016
* License: 
********************************************************************************
"""
from django.utils.functional import wraps
from tethys_apps.utilities import get_active_app
from tethys_portal.views import error as tethys_portal_error


def permission_required(perm):
    """
    Decorator for Tethys App controllers that checks whether a user has a permission.
    """

    if not isinstance(perm, basestring):
        raise ValueError("First argument must be a string.")

    def decorator(controller_func):
        def _wrapped_controller(request, *args, **kwargs):
            app = get_active_app(request)
            user = request.user
            namespaced_perm = 'tethys_apps.' + app.package + ':' + perm

            # Check permission
            if not user.has_perm(namespaced_perm, app):
                return tethys_portal_error.handler_403(request)

            return controller_func(request, *args, **kwargs)
        return wraps(controller_func)(_wrapped_controller)
    return decorator