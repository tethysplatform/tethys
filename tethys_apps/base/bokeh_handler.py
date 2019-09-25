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

# Django Imports
from django.http.request import HttpRequest

# Tethys Imports
from tethys_sdk.workspaces import user_workspace, app_workspace


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
        doc.user_workspace = get_user_workspace(doc.request)
        doc.app_workspace = get_app_workspace(doc.request)
        return handler(doc)
    return wrapper


@user_workspace
def get_user_workspace(request, user_workspace):
    return user_workspace


@app_workspace
def get_app_workspace(request, app_workspace):
    return app_workspace
