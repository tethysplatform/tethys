"""
********************************************************************************
* Name: update_status.py
* Author: Scott Christensen
* Created On: 2024
* Copyright: (c) Tethys Geoscience Foundation 2024
* License: BSD 2-Clause
********************************************************************************
"""

import asyncio
import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from guardian.utils import get_anonymous_user
from channels.db import database_sync_to_async

from tethys_compute.models import TethysJob, DaskJob

from ..tasks import create_task

logger = logging.getLogger(f"tethys.{__name__}")


def _get_job_sync(job_id, user=None):
    """
    Helper method to query a `TethysJob` object.

    Args:
        job_id: database ID of a `TethysJob`
        user: django user object. If `None` then permission are not checked. Default=None

    Returns: `TethysJob` object

    """
    if user is not None and user.is_anonymous:
        user = get_anonymous_user()
    if (
        user is None
        or user.is_staff
        or user.has_perm("tethys_compute.jobs_table_actions")
    ):
        return TethysJob.objects.get_subclass(id=job_id)
    return TethysJob.objects.get_subclass(id=job_id, user=user)


# The async views query through this; `report_job_status` is sync and calls the
# implementation directly.
get_job = database_sync_to_async(_get_job_sync)


async def do_job_action(job, action):
    """
    Helper function to call job actions from an asynchronous context.
    Handles both sync methods and coroutine job actions.

    Args:
        job: `TethysJob` object
        action (str): name of method to call (without arguments) on the  `job`

    Returns: return value of `action`

    """
    func = getattr(job, action)
    if asyncio.iscoroutinefunction(func):
        ret = await func()
        await job.safe_close()
    else:
        ret = await database_sync_to_async(func)()
    return ret


async def _update_job_status(job_id):
    """
    Helper method to update a jobs status as a task (with delayed execution).

    Args:
        job_id: database ID for a `TethysJob`

    Returns: `True` if status was successfully updated, `False` otherwise.

    """
    try:
        job = await get_job(job_id)
        await do_job_action(job, "update_status")
        return True
    except Exception as e:
        logger.warning(
            f"The following exception occurred while updating the status of job_id={job_id}: {e}"
        )
        return False


async def update_job_status(request, job_id):
    """
    Callback endpoint for jobs to update status.
    """
    delay = request.GET.get("delay")
    if delay:
        logger.debug(
            f"Updating the status of job_id={job_id} after {delay} second delay."
        )
        try:
            delay = int(delay)
            create_task(_update_job_status, job_id, delay=delay)
            result = "scheduled"
        except Exception as e:
            logger.warning(
                f"The following exception occurred while scheduling the status update of job_id={job_id}: {e}"
            )
            result = False
    else:
        result = await _update_job_status(job_id)

    return JsonResponse({"success": result})


@csrf_exempt
def report_job_status(request, job_id):
    """Callback endpoint for reporting a job's status to the portal.

    Unlike ``update_job_status``, which asks the job's source what the status is,
    this accepts the status from whoever already knows it. For condor jobs that is
    a process alongside the scheduler, which can see evictions and holds that a
    job cannot report about itself, and which reaches the queue locally rather
    than over SSH.

    Requires ``token`` to be the job's ``status_report_token``, which authorises
    reports for that job and no other. Note that for condor jobs the token travels
    in a job ad, which any user who can query the scheduler can read, so a report is
    only as trustworthy as the pool.

    A report may not move a job out of a terminal status; such a report is refused
    with 409 rather than reviving a finished job.

    Query parameters:
        token: the job's status report token.
        status: a valid status code or display name.
        node_statuses: optional JSON object of condorpy job name -> condor status
            name, persisted so the workflow's DAG can be rendered without asking
            the scheduler about each node.

    Returns:
        JsonResponse: always ``success``; on success also ``nodes_applied`` (how many
            nodes the reported statuses matched) and ``post_processing`` (False when
            the status was recorded but the work following it raised). On refusal,
            ``error``, with 403 (token), 400 (status), 404 (job) or 409 (finished).
    """
    params = request.GET
    token = params.get("token")
    status = params.get("status")

    if TethysJob.id_from_status_report_token(token) != str(job_id):
        logger.warning(f"Rejected a status report for job_id={job_id}: bad token.")
        return JsonResponse({"success": False, "error": "invalid token"}, status=403)

    if status not in TethysJob.VALID_STATUSES + TethysJob.DISPLAY_STATUSES:
        return JsonResponse(
            {"success": False, "error": f"invalid status: {status}"}, status=400
        )

    try:
        job = _get_job_sync(job_id)
    except Exception:
        return JsonResponse({"success": False, "error": "no such job"}, status=404)

    # Reports can arrive out of order, and reviving a finished job is not a harmless
    # display error: the next poll re-reaches the terminal status with a non-terminal
    # one recorded, so update_status treats it as a fresh completion and processes the
    # results a second time -- for condor, syncing the remote output again.
    # ``is_terminal`` rather than a check against TERMINAL_STATUS_CODES because a
    # custom terminal status is stored as OTH; only a reported status can be trusted
    # to be one of the standard codes, since the endpoint rejects anything else above.
    reported_code = TethysJob.REVERSE_STATUSES.get(status, status)
    if job.is_terminal and reported_code not in TethysJob.TERMINAL_STATUS_CODES:
        logger.warning(
            f"Refused a report of {status} for job_id={job_id}: it already finished "
            f"as {job.cached_status}."
        )
        return JsonResponse(
            {"success": False, "error": "job has already finished"}, status=409
        )

    nodes_applied = 0
    node_statuses = params.get("node_statuses")
    if node_statuses:
        try:
            nodes_applied = len(job.apply_node_statuses(json.loads(node_statuses)))
        except Exception as e:
            logger.warning(
                f"Could not apply reported node statuses for job_id={job_id}: {e}"
            )

    # The status is recorded even when the work that follows a terminal status
    # fails, so a transient problem syncing results does not leave the portal
    # believing the job is still running.
    try:
        job.update_status(status=status)
        return JsonResponse(
            {"success": True, "nodes_applied": nodes_applied, "post_processing": True}
        )
    except Exception as e:
        logger.exception(
            f"Status {status} was recorded for job_id={job_id} but the work that "
            f"follows it did not complete: {e}"
        )
        return JsonResponse(
            {"success": True, "nodes_applied": nodes_applied, "post_processing": False}
        )


def update_dask_job_status(request, key):
    """
    Callback endpoint for dask jobs to update status.
    """
    params = request.GET
    status = params.get("status", None)
    logger.debug(f"Received update status for DaskJob<key: {key} status: {status}>")

    try:
        job = DaskJob.objects.filter(key=key)[0]
        job_status = job.DASK_TO_STATUS_TYPES[status]
        logger.debug(
            f'Mapped dask status "{status}" to tethys job status: "{job_status}"'
        )
        job.status = job_status
        json = {"success": True}
    except Exception:
        json = {"success": False}

    return JsonResponse(json)
