# ********************************************************************************
# * Name: controller.py
# * Author: Nathan Swain
# * Created On: August 2013
# * Copyright: (c) Brigham Young University 2013
# * License: BSD 2-Clause
# ********************************************************************************
import importlib
import inspect
from collections import OrderedDict
import traceback

from channels.consumer import SyncConsumer, AsyncConsumer
from django.views.generic import View
from django.http import HttpRequest
from django.contrib.auth import REDIRECT_FIELD_NAME

from tethys_apps.base.page_handler import global_page_controller
from tethys_cli.cli_colors import write_warning
from tethys_components.library import ComponentLibraryManager
from tethys_quotas.decorators import enforce_quota
from tethys_services.utilities import ensure_oauth2
from tethys_utils import deprecation_warning, DOCS_BASE_URL
from . import url_map_maker
from .app_base import DEFAULT_CONTROLLER_MODULES

from .bokeh_handler import (
    _get_bokeh_controller,
    with_workspaces as with_workspaces_decorator,
    with_paths as with_paths_decorator,
    with_request as with_request_decorator,
)
from .paths import _add_path_decorator
from ..decorators import login_required as login_required_decorator, permission_required
from ..utilities import get_all_submodules, update_decorated_websocket_consumer_class

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


def consumer(
    consumer_class: SyncConsumer | AsyncConsumer = None,
    /,
    *,
    # UrlMap Overrides
    name: str = None,
    url: str = None,
    regex: Union[str, list, tuple] = None,
    with_paths: bool = False,
    # login_required kwargs
    login_required: bool = True,
    # permission_required kwargs
    permissions_required: Union[str, list, tuple] = None,
    permissions_use_or: bool = False,
) -> Callable:
    """
    Decorator to register a Consumer class as routed consumer endpoint
    (by automatically registering a UrlMap for it).

    Args:
        name: Name of the url map. Letters and underscores only (_). Must be unique within the app. The default is the name of the class being decorated.
        url: URL pattern to map the endpoint for the consumer. If a `list` then a seperate UrlMap is generated for each URL in the list. The first URL is given `name` and subsequent URLS are named `name`_1, `name`_2 ... `name`_n. Can also be passed as dict mapping names to URL patterns. In this case the `name` argument is ignored.
        regex: Custom regex pattern(s) for url variables. If a string is provided, it will be applied to all variables. If a list or tuple is provided, they will be applied in variable order.
        with_paths: If `True` then initialize the following path properties on the consumer class when it is called (`app_workspace`, `user_workspace`, `app_media`, `user_media`, `app_public`, `app_resources`). Default is `False`
        login_required: If user is required to be logged in to access the consumer endpoint. Default is `True`.
        permissions_required: The name(s) of permissions that a user is required to have to access the consumer endpoint. Default is `None`
        permissions_use_or: When multiple permissions are provided and this is True, use OR comparison rather than AND comparison, which is default. Default is `False`

    **Example:**

    .. code-block:: python

        from tethys_sdk.routing import consumer

        from channels.generic.websocket import AsyncWebsocketConsumer


        @consumer
        class MyConsumer(AsyncWebsocketConsumer):
            pass

        ------------

        @consumer(
            name='custom_name',
            url='customized/url',
        )
        class MyConsumer(AsyncWebsocketConsumer):
            pass

        ------------

        @consumer(
            name='custom_name',
            url='customized/url',
            permissions_required='permission',
            login_required=True
        )
        class MyConsumer(AsyncWebsocketConsumer):

            async def authorized_connect(self):
                ...

       ------------

        @consumer(
            with_paths=True,
            login_required=True,
        )
        class MyConsumer(AsyncWebsocketConsumer):

            async def authorized_connect(self):
                self.app_workspace
                self.user_workspace
                self.app_media
                self.user_media
                self.app_public
                self.app_resources

    """  # noqa: E501

    def wrapped(consumer_class):
        url_map_kwargs_list = _get_url_map_kwargs_list(
            function_or_class=consumer_class,
            name=name,
            url=url,
            protocol="websocket",
            regex=regex,
        )

        consumer_class = update_decorated_websocket_consumer_class(
            consumer_class,
            permissions_required,
            permissions_use_or,
            login_required,
            with_paths,
        )

        asgi_controller = consumer_class.as_asgi()
        _process_url_kwargs(asgi_controller, url_map_kwargs_list)
        return consumer_class

    return wrapped if consumer_class is None else wrapped(consumer_class)


