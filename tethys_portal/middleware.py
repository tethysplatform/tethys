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
from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from django.http import HttpResponse
from social import exceptions as social_exceptions
from social.exceptions import AuthCanceled, AuthAlreadyAssociated, NotAllowedToDisconnect

import logging

class TethysSocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if hasattr(social_exceptions, exception.__class__.__name__):
            if isinstance(exception, AuthCanceled):
                if request.user.is_anonymous():
                    return redirect('accounts:login')
                else:
                    return redirect('user:settings', username=request.user.username)
            elif isinstance(exception, AuthAlreadyAssociated):
                blurb = 'The {0} account you tried to connect to has already been associated with another account.'
                print(exception.backend.name)
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

                if request.user.is_anonymous():
                    return redirect('accounts:login')
                else:
                    return redirect('user:settings', username=request.user.username)
            elif isinstance(exception, NotAllowedToDisconnect):
                blurb = 'Unable to disconnect from this social account.'
                messages.success(request, blurb)
                if request.user.is_anonymous():
                    return redirect('accounts:login')
                else:
                    return redirect('user:settings', username=request.user.username)
                    
                    
class MetricsTracking():
    def process_response(self, request, response):
        tethys_log = logging.getLogger('metrics_logger')
        username = "None"
        if hasattr(request, 'user'):
            if request.user:
                username = request.user
            else:
                username = 'Anonymous'
        request_method = request.META.get('REQUEST_METHOD')
        clientip = request.META.get('REMOTE_ADDR')
        url = request.path
        response_status =  response.status_code
        tethys_log.debug('%s,%s,%s,%s,%s' % (request_method, url, username, clientip, response_status))
        return response
    
