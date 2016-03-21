from django.http import JsonResponse
from django.template.loader import render_to_string
from tethys_compute.models import TethysJob
from tethys_gizmos.gizmo_options.jobs_table import JobsTable
import logging
log = logging.getLogger('tethys.tethys_gizmos.views.jobs_table')


def execute(request, job_id):
    try:
        job = TethysJob.objects.get_subclass(id=job_id)
        job.execute()
        success = True
        message = ''
    except Exception, e:
        success = False
        message = e.message
        log.error('The following error occurred when executing job %s: %s', job_id, message)
    return JsonResponse({'success': success, 'message': message})


def delete(request, job_id):
    try:
        job = TethysJob.objects.get_subclass(id=job_id)
        job.delete()
        success = True
        message = ''
    except Exception, e:
        success = True
        message = e.message
        log.error('The following error occurred when deleting job %s: %s', job_id, message)
    return JsonResponse({'success': success, 'message': message})


def update_row(request, job_id):
    try:
        data = {key: val for key, val in request.POST.iteritems()}
        filter_string = data.pop('column_fields')
        filters = [f.strip('\'\" ') for f in filter_string.strip('()').split(',')]
        job = TethysJob.objects.get_subclass(id=job_id)
        status = job.status
        statuses = None
        if status == "Various":
            # Hard code statues for the gizmo showcase
            if job.label == 'gizmos_showcase':
                statuses = {'Completed': 40, 'Error': 10, 'Running': 30, 'Aborted': 5}
            else:
                statuses = job.statuses

        row = JobsTable.get_rows([job], filters)[0]

        data.update({'job': job, 'row': row, 'job_status': status,
                     'job_statuses': statuses, 'delay_loading_status': False})

        success = True
        html = render_to_string('tethys_gizmos/gizmos/job_row.html', data)
    except Exception, e:
        log.error('The following error occurred when updating row for job %s: %s', job_id, e.message)
        success = False
        status = None
        html = None

    return JsonResponse({'success': success, 'status': status, 'html': html})


def update_status(request, job_id):
    try:
        data = request.POST.dict()
        job = TethysJob.objects.get_subclass(id=job_id)
        status = job.status
        statuses = None
        if status == "Various":
            # Hard code statues for the gizmo showcase
            if job.label == 'gizmos_showcase':
                statuses = {'Completed': 40, 'Error': 10, 'Running': 30, 'Aborted': 5}
            else:
                statuses = job.statuses

        data.update({'job': job, 'job_status': status, 'job_statuses': statuses})

        success = True
        html = render_to_string('tethys_gizmos/gizmos/job_status.html', data)
    except Exception, e:
        log.error('The following error occurred when updating status for job %s: %s', job_id, e.message)
        success = False
        status = None
        html = None

    return JsonResponse({'success': success, 'status': status, 'html': html})
