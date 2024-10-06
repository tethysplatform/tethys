"""
********************************************************************************
* Name: update_status.py
* Author: Scott Christensen
* Created On: 2024
* Copyright: (c) Tethys Geospatial Foundation 2024
* License: BSD 2-Clause
********************************************************************************
"""

import asyncio
import logging

from django.http import JsonResponse
from channels.db import database_sync_to_async

from tethys_compute.models import TethysJob, DaskJob

from ..tasks import create_task

logger = logging.getLogger(f"tethys.{__name__}")


@database_sync_to_async
def get_job(job_id, user=None):
    if (
        user is None
        or user.is_staff
        or user.has_perm("tethys_compute.jobs_table_actions")
    ):
        return TethysJob.objects.get_subclass(id=job_id)
    return TethysJob.objects.get_subclass(id=job_id, user=user)


async def do_job_action(job, action):
    func = getattr(job, action)
    if asyncio.iscoroutinefunction(func):
        ret = await func()
        await job.safe_close()
    else:
        ret = await database_sync_to_async(func)()
    return ret


async def _update_job_status(job_id):
    try:
        job = await get_job(job_id)
        await do_job_action(job, "update_status")
        return True
    except Exception as e:
        logger.warning(
            f"The following exception occurred while updating the status of job_id={job_id}: {e}"
        )
        logger.exception(e)
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
            logger.exception(e)
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