def controller(
    function_or_class: Union[
        Callable[[HttpRequest, ...], Any], TethysController
    ] = None,
    /,
    *,
    # UrlMap Overrides
    name: str = None,
    url: Union[str, list, tuple, dict, None] = None,
    protocol: str = "http",
    regex: Union[str, list, tuple] = None,
    _handler: Union[str, Callable] = None,
    _handler_type: str = None,
    # login_required kwargs
    login_required: bool = True,
    redirect_field_name: str = REDIRECT_FIELD_NAME,
    login_url: str = None,
    # paths decorators
    app_workspace: bool = False,
    user_workspace: bool = False,
    app_media: bool = False,
    user_media: bool = False,
    app_resources: bool = False,
    app_public: bool = False,
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
    **kwargs,
) -> Callable:
    """
    Decorator to register a function or TethysController class as a controller
    (by automatically registering a UrlMap for it).

    Args:
        name: Name of the url map. Letters and underscores only (_). Must be unique within the app. The default is the name of the function being decorated.
        url: URL pattern to map the endpoint for the controller or consumer. If a `list` then a separate UrlMap is generated for each URL in the list. The first URL is given `name` and subsequent URLS are named `name` _1, `name` _2 ... `name` _n. Can also be passed as dict mapping names to URL patterns. In this case the `name` argument is ignored.
        protocol: 'http' for controllers or 'websocket' for consumers. Default is http.
        regex: Custom regex pattern(s) for url variables. If a string is provided, it will be applied to all variables. If a list or tuple is provided, they will be applied in variable order.
        login_required: If user is required to be logged in to access the controller. Default is `True`.
        redirect_field_name: URL query string parameter for the redirect path. Default is "next".
        login_url: URL to send users to in order to authenticate.
        app_workspace: Whether to pass the app workspace as an argument to the controller.
        user_workspace: Whether to pass the user workspace as an argument to the controller.
        app_media: Whether to pass the app media directory as an argument to the controller.
        user_media: Whether to pass the user media directory as an argument to the controller.
        app_resources: Whether to pass the app resources directory as an argument to the controller.
        app_public: Whether to pass the app public directory as an argument to the controller.
        ensure_oauth2_provider: An OAuth2 provider name to ensure is authenticated to access the controller.
        enforce_quotas: The name(s) of quotas to enforce on the controller.
        permissions_required: The name(s) of permissions that a user is required to have to access the controller.
        permissions_use_or: When multiple permissions are provided and this is True, use OR comparison rather than AND comparison, which is default.
        permissions_message: Override default message that is displayed to user when permission is denied. Default message is "We're sorry, but you are not allowed to perform this operation.".
        permissions_raise_exception: Raise 403 error if True. Defaults to False.


    **NOTE:** The :ref:`handler-decorator` should be used in favor of using the following arguments directly.

    Args:
        _handler: Dot-notation path a handler function. A handler is associated to a specific controller and contains the main logic for creating and establishing a communication between the client and the server.
        _handler_type: Tethys supported handler type. 'bokeh' is the only handler type currently supported.

    **Example:**

    ::

        from tethys_sdk.routing import controller

        @controller
        def my_app_controller(request):
            ...

        ------------

        @controller
        def my_app_controller(request, url_arg):
            ...

        ------------

        @controller(
            name='custom_name',
            url='customized-url/{url_arg}/with/arg',
        )
        def my_app_controller(request, url_arg):
            ...

        ------------

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

        ------------

        # Alternatively, you can explicitly define the names and urls generated by passing a dict as the ``url`` argument:

        @controller(
            url={
                'custom_controller_name': 'custom-controller/{url_arg1}/{url_arg2}/',
                'another_custom_name': 'another-custom-controller/{url_arg1}/{url_arg3}/'
            }
        )
        def my_app_controller(request, url_arg1, url_arg2=None, url_arg3=None):
            ...

        ------------

        @controller(
            app_workspace=True,
        )
        def my_app_controller(request, app_workspace):
            ...

        ------------

        @controller(
            app_workspace=True,
            user_workspace=True,
            app_media=True,
            user_media=True,
            app_resources=True,
            app_public=True,
        )
        def my_app_controller(request, app_workspace, user_workspace, app_media, user_media, app_public, app_resources, url_arg):
            # Note that the path arguments are passed in as key-word arguments, so the order does not matter,
            #   but the name of the argument must match what is shown here (i.e. the same as the argument name
            #   that is passed to the controller decorator).
            ...

        ------------

        @controller(
            login_required=False,
        )
        def my_app_controller(request):
            # Note that ``login_required`` is True by default (recommended). However, the login requirement is automatically dropped on all controllers when ``OPEN_PORTAL_MODE`` is enabled on the portal."
            ...

        ------------

        @controller(
            ensure_oauth2_provider='Google',
        )
        def my_app_controller(request):
            ...

        ------------

        @controller(
            permissions_required=['create_projects', 'delete_projects'],
            permissions_use_or=True,
        )
        def my_app_controller(request):
            ...

        ------------

        @controller(
            enforce_quotas='my_quota',
        )
        def my_app_controller(request):
            ...

        ------------

        @controller(
            enforce_quotas=['my_quota1', 'my_quota2'],
        )
        def my_app_controller(request):
            ...

        ------------

        # The ``controller`` decorator can also be used to decorate ``TethysController`` subclasses.

        from tethys_sdk.routing import TethysController

        @controller
        class MyControllerClass(TethysController):
            ...

        ------------

        # Note that when the ``controller`` decorator is applied to a class it applies to all the HTTP methods that are defined on that class:

        @controller(
            user_workspace=True,
        )
        class MyControllerClass(TethysController):
            def get(self, request, user_workspace, url_arg):
                ...

            def post(self, request, user_workspace, url_arg):
                ...

    """  # noqa: E501
    permissions_required = _listify(permissions_required)
    enforce_quota_codenames = _listify(enforce_quotas)

    def wrapped(function_or_class):
        url_map_kwargs_list = _get_url_map_kwargs_list(
            function_or_class=function_or_class,
            name=name,
            url=url,
            protocol=protocol,
            regex=regex,
            handler=_handler,
            handler_type=_handler_type,
            app_workspace=app_workspace,
            user_workspace=user_workspace,
            user_media=user_media,
            app_media=app_media,
            app_public=app_public,
            app_resources=app_resources,
        )

        if inspect.isclass(function_or_class):
            if protocol == "websocket":
                controller = function_or_class.as_asgi()
            else:
                controller = function_or_class.as_view(**kwargs)
        else:
            controller = function_or_class

        # process paths and add keyword arguments to controller
        for argument_name, value in (
            ("app_public", app_public),
            ("app_resources", app_resources),
            ("user_media", user_media),
            ("app_media", app_media),
            ("user_workspace", user_workspace),
            ("app_workspace", app_workspace),
        ):
            if value:
                controller = _add_path_decorator(argument_name)(controller)

        if permissions_required:
            controller = permission_required(
                *permissions_required,
                use_or=permissions_use_or,
                message=permissions_message,
                raise_exception=permissions_raise_exception,
            )(controller)

        for codename in enforce_quota_codenames:
            controller = enforce_quota(codename)(controller)

        if ensure_oauth2_provider:
            # this needs to come before login_required
            controller = ensure_oauth2(ensure_oauth2_provider)(controller)

        if login_required:
            # this should be at the end, so it's the first to be evaluated
            controller = login_required_decorator(
                redirect_field_name=redirect_field_name, login_url=login_url
            )(controller)

        _process_url_kwargs(controller, url_map_kwargs_list)
        return function_or_class if inspect.isclass(function_or_class) else controller

    return wrapped if function_or_class is None else wrapped(function_or_class)


