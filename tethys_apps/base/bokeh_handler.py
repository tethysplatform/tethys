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
from bokeh.document import Document
from bokeh.embed import server_document

# Django Imports
from django.http.request import HttpRequest
from django.shortcuts import render

# Tethys Imports
from tethys_sdk.workspaces import get_user_workspace, get_app_workspace


def with_request(handler):
    @wraps(handler)
    def wrapper(doc: Document):
        bokeh_request = doc.session_context.request
        bokeh_request.pop('scheme')
        django_request = HttpRequest()
        for k, v in bokeh_request.items():
            setattr(django_request, k, v)
        doc.request = django_request
        return handler(doc)
    return wrapper


def with_workspaces(handler):
    @with_request
    @wraps(handler)
    def wrapper(doc: Document):
        doc.user_workspace = get_user_workspace(doc.request, doc.request.user)
        doc.app_workspace = get_app_workspace(doc.request)
        return handler(doc)
    return wrapper


def _get_bokeh_controller(template=None, app_package=None):
    template = template or 'tethys_apps/bokeh_default.html' if app_package is None else 'tethys_apps/bokeh_base.html'
    extends_template = f'{app_package}/base.html' if app_package else None

    def bokeh_controller(request):
        script = server_document(request.build_absolute_uri())
        context = {'script': script}
        if extends_template:
            context['extends_template'] = extends_template
        return render(request, template, context)
    return bokeh_controller
