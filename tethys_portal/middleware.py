"""
********************************************************************************
* Name: middleware.py
* Author: Nathan Swain
* Created On: August 1, 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from mfa.helpers import has_mfa
from social_django.middleware import SocialAuthExceptionMiddleware
from social_core import exceptions as social_exceptions
from tethys_cli.cli_colors import pretty_output, FG_WHITE
from tethys_apps.utilities import get_active_app, user_can_access_app
from tethys_portal.views.error import handler_404


class TethysSocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if hasattr(social_exceptions, exception.__class__.__name__):
            if isinstance(exception, social_exceptions.AuthCanceled):
                if request.user.is_anonymous:
                    return redirect('accounts:login')
                else:
                    return redirect('user:settings')
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
                    return redirect('user:settings')
            elif isinstance(exception, social_exceptions.NotAllowedToDisconnect):
                blurb = 'Unable to disconnect from this social account.'
                messages.success(request, blurb)
                if request.user.is_anonymous:
                    return redirect('accounts:login')
                else:
                    return redirect('user:settings')


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


class TethysMfaRequiredMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        mfa_required = getattr(settings, 'MFA_REQUIRED', False)
        sso_mfa_required = getattr(settings, 'SSO_MFA_REQUIRED', False)
        admin_mfa_required = getattr(settings, 'ADMIN_MFA_REQUIRED', True)

        # Override MFA_REQUIRED setting for API Token authentication
        if mfa_required and 'Authorization' in request.headers \
                and TokenAuthentication.keyword in request.headers['Authorization']:
            # Verify Token
            try:
                ta = TokenAuthentication()
                ta.authenticate(request)
                mfa_required = False
            except AuthenticationFailed:
                pass

        # Override MFA_REQUIRED setting for users logged in with SSO
        has_social_auth_attr = getattr(request.user, 'social_auth', None) is not None
        if mfa_required and not sso_mfa_required and has_social_auth_attr and request.user.social_auth.count() > 0:
            mfa_required = False

        # Override MFA_REQUIRED setting for staff users
        if mfa_required and not admin_mfa_required and request.user.is_staff:
            mfa_required = False

        if mfa_required and not has_mfa(request, request.user.username):
            if '/mfa' not in request.path \
                    and '/devices' not in request.path \
                    and '/oauth2' not in request.path \
                    and '/accounts' not in request.path \
                    and '/user' not in request.path \
                    and '/captcha' not in request.path \
                    and request.path != '/':
                messages.error(request, 'You must configure Multi Factor Authentication to continue.')
                return redirect('mfa_home')

        response = self.get_response(request)

        return response
