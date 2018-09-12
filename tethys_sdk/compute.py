"""
********************************************************************************
* Name: compute.py
* Author: Nathan Swain
* Created On: 7 August 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
# flake8: noqa
# DO NOT ERASE
from tethys_compute.scheduler_manager import list_schedulers, get_scheduler, create_scheduler, \
    create_condor_scheduler, create_dask_scheduler
