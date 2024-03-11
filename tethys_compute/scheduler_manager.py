"""
********************************************************************************
* Name: scheduler_manager.py
* Author: Scott Christensen
* Created On: August 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""

from tethys_compute.models import Scheduler
from tethys_compute.models.condor.condor_scheduler import CondorScheduler
from tethys_compute.models.dask.dask_scheduler import DaskScheduler


def list_schedulers():
    """
    Gets a list of all scheduler objects registered in the Tethys Portal

    Returns:
        List of Schedulers
    """
    schedulers = Scheduler.objects.all()
    return schedulers


def get_scheduler(name):
    """
    Gets the scheduler associated with the given name

    Args:
        name (str): The name of the scheduler to return

    Returns:
        The scheduler with the given name or None if no scheduler has the name given.
    """
    schedulers = Scheduler.objects.filter(name=name).select_subclasses()
    if schedulers:
        return schedulers[0]


def create_scheduler(name, host, scheduler_type="condor", **kwargs):
    """
    Creates a new scheduler of the type given.

    Args:
        name (str): The name of the scheduler
        host (str): The hostname or IP address of the scheduler
        scheduler_type (str): Type of scheduler to create. Either 'dask' or 'condor'. Defaults to 'condor'.
        kwargs: Keyword arguments of scheduler-specific options. See: create_dask_scheduler and create_condor_scheduler.

    Returns:
        The newly created scheduler

    Note:
        The newly created scheduler object is not committed to the database.
    """
    if scheduler_type.lower() not in ["dask", "condor"]:
        raise ValueError(
            '"{}" is not a valid scheduler_type. Must be either "dask" or "condor".'.format(
                scheduler_type
            )
        )

    try:
        if scheduler_type.lower() == "dask":
            return create_dask_scheduler(name, host, **kwargs)
        elif scheduler_type.lower() == "condor":
            return create_condor_scheduler(name, host, **kwargs)
    except TypeError:
        raise ValueError(
            "Invalid argument(s) for {} scheduler: {}.".format(
                scheduler_type, ", ".join(kwargs.keys())
            )
        )


def create_condor_scheduler(
    name,
    host,
    username=None,
    password=None,
    private_key_path=None,
    private_key_pass=None,
):
    """
    Creates a new condor scheduler

    Args:
        name (str): The name of the scheduler
        host (str): The hostname or IP address of the scheduler
        username (str, optional): The username to use when connecting to the scheduler
        password (str, optional): The password for the username
        private_key_path (str, optional): The path to the location of the SSH private key file
        private_key_pass (str, optional): The passphrase for the private key

    Returns:
        The newly created condor scheduler

    Note:
        The newly created condor scheduler object is not committed to the database.
    """
    condor_scheduler = CondorScheduler(
        name,
        host,
        username=username,
        password=password,
        private_key_path=private_key_path,
        private_key_pass=private_key_pass,
    )
    return condor_scheduler


def create_dask_scheduler(
    name, host, timeout=None, heartbeat_interval=None, dashboard=None
):
    """
    Creates a new dask scheduler

    Args:
        name (str): The name of the scheduler
        host (str): The hostname or IP address of the scheduler
        timeout (str, optional):
        heartbeat_interval (str, optional):
        dashboard (str, optional):

    Returns:
        The newly created dask scheduler

    Note:
        The newly created dask scheduler object is not committed to the database.
    """
    dask_scheduler = DaskScheduler(
        name,
        host,
        timeout=timeout,
        heartbeat_interval=heartbeat_interval,
        dashboard=dashboard,
    )
    return dask_scheduler
