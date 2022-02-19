"""
********************************************************************************
* Name: controller.py
* Author: Nathan Swain
* Created On: August 2013
* Copyright: (c) Brigham Young University 2013
* License: BSD 2-Clause
********************************************************************************
"""
from django.views.generic import View

import inspect
from functools import wraps
from urllib.parse import urlparse
from collections import OrderedDict

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from social_core.exceptions import AuthAlreadyAssociated

from tethys_quotas.decorators import enforce_quota
from tethys_services.utilities import ensure_oauth2

from .permissions import has_permission
from .workspace import (
    app_workspace as app_workspace_decorator,
    user_workspace as user_workspace_decorator,
)
from ..decorators import login_required as login_required_decorator, permission_required

# imports for type hinting
from typing import Union, Any
from collections.abc import Callable


app_controllers_list = list()

class TethysController(View):

    @classmethod
    def as_controller(cls, **kwargs):
        """
        Thin veneer around the as_view method to make interface more consistent with Tethys terminology.
        """
        return cls.as_view(**kwargs)


def controller(
        function_or_class: Union[Callable[[HttpRequest, ...], Any], TethysController] = None,
        /, *,

        # UrlMap Overrides
        name: str = None,
        url: Union[str, list, tuple, dict, None] = None,
        protocol: str = 'http',
        regex: Union[str, list, tuple] = None,
        handler: Union[str, Callable] = None,
        handler_type: str = None,

        # login_required kwargs
        login_required: bool = True,
        redirect_field_name: str = REDIRECT_FIELD_NAME,
        login_url: str = None,

        # workspace decorators
        app_workspace: bool = False,
        user_workspace: bool = False,

        # ensure_oauth2 kwarg
        ensure_oauth2_provider: str = None,

        # enforce_quota kwargs
        enforce_quotas: Union[str, list, tuple, None] = None,

        # permission_required kwargs
        permissions_required: Union[str, list, tuple] = None,
        permissions_use_or: bool = False,
        permissions_message: str = None,
        permissions_raise_exception: bool = False,

        # additional kwargs to pass to TethysController.as_controller
        **kwargs
) -> Callable:
    """
    Decorator to register a function or TethysController class as a controller
    (by automatically registering a UrlMap for it).

    Args:
        name: Name of the url map. Letters and underscores only (_). Must be unique within the app. The default is the name of the function being decorated.
        url: URL pattern to map the endpoint for the controller or consumer. If a `list` then a seperate UrlMap is generated for each URL in the list. The first URL is given `name` and subsequent URLS are named `name`_1, `name`_2 ... `name`_n. Can also be passed as dict mapping names to URL patterns. In this case the `name` argument is ignored.
        protocol: 'http' for consumers or 'websocket' for consumers. Default is http.
        regex: Custom regex pattern(s) for url variables. If a string is provided, it will be applied to all variables. If a list or tuple is provided, they will be applied in variable order.
        handler: Dot-notation path a handler function. A handler is associated to a specific controller and contains the main logic for creating and establishing a communication between the client and the server.
        handler_type: Tethys supported handler type. 'bokeh' is the only handler type currently supported.
        login_required: If user is required to be logged in to access the controller. Default is `True`.
        redirect_field_name: URL query string parameter for the redirect path. Default is "next".
        login_url: URL to send users to in order to authenticate.
        app_workspace: Whether to pass the app workspace as an argument to the controller.
        user_workspace: Whether to pass the user workspace as an argument to the controller.
        ensure_oauth2_provider: An OAuth2 provider name to ensure is authenticated to access the controller.
        enforce_quotas: The name(s) of quotas to enforce on the controller.
        permissions_required: The name(s) of permissions that a user is required to have to access the controller.
        permissions_use_or: When multiple permissions are provided and this is True, use OR comparison rather than AND comparison, which is default.
        permissions_message: Override default message that is displayed to user when permission is denied. Default message is "We're sorry, but you are not allowed to perform this operation.".
        permissions_raise_exception: Raise 403 error if True. Defaults to False.

    **Example:**

    ::

        from tethys_sdk.base import controller

        @controller
        def my_app_controller(request):
            ...

        @controller
        def my_app_controller(request, url_arg):
            ...

        @controller(
            name='custom_name',
            url='customized-url/{url_arg}/with/arg',
        )
        def my_app_controller(request, url_arg):
            ...

        @controller
        def my_app_controller(request, url_arg1, url_arg2=None, url_arg3=None):
            ...

        # Note: having arguments with default values in the controller function without specifying the ``url`` argument
        # in the ``controller`` decorator will result in multiple ``UrlMap`` instances being created.
        # In this case the following ``UrlMap`` instances would be generated:

        [
            UrlMap(
                name='my_app_controller',
                url='my-app-controller/{url_arg1}/'
            ),
            UrlMap(
                name='my_app_controller_1',
                url='my-app-controller/{url_arg1}/{url_arg2}/'
            ),
            UrlMap(
                name='my_app_controller_2',
                url='my-app-controller/{url_arg1}/{url_arg2}/{url_arg3}/'
            )
        ]

        # Alternatively, you can explicitly define the names and urls generated by passing a dict as the ``url`` argument:

        @controller(
            url={
                'custom_controller_name': 'custom-controller/{url_arg1/{url_arg2}/',
                'another_custom_name': 'another-custom-controller/{url_arg1}/{url_arg3}/'
            }
        )
        def my_app_controller(request, url_arg1, url_arg2=None, url_arg3=None):
            ...

        @controller(
            name='controller_for_bokeh_handler',
            handler='my_app.handlers.handler_func',
            handler_type='bokeh',
        )
        def my_app_controller(request):
            ...

        @controller(
            app_workspace=True,
        )
        def my_app_controller(request, app_workspace):
            ...

        @controller(
            app_workspace=True,
            user_workspace=True,
        )
        def my_app_controller(request, app_workspace, user_workspace, url_arg):
            # Note that if both the ``app_workspace`` and ``user_workspace`` arguments are passed to the controller
            # decorator, then "app_workspace" should preceed "user_workspace" in the function argument list,
            # and both should be directly after the "request" argument.
            ...

        @controller(
            login_required=False,
        )
        def my_app_controller(request):
            # Note that ``login_required`` is ``True`` by default.
            ...

        @controller(
            ensure_oauth2_provider='Google',
        )
        def my_app_controller(request):
            ...

        @controller(
            permissions_required=['create_projects', 'delete_projects'],
            permissions_use_or=True,
        )
        def my_app_controller(request):
            ...

        @controller(
            enforce_quotas='my_quota',
        )
        def my_app_controller(request):
            ...

        @controller(
            enforce_quotas=['my_quota1', 'my_quota2'],
        )
        def my_app_controller(request):
            ...

        # The ``controller`` decorator can also be used to decorate ``TethysController`` subclasses.

        from tethys_sdk.base import TethysController

        @controller
        class MyControllerClass(TethysController):
            ...


        # Note that when the ``controller`` decorator is applied to a class it applies to all of the HTTP methods that are defined on that class:

        @controller(
            user_workspace=True,
        )
        class MyControllerClass(TethysController):
            def get(self, request, user_workspace, url_arg):
                ...

            def post(self, request, user_workspace, url_arg):
                ...

    """
    permissions_required = _listify(permissions_required)
    enforce_quota_codenames = _listify(enforce_quotas)

    def wrapped(function_or_class):
        final_urls = []
        if url is not None:
            final_urls = _listify(url)

        if not final_urls:
            module_parts = function_or_class.__module__.split('.')[3:]
            module_parts.append(function_or_class.__name__)
            working_url = '/'.join(module_parts)
            working_url = working_url.replace('_', '-')
            if inspect.isclass(function_or_class):
                controller_func = getattr(function_or_class, function_or_class._allowed_methods(function_or_class)[0].lower())
                parameters = OrderedDict(inspect.signature(controller_func).parameters)
                self_arg = list(parameters.keys())[0]
                parameters.pop(self_arg)
            else:
                parameters = OrderedDict(inspect.signature(function_or_class).parameters)

            for condition in [app_workspace, user_workspace]:  # note order of list is important
                if condition:
                    arg = list(parameters.keys())[1]
                    parameters.pop(arg)

            optional_url_parameters = list()
            for parameter_name, parameter in parameters.items():
                if parameter_name == 'request':
                    continue
                if parameter.default == inspect._empty:
                    working_url += f'/{{{parameter_name}}}'
                else:
                    optional_url_parameters.append(parameter_name)

            working_url += '/'
            final_urls = [working_url]
            for parameter_name in optional_url_parameters:
                working_url += f'{{{parameter_name}}}/'
                final_urls.append(working_url)

        if not isinstance(final_urls, dict):
            url_name = name or function_or_class.__name__
            final_urls = {f'{url_name}_{i}' if i else url_name: final_url for i, final_url in enumerate(final_urls)}

        controller = function_or_class.as_controller(**kwargs) if inspect.isclass(function_or_class) else function_or_class

        if login_required:
            controller = login_required_decorator(
                redirect_field_name=redirect_field_name, login_url=login_url
            )(controller)

        if user_workspace:
            controller = user_workspace_decorator(controller)

        if app_workspace:
            controller = app_workspace_decorator(controller)

        if ensure_oauth2_provider:
            controller = ensure_oauth2(ensure_oauth2_provider)(controller)

        if permissions_required:
            controller = permission_required(
                *permissions_required,
                use_or=permissions_use_or, message=permissions_message, raise_exception=permissions_raise_exception
            )(controller)

        for codename in enforce_quota_codenames:
            controller = enforce_quota(codename)(controller)

        for url_name, final_url in final_urls.items():
            url_map_kwargs = dict(
                name=url_name,
                url=final_url,
                controller=controller,
                protocol=protocol,
                regex=regex,
                handler=handler,
                handler_type=handler_type
            )
            app_controllers_list.append(url_map_kwargs)
        return function_or_class if inspect.isclass(function_or_class) else controller
    return wrapped if function_or_class is None else wrapped(function_or_class)


def _listify(obj):
    if obj is None:
        return []
    return obj if isinstance(obj, list) or isinstance(obj, tuple) else [obj]