from django.http import JsonResponse
from django.template.loader import render_to_string
from tethys_compute.models import TethysJob

def execute(request, job_id):
    try:
        job = TethysJob.objects.filter(id=job_id)[0].child
        job.execute()
        success = True
    except:
        success = False
    return JsonResponse({'success': success})

def delete(request, job_id):
    try:
        job = TethysJob.objects.filter(id=job_id)[0].child
        job.delete()
        success = True
    except:
        success = False
    return JsonResponse({'success': success})

def update_status(request, job_id):
    try:
        results_url = request.POST['results_url']
        run = request.POST['run']
        job = TethysJob.objects.filter(id=job_id)[0].child
        if job.label == 'gizmos_showcase':
            job.statuses = {'Complete': 40, 'Error': 10, 'Running': 30, 'Aborted':5}
        success = True
        status = job.status
        html = render_to_string('tethys_gizmos/gizmos/job_status.html', {'job': job, 'results_url': results_url, 'run': run})
    except:
        success = False
        status = None
        html = None

    return JsonResponse({'success': success, 'status': status, 'html': html})

def update_row(request, job_id):
    try:
        data = {key:val for key, val in request.POST.iteritems()}
        filter_string = data.pop('filters')
        filters = [f.strip('\'\" ') for f in filter_string.strip('()').split(',')]
        job = TethysJob.objects.filter(id=job_id)[0].child

        attributes = job.__dict__.keys()
        row = []
        for attribute in filters:
            if attribute in attributes:
                row.append(job.__getattribute__(attribute))

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