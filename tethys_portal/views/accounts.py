"""
********************************************************************************
* Name: accounts.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.cache import never_cache
from tethys_portal.forms import LoginForm, RegisterForm
from tethys_portal.utilities import log_user_in, sanitize_next_url
from tethys_config.models import get_custom_template

from tethys_portal.optional_dependencies import optional_import, has_module

# optional imports
has_mfa = optional_import("has_mfa", from_module="mfa.helpers")


@never_cache
def login_view(request):
    """
    Handle login
    """
    # Only allow users to access login page if they are not logged in
    if not request.user.is_anonymous:
        return redirect("user:profile")

    # Handle form
    if request.method == "POST" and "login-submit" in request.POST:
        # Create login form bound to request data
        form = LoginForm(request.POST)

        # Validate the form
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            # Authenticate
            user = authenticate(request, username=username, password=password)

            # If not authenticated, user will be None
            if user is not None:
                # The password has been verified for the user
                if user.is_active:
                    # Check for multi factor authentication
                    if has_module(has_mfa):
                        mfa_response = has_mfa(request, user.username)
                        if mfa_response:
                            return mfa_response

                    return log_user_in(request, user)
                else:
                    # The password is valid, but the user account has been disabled
                    # Return a disabled account 'error' message
                    messages.error(
                        request,
                        "Sorry, but your account has been disabled. Please contact the site "
                        "administrator for more details.",
                    )
            else:
                # User was not authenticated, return errors
                messages.warning(
                    request,
                    "Whoops! We were not able to log you in. Please check your username and "
                    "password and try again.",
                )

    else:
        # Create new empty login form
        form = LoginForm()

    # Determine if signup is disabled or not
    signup_enabled = (
        settings.ENABLE_OPEN_SIGNUP
        if hasattr(settings, "ENABLE_OPEN_SIGNUP")
        else False
    )

    context = {"form": form, "signup_enabled": signup_enabled}

    template = get_custom_template(
        "Login Page Template", "tethys_portal/accounts/login.html"
    )

    return render(request, template, context)


@never_cache
def register(request):
    """
    Handle new user registration
    """
    # Only allow users to access register page if they are not logged in
    if not request.user.is_anonymous:
        return redirect("user:profile")

    # Disallow access to this page if open signup is disabled
    if not hasattr(settings, "ENABLE_OPEN_SIGNUP") or not settings.ENABLE_OPEN_SIGNUP:
        return redirect("accounts:login")

    # Handle form
    if request.method == "POST" and "register-submit" in request.POST:
        # Create form bound to request data
        form = RegisterForm(request.POST)

        # Validate the form
        if form.is_valid():
            # Validate username and password using form methods
            username = form.clean_username()
            email = form.clean_email()  # noqa: F841
            password = form.clean_password2()

            # If no exceptions raised to here, then the username is unique and the passwords match.
            # Commit the new user to database
            form.save()

            # Authenticate the new user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # The password has been verified for the user
                if user.is_active:
                    # The user is valid, active, and authenticated, so login in the user
                    login(request, user)

                    # Redirect after logged in using next parameter or default to user profile
                    if "next" in request.GET:
                        next_url = sanitize_next_url(request.GET["next"])
                        if next_url:
                            return redirect(next_url)

                    return redirect("user:profile")
                else:
                    # The password is valid, but the user account has been disabled
                    # Return a disabled account 'error' message
                    messages.error(
                        request,
                        "Sorry, but your account has been disabled. Please contact the site "
                        "administrator for more details.",
                    )
            else:
                # User was not authenticated, return errors
                messages.warning(
                    request,
                    "Whoops! We were not able to log you in. Please check your username and "
                    "password and try again.",
                )

    else:
        # Create new empty form
        form = RegisterForm()

    context = {"form": form}
    template = get_custom_template(
        "Register Page Template", "tethys_portal/accounts/register.html"
    )
    return render(request, template, context)


def logout_view(request):
    """
    Handle logout
    """
    # Present goodbye message and logout if not anonymous
    if not request.user.is_anonymous:
        name = request.user.first_name or request.user.username
        messages.success(request, "Goodbye, {0}. Come back soon!".format(name))
        logout(request)

    # Redirect home
    if settings.MULTIPLE_APP_MODE:
        return redirect("home")
    else:
        return redirect("accounts:login")
