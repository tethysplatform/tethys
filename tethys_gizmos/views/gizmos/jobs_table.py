from django.http import JsonResponse
from django.template.loader import render_to_string
from tethys_compute.models import TethysJob, CondorWorkflow, DaskJob, DaskScheduler
from tethys_gizmos.gizmo_options.jobs_table import JobsTable
import logging
from bokeh.embed import server_document

log = logging.getLogger('tethys.tethys_gizmos.views.jobs_table')


def execute(request, job_id):
    try:
        job = TethysJob.objects.get_subclass(id=job_id)
        job.execute()
        success = True
        message = ''
    except Exception as e:
        success = False
        message = str(e)
        log.error('The following error occurred when executing job %s: %s', job_id, message)
    return JsonResponse({'success': success, 'message': message})


def delete(request, job_id):
    try:
        job = TethysJob.objects.get_subclass(id=job_id)
        job.delete()
        success = True
        message = ''
    except Exception as e:
        success = True
        message = str(e)
        log.error('The following error occurred when deleting job %s: %s', job_id, message)
    return JsonResponse({'success': success, 'message': message})


def update_row(request, job_id):
    try:
        data = {key: _parse_value(val) for key, val in request.POST.items()}
        filter_string = data.pop('column_fields')
        filters = [f.strip('\'\" ') for f in filter_string.strip('[]').split(',')]
        job = TethysJob.objects.get_subclass(id=job_id)
        status = job.status
        statuses = None

        if status == "Various":
            # Hard code statues for the gizmo showcase
            if job.label == 'gizmos_showcase':
                if isinstance(job, CondorWorkflow):
                    statuses = {'Completed': 20, 'Error': 20, 'Running': 40, 'Aborted': 0}
                else:
                    statuses = {'Completed': 40, 'Error': 10, 'Running': 30, 'Aborted': 5}
            elif isinstance(job, CondorWorkflow):
                num_statuses = 0
                statuses = {'Completed': 0, 'Error': 0, 'Running': 0, 'Aborted': 0}
                for key, value in job.statuses.items():
                    if key in statuses:
                        num_statuses += value
                        statuses[key] = float(value) / float(job.num_jobs) * 100.0

                # Handle case with CondorWorkflows where DAG has started working,
                # but jobs have not necessarily started yet.
                if isinstance(job, CondorWorkflow) and not num_statuses:
                    status = 'Submitted'

        if isinstance(job, DaskJob):
            # Display results ready as running on jobs table
            if status == 'Results-Ready':
                status = 'Running'

        row = JobsTable.get_row(job, filters)

        data.update({'job': job, 'row': row, 'column_fields': filters, 'job_status': status,
                     'job_statuses': statuses, 'delay_loading_status': False})

        success = True
        html = render_to_string('tethys_gizmos/gizmos/job_row.html', data)
    except Exception as e:
        log.error('The following error occurred when updating row for job %s: %s', job_id, str(e))
        success = False
        status = None
        html = None

    return JsonResponse({'success': success, 'status': status, 'html': html})


def update_status(request, job_id):
    try:
        data = {key: _parse_value(val) for key, val in request.POST.items()}
        job = TethysJob.objects.get_subclass(id=job_id)
        status = job.status
        statuses = None
        if status == "Various":
            # Hard code statues for the gizmo showcase
            if job.label == 'gizmos_showcase':
                if isinstance(job, CondorWorkflow):
                    statuses = {'Completed': 20, 'Error': 20, 'Running': 40, 'Aborted': 0}
                else:
                    statuses = {'Completed': 40, 'Error': 10, 'Running': 30, 'Aborted': 5}
            else:
                num_statuses = 0
                statuses = {'Completed': 0, 'Error': 0, 'Running': 0, 'Aborted': 0}
                for key, value in job.statuses.items():
                    if key in statuses:
                        num_statuses += value
                        statuses[key] = float(value) / float(job.num_jobs) * 100.0

                # Handle case with CondorWorkflows where DAG has started working,
                # but jobs have not necessarily started yet.
                if isinstance(job, CondorWorkflow) and not num_statuses:
                    status = 'Submitted'

        data.update({'job': job, 'job_status': status, 'job_statuses': statuses})

        success = True
        html = render_to_string('tethys_gizmos/gizmos/job_status.html', data)
    except Exception as e:
        log.exception('The following error occurred when updating status for job %s: %s', job_id, str(e))
        success = False
        status = None
        html = None

    return JsonResponse({'success': success, 'status': status, 'html': html})


def update_workflow_nodes_row(request, job_id):
    dag = {}
    try:
        job = TethysJob.objects.get_subclass(id=job_id)
        status = job.status

        # Hard code example for gizmos_showcase
        if job.label == 'gizmos_showcase':
            dag = {
                'a': {
                    'status': 'com',
                    'parents': [],
                    'cluster_id': 1,
                    'display': 'Job A'
                },
                'b': {
                    'status': 'err',
                    'parents': ['a'],
                    'cluster_id': 2,
                    'display': 'Job B'
                },
                'c': {
                    'status': 'run',
                    'parents': ['a'],
                    'cluster_id': 3,
                    'display': 'Job C'
                },
                'd': {
                    'status': 'sub',
                    'parents': ['a'],
                    'cluster_id': 4,
                    'display': 'Job D'
                },
                'e': {
                    'status': 'pen',
                    'parents': ['c', 'd'],
                    'cluster_id': 5,
                    'display': 'Job E'
                },
                'f': {
                    'status': 'abt',
                    'parents': ['b', ],
                    'cluster_id': 0,
                    'display': 'Job F'
                },
            }

        else:
            nodes = job.condor_object.node_set

            for node in nodes:
                parents = []
                for parent in node.parent_nodes:
                    parents.append(parent.job.name)

                job_name = node.job.name
                display_job_name = job_name.replace('_', ' ').replace('-', ' ').title()
                dag[node.job.name] = {
                    'cluster_id': node.job.cluster_id,
                    'display': display_job_name,
                    'status': CondorWorkflow.STATUS_MAP[node.job.status].lower(),
                    'parents': parents
                }

        success = True
    except Exception as e:
        log.error('The following error occurred when updating details row for job %s: %s', job_id, str(e))
        success = False
        status = None

    return JsonResponse({'success': success, 'status': status, 'dag': dag})


def bokeh_row(request, job_id, type='individual-graph'):
    """
    Returns an embeded bokeh document in json. Javascript can use this method to inject bokeh document to jobs table.
    """
    try:
        job = TethysJob.objects.get_subclass(id=job_id)
        status = job.status

        # Get dashboard link for a given job_id
        scheduler_id = job.scheduler_id
        dask_scheduler = DaskScheduler.objects.get(id=scheduler_id)
        base_link = dask_scheduler.dashboard

        # Append http if not exists
        if 'http' not in base_link:
            base_link = 'http://' + base_link

        # Add forward slash if not exist
        if base_link[-1] != '/':
            base_link = base_link + '/'

        # use bokeh server_document to embed
        url_link = base_link + type
        script = server_document(url_link)

        context = {"the_script": script}
        success = True

    except Exception as e:
        log.error('The following error occurred when getting bokeh chart '
                  'from scheduler {} for job {}: {}'.format(dask_scheduler.name, job_id, str(e)))
        return

    # Render bokeh app into a string to pass in JsonResponse
    html = render_to_string('tethys_gizmos/gizmos/bokeh_application.html', context)
    return JsonResponse({'success': success, 'status': status, 'html': html})


def _parse_value(val):
    if val == 'True':
        return True
    elif val == 'False':
        return False
    else:
        return val
