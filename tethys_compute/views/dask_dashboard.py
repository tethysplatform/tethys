import re
from django.shortcuts import render, reverse
from bokeh.embed import components
from bokeh.client import pull_session
from bokeh.embed import server_document
from tethys_compute.models.dask.dask_scheduler import DaskScheduler


def dask_dashboard(request, dask_scheduler_id, page='status'):
    dask_object = DaskScheduler.objects.get(id=dask_scheduler_id)
    name = dask_object.name
    base_link = dask_object.dashboard

    # Append http(s) if not exists
    if 'http' not in base_link:
        base_link = 'http://' + base_link

    # Add forward slash if not exist
    if base_link[-1] != '/':
        base_link = base_link + '/'

    # Define url link for each page
    url_link = base_link + page
    status_link = reverse('admin:dask_dashboard', kwargs={'page': 'status', 'dask_scheduler_id': dask_scheduler_id})
    workers_link = reverse('admin:dask_dashboard', kwargs={'page': 'workers', 'dask_scheduler_id': dask_scheduler_id})
    tasks_link = reverse('admin:dask_dashboard', kwargs={'page': 'tasks', 'dask_scheduler_id': dask_scheduler_id})
    systems_link = reverse('admin:dask_dashboard', kwargs={'page': 'system', 'dask_scheduler_id': dask_scheduler_id})
    profile_link = reverse('admin:dask_dashboard', kwargs={'page': 'profile', 'dask_scheduler_id': dask_scheduler_id})
    graph_link = reverse('admin:dask_dashboard', kwargs={'page': 'graph', 'dask_scheduler_id': dask_scheduler_id})

    header_link = {"workers_link": workers_link, "tasks_link": tasks_link, "systems_link": systems_link,
                   "profile_link": profile_link, "graph_link": graph_link, "status_link": status_link}

    if page == 'status':
        # Get link for each bokeh application
        url_link_nbytes = base_link + 'individual-nbytes'
        url_link_nprocessing = base_link + 'individual-nprocessing'
        url_link_task_stream = base_link + 'individual-task-stream'
        url_link_progress = base_link + 'individual-progress'

        # Generate script using bokeh server_document method
        nbyte_script = server_document(url_link_nbytes)
        nprocessing_script = server_document(url_link_nprocessing)
        task_stream_script = server_document(url_link_task_stream)
        progress_script = server_document(url_link_progress)

        # get Div ID
        nbyte_id = re.search('id="(.+?)"><', nbyte_script).group(1)
        nprocessing_id = re.search('id="(.+?)"><', nprocessing_script).group(1)
        task_stream_id = re.search('id="(.+?)"><', task_stream_script).group(1)
        progress_id = re.search('id="(.+?)"><', progress_script).group(1)

        context = {"the_name": name, "nbyte_script": nbyte_script, "nprocessing_script": nprocessing_script,
                   "task_stream_script": task_stream_script, "progress_script": progress_script, "nbyte_id": nbyte_id,
                   "nprocessing_id": nprocessing_id, "task_stream_id": task_stream_id, "progress_id": progress_id}

        # add Header link into context
        context.update(header_link)

        return render(request, "tethys_compute/dask_scheduler_status.html", context)

    # For system we have to use session to load because they have many plots inside one application. If we use
    # use server_document, it will look very ugly when load to our page.
    elif page == 'system':
        with pull_session(url=url_link) as session:
            id_dict = {}
            scripts, divs = components({session.document.roots[0].title.text: session.document.roots[0],
                                        session.document.roots[1].title.text: session.document.roots[1],
                                        session.document.roots[2].title.text: session.document.roots[2],
                                        session.document.roots[3].title.text: session.document.roots[3]})
            # Extract out ID for each graph type
            for div in divs:
                id_value = re.search('id="(.+?)"><', divs[div]).group(1)
                id_dict[div.replace(' ', '_')] = {'id': id_value}

            context = {"the_script": scripts, "the_divs": id_dict, "the_name": name}

            # add Header link into context
            context.update(header_link)

            # use the script in the rendered page
            return render(request, "tethys_compute/dask_scheduler_system.html", context)
    else:
        script = server_document(url_link)

        context = {"the_name": name, "the_script": script}

        # Add header link into context
        context.update(header_link)

        if page == 'workers':
            return render(request, "tethys_compute/dask_scheduler_workers.html", context)
        elif page == 'tasks':
            return render(request, "tethys_compute/dask_scheduler_tasks.html", context)
        elif page == 'profile':
            return render(request, "tethys_compute/dask_scheduler_profile.html", context)
        elif page == 'graph':
            return render(request, "tethys_compute/dask_scheduler_graph.html", context)