def page(
    component_function: Callable = None,
    /,
    *,
    # UrlMap Overrides
    name: str = None,
    url: Union[str, list, tuple, dict, None] = None,
    regex: Union[str, list, tuple] = None,
    handler: Union[str, Callable] = None,
    # login_required kwargs
    login_required: bool = True,
    redirect_field_name: str = REDIRECT_FIELD_NAME,
    login_url: str = None,
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
    layout="default",
    title=None,
    index=None,
    custom_css=None,
    custom_js=None,
    app=None,
) -> Callable:
    """
    Decorator to register a function as a Page in the Component App paradigm
    (by automatically registering a UrlMap for it).

    Args:
        name: The internal name of the page, using only letters and underscores. Must be unique within the app. Defaults to the name of the function being decorated.
        url: The page portion (i.e. slug) of the URL associated with this page (e.g. http://localhost:8000/app/my-app/<url>). Defaults to the name of the function being decorated, with underscores replaced by dashes (e.g. ``my_page`` becomes "my-page").
        regex: Custom regex pattern(s) for url variables. If a string is provided, it will be applied to all variables. If a list or tuple is provided, they will be applied in variable order.
        handler: Function that will process the actual request. This is for an advanced escape-hatch pattern to get back to Django templating.
        login_required: If user is required to be logged in to access the controller. Default is `True`.
        redirect_field_name: URL query string parameter for the redirect path. Default is "next".
        login_url: URL to send users to in order to authenticate. This defaults to the built-in login page of your Tethys Portal.
        ensure_oauth2_provider: An OAuth2 provider name to ensure is authenticated to access the controller.
        enforce_quotas: The name(s) of quotas to enforce on the controller.
        permissions_required: The name(s) of permissions that a user is required to have to access the controller.
        permissions_use_or: When multiple permissions are provided and this is True, use OR comparison rather than AND comparison, which is default.
        permissions_message: Override default message that is displayed to user when permission is denied. Default message is "We're sorry, but you are not allowed to perform this operation.".
        permissions_raise_exception: Raise 403 error if True. Defaults to False.
        layout: Custom layout component within which the page's returned component content will be wrapped. Defaults to the ``default_layout`` as defined in the ``App`` class of the app that this page belongs to.
        title: Title of page as used in both the built-in Navigation component and the browser tab. Defaults to a title-cased version of the name of the function being decorated (e.g. ``my_page`` becomes "My Page").
        index: Index of the page as used to determine the display order in the built-in Navigation component. Defaults to an incrementing integer based on the order the function is processed by code. Pass -1 to remove the page entry from built-in Navigation component.
        custom_css: A list of URLs to additional css files that should be rendered with the page. These will be rendered in the order provided.
        custom_js: A list of URLs to additional js files that should be rendered with the page. These will be rendered in the order provided.
        app: The TethysAppBase instance that this page belongs to. This defaults to the App of the ``App.page`` decorator, which is the recommended way to use this decorator. If you are using this decorator outside of the context of an App, then you must provide the app argument.
    """  # noqa: E501
    if not app:
        raise ValueError(
            "The app argument must be supplied. Alternatively, use the @App.page wrapper, which supplies the app argument."
        )
    permissions_required = _listify(permissions_required)
    enforce_quota_codenames = _listify(enforce_quotas)

    def wrapped(component_function):
        url_map_kwargs_list = _get_url_map_kwargs_list(
            function_or_class=component_function,
            name=name,
            url=url,
            protocol="http",
            regex=regex,
            title=title,
            index=index,
            for_page=True,
        )

        component_source_code = inspect.getsource(component_function)

        lib = ComponentLibraryManager.get_library(
            f"{app.package}-{component_function.__name__}"
        )
        lib.load_dependencies_from_source_code(component_source_code)

        def controller_wrapper(request, **kwargs):
            controller = handler or global_page_controller
            if permissions_required:
                controller = permission_required(
                    *permissions_required,
                    use_or=permissions_use_or,
                    message=permissions_message,
                    raise_exception=permissions_raise_exception,
                )(controller)

            for codename in enforce_quota_codenames:
                controller = enforce_quota(codename)(controller)

            if ensure_oauth2_provider:
                # this needs to come before login_required
                controller = ensure_oauth2(ensure_oauth2_provider)(controller)

            if login_required:
                # this should be at the end, so it's the first to be evaluated
                controller = login_required_decorator(
                    redirect_field_name=redirect_field_name, login_url=login_url
                )(controller)

            return controller(
                request,
                app=app,
                layout=layout,
                component_func=component_function,
                title=url_map_kwargs_list[0]["title"],
                custom_css=custom_css,
                custom_js=custom_js,
                **kwargs,
            )

        _process_url_kwargs(controller_wrapper, url_map_kwargs_list)
        return component_function

    return wrapped if component_function is None else wrapped(component_function)


