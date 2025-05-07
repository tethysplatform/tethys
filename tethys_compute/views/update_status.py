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
import logging

from django.http import JsonResponse
from guardian.utils import get_anonymous_user
from channels.db import database_sync_to_async

from tethys_compute.models import TethysJob, DaskJob

from ..tasks import create_task

logger = logging.getLogger(f"tethys.{__name__}")


@database_sync_to_async
def get_job(job_id, user=None):
    """
    Helper method to query a `TethysJob` object safely from an asynchronous context.

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
