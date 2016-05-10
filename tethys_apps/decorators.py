"""
********************************************************************************
* Name: decorators.py
* Author: nswain
* Created On: May 09, 2016
* Copyright: (c) Aquaveo 2016
* License: 
********************************************************************************
"""
from urlparse import urlparse

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.functional import wraps
from tethys_apps.utilities import get_active_app
from tethys_portal.views import error as tethys_portal_error
from tethys_apps.base import has_permission


def permission_required(perm, raise_exception=False):
    """
    Decorator for Tethys App controllers that checks whether a user has a permission.

    Args:
        perm (string): The name of a permission for the app (e.g. 'create_things')
        raise_exception (bool, optional): Raise 403 error if True. Defaults to False.
    """

    if not isinstance(perm, basestring):
        raise ValueError("First argument must be a string.")

    def decorator(controller_func):
        def _wrapped_controller(request, *args, **kwargs):
            # Check permission
            if not has_permission(request, perm):

                if not raise_exception:
                    # If user is authenticated...
                    if request.user.is_authenticated():
                        # User feedback
                        messages.add_message(request, messages.WARNING, "We're sorry, but you are not allowed "
                                                                        "to perform this operation.")

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