controller_decorator = controller


def handler(
    function: Callable = None,
    /,
    *,
    controller: Union[str, Callable[[HttpRequest, ...], None]] = None,
    template: str = None,
    app_package: str = None,
    handler_type: str = "bokeh",
    with_request: bool = False,
    with_workspaces: bool = False,
    with_paths: bool = False,
    **kwargs,
):
    """
    Decorator to register a handler function and connect it with a controller function
    (by automatically registering a UrlMap for it). Handler function may be synchronous or asynchronous.

    Args:
        controller: reference to controller function or string with dot-notation path to controller function. This is only required if custom logic is needed in the controller. Otherwise use `template` or `app_package`.
        template: The namespaced template file file (e.g. my_app/my_template.html). Use as an alternative to `controller` to automatically create a controller function that renders provided template.
        app_package: The app_package name from the `app.py` file. Used as an alternative to `controller` and `template` to automatically create a controller and template that extends the app's "base.html" template. If none of `controller`, `template` and `app_package` are provided then a default controller and template will be created.
        handler_type: Tethys supported handler type. 'bokeh' is the only handler type currently supported.
        with_request: If `True` then the ``HTTPRequest`` object will be added to the `Bokeh Document`.
        with_workspaces (DEPRECATED): if `True` then the `app_workspace` and `user_workspace` will be added to the `Bokeh Document`.
        with_paths: if `True` then the `app_media_path`, `user_media_path`, and `app_resources_path` will be added to the `Bokeh Document`.

    **Example:**

    .. code-block:: python

        from tethys_sdk.routing import handler

        @handler
        async def my_app_handler(document):
            ...

        ------------

        @handler
        def my_sync_app_handler(document):
            ...

        ------------

        @handler(
            name='home',
            app_package='my_app',
        )
        async def my_app_handler(document):
            ...

        ------------

        @handler(
            name='home',
            template='my_app/home.html',
        )
        def my_app_handler(document):
            ...

        ------------

        from bokeh.embed import server_document
        from .app import App

        def home_controller(request):
            # custom logic here
            custom_value = ...

            script = server_document(request.build_absolute_uri())
            context = {
                'script': script,
                'custom_key': custom_value,
            }
            return App.render(request, 'home.html', context)

        @handler(
            name='home',
            controller=home_controller,
        )
        def my_app_handler(document):
            ...

        ------------

        @handler(
            name='home',
            controller='my_app.controllers.my_app_controller',
        )
        def my_app_handler(document):
            ...

        ------------

        @handler(
            name='home',
            controller='tethysext.my_extension.controllers.my_controller',
        )
        def my_app_handler(document):
            ...

        ------------

        @handler(
            with_request=True
        )
        def my_app_handler(document):
            # attribute available when using "with_request" argument
            request = document.request
            ...

        ------------

        @handler(
            with_paths=True
        )
        async def my_app_handler(document):
            # attributes available when using "with_paths" argument
            request = document.request
            user_workspace = document.user_workspace
            user_media = document.user_media
            app_workspace = document.app_workspace
            app_media = document.app_media
            app_public = document.app_public
            app_resources = document.app_resources
            ...

        ------------

        def job_view(request, job_id):
            # Do something with URL variable ``job_id``

        @handler(
            name='job_view',
            url='job-view/{job_id}',
            login_required=True,
            ensure_oauth2_provider=app.PROVIDER_NAME
        )
        def job_view_handler(document):
            ...

        ------------


    """  # noqa: E501
    controller = controller or _get_bokeh_controller(template, app_package)
    if isinstance(controller, str):
        from .function_extractor import TethysFunctionExtractor

        modules = controller.split(".")
        prefix = (
            None
            if modules[0] in ["tethysapp", "tethysext"]
            else TethysFunctionExtractor.PATH_PREFIX
        )
        controller = TethysFunctionExtractor(controller, prefix=prefix).function

    def wrapped(function):
        controller.__name__ = function.__name__

        if with_paths:
            function = with_paths_decorator(function)
        elif with_workspaces:
            deprecation_warning(
                "5.0",
                'the "with_workspaces" argument to the "handler" decorator',
                'The workspaces API has been replaced with the new Paths API. In place of the "with_workspaces" '
                f'argument please use the "with_paths" argument on "{function.__module__}.{function.__name__}" '
                f"(see {DOCS_BASE_URL}tethys_sdk/paths.html#consumer-decorator>).\n"
                f"For a full guide to transitioning to the Paths API see "
                f"{DOCS_BASE_URL}/tethys_sdk/workspaces.html#transition-to-paths-guide",
            )
            function = with_workspaces_decorator(function)
        elif with_request:
            function = with_request_decorator(function)

        kwargs.update(
            dict(
                _handler=function,
                _handler_type=handler_type,
            )
        )
        kwargs.setdefault("name", function.__name__)
        controller_decorator(**kwargs)(controller)
        return function

    return wrapped if function is None else wrapped(function)


