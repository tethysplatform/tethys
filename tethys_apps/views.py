"""
********************************************************************************
* Name: views.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.core.mail import send_mail

from tethys_apps.app_harvester import SingletonAppHarvester
from tethys_apps.base.app_base import TethysAppBase


@login_required()
def library(request):
    """
    Handle the library view
    """
    # Retrieve the app harvester
    harvester = SingletonAppHarvester()

    # Define the context object
    context = {'apps': harvester.apps}

    return render(request, 'tethys_apps/app_library.html', context)

@login_required()
def handoff_capabilities(request, app_name):
    """
    Show handoff capabilities of the app name provided.
    """
    app_name = app_name.replace('-', '_')

    manager = TethysAppBase.get_handoff_manager()
    handlers = manager.get_capabilities(app_name, external_only=True, jsonify=True)

    return HttpResponse(handlers, content_type='application/javascript')


@login_required()
def handoff(request, app_name, handler_name):
    """
    Handle handoff requests.
    """
    app_name = app_name.replace('-', '_')

    manager = TethysAppBase.get_handoff_manager()

    return manager.handoff(request, handler_name, app_name, **request.GET.dict())

@login_required()
def send_beta_feedback_email(request):
    """
    Processes and send the beta form data submitted by beta testers
    """

    post = request.POST
    #email_users = User.objects.filter(is_staff=True)
    # Setup variables
    harvester = SingletonAppHarvester()
    apps_root = 'apps'

    # Get url and parts
    url = post.get('betaFormUrl')
    url_parts = url.split('/')

    # Find the app key
    if apps_root in url_parts:
        # The app root_url is the path item following (+1) the apps_root item
        app_root_url_index = url_parts.index(apps_root) + 1
        print app_root_url_index
        app_root_url = url_parts[app_root_url_index]
        print app_root_url

        # Get list of app dictionaries from the harvester
        apps = harvester.apps
        print apps

        # If a match can be made, return the app dictionary as part of the context
        for app in apps:
            if app.root_url == app_root_url:
                if hasattr(app, 'feedback_emails'):
                    email_users = app.feedback_emails
                else:
                    json = {'error': 'feedback_emails not defined in app.py'}
                    return JsonResponse(json)

    subject = 'User-Feedback'

    username =  post.get('betaUser')
    local_user_time =  post.get('betaSubmitLocalTime')
    UTC_offset_in_hours =  post.get('betaSubmitUTCOffset')
    app_url =  post.get('betaFormUrl')
    comments =  post.get('betaUserComments')

    message = 'User: {0}\n'\
            'Local User Time: {1}\n'\
            'UTC Offset in Hours: {2}\n'\
            'App URL: {3}\n'\
            'Comments: {4}'.format(username,local_user_time,UTC_offset_in_hours,app_url,comments)

    try:
        send_mail(subject,message, from_email=None,recipient_list=email_users)
    except:
        json = {'error': 'Failed to send emails'}
        return JsonResponse(json)

    json = {'success': 'Emails sent to specified developers'}
    return JsonResponse(json)