from django.http import JsonResponse
from django.shortcuts import render
from tethys_compute.models import TethysJob


def execute(request, job_id):
    try:
        job = TethysJob.objects.filter(id=job_id)
        job.execute()
        success = True
    except:
        success = False
    return JsonResponse({'success': success})

def delete(request, job_id):
    try:
        job = TethysJob.objects.filter(id=job_id)
        job.delete()
        success = True
    except:
        success = False
    return JsonResponse({'success': success})

def update_status(request, job_id):
    job = TethysJob.objects.filter(id=job_id)
    context = {'job': job}
    return render(request, 'tethys_gizmos/gizmos/job_status.html', context)
