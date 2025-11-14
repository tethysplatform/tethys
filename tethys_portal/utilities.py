"""
********************************************************************************
* Name: utilities.py
* Author: Nathan Swain
* Created On: 2020
* Copyright: (c) Aquaveo, LLC 2020
* License: BSD 2-Clause
********************************************************************************
"""

import datetime
from uuid import UUID
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme


def log_user_in(request, user=None, username=None):
    """
    Handle user login and session creation of existing user.

    Args:
        request (HttpRequest): The request object.
        user (auth.models.User): The user to login. Required if username not provided.
        username (str): The username of the user to login. Required if user not provided.

    Returns:
        HttpResponse: redirect to post login page.
    """
    if not user and not username:
        raise ValueError(
            'You must provide either the "user" or the "username" arguments.'
        )

    # Get user from username if not provided
    if not user and username:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.warning(
                request,
                "Whoops! We were not able to log you in. Please check your username and "
                "password and try again.",
            )
            return redirect("accounts:login")

    # The user is valid, active, and authenticated, so login in the user
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")

    # Redirect after logged in using next parameter or default to user profile
    if "next" in request.GET:
        next_url = sanitize_next_url(request.GET["next"])
        if next_url:
            return redirect(next_url)

    if settings.MULTIPLE_APP_MODE:
        return redirect("app_library")
    else:
        return redirect("/")


def json_serializer(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, UUID):
        return str(obj)
    raise TypeError(
        f'Object of type "{obj.__class__.__name__}" is not JSON serializable'
    )


def sanitize_next_url(next_url):
    """
    Sanitize the "next" URL parameter to prevent open redirect vulnerabilities.

    Args:
        next_url (str): The next URL parameter to sanitize.

    Returns:
        str: The sanitized next URL or None if invalid.
    """
    if settings.ALLOWED_HOSTS:
        allowed_hosts = set(settings.ALLOWED_HOSTS)

    else:
        # Default if ALLOWED_HOSTS is not set (for development)
        allowed_hosts = {"localhost", "127.0.0.1"}

    if next_url and url_has_allowed_host_and_scheme(
        url=next_url, allowed_hosts=allowed_hosts
    ):
        return next_url
    return None
