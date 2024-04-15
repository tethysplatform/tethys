"""
********************************************************************************
* Name: bokeh_handler.py
* Author: Michael Souffront and Scott Christensen
* Created On: September 2019
* License: BSD 2-Clause
********************************************************************************
"""

# Native Imports
from functools import wraps

# Third Party Imports

# Django Imports
from django.http.request import HttpRequest
from django.shortcuts import render

# Tethys Imports
# TODO remove deprecated workspaces imports in 5.0
from tethys_sdk.workspaces import (
    get_user_workspace as get_user_workspace_old,
    get_app_workspace as get_app_workspace_old
)

from tethys_portal.optional_dependencies import optional_import

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


def with_request(handler):
    @wraps(handler)
    def wrapper(doc: Document):
        bokeh_request = doc.session_context.request
        bokeh_request.pop("scheme")
        django_request = HttpRequest()
        for k, v in bokeh_request.items():
            setattr(django_request, k, v)
        doc.request = django_request
        return handler(doc)

    return wrapper


def with_workspaces(handler):
    # TODO deprecation warning
    @with_request
    @wraps(handler)
    def wrapper(doc: Document):
        doc.user_workspace = get_user_workspace_old(doc.request, doc.request.user)
        doc.app_workspace = get_app_workspace_old(doc.request)
        return handler(doc)

    return wrapper


def with_paths(handler):
    @with_request
    @wraps(handler)
    def wrapper(doc: Document):
        app = _resolve_app_class(doc.request)
        user = doc.request.user
        doc.app_workspace = get_app_workspace(app)
        doc.user_workspace = get_user_workspace(app, user)
        doc.app_media_path = get_app_media(app)
        doc.user_media_path = get_user_media(app, user)
        doc.app_resources_path = get_app_resources(app)
        doc.app_public_path = get_app_public(app)
        return handler(doc)

    return wrapper


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
