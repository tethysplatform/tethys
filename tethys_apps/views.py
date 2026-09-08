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
import requests

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.core.mail import send_mail

from tethys_config.models import get_custom_template
from .base.app_base import TethysAppBase
from .models import TethysApp
from .utilities import get_active_app, user_can_access_app
from .models import ProxyApp
from .decorators import login_required

logger = logging.getLogger("tethys." + __name__)

# Forwarded so the browser's cached-copy check reaches the service and it can
# reply 304 instead of resending the whole body.
PROXY_FORWARDED_REQUEST_HEADERS = ("If-None-Match", "If-Modified-Since")

# Forwarded so the browser can cache proxied responses instead of making a new request
# on every pan and zoom.
PROXY_FORWARDED_RESPONSE_HEADERS = (
    "Cache-Control",
    "ETag",
    "Expires",
    "Last-Modified",
    "Vary",
    "Age",
)


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


@login_required()
def secure_map_proxy(request, setting_id):
    """
    Proxy view for securely accessing map services with credentials stored in Tethys Services or OAuth.
    """
    from tethys_services.models import SecureMapService

    try:
        service = SecureMapService.objects.get(id=setting_id)
    except SecureMapService.DoesNotExist:
        return HttpResponse("Service setting not found.", status=404)

    browser_params = {key: value for key, value in request.GET.items()}
    service_params = service.get_resolved_params()
    params = {**service_params, **browser_params}

    headers = {}
    if service.authentication_method == "oauth":
        access_token = service.get_oauth_token(request.user)
        if not access_token:
            return HttpResponse("Failed to retrieve OAuth token.", status=500)
        headers["Authorization"] = f"Bearer {access_token}"

    if request.content_type:
        headers["Content-Type"] = request.content_type

    for header in PROXY_FORWARDED_REQUEST_HEADERS:
        value = request.headers.get(header)
        if value:
            headers[header] = value

    connection_timeout = (
        service.connection_timeout if service.connection_timeout is not None else 10
    )
    read_timeout = service.read_timeout if service.read_timeout is not None else 30
    try:
        resp = requests.request(
            method=request.method,
            url=service.endpoint,
            params=params,
            headers=headers,
            data=request.body if request.body else None,
            stream=True,
            timeout=(connection_timeout, read_timeout),
        )
    except requests.Timeout:
        logger.error(
            f"Request to {service.endpoint} timed out. "
            f"(connection_timeout: {connection_timeout}s, read_timeout: {read_timeout}s)"
        )
        return HttpResponse("Request timed out.", status=504)

    if not resp.ok:
        logger.error(
            f"Upstream request to {service.endpoint} failed with status {resp.status_code}."
        )

    # A 304 has no body, so return it directly rather than returning an empty response
    if resp.status_code == 304:
        proxy_response = HttpResponse(status=304)
    else:
        proxy_response = StreamingHttpResponse(
            resp.iter_content(chunk_size=8192),
            status=resp.status_code,
            content_type=resp.headers.get("Content-Type", "application/octet-stream"),
        )

    for header in PROXY_FORWARDED_RESPONSE_HEADERS:
        value = resp.headers.get(header)
        if value:
            proxy_response[header] = value

    # Prevent shared caches from storing OAuth2 responses fetched with user credentials.
    if service.authentication_method == "oauth":
        proxy_response["Cache-Control"] = "private, no-store"

    return proxy_response
