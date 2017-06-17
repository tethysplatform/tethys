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


def create_scheduler(name, host, username=None, password=None, private_key_path=None, private_key_pass=None):
    """
    Creates a new scheduler

    Args:
        name (str): The name of the scheduler
        host (str): The hostname or IP address of the scheduler
        username (str, optional): The username to use when connecting to the scheduler
        password (str, optional): The password for the username
        private_key_path (str, optional): The path to the location of the SSH private key file
        private_key_pass (str, optional): The passphrase for the private key

    Returns:
        The newly created scheduler

    Note:
        The newly created scheduler object is not committed to the database.
    """
    scheduler = Scheduler(name, host, username, password, private_key_path, private_key_pass)
    return scheduler
