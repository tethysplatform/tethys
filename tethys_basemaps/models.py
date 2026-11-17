"""
********************************************************************************
* Name: models.py
* Author: Jacob Johnson
* Created On: 2026
* Copyright: (c) Aquaveo 2026
********************************************************************************
"""

from django.conf import settings
from django.db import models, transaction

from tethys_compute.models import DaskScheduler

from .jobs import refresh_from_result_file

import os
from pathlib import Path


# Files a generated image run uses
IMAGE_RUN_SUFFIXES = (".partial", ".result.json", ".cancel")

def original_basemap_upload_path(instance, filename):
    return f"basemaps/images/original/{instance.name}/{filename}"

def generated_basemap_upload_path(instance, filename):
    return f"basemaps/images/generated/{instance.name}/{filename}"

def basemap_capture_upload_path(instance, filename):
    return f"basemaps/captures/{filename}"



def image_generation_run_output_name(image):
    """
    A storage name for a new generation run's COG that no earlier run's files use.

    Like unique_capture_output_name: a cancelled run never creates its COG, so
    get_available_name alone would hand its leftover cancel flag to the next run.
    """
    from django.core.files.storage import default_storage

    stem = generated_basemap_upload_path(image, Path(image.source_file.name).stem + "_cog")

    run = 1
    while True:
        output_name = f"{stem}_run_{run}.tif"
        if not any(default_storage.exists(output_name + suffix) for suffix in IMAGE_RUN_SUFFIXES):
            return output_name
        run += 1

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
    dask_scheduler = models.ForeignKey(
        DaskScheduler,
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

    def as_basemap(self):
        from django.urls import reverse
        from django.utils.functional import lazy
        def _tile_url(image_pk):
            url = reverse(
                "basemaps:image_tile",
                kwargs={"image_id": image_pk, "z": 0, "x": 0, "y": 0},
            )
            suffix = "/0/0/0"
            if not url.endswith(suffix):
                raise ValueError(f"Unexpected tile URL shape: {url}")
            return url[: -len(suffix)] + "/{z}/{x}/{y}"

        if self.status != self.StatusChoices.READY:
            raise ValueError(f'The "{self.name}" image is not ready.')

        options = {
            "url": lazy(_tile_url, str)(self.pk),
            "control_label": self.name,
            "minZoom": self.MIN_ZOOM, # TODO add min/max zoom for basemap images?
            "maxZoom": self.MAX_ZOOM,
        }
        if self.attribution:
            options["attributions"] = self.attribution

        bounds = [self.min_x, self.min_y, self.max_x, self.max_y]
        if None not in bounds:
            options["layer_extent"] = bounds

        return {"XYZ": options}

    def refresh_status(self):
        """Apply the generation job's result once it's available"""
        if self.status == self.StatusChoices.PROCESSING:
            refresh_from_result_file(self, self.apply_generation_result, "generation")
        return self.status

    def start_generation(self, user, dask_scheduler=None):
        """Convert the uploaded image into a COG."""
        from .jobs import run_basemap_task
        from .tasks import build_cog

        with transaction.atomic():
            target = BasemapImage.objects.select_for_update().get(pk=self.pk)
            if target.status == self.StatusChoices.PROCESSING:
                raise ValueError(f'The "{self.name}" image is already processing.')

            self.generated_file.name = image_generation_run_output_name(self)
            self.status = self.StatusChoices.PROCESSING
            self.error_message = ""
            self.job = None
            self.save(update_fields=["generated_file", "status", "error_message", "job"])

        try:
            job = run_basemap_task(
                build_cog,
                self.pk,
                self.source_file.path,
                self.generated_file.path,
                georeference_bounds=self.georeference_bounds,
                georeference_epsg=self.georeference_epsg,
                name=f"Generate basemap image {self.pk}",
                user=user,
                result_path=self.result_path,
                non_dask_result_handler=self.apply_generation_result,
                dask_scheduler=dask_scheduler,
                cancel_path=self.cancel_path,
            )
        except Exception as e:
            BasemapImage.objects.filter(pk=self.pk).update(
                status=self.StatusChoices.FAILED, error_message=str(e)
            )
            raise

        if job:
            BasemapImage.objects.filter(pk=self.pk).update(job=job)
        self.refresh_from_db()

    def apply_generation_result(self, result):
        """
        Apply a finished run's result, only while the image is still processing: a run
        cancelled (or superseded) in the meantime keeps the status it was given.
        """
        if not result.get("ok"):
            fields = {"status": self.StatusChoices.FAILED, "error_message": result.get("error", "Unknown error")}
        else:
            min_x, min_y, max_x, max_y = result["bounds"]
            fields = {
                "min_x": min_x, "min_y": min_y, "max_x": max_x, "max_y": max_y,
                "srs": result["srs"],
                "wkt": result["wkt"],
                "generated_file": os.path.relpath(result["output_path"], settings.MEDIA_ROOT),
                "status": self.StatusChoices.READY,
                "error_message": "",
            }
            if result.get("source_epsg") and not self.georeference_epsg:
                fields["georeference_epsg"] = result["source_epsg"]
        BasemapImage.objects.filter(pk=self.pk, status=self.StatusChoices.PROCESSING).update(**fields)
        self.refresh_from_db()

    @property
    def result_path(self):
        return f"{self.generated_file.path}.result.json" if self.generated_file else None

    @property
    def cancel_path(self):
        """
        The flag file that tells this run's build_cog to stop. Each run gets its own
        COG name (see unique_image_output_name), so a new run never sees an old run's flag.
        """
        return f"{self.generated_file.path}.cancel" if self.generated_file else None

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