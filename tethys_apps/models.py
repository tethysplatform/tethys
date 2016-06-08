"""
********************************************************************************
* Name: models.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from django.db import models
from tethys_compute.utilities import ListField


class TethysApp(models.Model):
    """
    DB Model for Tethys Apps
    """
    # The package is enforced to be unique by the file system
    package = models.CharField(max_length=200, unique=True, default='')

    # Portal admin first attributes
    name = models.CharField(max_length=200, default='')
    description = models.TextField(max_length=1000, blank=True, default='')
    enable_feedback = models.BooleanField(default=False)
    feedback_emails = ListField(default='', blank=True)
    tags = models.CharField(max_length=200, blank=True,  default='')

    # Developer first attributes
    index = models.CharField(max_length=200, default='')
    icon = models.CharField(max_length=200, default='')
    root_url = models.CharField(max_length=200, default='')
    color = models.CharField(max_length=10, default='')

    # Portal admin only attributes
    enabled = models.BooleanField(default=True)
    show_in_apps_library = models.BooleanField(default=True)

    class Meta:
        permissions = (
            ('view_app', 'Can see app in library'),
            ('access_app', 'Can access app'),
        )
        verbose_name = 'Tethys App'
        verbose_name_plural = 'Installed Apps'

    def __unicode__(self):
        return unicode(self.name)


