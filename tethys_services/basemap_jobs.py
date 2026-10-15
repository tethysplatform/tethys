"""
********************************************************************************
* Name: basemap_jobs.py
* Author: Jacob Johnson
* Created On: 2026
* Copyright: (c) Aquaveo 2026
* License: BSD 2-Clause
********************************************************************************
"""
import logging

from django.conf import settings

log = logging.getLogger(f"tethys.{__name__}")

JOB_LABEL = "tethys_services.basemaps"


def get_basemap_scheduler():
    """
    The Dask scheduler for basemap work, or None to do it without Dask.

    Dask is used only when USE_BASEMAP_UPLOAD_DASK is true and BASEMAP_DASK_SCHEDULER
    names an existing Dask scheduler. Otherwise capture tiles are downloaded in the
    browser and basemap files are processed in Tethys.
    """

    name = getattr(settings, "BASEMAP_DASK_SCHEDULER", None)
    if not name:
        return None

    from tethys_compute.models import DaskScheduler

    scheduler = DaskScheduler.objects.filter(name=name).first()
    if scheduler is None:
        log.warning(
            'USE_BASEMAP_UPLOAD_DASK is true, but no Dask scheduler named "%s" exists; '
            "processing basemaps without Dask.",
            name,
        )
    return scheduler


def run_basemap_task(func, *args, name, user, result_path, apply_inline, use_dask=False, **kwargs):
    """
    Run a basemap task as a DaskJob, or inline when no scheduler is configured.

    On Dask, the task writes its result to ``result_path`` and the record's
    ``refresh_status()`` applies it. Inline, the result goes straight to ``apply_inline``.

    Returns:
        DaskJob or None: the submitted job, or None if the task ran inline.
    """
    if not use_dask:
        apply_inline(func(*args, **kwargs))
        return None
    
    scheduler = get_basemap_scheduler()
    if scheduler is None:
        raise RuntimeError("Dask was requested, but no Dask scheduler is available for basemaps.")

    from tethys_compute.models import DaskJob

    # forget=True: Tethys only tracks the job's status. It never gathers the result
    # or takes its results lock, so nothing blocks or gets stranded.
    job = DaskJob(name=name, user=user, label=JOB_LABEL, scheduler=scheduler, forget=True)
    job.save()

    future = job.client.submit(func, *args, result_path=result_path, pure=False, **kwargs)
    job.execute(future)  # TethysJob.execute swallows errors and sets ERR
    if job._status == "ERR":
        raise RuntimeError(f'Could not submit "{name}" to the Dask scheduler.')
    return job