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
