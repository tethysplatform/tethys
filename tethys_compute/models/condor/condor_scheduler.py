"""
********************************************************************************
* Name: scheduler
* Author: nswain
* Created On: September 12, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""

from django.db import models
from tethys_compute.models.scheduler import Scheduler


class CondorScheduler(Scheduler):
    """
    Scheduler for Condor jobs.
    """

    port = models.IntegerField(default=22, blank=True, null=True)
    username = models.CharField(max_length=1024, blank=True, null=True)
    password = models.CharField(max_length=1024, blank=True, null=True)
    private_key_path = models.CharField(max_length=1024, blank=True, null=True)
    private_key_pass = models.CharField(max_length=1024, blank=True, null=True)

    class Meta:
        verbose_name = "HTCondor Scheduler"
        verbose_name_plural = "HTCondor Schedulers"
