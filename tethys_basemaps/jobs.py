"""
********************************************************************************
* Name: jobs.py
* Author: Jacob Johnson
* Created On: 2026
* Copyright: (c) Aquaveo 2026
********************************************************************************
"""

import contextlib
import json
import logging
import os

from django.conf import settings

log = logging.getLogger(f"tethys.{__name__}")

JOB_LABEL = "tethys_basemaps"


def run_basemap_task(
    func,
    *args,
    name,
    user,
    result_path,
    non_dask_result_handler,
    dask_scheduler=None,
    **kwargs,
):
    """
    Run a basemaps generation task using either dask or on the server inline.

    Returns:
        DaskJob or None: the submitted job, or None if the task ran inline.
    """
    if dask_scheduler is None:
        non_dask_result_handler(func(*args, **kwargs))
        return None

    import cloudpickle
    from tethys_compute.models import DaskJob
    from . import tasks

    # Send task code to dask runner
    cloudpickle.register_pickle_by_value(tasks)

    job = DaskJob(
        name=name, user=user, label=JOB_LABEL, scheduler=dask_scheduler, forget=True
    )
    job.save()

    future = job.client.submit(
        func, *args, result_path=result_path, pure=False, **kwargs
    )
    job.execute(future)
    if job._status == "ERR":
        raise RuntimeError(f'Could not submit "{name}" to the Dask scheduler.')
    return job


def delete_safely(path):
    if path:
        with contextlib.suppress(FileNotFoundError):
            os.remove(path)


def _dask_task_state(job):
    """
    The job's task state straight from the Dask scheduler: (state, error).
    """
    from .tasks import dask_task_state

    if not job.key or job.scheduler is None:
        return "unknown", None
    try:
        client = job.scheduler.client
    except Exception:
        log.exception("Could not connect to the Dask scheduler for job %s", job.pk)
        return "unknown", None
    try:
        return tuple(client.run_on_scheduler(dask_task_state, key=job.key))
    except Exception:
        log.exception("Could not get the state of Dask task %s", job.key)
        return "unknown", None
    finally:
        client.close()


def refresh_from_result_file(record, apply_result, job_type):
    """
    Applies the task's result file if it has appeared. Otherwise get the state of the dask

    job_type names the job in error messages, e.g. "generation" or "capture".
    """
    progress_path = getattr(record, "progress_path", None)

    def apply_if_ready():
        path = record.result_path
        try:
            with open(path) as fh:
                result = json.load(fh)
        except (TypeError, FileNotFoundError):
            # No result file found
            return False
        apply_result(result)
        # Delete the result and progress files after applying the result
        delete_safely(path)
        delete_safely(progress_path)
        return True

    if apply_if_ready():
        return

    # If the result file isn't ready, check the status of the task
    job = record.job if record.job_id else None
    if job is None:
        return

    state, error = _dask_task_state(job)
    if state == "erred":
        message = f"The {job_type} job failed on the Dask worker." + (
            f"\n{error}" if error else ""
        )
    elif state is None:
        # If the state is None, the task may have finished, so check for the results file
        if apply_if_ready():
            return
        message = (
            f"The {job_type} job finished without writing a result file. Check that the Dask workers "
            "share the Tethys media directory at the same path, and that the Dask scheduler "
            "wasn't restarted mid-job."
        )
    else:
        return  # Task is still running or is in the queue, or can't reach the scheduler right now

    # Mark the record as failed if it's still processing, and get rid of the progress file.
    type(record).objects.filter(pk=record.pk, status="processing").update(
        status="failed", error_message=message
    )
    delete_safely(progress_path)
    record.refresh_from_db()


def cancel_dask_task(job):
    """
    Cancel the job's task in Dask if it hasn't started yet.
    """
    if not job.key or job.scheduler is None:
        return
    try:
        client = job.scheduler.client
    except Exception:
        log.exception(f"Could not connect to the Dask scheduler to cancel job {job.pk}")
        return
    try:
        from dask.distributed import Future

        client.cancel(Future(job.key, client=client), force=True)
    except Exception:
        log.exception(f"Could not cancel Dask task {job.key}")
    finally:
        client.close()
