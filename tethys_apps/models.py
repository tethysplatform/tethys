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
from model_utils.managers import InheritanceManager
from tethys_compute.utilities import ListField
from tethys_services.models import (DatasetService, SpatialDatasetService,
                                    WebProcessingService, PersistentStoreService)


from tethys_apps.base.persistent_store import TethysFunctionExtractor


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

    def add_settings(self, setting_list):
        """
        Associate setting with app in database
        """
        if setting_list is not None:
            for setting in setting_list:
                setting.tethys_app = self
                setting.save()

    @property
    def settings(self):
        return self.settings_set.select_subclasses()

    @property
    def custom_settings(self):
        return self.settings_set \
                .select_subclasses('customtethysappsetting')

    @property
    def dataset_service_settings(self):
        return self.settings_set \
                .select_subclasses('datasetservicesetting')

    @property
    def spatial_dataset_services_settings(self):
        return self.settings_set \
                .select_subclasses('spatialdatasetservicesetting')

    @property
    def wps_services_settings(self):
        return self.settings_set \
                .select_subclasses('webprocessingservicesetting')

    @property
    def persistent_store_services_settings(self):
        return self.settings_set \
            .select_subclasses('persistentstoreservicesetting')


class TethysAppSetting(models.Model):
    """
    DB Model for Tethys App Settings
    """
    objects = InheritanceManager()

    tethys_app = models.ForeignKey(TethysApp, on_delete=models.CASCADE,
                                   related_name='settings_set')
    name = models.CharField(max_length=200, default='')
    description = models.TextField(max_length=1000, blank=True, default='')
    required = models.BooleanField(default=True)
    initializer = models.CharField(max_length=1000, default='')

    def __unicode__(self):
        return self.name

    @property
    def initializer_function(self):
        """
        The function pointed to by the initializer attribute.

        Returns:
            A handle to a Python function that will initialize the database or None if function is not valid.
        """
        func_ext = TethysFunctionExtractor(self.initializer)
        return func_ext.function

    def initialize(self, first_time):
        """
        Initialize the setting
        """
        self.initializer_function(first_time)


class CustomTethysAppSetting(TethysAppSetting):
    """
    DB Model for Tethys App General Setting
    """
    value = models.CharField(max_length=1000, default='')

    def initialize(self, first_time):
        """
        Initialize the setting
        """
        if first_time:
            self.value = self.initializer


class DatasetServiceSetting(TethysAppSetting):
    """
    DB Model for Tethys App DatasetService Setting
    """
    CKAN = DatasetService.CKAN
    HYSROSHARE = DatasetService.HYDROSHARE

    dataset_service = models.ForeignKey(DatasetService, blank=False, null=True)
    engine = models.CharField(max_length=200,
                              choices=DatasetService.ENGINE_CHOICES,
                              default=DatasetService.CKAN)


class SpatialDatasetServiceSetting(TethysAppSetting):
    """
    DB Model for Tethys App SpatialDatasetService Setting
    """
    GEOSERVER = SpatialDatasetService.GEOSERVER

    spatial_dataset_service = models.ForeignKey(SpatialDatasetService, blank=False, null=True)
    engine = models.CharField(max_length=200,
                              choices=SpatialDatasetService.ENGINE_CHOICES,
                              default=SpatialDatasetService.GEOSERVER)


class WebProcessingServiceSetting(TethysAppSetting):
    """
    DB Model for Tethys App WebProcessingService Setting
    """
    web_processing_service = models.ForeignKey(WebProcessingService, blank=False, null=True)


class PersistentStoreConnectionSetting(TethysAppSetting):
    """
    DB Model for Tethys App PersistentStoreService Setting
    """
    persistent_store_service = models.ForeignKey(PersistentStoreService, blank=False, null=True)


class PersistentStoreDatabaseSetting(TethysAppSetting):
    """
    DB Model for Tethys App PersistentStoreDatabase Setting
    """
    spatial = models.BooleanField(default=False)
    connection = models.ForeignKey(PersistentStoreConnectionSetting, blank=False, null=True)