def _get_url_map_kwargs_list(
    function_or_class: Union[
        Callable[[HttpRequest, ...], Any], TethysController
    ] = None,
    name: str = None,
    url: Union[str, list, tuple, dict, None] = None,
    protocol: str = "http",
    regex: Union[str, list, tuple] = None,
    handler: Union[str, Callable] = None,
    handler_type: str = None,
    app_workspace=False,
    user_workspace=False,
    user_media=False,
    app_media=False,
    app_public=False,
    app_resources=False,
    title=None,
    index=None,
    for_page=False,
):
    final_urls = []
    if url is not None:
        final_urls = url if isinstance(url, dict) else _listify(url)

    if not final_urls:
        module_parts = function_or_class.__module__.split(".")[3:]
        module_parts.append(function_or_class.__name__)
        working_url = "/".join(module_parts)
        working_url = working_url.replace("_", "-")
        working_url += "/"
        if inspect.isclass(function_or_class) and issubclass(
            function_or_class, AsyncConsumer
        ):
            final_urls = [working_url]
        else:
            if inspect.isclass(function_or_class):
                controller_func = getattr(
                    function_or_class,
                    function_or_class._allowed_methods(function_or_class)[0].lower(),
                )
                parameters = OrderedDict(inspect.signature(controller_func).parameters)
                self_arg = list(parameters.keys())[0]
                parameters.pop(self_arg)
            else:
                parameters = OrderedDict(
                    inspect.signature(function_or_class).parameters
                )

            if for_page:
                # Removes the standard ComponentLib parameter
                arg = list(parameters.keys())[0]
                parameters.pop(arg)

            for condition in [
                app_workspace,
                user_workspace,
                user_media,
                app_media,
                app_public,
                app_resources,
            ]:  # note order of list is important
                if condition:
                    arg = list(parameters.keys())[1]
                    parameters.pop(arg)

            optional_url_parameters = list()
            for parameter_name, parameter in parameters.items():
                if parameter_name == "request":
                    continue
                if parameter.default == inspect._empty:
                    working_url += f"{{{parameter_name}}}/"
                else:
                    optional_url_parameters.append(parameter_name)
            final_urls = [working_url]
            for parameter_name in optional_url_parameters:
                working_url += f"{{{parameter_name}}}/"
                final_urls.append(working_url)

    if not isinstance(final_urls, dict):
        url_name = name or function_or_class.__name__
        final_urls = {
            f"{url_name}_{i}" if i else url_name: final_url
            for i, final_url in enumerate(final_urls)
        }

    return [
        dict(
            name=url_name,
            url=final_url,
            controller=controller,
            protocol=protocol,
            regex=regex,
            handler=handler,
            handler_type=handler_type,
            title=title or url_name.replace("_", " ").title(),
            index=index,
        )
        for url_name, final_url in final_urls.items()
    ]


