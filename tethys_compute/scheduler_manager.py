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
    schedulers = Scheduler.objects.all()
    return schedulers

def get_scheduler(name):
    schedulers = Scheduler.objects.filter(name=name)
    return schedulers[0]