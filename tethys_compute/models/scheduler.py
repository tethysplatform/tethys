"""
********************************************************************************
* Name: scheduler
* Author: nswain
* Created On: September 12, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""

from django.db import models
from model_utils.managers import InheritanceManager


class Scheduler(models.Model):
    """
    Generic scheduler.
    """

    objects = InheritanceManager()

    name = models.CharField(max_length=1024)
    host = models.CharField(max_length=1024)

    class Meta:
        verbose_name = "Scheduler"
        verbose_name_plural = "Schedulers"

    def __str__(self):
        return self.name
