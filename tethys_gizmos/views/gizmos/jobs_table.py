"""
********************************************************************************
* Name: jobs_table.py
* Author: Scott Christensen
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

import inspect
import logging
import re

from django.http import JsonResponse
from django.template.loader import render_to_string
from channels.db import database_sync_to_async

from tethys_apps.decorators import async_login_required
from tethys_compute.models import CondorWorkflow, DaskJob, DaskScheduler
from tethys_gizmos.gizmo_options.jobs_table import JobsTable
from tethys_sdk.gizmos import SelectInput
from tethys_portal.optional_dependencies import optional_import
from tethys_compute.views import get_job, do_job_action

# optional imports
server_document = optional_import("server_document", from_module="bokeh.embed")

logger = logging.getLogger(f"tethys.{__name__}")


async def _get_log_content(job, key1, key2):
    # Get the Job logs.
    if inspect.iscoroutinefunction(job.get_logs):
        data = await job.get_logs()
        needs_safe_close = True
    else:
        data = await database_sync_to_async(job.get_logs)()
        needs_safe_close = False

    log_func = data[key1]
    if key2 is not None:
        log_func = log_func[key2]
    if callable(log_func):
        if inspect.iscoroutinefunction(log_func):
            content = await log_func()
            needs_safe_close = True
        else:
            content = await database_sync_to_async(log_func)()
    else:
        content = log_func

    if needs_safe_close:
        await job.safe_close()
    return content


@database_sync_to_async
def get_dask_scheduler(scheduler_id):
    return DaskScheduler.objects.get(id=scheduler_id)


def _display_node_name(job_name):
    """The node name as shown in the diagram."""
    return job_name.replace("_", " ").replace("-", " ").title()


def _persisted_dag_nodes(job):
    """Each node's name, status, cluster id and parent names, from the database.

    Names are the CondorPy job name, the same as the live source uses, so a workflow
    whose node names contain spaces produces the same keys whichever source served it.
    Condor assigns cluster ids at submit time and does not persist them; nothing reads
    them, and fetching them would need the remote connection this path exists to avoid.
    """
    nodes = list(job.node_set.select_subclasses().prefetch_related("parent_nodes"))
    names = {node.pk: node.job.name for node in nodes}

    for node in nodes:
        yield (
            names[node.pk],
            node.cached_node_status or "Unexpanded",
            None,
            [names.get(p.pk, p.name) for p in node.parent_nodes.all()],
        )


def _live_dag_nodes(job):
    """The same, read from the scheduler: a connection plus one query per node."""
    for node in job.condor_object.node_set:
        yield (
            node.job.name,
            node.job.status,
            node.job.cluster_id,
            [parent.job.name for parent in node.parent_nodes],
        )


@database_sync_to_async
def get_condor_job_nodes(job):
    """Build the DAG for a CondorWorkflow.

    Assembled from the database while persisted statuses are current -- statuses from
    ``CondorWorkflowNode.cached_node_status``, topology from the node rows themselves.
    A node with no persisted status has not been expanded by DAGMan yet and is reported
    as ``Unexpanded``.

    Only where the rows come from differs between the two sources; the shape they are
    turned into is built in one place, so the two cannot drift apart.
    """
    nodes = _persisted_dag_nodes if job.node_statuses_are_current else _live_dag_nodes

    return {
        name: {
            "cluster_id": cluster_id,
            "display": _display_node_name(name),
            # Defaulted rather than indexed: a persisted status comes from a remote
            # reporter, and one condor does not define must not take the diagram down.
            "status": CondorWorkflow.STATUS_MAP.get(status, "SUB").lower(),
            "parents": parents,
        }
        for name, status, cluster_id, parents in nodes(job)
    }


@database_sync_to_async
def get_job_statuses(job):
    """Percentage of the workflow in each status.

    The denominator has to match whatever the counts were taken from.
    ``cached_node_statuses`` buckets every node row, so its values already sum to the node
    count -- no second query for it. Reading ``num_jobs`` there would build the
    condorpy workflow, which means a connection to the scheduler on every poll, the
    cost this path exists to avoid.
    """
    num_statuses = 0
    statuses = {"Completed": 0, "Error": 0, "Running": 0, "Aborted": 0}
    if job.node_statuses_are_current:
        node_statuses = job.cached_node_statuses
        total = sum(node_statuses.values())
    else:
        node_statuses = job.statuses
        total = job.num_jobs

    for key, value in node_statuses.items():
        if key in statuses:
            num_statuses += value
            statuses[key] = float(value) / float(total or 1) * 100.0

    return statuses, num_statuses


@async_login_required
async def perform_action(
    request, job_id, action, success_message="", error_message=None
):
    try:
        job = await get_job(job_id, request.user)
        await do_job_action(job, action)
        success = True
        message = success_message
    except Exception as e:
        success = False
        logger.error(
            f'The following error occurred when running "{action}" on job {job_id}: {str(e)}'
        )
        message = error_message or f"Unable to {action} job {job_id}."
    return JsonResponse({"success": success, "message": message})


async def resubmit(request, job_id):
    return await perform_action(
        request, job_id, "resubmit", f"Successfully resubmitted job: {job_id}."
    )


@async_login_required
async def delete(request, job_id):
    try:
        job = await get_job(job_id, request.user)
        job.clean_on_delete = True
        await do_job_action(job, "delete")
        success = True
        message = ""
    except Exception as e:
        success = False
        message = str(e)
        logger.error(
            f"The following error occurred when deleting job {job_id}: {message}"
        )
    return JsonResponse({"success": success, "message": message})


@async_login_required
async def show_log(request, job_id):
    try:
        job = await get_job(job_id, request.user)
        # Get the Job logs.
        data = await do_job_action(job, "get_logs")

        sub_job_options = [(k, k) for k in data.keys()]
        sub_job_select = SelectInput(
            display_text="Select Log:",
            name="sub_job_select",
            multiple=False,
            options=sub_job_options,
            attributes={"data-job-id": job_id},
        )

        context = {"sub_job_select": sub_job_select, "log_options": {}}

        for k, v in data.items():
            if isinstance(v, dict):
                context["log_options"][f"log_select_{k}"] = SelectInput(
                    name=f"log_{k}",
                    multiple=False,
                    options=[(key, key) for key in v.keys()],
                )

        html = render_to_string("tethys_gizmos/gizmos/job_logs.html", context)

        def remove_callables(item):
            if callable(item):
                return
            elif isinstance(item, dict):
                for k, v in item.items():
                    item[k] = remove_callables(v)
                return item
            else:
                return item.replace("\n", "<br/>")

        log_contents = remove_callables(data)

        return JsonResponse(
            {"success": True, "html": html, "log_contents": log_contents}
        )
    except Exception as e:
        logger.exception(e)
        message = str(e)
        logger.error(
            "The following error occurred when retrieving logs for job %s: %s",
            job_id,
            message,
        )

        return JsonResponse(
            {
                "success": False,
                "error_message": "ERROR: An error occurred while retrieving job logs.",
            }
        )


@async_login_required
async def get_log_content(request, job_id, key1, key2=None):
    try:
        job = await get_job(job_id, request.user)
        # Get the Job logs.
        content = await _get_log_content(job, key1, key2)

        return JsonResponse({"success": True, "content": content})
    except Exception as e:
        if key2 is None:
            key2 = ""  # for error message formatting
        message = str(e)
        logger.error(
            "The following error occurred when retrieving log content for log %s in job %s: %s",
            job_id,
            f"{key1} {key2}",
            message,
        )
        return JsonResponse(
            {
                "success": False,
                "error_message": f"ERROR: An error occurred while retrieving log content for: {key1} {key2}",
            },
        )


@async_login_required
async def update_row(request, job_id):
    data = reconstruct_post_dict(request)
    try:
        job = await get_job(job_id, request.user)
        await do_job_action(job, "update_status")
        status = job.cached_status
        status_msg = job.status_message
        statuses = None
        if status in ["Various", "Various-Complete"]:
            # Hard code statues for the gizmo showcase
            if job.label == "gizmo_showcase":
                if isinstance(job, CondorWorkflow):
                    statuses = {
                        "Completed": 20,
                        "Error": 20,
                        "Running": 40,
                        "Aborted": 0,
                    }
                else:
                    statuses = {
                        "Completed": 40,
                        "Error": 10,
                        "Running": 30,
                        "Aborted": 5,
                    }
                    if status == "Various-Complete":
                        statuses = {
                            "Completed": 80,
                            "Error": 15,
                            "Running": 0,
                            "Aborted": 5,
                        }
            elif isinstance(job, CondorWorkflow):
                statuses, num_statuses = await get_job_statuses(job)

                # Handle case with CondorWorkflows where DAG has started working,
                # but jobs have not necessarily started yet.
                if isinstance(job, CondorWorkflow) and not num_statuses:
                    status = "Submitted"

        if isinstance(job, DaskJob):
            # Display results ready as running on jobs table
            if status == "Results-Ready":
                status = "Running"

        row = JobsTable.get_row(
            job, data["column_fields"], data.get("actions"), delay_loading_status=True
        )
        data.update(
            {
                "job": job,
                "row": row,
                "job_status": status,
                "job_statuses": statuses,
                "delay_loading_status": False,
                "error_message": status_msg,
            }
        )
        success = True
        html = render_to_string("tethys_gizmos/gizmos/job_row.html", data)
    except Exception as e:
        error_msg = "Updating row for job {} failed: {}".format(job_id, str(e))
        logger.warning(error_msg)
        user_friendly_error = (
            'An unexpected error occurred while updating this row. Press the "Refresh Status" '
            "button to update the row manually."
        )
        success = False
        status = None
        html = render_to_string(
            "tethys_gizmos/gizmos/job_row_error.html",
            {
                "job_id": job_id,
                "error_msg": user_friendly_error,
                "num_cols": len(data.get("column_fields", [1])),
            },
        )

    return JsonResponse({"success": success, "status": status, "html": html})


@async_login_required
async def update_workflow_nodes_row(request, job_id):
    dag = {}
    try:
        job = await get_job(job_id, request.user)
        await do_job_action(job, "update_status")
        status = job.cached_status

        # Hard code example for gizmo_showcase
        if job.label == "gizmo_showcase":
            dag = {
                "a": {
                    "status": "com",
                    "parents": [],
                    "cluster_id": 1,
                    "display": "Job A",
                },
                "b": {
                    "status": "err",
                    "parents": ["a"],
                    "cluster_id": 2,
                    "display": "Job B",
                },
                "c": {
                    "status": "run",
                    "parents": ["a"],
                    "cluster_id": 3,
                    "display": "Job C",
                },
                "d": {
                    "status": "sub",
                    "parents": ["a"],
                    "cluster_id": 4,
                    "display": "Job D",
                },
                "e": {
                    "status": "pen",
                    "parents": ["c", "d"],
                    "cluster_id": 5,
                    "display": "Job E",
                },
                "f": {
                    "status": "abt",
                    "parents": [
                        "b",
                    ],
                    "cluster_id": 0,
                    "display": "Job F",
                },
            }

        else:
            dag = await get_condor_job_nodes(job)

        success = True
    except Exception as e:
        logger.error(
            "The following error occurred when updating details row for job %s: %s",
            job_id,
            str(e),
        )
        success = False
        status = None

    return JsonResponse({"success": success, "status": status, "dag": dag})


@async_login_required
async def bokeh_row(request, job_id, type="individual-graph"):
    """
    Returns an embeded bokeh document in json. Javascript can use this method to inject bokeh document to jobs table.
    """
    try:
        job = await get_job(job_id, request.user)
        await do_job_action(job, "update_status")
        status = job.cached_status

        # Get dashboard link for a given job_id
        scheduler_id = job.scheduler_id
        dask_scheduler = await get_dask_scheduler(scheduler_id)
    except Exception as e:
        logger.error(
            "The following error occurred when getting Dask "
            "scheduler for job {}: {}".format(job_id, str(e))
        )
        return
    try:
        base_link = dask_scheduler.dashboard

        # Append http if not exists
        if "http" not in base_link:
            base_link = "http://" + base_link

        # Add forward slash if not exist
        if base_link[-1] != "/":
            base_link = base_link + "/"

        # use bokeh server_document to embed
        url_link = base_link + type
        script = server_document(url_link)

        context = {"the_script": script}
        success = True

    except Exception as e:
        logger.error(
            "The following error occurred when getting bokeh chart "
            "from scheduler {} for job {}: {}".format(
                dask_scheduler.name, job_id, str(e)
            )
        )
        return

    # Render bokeh app into a string to pass in JsonResponse
    html = render_to_string("tethys_gizmos/gizmos/bokeh_application.html", context)
    return JsonResponse({"success": success, "status": status, "html": html})


def _parse_value(val):
    if val in ("True", "true"):
        return True
    elif val in ("False", "false"):
        return False
    elif val.startswith("["):
        return [f.strip("'\" ") for f in val.strip("[]").split(",")]
    else:
        return val


def reconstruct_post_dict(request):
    data = {key: _parse_value(val) for key, val in request.POST.items()}
    # parse out dictionaries from POST items
    parts = [re.split("[][]+", k)[:-1] for k in data.keys() if "[" in k]  # noqa: W605
    for p in parts:
        name = p[0]
        keys = p[1:]
        value = data.pop(f"{name}{''.join([f'[{k}]' for k in keys])}")
        data.setdefault(name, {})
        d = data[name]
        for k in keys[:-1]:
            d.setdefault(k, {})
            d = d[k]
        d[keys[-1]] = value
    return data
