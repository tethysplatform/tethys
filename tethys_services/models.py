from django.db import models
from tethys_dataset_services.valid_engines import VALID_ENGINES, VALID_SPATIAL_ENGINES


# Create your models here.
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
    endpoint = models.CharField(max_length=1024)
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
    endpoint = models.CharField(max_length=1024)
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
    endpoint = models.CharField(max_length=1024)
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Web Processing Service'
        verbose_name_plural = 'Web Processing Services'

    def __unicode__(self):
        return self.name
