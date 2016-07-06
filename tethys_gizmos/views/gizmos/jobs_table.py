from django.http import JsonResponse
from django.template.loader import render_to_string
from tethys_compute.models import TethysJob
from tethys_gizmos.gizmo_options.jobs_table import JobsTable

def execute(request, job_id):
    try:
        job = TethysJob.objects.filter(id=job_id)[0].child
        job.execute()
        success = True
        message = ''
    except Exception, e:
        success = False
        message = str(e)
    return JsonResponse({'success': success, 'message': message})

def delete(request, job_id):
    try:
        job = TethysJob.objects.filter(id=job_id)[0].child
        job.delete()
        success = True
        message = ''
    except Exception, e:
        success = True
        message = str(e)
    return JsonResponse({'success': success, 'message': message})

def update_row(request, job_id):
    try:
        data = {key:val for key, val in request.POST.iteritems()}
        filter_string = data.pop('column_fields')
        filters = [f.strip('\'\" ') for f in filter_string.strip('()').split(',')]
        job = TethysJob.objects.filter(id=job_id)[0].child

        row = JobsTable.get_rows([job], filters)[0]

        data.update({'job':job, 'row':row})

        #Hard code statues for the gizmo showcase
        if job.label == 'gizmos_showcase':
            job.statuses = {'Complete': 40, 'Error': 10, 'Running': 30, 'Aborted': 5}

        success = True
        status = job.status
        html = render_to_string('tethys_gizmos/gizmos/job_row.html', data)
    except Exception, e:
        print 'Error: ', e
        success = False
        status = None
        html = None

    return JsonResponse({'success': success, 'status': status, 'html': html})

