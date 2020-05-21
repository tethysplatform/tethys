"""
********************************************************************************
* Name: middleware.py
* Author: Nathan Swain
* Created On: August 1, 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
from django.contrib import messages
from django.shortcuts import redirect
from social_django.middleware import SocialAuthExceptionMiddleware
from social_core import exceptions as social_exceptions
from tethys_cli.cli_colors import pretty_output, FG_WHITE

from tethys_apps.utilities import get_active_app, user_can_access_app
from django.core.exceptions import PermissionDenied
from tethys_portal.views.error import handler_404


class TethysSocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if hasattr(social_exceptions, exception.__class__.__name__):
            if isinstance(exception, social_exceptions.AuthCanceled):
                if request.user.is_anonymous:
                    return redirect('accounts:login')
                else:
                    return redirect('user:settings', username=request.user.username)
            elif isinstance(exception, social_exceptions.AuthAlreadyAssociated):
                blurb = 'The {0} account you tried to connect to has already been associated with another account.'
                with pretty_output(FG_WHITE) as p:
                    p.write(exception.backend.name)
                if 'google' in exception.backend.name:
                    blurb = blurb.format('Google')
                elif 'linkedin' in exception.backend.name:
                    blurb = blurb.format('LinkedIn')
                elif 'hydroshare' in exception.backend.name:
                    blurb = blurb.format('HydroShare')
                elif 'facebook' in exception.backend.name:
                    blurb = blurb.format('Facebook')
                else:
                    blurb = blurb.format('social')

                messages.success(request, blurb)

                if request.user.is_anonymous:
                    return redirect('accounts:login')
                else:
                    return redirect('user:settings', username=request.user.username)
            elif isinstance(exception, social_exceptions.NotAllowedToDisconnect):
                blurb = 'Unable to disconnect from this social account.'
                messages.success(request, blurb)
                if request.user.is_anonymous:
                    return redirect('accounts:login')
                else:
                    return redirect('user:settings', username=request.user.username)


class TethysAppAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        app = get_active_app(request)

        if app is None:
            return response
        else:
            if not app.enabled:
                if request.user.is_staff:
                    return handler_404(request, PermissionDenied, "This app is disabled. A user with admin permissions "
                                                                  "can enable this app from the app settings page.")
                else:
                    return handler_404(request, PermissionDenied)
            elif user_can_access_app(request.user, app):
                return response
            else:
                return handler_404(request, PermissionDenied)
