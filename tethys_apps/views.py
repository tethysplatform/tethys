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
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail

from tethys_apps.base.app_base import TethysAppBase
from tethys_apps.models import TethysApp
from tethys_apps.utilities import get_active_app

from tethys_compute.models import TethysJob, DaskJob

log = logging.getLogger('tethys.' + __name__)


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
        if app.configured:
            configured_apps.append(app)
        else:
            if request.user.is_staff:
                unconfigured_apps.append(app)

    # Define the context object
    context = {'apps': {'configured': configured_apps, 'unconfigured': unconfigured_apps}}

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
    # Form parameters
    post = request.POST

    # Get url and parts
    url = post.get('betaFormUrl')

    # Get app
    app = get_active_app(url=url)

    if app is None or not hasattr(app, 'feedback_emails'):
        json = {'success': False,
                'error': 'App not found or feedback_emails not defined in app.py'}
        return JsonResponse(json)

    # Formulate email
    subject = 'User Feedback for {0}'.format(app.name.encode('utf-8'))

    message = 'User: {0}\n'\
              'User Local Time: {1}\n'\
              'UTC Offset in Hours: {2}\n'\
              'App URL: {3}\n'\
              'User Agent: {4}\n'\
              'Vendor: {5}\n'\
              'Comments:\n' \
              '{6}'.\
        format(
            post.get('betaUser'),
            post.get('betaSubmitLocalTime'),
            post.get('betaSubmitUTCOffset'),
            post.get('betaFormUrl'),
            post.get('betaFormUserAgent'),
            post.get('betaFormVendor'),
            post.get('betaUserComments')
        )

    try:
        send_mail(subject, message, from_email=None, recipient_list=app.feedback_emails)
    except Exception as e:
        json = {'success': False,
                'error': 'Failed to send email: ' + str(e)}
        return JsonResponse(json)

    json = {'success': True,
            'result': 'Emails sent to specified developers'}
    return JsonResponse(json)


def update_job_status(request, job_id):
    """
    Callback endpoint for jobs to update status.
    """
    try:
        job = TethysJob.objects.filter(id=job_id)[0]
        job.status
        json = {'success': True}
    except Exception:
        json = {'success': False}

    return JsonResponse(json)


def update_dask_job_status(request, key):
    """
    Callback endpoint for dask jobs to update status.
    """
    params = request.GET
    status = params.get('status', None)
    log.debug('Recieved update status for DaskJob<key: {} status: {}>'.format(key, status))

    try:
        job = DaskJob.objects.filter(key=key)[0]
        job_status = job.DASK_TO_STATUS_TYPES[status]
        log.debug('Mapped dask status "{}" to tethys job status: "{}"'.format(status, job_status))
        job.status = job_status
        json = {'success': True}
    except Exception:
        json = {'success': False}

    return JsonResponse(json)
