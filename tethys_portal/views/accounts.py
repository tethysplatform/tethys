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
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import password_reset, password_reset_confirm
from django.contrib import messages
from tethys_portal.forms import LoginForm, RegisterForm


def login_view(request):
    """
    Handle login
    """
    # Only allow users to access login page if they are not logged in
    if not request.user.is_anonymous:
        return redirect('user:profile', username=request.user.username)

    # Handle form
    if request.method == 'POST' and 'login-submit' in request.POST:
        # Create login form bound to request data
        form = LoginForm(request.POST)

        # Validate the form
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Authenticate
            user = authenticate(username=username, password=password)

            # If not authenticated, user will be None
            if user is not None:
                # The password has been verified for the user
                if user.is_active:
                    # The user is valid, active, and authenticated, so login in the user
                    login(request, user)

                    # Redirect after logged in using next parameter or default to user profile
                    if 'next' in request.GET:
                        return redirect(request.GET['next'])
                    else:
                        return redirect('app_library')
                else:
                    # The password is valid, but the user account has been disabled
                    # Return a disabled account 'error' message
                    messages.error(request, "Sorry, but your account has been disabled. Please contact the site "
                                            "administrator for more details."
                    )
            else:
                # User was not authenticated, return errors
                 messages.warning(request, "Whoops! We were not able to log you in. Please check your username and "
                                           "password and try again."
                 )

    else:
        # Create new empty login form
        form = LoginForm()

    # Determine if signup is disabled or not
    signup_enabled = settings.ENABLE_OPEN_SIGNUP if hasattr(settings, 'ENABLE_OPEN_SIGNUP') else False

    context = {'form': form,
               'signup_enabled': signup_enabled}

    return render(request, 'tethys_portal/accounts/login.html', context)


def register(request):
    """
    Handle new user registration
    """
    # Only allow users to access register page if they are not logged in
    if not request.user.is_anonymous:
        return redirect('user:profile', username=request.user.username)

    # Disallow access to this page if open signup is disabled
    if not hasattr(settings, 'ENABLE_OPEN_SIGNUP') or not settings.ENABLE_OPEN_SIGNUP:
        return redirect('accounts:login')

    # Handle form
    if request.method == 'POST' and 'register-submit' in request.POST:
        # Create form bound to request data
        form = RegisterForm(request.POST)

        # Validate the form
        if form.is_valid():
            # Validate username and password using form methods
            username = form.clean_username()
            email = form.clean_email()
            password = form.clean_password2()

            # If no exceptions raised to here, then the username is unique and the passwords match.
            # Commit the new user to database
            form.save()

            # Authenticate the new user
            user = authenticate(username=username, password=password)

            if user is not None:
                # The password has been verified for the user
                if user.is_active:
                    # The user is valid, active, and authenticated, so login in the user
                    login(request, user)

                    # Redirect after logged in using next parameter or default to user profile
                    if 'next' in request.GET:
                        return redirect(request.GET['next'])
                    else:
                        return redirect('user:profile', username=user.username)
                else:
                    # The password is valid, but the user account has been disabled
                    # Return a disabled account 'error' message
                    messages.error(request, "Sorry, but your account has been disabled. Please contact the site "
                                            "administrator for more details."
                    )
            else:
                # User was not authenticated, return errors
                 messages.warning(request, "Whoops! We were not able to log you in. Please check your username and "
                                           "password and try again."
                 )

    else:
        # Create new empty form
        form = RegisterForm()

    context = {'form': form}
    return render(request, 'tethys_portal/accounts/register.html', context)


def logout_view(request):
    """
    Handle logout
    """
    # Present goodbye message and logout if not anonymous
    if not request.user.is_anonymous:
        name = request.user.first_name or request.user.username
        messages.success(request, 'Goodbye, {0}. Come back soon!'.format(name))
        logout(request)

    # Redirect home
    return redirect('home')


def reset_confirm(request, uidb64=None, token=None):
    return password_reset_confirm(request,
                                  template_name='tethys_portal/accounts/password_reset/reset_confirm.html',
                                  uidb64=uidb64,
                                  token=token,
                                  post_reset_redirect=reverse('accounts:login')
    )


def reset(request):
    return password_reset(request,
                          template_name='tethys_portal/accounts/password_reset/reset_request.html',
                          email_template_name='tethys_portal/accounts/password_reset/reset_email.html',
                          subject_template_name='tethys_portal/accounts/password_reset/reset_subject.txt',
                          post_reset_redirect=reverse('accounts:login')
    )