def _process_url_kwargs(controller, url_map_kwargs_list):
    for url_map_kwargs in url_map_kwargs_list:
        url_map_kwargs["controller"] = controller
        app_controllers_list.append(url_map_kwargs)


def _listify(obj):
    if obj is None:
        return []
    return obj if isinstance(obj, (list, tuple)) else [obj]


def register_controllers(
    root_url: str,
    modules: Union[str, list, tuple],
    index: str = None,
    catch_all: str = "",
) -> list:
    """
    Registers ``UrlMap`` entries for all controllers that have been decorated with the ``@controller`` decorator.

    Args:
        root_url: The root-url to be used for all registered controllers found in ``module``.
        modules: The dot-notation path(s) to the module to search for controllers to register.
        index: The index url name. If passed then the URL with <url_name> will be overridden with the ``root_url``.
        catch_all: Add a catch-all endpoint for the app (e.g. /my-first-app/.*/) that maps to the named controller.

    Returns:
        A list of `UrlMap` objects.

    **Example:**

    ::

        from tethys_sdk.routing import register_controllers

        # app = TethysAppBase instance

        register_controllers(
            root_url=app.root_url,
            module=[f'{app.package_namespace}.{app.package}.controllers'],
            index=app.index,
        )

    """
    global app_controllers_list

    modules = _listify(modules)
    all_modules = list()
    for module in modules:
        try:
            module = importlib.import_module(module)
        except ImportError as e:
            module_name = module.split(".")[-1]
            if module_name not in DEFAULT_CONTROLLER_MODULES:
                write_warning(
                    f'Warning: The app with root_url "{root_url}" specified a controller module '
                    f'"{module_name}" but the module "{module}" could not be imported. '
                    f"Any controllers in that module will not be registered."
                )
            module_not_found = None
            if isinstance(e, ModuleNotFoundError):
                module_not_found = e.msg.split("'")[-2]
            if module_not_found != module:
                tb = traceback.format_exc()
                write_warning(
                    f'Warning: Found controller module "{module}", but it could not be imported '
                    f"because of the following error: {e}\n\n{tb}"
                )

        else:
            all_modules.extend(get_all_submodules(module))

    app_controllers_list = list()
    for module in all_modules:
        importlib.reload(module)  # load again to register controllers

    names = dict()
    for kwargs in app_controllers_list:
        name = kwargs["name"]
        if name in names:
            old_name = name
            while name in names:
                name += "_1"
            kwargs["name"] = name
            write_warning(
                f"Warning: Controller name conflict! "
                f'The controller "{kwargs["controller"].__module__}.{kwargs["controller"].__name__}" cannot be '
                f'registered with the name "{old_name}" because the controller '
                f'"{names[old_name]["controller"].__module__}.{names[old_name]["controller"].__name__}" is already '
                f'registered with that name. It will be registered with the name "{name}" instead. '
                f"You can make this warning go away by manually specifying a unique name in the controller decorator: "
                f"e.g. @controller(name='{name}')."
            )
        names[name] = kwargs

    # if index is provided then set the index controller url to the root_url
    if index:
        try:
            index_kwargs = names[index]
            index_kwargs["url"] = root_url
        except KeyError:
            raise RuntimeError(
                f'The app with root_url "{root_url}" specifies an index of "{index}", '
                f"but there are no controllers registered with that name."
            )

    UrlMap = url_map_maker(root_url)
    url_maps = [UrlMap(**kwargs) for name, kwargs in names.items()]

    # Add a catch-all endpoint for any URL following the app's root URL and map it to the named controller
    if catch_all and catch_all in names:
        url_maps.append(
            UrlMap(
                name="catch_all",
                url=root_url + "/.*/",
                controller=names[catch_all]["controller"],
            )
        )

    return url_maps
