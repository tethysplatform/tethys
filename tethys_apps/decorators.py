"""
********************************************************************************
* Name: decorators.py
* Author: nswain
* Created On: May 09, 2016
* Copyright: (c) Aquaveo 2016
* License: 
********************************************************************************
"""
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.functional import wraps
from past.builtins import basestring
from tethys_portal.views import error as tethys_portal_error
from tethys_apps.base import has_permission


def permission_required(*args, **kwargs):
    """
    Decorator for Tethys App controllers that checks whether a user has a permission.

    Args:
        *args: Any number of permission names for the app (e.g. 'create_projects')
        **kwargs: Any of keyword arguments specified below.

    **Valid Kwargs:**

    * **message: (string):** Override default message that is displayed to user when permission is denied. Default message is "We're sorry, but you are not allowed to perform this operation.".
    * **raise_exception (bool):** Raise 403 error if True. Defaults to False.
    * **use_or (bool):** When multiple permissions are provided and this is True, use OR comparison rather than AND comparison, which is default.

    **Example:**

    ::

        from tethys_sdk.permissions import permission_required

        # Basic use
        @permission_required('create_projects')
        def my_controller(request):
            \"""
            Example controller
            \"""
            ...

        # Custom message when permission is denied
        @permission_required('create_projects', message="You do not have permission to create projects")
        def my_controller(request):
            \"""
            Example controller
            \"""
            ...

        # Multiple permissions with AND comparison (must pass both permissions tests)
        @permission_required('create_projects', 'delete_projects')
        def my_controller(request):
            \"""
            Example controller
            \"""
            ...

        # Multiple permissions with OR comparison (must pass at least one permissions test)
        @permission_required('create_projects', 'delete_projects', use_or=True)
        def my_controller(request):
            \"""
            Example controller
            \"""
            ...

        # Raise 403 exception rather than redirecting and displaying message (useful for REST controllers).
        @permission_required('create_projects', raise_exception=True)
        def my_controller(request):
            \"""
            Example controller
            \"""
            ...

    """

    use_or = kwargs.pop('use_or', False)
    message = kwargs.pop('message', "We're sorry, but you are not allowed to perform this operation.")
    raise_exception = kwargs.pop('raise_exception', False)

    for arg in args:
        if not isinstance(arg, basestring):
            raise ValueError("Arguments must be a string and the name of a permission for the app.")

    perms = args

    def decorator(controller_func):
        def _wrapped_controller(request, *args, **kwargs):
            # With OR check, we assume the permission test passes upfront

            # Check permission
            pass_permission_test = True

            # OR Loop
            if use_or:
                pass_permission_test = False
                for perm in perms:
                    # If any one of the permission evaluates to True, the test passes
                    if has_permission(request, perm):
                        pass_permission_test = True
                        break

            # AND Loop
            else:
                # Assume pass test
                pass_permission_test = True

                for perm in perms:
                    # If any one of the permissions evaluates to False, the test fails
                    if not has_permission(request, perm):
                        pass_permission_test = False
                        break

            if not pass_permission_test:
                if not raise_exception:
                    # If user is authenticated...
                    if request.user.is_authenticated:
                        # User feedback
                        messages.add_message(request, messages.WARNING, message)

                        # Default redirect URL
                        redirect_url = reverse('app_library')

                        # If there is a referer (i.e.: we followed a link to get here)
                        if 'HTTP_REFERER' in request.META:
                            # Try to redirect to the referer URL
                            referer = request.META['HTTP_REFERER']
                            parsed_referer = urlparse(referer)

                            # But avoid an infinite redirect loop (if referer is self somehow)
                            if parsed_referer.path != request.path:
                                # e.g. hostname:port
                                request_host_parts = request.get_host().split(':')

                                # Only attempt redirect if host names are the same
                                if len(request_host_parts) > 0 and parsed_referer.hostname == request_host_parts[0]:
                                    redirect_url = parsed_referer.path

                        # Redirect to apps library with message
                        return redirect(redirect_url)

                    # If not authenticated...
                    else:
                        # User feedback
                        messages.add_message(request, messages.INFO, "You must be logged in to access this feature.")

                        # Redirect to login page
                        return redirect(reverse('accounts:login') + '?next=' + request.path)

                else:
                    return tethys_portal_error.handler_403(request)

            return controller_func(request, *args, **kwargs)
        return wraps(controller_func)(_wrapped_controller)
    return decorator