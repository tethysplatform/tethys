"""
********************************************************************************
* Name: views.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

import logging

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail

from tethys_config.models import get_custom_template
from .base.app_base import TethysAppBase
from .models import TethysApp
from .utilities import get_active_app, user_can_access_app
from .models import ProxyApp
from .decorators import login_required

logger = logging.getLogger("tethys." + __name__)


@login_required()
def library(request):
    """
    Handle the library view
    """
    # Retrieve the app harvester
    apps = TethysApp.objects.all()

    configured_apps = list()
    unconfigured_apps = list()

    for app in apps:
        if request.user.is_staff:
            if app.configured:
                configured_apps.append(app)
            else:
                unconfigured_apps.append(app)
        elif user_can_access_app(request.user, app):
            if app.configured and app.show_in_apps_library:
                configured_apps.append(app)

    # Fetch any proxied apps (these are always assumed to be configured)
    proxy_apps = ProxyApp.objects.all()

    for proxy_app in proxy_apps:
        if request.user.is_staff or (
            proxy_app.enabled
            and proxy_app.show_in_apps_library
            and user_can_access_app(request.user, proxy_app)
        ):
            configured_apps.append(proxy_app)

    # sort apps alphabetically
    configured_apps.sort(key=lambda a: a.name)

    # sort apps by order
    configured_apps.sort(key=lambda a: a.order)

    # Define the context object
    context = {
        "apps": {"configured": configured_apps, "unconfigured": unconfigured_apps}
    }

    template = get_custom_template(
        "Apps Library Template", "tethys_apps/app_library.html"
    )

    return render(request, template, context)


@login_required()
def handoff_capabilities(request, app_name):
    """
    Show handoff capabilities of the app name provided.
    """
    app_name = app_name.replace("-", "_")

    manager = TethysAppBase.get_handoff_manager()
    handlers = manager.get_capabilities(app_name, external_only=True, jsonify=True)

    return HttpResponse(handlers, content_type="application/javascript")


@login_required()
def handoff(request, app_name, handler_name):
    """
    Handle handoff requests.
    """
    app_name = app_name.replace("-", "_")

    manager = TethysAppBase.get_handoff_manager()

    return manager.handoff(request, handler_name, app_name, **request.GET.dict())


@login_required()
def send_beta_feedback_email(request):
    """
    Processes and send the beta form data submitted by beta testers
    """
    # Form parameters
    post = request.POST

    # Get url and parts
    url = post.get("betaFormUrl")

    # Get app
    app = get_active_app(url=url)

    if app is None or not hasattr(app, "feedback_emails"):
        json = {
            "success": False,
            "error": "App not found or feedback_emails not defined in app.py",
        }
        return JsonResponse(json)

    # Formulate email
    subject = "User Feedback for {0}".format(app.name.encode("utf-8"))

    message = (
        "User: {0}\n"
        "User Local Time: {1}\n"
        "UTC Offset in Hours: {2}\n"
        "App URL: {3}\n"
        "User Agent: {4}\n"
        "Vendor: {5}\n"
        "Comments:\n"
        "{6}".format(
            post.get("betaUser"),
            post.get("betaSubmitLocalTime"),
            post.get("betaSubmitUTCOffset"),
            post.get("betaFormUrl"),
            post.get("betaFormUserAgent"),
            post.get("betaFormVendor"),
            post.get("betaUserComments"),
        )
    )

    try:
        send_mail(subject, message, from_email=None, recipient_list=app.feedback_emails)
    except Exception as e:
        json = {"success": False, "error": "Failed to send email: " + str(e)}
        return JsonResponse(json)

    json = {"success": True, "result": "Emails sent to specified developers"}
    return JsonResponse(json)
