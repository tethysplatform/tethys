"""
********************************************************************************
* Name: decorators.py
* Author: nswain
* Created On: May 09, 2016
* Copyright: (c) Aquaveo 2016
* License:
********************************************************************************
"""

from functools import wraps
from urllib.parse import urlparse

from django.http import HttpRequest
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME

from tethys_portal.views import error as tethys_portal_error

from .base import has_permission


def async_login_required(func):
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        redirect = login_required(lambda r: r)(request)
        if redirect != request:
            return redirect
        return await func(request, *args, **kwargs)

    return wrapper


def login_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    """
    Decorator for Tethys App controllers that checks whether a user has a permission.
    """

    def decorator(controller_func):
        def wrapper(request, *args, **kwargs):
            if not getattr(settings, "ENABLE_OPEN_PORTAL", False):
                from django.contrib.auth.decorators import login_required as lr

                dec = lr(redirect_field_name=redirect_field_name, login_url=login_url)
                controller = dec(controller_func)
                return controller(request, *args, **kwargs)
            else:
                return controller_func(request, *args, **kwargs)

        return wraps(controller_func)(wrapper)

    return decorator if function is None else decorator(function)


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

    """  # noqa: E501

    use_or = kwargs.pop("use_or", False)
    message = kwargs.pop("message", None)
    message = message or "We're sorry, but the operation you requested cannot be found."
    raise_exception = kwargs.pop("raise_exception", False)
    perms = [arg for arg in args if isinstance(arg, str)]

    if not perms:
        raise ValueError("Must supply at least one permission to test.")

    def decorator(controller_func):
        def _wrapped_controller(*args, **kwargs):
            # With OR check, we assume the permission test passes upfront
            # Find request (varies position if class method is wrapped)
            # e.g.: func(request, *args, **kwargs) vs. method(self, request, *args, **kwargs)
            request_args_index = None
            the_self = None

            for index, arg in enumerate(args):
                if isinstance(arg, HttpRequest):
                    request_args_index = index

            # Args are everything after the request object
            if request_args_index is not None:
                request = args[request_args_index]
            else:
                raise ValueError("No HttpRequest object provided.")

            if request_args_index > 0:
                the_self = args[0]

            args = args[request_args_index + 1 :]

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
                        if settings.MULTIPLE_APP_MODE:
                            redirect_url = reverse("app_library")
                        else:
                            redirect_url = reverse("user:profile")

                        # If there is a referer (i.e.: we followed a link to get here)
                        if "HTTP_REFERER" in request.META:
                            # Try to redirect to the referer URL
                            referer = request.META["HTTP_REFERER"]
                            parsed_referer = urlparse(referer)

                            # But avoid an infinite redirect loop (if referer is self somehow)
                            if parsed_referer.path != request.path:
                                # e.g. hostname:port
                                request_host_parts = request.get_host().split(":")

                                # Only attempt redirect if host names are the same
                                if (
                                    len(request_host_parts) > 0
                                    and parsed_referer.hostname == request_host_parts[0]
                                ):
                                    redirect_url = parsed_referer.path

                        # Redirect to apps library with message
                        return redirect(redirect_url)

                    # If not authenticated...
                    else:
                        # User feedback
                        messages.add_message(
                            request,
                            messages.INFO,
                            "You must be logged in to access this feature.",
                        )

                        # Redirect to login page
                        return redirect(
                            reverse("accounts:login") + "?next=" + request.path
                        )

                else:
                    # Return Error 404: Not Found in production to prevent directory enumeration
                    if not getattr(settings, "DEBUG", False):
                        return tethys_portal_error.handler_404(request)
                    return tethys_portal_error.handler_403(request)

            # Call the controller
            if the_self is not None:
                response = controller_func(the_self, request, *args, **kwargs)
            else:
                response = controller_func(request, *args, **kwargs)

            return response

        return wraps(controller_func)(_wrapped_controller)

    return decorator
