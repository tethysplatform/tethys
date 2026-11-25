"""
********************************************************************************
* Name: models.py
* Author: Jacob Johnson
* Created On: 2026
* Copyright: (c) Aquaveo 2026
********************************************************************************
"""

import contextlib
import os
import re
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from tethys_basemaps.jobs import refresh_from_result_file
from tethys_compute.models import DaskScheduler


def original_basemap_upload_path(instance, filename):
    return f"basemaps/images/original/{instance.basemap.name}/{filename}"


def generated_basemap_upload_path(instance, filename):
    return f"basemaps/images/generated/{instance.name}/{filename}"


def basemap_capture_upload_path(instance, filename):
    return f"basemaps/captures/{filename}"


def remove_files(*paths):
    for path in paths:
        with contextlib.suppress(FileNotFoundError):
            os.remove(path)


class PortalBasemap(models.Model):
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
        "tethys_apps.TethysApp", blank=True, related_name="portal_basemaps"
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
        return {self.basemap_type: options}


class BasemapImage(PortalBasemap):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        FAILED = "failed", "Failed"
        READY = "ready", "Ready"
        CANCELLED = "cancelled", "Cancelled"

    MIN_ZOOM = 0
    MAX_ZOOM = 22

    # Files a generated image run uses
    RUN_SUFFIXES = (".partial", ".result.json", ".cancel")

    generated_file = models.FileField(
        upload_to=generated_basemap_upload_path, blank=True, null=True
    )
    status = models.CharField(
        max_length=30, choices=StatusChoices.choices, default=StatusChoices.PENDING
    )
    srs = models.CharField(max_length=64, blank=True, null=True)
    wkt = models.TextField(blank=True, null=True)

    @property
    def result_path(self):
        return (
            f"{self.generated_file.path}.result.json" if self.generated_file else None
        )

    def unique_output_name(self):
        """
        A storage name for a new generation run's COG that no earlier run's files use.

        Like unique_capture_output_name: a cancelled run never creates its COG, so
        get_available_name alone would hand its leftover cancel flag to the next run.
        """
        from django.core.files.storage import default_storage

        stem = generated_basemap_upload_path(self, "_cog")

        current = re.search(r"_run_(\d+)\.tif$", self.generated_file.name or "")
        run = int(current.group(1)) + 1 if current else 1
        while True:
            output_name = f"{stem}_run_{run}.tif"
            if not any(
                default_storage.exists(output_name + suffix)
                for suffix in ("", *self.RUN_SUFFIXES)
            ):
                return output_name
            run += 1

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
            "minZoom": self.MIN_ZOOM,  # TODO add min/max zoom for basemap images?
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
        """Build the mosaic COG from this basemap's images."""
        from .jobs import run_basemap_task
        from .tasks import build_cog

        with transaction.atomic():
            target = BasemapImage.objects.select_for_update().get(pk=self.pk)
            if target.status == self.StatusChoices.PROCESSING:
                raise ValueError(f'The "{self.name}" image is already processing.')

            # Drawn in this order: later sources will cover up earlier ones if there is overlap
            sources = [
                {
                    "id": source.pk,
                    "path": source.source_file.path,
                    "bounds": source.georeference_bounds,
                    "epsg": source.georeference_epsg,
                }
                for source in self.sources.all()
                if source.source_file
            ]
            if not sources:
                raise ValueError(f'Add at least one image to "{self.name}".')

            self._remove_old_cogs()
            self.generated_file.name = self.unique_output_name()
            self.status = self.StatusChoices.PROCESSING
            self.error_message = ""
            self.job = None
            self.save(
                update_fields=["generated_file", "status", "error_message", "job"]
            )

        try:
            job = run_basemap_task(
                build_cog,
                self.pk,
                sources,
                self.generated_file.path,
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
            fields = {
                "status": self.StatusChoices.FAILED,
                "error_message": result.get("error", "Unknown error"),
            }
        else:
            min_x, min_y, max_x, max_y = result["bounds"]
            fields = {
                "min_x": min_x,
                "min_y": min_y,
                "max_x": max_x,
                "max_y": max_y,
                "srs": result["srs"],
                "wkt": result["wkt"],
                "generated_file": os.path.relpath(
                    result["output_path"], settings.MEDIA_ROOT
                ),
                "status": self.StatusChoices.READY,
                "error_message": "",
            }
        updated = BasemapImage.objects.filter(
            pk=self.pk, status=self.StatusChoices.PROCESSING
        ).update(**fields)
        if updated and result.get("ok"):
            # Remember each georeferenced source's own coordinate system
            for source_id, epsg in (result.get("source_epsgs") or {}).items():
                if epsg:
                    BasemapImageSource.objects.filter(
                        pk=source_id, basemap=self, georeference_epsg__isnull=True
                    ).update(georeference_epsg=epsg)
        self.refresh_from_db()

    def _remove_old_cogs(self):
        """
        Delete this basemap's finished COGs
        """
        folder = Path(settings.MEDIA_ROOT) / generated_basemap_upload_path(self, "")
        remove_files(*(str(old) for old in folder.glob("*_run_*.tif")))

    def _stop_run(self):
        from .jobs import cancel_dask_task

        if self.cancel_path:
            flag = Path(self.cancel_path)
            flag.parent.mkdir(parents=True, exist_ok=True)
            flag.touch()
        # Stop a dask task if its still in the queue
        if self.job_id and self.job is not None:
            cancel_dask_task(self.job)

    def cancel(self, user=None):
        """
        Stop a generation that is processing on Dask.

        Returns:
            bool: True if it was cancelled, False if it had already finished.
        """
        if self.refresh_status() != self.StatusChoices.PROCESSING:
            return False

        message = f"Cancelled by {user}." if user else "Cancelled."
        updated = BasemapImage.objects.filter(
            pk=self.pk, status=self.StatusChoices.PROCESSING
        ).update(status=self.StatusChoices.CANCELLED, error_message=message)
        if not updated:
            self.refresh_from_db()
            return False

        self._stop_run()
        self.refresh_from_db()
        return True

    def delete_files(self):
        """
        Remove this image's COG and run files. Each source removes its own upload
        when it is deleted (see BasemapImageSource.delete_files).
        """
        processing = self.status == self.StatusChoices.PROCESSING
        if processing and self.job_id:
            self._stop_run()
        paths = []
        if self.generated_file:
            cog = self.generated_file.path
            paths += [cog, cog + ".partial", cog + ".result.json"]
            if not processing:
                paths.append(cog + ".cancel")  # a running task removes its own flag
        remove_files(*paths)
        for folder in {os.path.dirname(p) for p in paths}:
            with contextlib.suppress(OSError):
                os.rmdir(folder)

    @property
    def cancel_path(self):
        """
        The flag file that tells this run's build_cog to stop. Each run gets its own
        COG name (see unique_image_output_name), so a new run never sees an old run's flag.
        """
        return f"{self.generated_file.path}.cancel" if self.generated_file else None


class BasemapImageSource(models.Model):
    """Uploaded image in a BasemapImage's mosaic."""

    basemap = models.ForeignKey(
        BasemapImage, on_delete=models.CASCADE, related_name="sources"
    )
    source_file = models.FileField(upload_to=original_basemap_upload_path)
    georeference_bounds = models.JSONField(blank=True, null=True)
    georeference_epsg = models.PositiveIntegerField(blank=True, null=True)
    order = models.PositiveIntegerField(
        default=0, help_text="Images with a higher order are drawn on top."
    )

    class Meta:
        ordering = ("order", "pk")
        verbose_name = "Image"
        verbose_name_plural = "Images"

    def __str__(self):
        return Path(self.source_file.name).name if self.source_file else "Image"

    def delete_files(self):
        """Remove this source's upload, and its folder once it is empty."""
        if not self.source_file:
            return
        path = self.source_file.path
        remove_files(path)
        with contextlib.suppress(OSError):
            os.rmdir(os.path.dirname(path))


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

    # Files a capture run keeps next to its MBTiles file while it's processing
    RUN_SUFFIXES = (".partial", ".progress.json", ".result.json", ".cancel")

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
    tile_size = models.PositiveSmallIntegerField(default=256)
    max_requests_per_second = models.IntegerField(null=True, blank=True)
    downloaded_on_server = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("-created_at",)

    @property
    def tile_content_type(self):
        return self.TILE_CONTENT_TYPES.get(self.tile_format, "application/octet-stream")

    # Paths to the various run-related files next to the MBTiles file
    @property
    def result_path(self):
        return f"{self.mbtiles_file.path}.result.json" if self.mbtiles_file else None

    @property
    def progress_path(self):
        return f"{self.mbtiles_file.path}.progress.json" if self.mbtiles_file else None

    @property
    def cancel_path(self):
        return f"{self.mbtiles_file.path}.cancel" if self.mbtiles_file else None

    @classmethod
    def unique_output_name(cls, name):
        """
        Generates a file name for a new capture's MBTiles that isn't used by any
        earlier run, including the leftover files of a failed or cancelled run
        """
        from django.core.files.storage import default_storage
        from django.utils.crypto import get_random_string
        from django.utils.text import slugify

        stem = basemap_capture_upload_path(None, slugify(name) or "basemap")
        candidate = default_storage.get_available_name(f"{stem}.mbtiles")
        while any(
            default_storage.exists(candidate + suffix) for suffix in cls.RUN_SUFFIXES
        ):
            candidate = default_storage.get_available_name(
                f"{stem}_{get_random_string(7)}.mbtiles"
            )
        return candidate

    def apply_build_result(self, result):
        """Apply the result of a build job to this capture. Result comes from the worker"""
        if result.get("ok"):
            self.mbtiles_file.name = os.path.relpath(
                result["output_path"], settings.MEDIA_ROOT
            )
            self.tile_format = result["tile_format"]
            self.status = self.StatusChoices.READY
            self.error_message = ""
        else:
            self.status = self.StatusChoices.FAILED
            self.error_message = result.get("error", "Unknown error")
        self.save()

    def refresh_status(self):
        """Apply the build job's result once it's available, and return the status."""
        if self.status == self.StatusChoices.PROCESSING:
            refresh_from_result_file(self, self.apply_build_result, "capture")
        return self.status

    def cancel(self, user=None):
        """
        Stop a capture that is processing on Dask.

        Returns:
            bool: True if it was cancelled, False if it had already finished.
        """
        from .jobs import cancel_dask_task

        if self.refresh_status() != self.StatusChoices.PROCESSING:
            return False

        # Mark it first, so a result the task writes from here on is never applied.
        # The status filter makes this a no-op if the capture finished just now.
        message = f"Cancelled by {user}." if user else "Cancelled."
        updated = BasemapCapture.objects.filter(
            pk=self.pk, status=self.StatusChoices.PROCESSING
        ).update(status=self.StatusChoices.CANCELLED, error_message=message)
        if not updated:
            self.refresh_from_db()
            return False

        flag = Path(self.cancel_path)
        flag.parent.mkdir(parents=True, exist_ok=True)
        flag.touch()
        if self.job_id:
            cancel_dask_task(self.job)

        self.refresh_from_db()
        return True

    def as_basemap(self):
        from django.urls import reverse
        from django.utils.functional import lazy

        def _tile_url(capture_pk):
            url = reverse(
                "basemaps:capture_tile",
                kwargs={"capture_id": capture_pk, "z": 0, "x": 0, "y": 0},
            )
            suffix = "/0/0/0"
            if not url.endswith(suffix):
                raise ValueError(f"Unexpected tile URL shape: {url}")
            return url[: -len(suffix)] + "/{z}/{x}/{y}"

        if self.status != self.StatusChoices.READY:
            raise ValueError(f'The "{self.name}" capture is not ready.')

        options = {
            "url": lazy(_tile_url, str)(self.pk),
            "control_label": self.name,
            "minZoom": self.min_zoom,
            "maxZoom": self.max_zoom,
        }
        if self.attribution:
            options["attributions"] = self.attribution

        bounds = [self.min_x, self.min_y, self.max_x, self.max_y]
        if None not in bounds:
            options["layer_extent"] = bounds

        return {"XYZ": options}

    def get_tile(self, z, x, y):
        """
        Return the XYZ tile at z/x/y, or None if the capture doesn't have it.
        """
        import sqlite3
        from pathlib import Path

        if self.status != self.StatusChoices.READY or not self.mbtiles_file:
            return None

        uri = Path(self.mbtiles_file.path).as_uri() + "?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        try:
            # MBTiles rows use the TMS scheme: row 0 is the southernmost row
            row = conn.execute(
                "SELECT tile_data FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?",
                (z, x, (2**z - 1) - y),
            ).fetchone()
        finally:
            conn.close()
        return row[0] if row else None

    def restart_problem(self):
        """Why this capture can't be restarted, or None if it can."""
        if self.status != self.StatusChoices.CANCELLED:
            return "Only a cancelled capture can be restarted."
        if not self.downloaded_on_server:
            return (
                "Only captures downloaded on the server can be restarted. "
                "This one was downloaded in the browser; capture it again instead."
            )
        if self.source_id is None and self.secure_source_id is None:
            return "The basemap this capture was downloaded from no longer exists."
        return None

    def delete_files(self):
        """Remove this capture's mbtiles file, result file, and run files"""
        from .jobs import cancel_dask_task

        if not self.mbtiles_file:
            return
        base = self.mbtiles_file.path
        if self.status == self.StatusChoices.PROCESSING and self.job_id:
            Path(self.cancel_path).touch()
            cancel_dask_task(self.job)
            remove_files(self.result_path)
        else:
            remove_files(base, *(base + s for s in self.RUN_SUFFIXES))


@receiver(
    post_delete,
    sender=BasemapCapture,
    dispatch_uid="tethys_basemaps_delete_capture_files",
)
@receiver(
    post_delete, sender=BasemapImage, dispatch_uid="tethys_basemaps_delete_image_files"
)
@receiver(
    post_delete,
    sender=BasemapImageSource,
    dispatch_uid="tethys_basemaps_delete_image_source_files",
)
def _delete_basemap_files(sender, instance, **kwargs):
    """Remove a deleted capture's, image's or image source's files once the delete commits."""
    transaction.on_commit(instance.delete_files)
