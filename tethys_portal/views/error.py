"""
********************************************************************************
* Name: error.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

from django.shortcuts import render


def handler_400(request, exception=None, *args, **kwargs):
    """
    Handle 400 errors
    """
    context = {
        "error_code": "400",
        "error_color": "#dc5842",
        "error_title": "Bad Request",
        "error_message": "We're sorry, but we can't process your request. Please, try something different.",
        "error_image": "/static/tethys_portal/images/error_500.png",
    }
    return render(request, "tethys_portal/error.html", context, status=400)


def handler_403(request, exception=None, *args, **kwargs):
    """
    Handle 403 errors
    """
    error_title = "Forbidden"
    default_error_message = (
        "We're sorry, but you do not have permission to access this page. "
        "Please, contact the portal administrator if there is a mistake."
    )

    if exception:
        error_title = str(exception)

    error_message = kwargs.get("error_message", default_error_message)

    context = {
        "error_code": "403",
        "error_color": "#8f61aa",
        "error_title": error_title,
        "error_message": error_message,
        "error_image": "/static/tethys_portal/images/data.png",
    }
    return render(request, "tethys_portal/error.html", context, status=403)


def handler_404(request, exception=None, error_message=None, *args, **kwargs):
    """
    Handle 404 errors
    """

    if not error_message:
        error_message = "We are unable to find the page you requested. Please, check the address and try again."

    context = {
        "error_code": "404",
        "error_color": "#778bbb",
        "error_title": "Not Found",
        "error_message": error_message,
        "error_image": "/static/tethys_portal/images/error_404.png",
    }
    return render(request, "tethys_portal/error.html", context, status=404)


def handler_500(request):
    """
    Handle 500 errors
    """
    context = {
        "error_code": "500",
        "error_color": "#dc5842",
        "error_title": "Server Error",
        "error_message": "We're sorry, but we have encountered an unexpected problem. "
        "Please, come back later and try again.",
        "error_image": "/static/tethys_portal/images/error_500.png",
    }
    return render(request, "tethys_portal/error.html", context, status=500)
