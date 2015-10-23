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
from django.core.exceptions import ValidationError
from tethys_dataset_services.valid_engines import VALID_ENGINES, VALID_SPATIAL_ENGINES


def validate_url(value):
    """
    Validate URLs
    """
    if 'http://' not in value and 'https://' not in value:
        raise ValidationError('Invalid Endpoint: Must be prefixed with "http://" or "https://".')


def validate_dataset_service_endpoint(value):
    """
    Validator for dataset service endpoints
    """
    validate_url(value)

    if '/api/3/action' not in value and '/hsapi' not in value:
        raise ValidationError('Invalid Endpoint: CKAN endpoints follow the pattern "http://example.com/api/3/action" '
                              'and HydroShare endpoints must follow the pattern "http://example.com/hsapi"')


def validate_spatial_dataset_service_endpoint(value):
    """
    Validator for spatial dataset service endpoints
    """
    validate_url(value)

    if '/geoserver/rest' not in value:
        raise ValidationError('Invalid Endpoint: GeoServer endpoints follow the pattern "http://example.com/geoserver/rest".')


def validate_wps_service_endpoint(value):
    """
    Validator for spatial dataset service endpoints
    """
    validate_url(value)

    if '/wps/WebProcessingService' not in value:
        raise ValidationError('Invalid Endpoint: 52 North WPS endpoints follow the pattern "http://example.com/wps/WebProcessingService".')


class DatasetService(models.Model):
    """
    ORM for Dataset Service settings.
    """
    # Define default values for engine choices
    CKAN = VALID_ENGINES['ckan']
    HYDROSHARE = VALID_ENGINES['hydroshare']

    # Define default choices for engine selection
    ENGINE_CHOICES = (
        (CKAN, 'CKAN'),
        (HYDROSHARE, 'HydroShare')
    )

    name = models.CharField(max_length=30, unique=True)
    engine = models.CharField(max_length=200, choices=ENGINE_CHOICES, default=CKAN)
    endpoint = models.CharField(max_length=1024, validators=[validate_dataset_service_endpoint])
    public_endpoint = models.CharField(max_length=1024, validators=[validate_dataset_service_endpoint], blank=True)
    apikey = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Dataset Service'
        verbose_name_plural = 'Dataset Services'

    def __unicode__(self):
        return self.name


class SpatialDatasetService(models.Model):
    """
    ORM for Spatial Dataset Service settings.
    """
    GEOSERVER = VALID_SPATIAL_ENGINES['geoserver']

    ENGINE_CHOICES = (
        (GEOSERVER, 'GeoServer'),
    )

    name = models.CharField(max_length=30, unique=True)
    engine = models.CharField(max_length=200, choices=ENGINE_CHOICES, default=GEOSERVER)
    endpoint = models.CharField(max_length=1024, validators=[validate_spatial_dataset_service_endpoint])
    public_endpoint = models.CharField(max_length=1024, validators=[validate_spatial_dataset_service_endpoint], blank=True)
    apikey = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Spatial Dataset Service'
        verbose_name_plural = 'Spatial Dataset Services'

    def __unicode__(self):
        return self.name


class WebProcessingService(models.Model):
    """
    ORM for Web Processing Services settings.
    """
    name = models.CharField(max_length=30, unique=True)
    endpoint = models.CharField(max_length=1024, validators=[validate_wps_service_endpoint])
    public_endpoint = models.CharField(max_length=1024, validators=[validate_wps_service_endpoint], blank=True)
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Web Processing Service'
        verbose_name_plural = 'Web Processing Services'

    def __unicode__(self):
        return self.name
