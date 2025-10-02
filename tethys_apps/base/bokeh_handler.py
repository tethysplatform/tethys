"""
********************************************************************************
* Name: bokeh_handler.py
* Author: Michael Souffront and Scott Christensen
* Created On: September 2019
* License: BSD 2-Clause
********************************************************************************
"""

# Native Imports
import inspect
from functools import wraps

# Third Party Imports
from channels.db import database_sync_to_async

# Django Imports
from django.http.request import HttpRequest
from django.shortcuts import render

# Tethys Imports
# TODO remove deprecated workspaces imports in 5.0
from tethys_sdk.workspaces import (
    get_user_workspace as _get_user_workspace_old,
    get_app_workspace as _get_app_workspace_old,
)

from tethys_portal.optional_dependencies import optional_import
from tethys_utils import deprecation_warning, DOCS_BASE_URL

from .paths import (
    _resolve_app_class,
    get_app_workspace,
    get_user_workspace,
    get_app_media,
    get_user_media,
    get_app_resources,
    get_app_public,
)

# Optional Imports
Document = optional_import("Document", from_module="bokeh.document")
server_document = optional_import("server_document", from_module="bokeh.embed")


def _add_request_to_doc(doc):
    """
    Adds a Django request object to a Bokeh document
    Args:
        doc: Bokeh document that Django request object should be added to
    """
    bokeh_request = doc.session_context.request
    bokeh_request.pop("scheme")
    django_request = HttpRequest()
    for k, v in bokeh_request.items():
        setattr(django_request, k, v)
    doc.request = django_request


def _add_paths_to_doc(doc):
    """
    Adds several Tethys Paths to a Bokeh document

    Args:
        doc: Bokeh document to add Tethys Paths to
    """
    app = _resolve_app_class(doc.request)
    user = doc.request.user
    doc.app_workspace = get_app_workspace(app)
    doc.user_workspace = get_user_workspace(app, user)
    doc.app_media_path = get_app_media(app)
    doc.user_media_path = get_user_media(app, user)
    doc.app_resources_path = get_app_resources(app)
    doc.app_public_path = get_app_public(app)


def with_request(handler):
    """
    Decorator for Bokeh handlers that adds the Django request object to the Bokeh document object
    Args:
        handler: decorated handler function (that accepts a document object). May be sync or async.

    Returns: wrapped handler function (either sync or async to match the decorated function).

    """

    @wraps(handler)
    def wrapper(doc: Document):
        _add_request_to_doc(doc)
        return handler(doc)

    @wraps(handler)
    async def async_wrapper(doc: Document):
        _add_request_to_doc(doc)
        return await handler(doc)

    return async_wrapper if inspect.iscoroutinefunction(handler) else wrapper


def with_workspaces(handler):
    deprecation_warning(
        "5.0",
        'the "with_workspaces" decorator',
        'The workspaces API has been replaced by the new Paths API. In place of the "with_workspaces" decorator '
        f'please use the "with_paths" decorator (see {DOCS_BASE_URL}tethys_sdk/paths.html#handler-decorator).\n'
        f"For a full guide to transitioning to the Paths API see "
        f"{DOCS_BASE_URL}/tethys_sdk/workspaces.html#transition-to-paths-guide",
    )

    @with_request
    @wraps(handler)
    def wrapper(doc: Document):
        doc.user_workspace = _get_user_workspace_old(doc.request, doc.request.user)
        doc.app_workspace = _get_app_workspace_old(doc.request)
        return handler(doc)

    return wrapper


def with_paths(handler):
    """
    Decorator for Bokeh handlers that adds Tethys paths to the Bokeh document object
    Args:
        handler: decorated handler function (that accepts a document object). May be sync or async.

    Returns: wrapped handler function (either sync or async to match the decorated function).

    """

    @with_request
    @wraps(handler)
    def wrapper(doc: Document):
        _add_paths_to_doc(doc)
        return handler(doc)

    @with_request
    @wraps(handler)
    async def async_wrapper(doc: Document):
        await database_sync_to_async(_add_paths_to_doc)(doc)
        return await handler(doc)

    return async_wrapper if inspect.iscoroutinefunction(handler) else wrapper


def _get_bokeh_controller(template=None, app_package=None):
    template = (
        template or "tethys_apps/bokeh_default.html"
        if app_package is None
        else "tethys_apps/bokeh_base.html"
    )
    extends_template = f"{app_package}/base.html" if app_package else None

    def bokeh_controller(request):
        script = server_document(request.get_full_path())
        context = {"script": script}
        if extends_template:
            context["extends_template"] = extends_template
        return render(request, template, context)

    return bokeh_controller
