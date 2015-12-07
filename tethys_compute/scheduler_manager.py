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
    schedulers = Scheduler.objects.filter(name=name)
    if schedulers:
        return schedulers[0]