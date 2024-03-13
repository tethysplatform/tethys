"""
********************************************************************************
* Name: tethys_layout.py
* Author: nswain
* Created On: June 24, 2021
* Copyright: (c) Aquaveo 2021
********************************************************************************
"""

import logging

from django.http import HttpResponseNotFound, HttpResponse
from django.shortcuts import render

from tethys_sdk.base import TethysController

log = logging.getLogger(f"tethys.{__name__}")


class TethysLayout(TethysController):
    """
    Base controller for all Tethys Layout views. Pass kwargs to as_controller() to override TethysLayout properties.
    """

    template_name = ""

    app = None
    back_url = None
    base_template = "tethys_layouts/tethys_layout.html"
    layout_title = ""
    layout_subtitle = ""

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests, either rendering the page or routing to class method.
        """
        from django.conf import settings

        # Call on get hook
        ret_on_get = self.on_get(request, *args, **kwargs)
        if ret_on_get and isinstance(ret_on_get, HttpResponse):
            return ret_on_get

        # Check for GET request alternative methods
        the_method = self.request_to_method(request)

        if the_method is not None:
            return the_method(request, *args, **kwargs)

        # Initialize context
        context = dict()

        # Add named url variables to context
        context.update(self.kwargs)

        # Add base view variables to context
        context.update(
            {
                "base_template": self.base_template,
                "back_url": self.back_url,
                "is_in_debug": settings.DEBUG,
                "nav_title": self.layout_title,
                "nav_subtitle": self.layout_subtitle,
                "open_portal_mode": getattr(settings, "ENABLE_OPEN_PORTAL", False),
            }
        )

        # Default Permissions
        permissions = dict()

        # Permissions hook
        permissions = self.get_permissions(request, permissions, *args, **kwargs)

        # Add permissions to context
        context.update(permissions)

        # Context hook
        context = self.get_context(request, context, *args, **kwargs)

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """
        Route POST requests to Python methods on the class.
        """
        the_method = self.request_to_method(request)

        if the_method is None:
            return HttpResponseNotFound()

        return the_method(request, *args, **kwargs)

    def request_to_method(self, request):
        """
        Derive python method on this class from "method" GET or POST parameter.

        Args:
            request (HttpRequest): The request.

        Returns:
            callable: the method or None if not found.
        """
        if request.method == "POST":
            method = request.POST.get("method", "")
        elif request.method == "GET":
            method = request.GET.get("method", "")
        else:
            return None
        python_method = method.replace("-", "_")
        the_method = getattr(self, python_method, None)
        return the_method

    def on_get(self, request, *args, **kwargs):
        """
        Hook that is called at the beginning of the get request, before any other controller logic occurs.

        Args:
            request (HttpRequest): The request.

        Returns:
            None or HttpResponse: If an HttpResponse is returned, render that instead.
        """  # noqa: E501
        return None

    def get_permissions(self, request, permissions, *args, **kwargs):
        """
        Hook to perform has_permission checks in. Values returned here are added to the context.

        Args:
            request (HttpRequest): The request.
            permissions (dict): The permissions dictionary with boolean values.

        Returns:
            dict: modified permisssions dictionary.
        """
        return permissions

    def get_context(self, request, context, *args, **kwargs):
        """
        Hook to add additional content to context. Avoid removing or modifying items in context already to prevent unexpected behavior.

        Args:
            request (HttpRequest): The request.
            context (dict): The context dictionary.

        Returns:
            dict: modified context dictionary.
        """  # noqa: E501
        return context
