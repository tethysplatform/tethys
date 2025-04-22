"""
********************************************************************************
* Name: tethys_compute/views/__init__.py
* Author: Scott Christensen
* Created On: October 2024
* Copyright: (c) Tethys Geoscience Foundation 2024
* License: BSD 2-Clause
********************************************************************************
"""

# flake8: noqa
from .dask_dashboard_view import dask_dashboard
from .update_status import (
    get_job,
    do_job_action,
    update_job_status,
    update_dask_job_status,
)
