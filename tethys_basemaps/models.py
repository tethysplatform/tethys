"""
********************************************************************************
* Name: models.py
* Author: Jacob Johnson
* Created On: 2026
* Copyright: (c) Aquaveo 2026
********************************************************************************
"""

from django.db import models

def original_basemap_upload_path(instance, filename):
    return f"basemaps/images/original/{instance.name}/{filename}"

def generated_basemap_upload_path(instance, filename):
    return f"basemaps/images/generated/{instance.name}/{filename}"

def basemap_capture_upload_path(instance, filename):
    return f"basemaps/captures/{filename}"

class PortalBasemap(models.Model):
    class Type(models.TextChoices):
        IMAGE = "image", "Uploaded Image"
        CAPTURE = "capture", "Capture"
        SOURCE = "source", "Source"

    type = models.CharField(max_length=16, choices=Type.choices)
    name = models.CharField(max_length=255, unique=True)
    attribution = models.CharField(max_length=255, blank=True, null=True)
    min_x = models.FloatField(blank=True, null=True)
    min_y = models.FloatField(blank=True, null=True)
    max_x = models.FloatField(blank=True, null=True)
    max_y = models.FloatField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    job = models.ForeignKey(
        "tethys_compute.DaskJob",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
    )
    apps = models.ManyToManyField(
        "tethys_apps.TethysApp",
        blank=True,
        related_name="portal_basemaps"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class PortalBasemapSource(PortalBasemap):
    class BasemapSourceType(models.TextChoices):
        XYZ = "XYZ", "XYZ"
        WMS = "WMS", "WMS"
        OpenStreetMap = "OpenStreetMap", "OpenStreetMap"
        CartoDB = "CartoDB", "CartoDB"
        ESRI = "ESRI", "ESRI"
        AZURE = "Azure", "Azure"
    TYPE = PortalBasemap.Type.SOURCE
    basemap_type = models.CharField(max_length=16, choices=BasemapSourceType.choices)
    options = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        verbose_name = "Portal Basemap"
        verbose_name_plural = "Portal Basemaps"
        ordering = ("name",)

    def as_basemap(self):
        return self.format_options()

    def format_options(self):
        options = {**(self.options or {}), "control_label": self.name}    
        return {self.basemap_type:  options}

class BasemapImage(PortalBasemap):
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        FAILED = 'failed', 'Failed'
        READY = 'ready', 'Ready'
        NEEDS_GEOREFERENCE = 'needs_georeference', 'Needs Georeference'
        CANCELLED = 'cancelled', 'Cancelled'

    MIN_ZOOM = 0
    MAX_ZOOM = 22

    TYPE = PortalBasemap.Type.IMAGE 
    source_file = models.FileField(upload_to=original_basemap_upload_path, blank=True)
    generated_file = models.FileField(upload_to=generated_basemap_upload_path, blank=True, null=True)
    status = models.CharField(max_length=30, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    srs = models.CharField(max_length=64, blank=True, null=True)
    wkt = models.TextField(blank=True, null=True)
    georeference_bounds = models.JSONField(blank=True, null=True)
    georeference_epsg = models.PositiveIntegerField(blank=True, null=True)

class BasemapCapture(PortalBasemap):
    """
    A basemap area saved from a map view as MBTiles
    """

    class StatusChoices(models.TextChoices):
        PROCESSING = "processing", "Processing"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    TILE_CONTENT_TYPES = {"png": "image/png", "jpg": "image/jpeg", "webp": "image/webp"}

    TYPE = PortalBasemap.Type.CAPTURE
    mbtiles_file = models.FileField(upload_to=basemap_capture_upload_path, blank=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.READY,
    )
    source = models.ForeignKey(
        PortalBasemapSource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    secure_source = models.ForeignKey(
        "tethys_services.SecureMapService",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tile_format = models.CharField(max_length=10, default="png")
    min_zoom = models.PositiveSmallIntegerField()
    max_zoom = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ("-created_at",)