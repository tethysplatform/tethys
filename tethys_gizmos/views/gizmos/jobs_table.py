import logging

from django.http import JsonResponse
from django.template.loader import render_to_string
from tethys_compute.models import TethysJob, CondorWorkflow, DaskJob, DaskScheduler
from tethys_gizmos.gizmo_options.jobs_table import JobsTable
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


def terminate(request, job_id):
    try:
        job = TethysJob.objects.get_subclass(id=job_id)
        job.stop()
        success = True
        message = ''
    except Exception as e:
        success = True
        message = str(e)
        log.error('The following error occurred when terminating job %s: %s', job_id, message)
    return JsonResponse({'success': success, 'message': message})


def delete(request, job_id):
    try:
        job = TethysJob.objects.get_subclass(id=job_id)
        job.clean_on_delete = True
        job.delete()
        success = True
        message = ''
    except Exception as e:
        success = True
        message = str(e)
        log.error('The following error occurred when deleting job %s: %s', job_id, message)
    return JsonResponse({'success': success, 'message': message})


def resubmit(request, job_id):
    try:
        job = TethysJob.objects.get_subclass(id=job_id)
        # Resubmit the Job.
        job.resubmit()

        success = True
        message = ''
    except Exception as e:
        success = True
        message = str(e)
        log.error('The following error occurred when resubmiting job %s: %s', job_id, message)
    return JsonResponse({'success': success, 'message': message})


def show_log(request, job_id):
    try:
        job = TethysJob.objects.get_subclass(id=job_id)
        # Get the Job logs.
        data = job.get_logs()

        def replace_new_lines(d):
            for k, v in d.items():
                if isinstance(v, str):
                    d[k] = v.replace('\n', '<br/>')
                elif isinstance(v, dict):
                    replace_new_lines(v)

        replace_new_lines(data)

        success = True

        return JsonResponse({'success': success, 'data': data})
    except Exception as e:
        success = False
        message = str(e)
        log.error('The following error occurred when retrieving log for job %s: %s', job_id, message)

        return JsonResponse({'success': success})


def update_row(request, job_id):
    filters = []

    try:
        data = {key: _parse_value(val) for key, val in request.POST.items()}

        # parse out dictionaries from POST items
        keys = [k.split('[') for k in data.keys() if '[' in k]
        for name, key in keys:
            data.setdefault(name, {})
            data[name][key.strip(']')] = _parse_value(data.pop(f'{name}[{key}'))

        filter_string = data.pop('column_fields')
        filters = [f.strip('\'\" ') for f in filter_string.strip('[]').split(',')]
        job = TethysJob.objects.get_subclass(id=job_id)
        status = job.status
        statuses = None
        if status in ['Various', 'Various-Complete']:
            # Hard code statues for the gizmo showcase
            if job.label == 'gizmos_showcase':
                if isinstance(job, CondorWorkflow):
                    statuses = {'Completed': 20, 'Error': 20, 'Running': 40, 'Aborted': 0}
                else:
                    statuses = {'Completed': 40, 'Error': 10, 'Running': 30, 'Aborted': 5}
                    if status == 'Various-Complete':
                        statuses = {'Completed': 80, 'Error': 15, 'Running': 0, 'Aborted': 5}
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

        data.update({'job': job, 'job_id': job.id, 'row': row, 'column_fields': filters, 'job_status': status,
                     'job_statuses': statuses, 'delay_loading_status': False})
        success = True
        html = render_to_string('tethys_gizmos/gizmos/job_row.html', data)
    except Exception as e:
        error_msg = 'Updating row for job {} failed: {}'.format(job_id, str(e))
        log.warning(error_msg)
        user_friendly_error = 'An unexpected error occurred while updating this row. Press the "Refresh Status" ' \
                              'button to update the row manually.'
        success = False
        status = None
        html = render_to_string('tethys_gizmos/gizmos/job_row_error.html',
                                {
                                    'job_id': job_id,
                                    'error_msg': user_friendly_error,
                                    'num_cols': len(filters) if filters else 1
                                })

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
    if val in ('True', 'true'):
        return True
    elif val in ('False', 'false'):
        return False
    else:
        return val
