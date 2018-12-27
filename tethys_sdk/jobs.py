"""
********************************************************************************
* Name: jobs.py
* Author: Nathan Swain and Scott Christensen
* Created On: 7 August 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
# flake8: noqa
# DO NOT ERASE
from tethys_compute.job_manager import JobManager
from tethys_compute.models import CondorWorkflowJobNode

# Depricated imports
from tethys_compute.job_manager import (
    JobTemplate,
    JOB_TYPES,
    BasicJobTemplate,
    CondorJobTemplate,
    CondorJobDescription,
    CondorWorkflowTemplate,
    CondorWorkflowJobTemplate,
)
