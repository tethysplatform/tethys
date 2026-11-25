"""
********************************************************************************
* Name: forms.py
* Author: Jacob Johnson
* Created On: 2026
* Copyright: (c) Aquaveo 2026
********************************************************************************
"""

import json
import warnings

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple

from tethys_apps.models import TethysApp
from tethys_basemaps.models import (
    PortalBasemap,
    BasemapCapture,
    BasemapImage,
    BasemapImageSource,
)
from tethys_compute.models import DaskScheduler


class TethysAppBasemapsForm(forms.ModelForm):
    portal_basemaps = forms.ModelMultipleChoiceField(
        queryset=PortalBasemap.objects.exclude(
            basemapimage__status__in=["pending", "processing", "failed", "cancelled"]
        )
        .exclude(basemapcapture__status__in=["processing", "failed", "cancelled"])
        .order_by("name"),
        required=False,
        widget=FilteredSelectMultiple("basemaps", is_stacked=False),
        help_text="Portal basemaps to include in this app's maps.",
    )

    class Meta:
        model = TethysApp
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["portal_basemaps"].initial = self.instance.portal_basemaps.all()


class BasemapImageForm(forms.ModelForm):
    dask_scheduler = forms.ModelChoiceField(
        queryset=DaskScheduler.objects.all(),
        required=False,
        label="Dask Scheduler",
    )

    class Meta:
        model = BasemapImage
        fields = ("name", "attribution")


class BasemapImageSourceForm(forms.ModelForm):
    """One image in a basemap image's mosaic, with its placement on the map."""

    georeference = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = BasemapImageSource
        fields = ("source_file", "order")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store the current georeference so we can check for changes
        self._saved_georeference = (
            self.instance.georeference_epsg,
            self.instance.georeference_bounds,
        )
        if self.instance.georeference_bounds:
            self.initial["georeference"] = json.dumps(
                {
                    "epsg": self.instance.georeference_epsg or 3857,
                    "bounds": self.instance.georeference_bounds,
                }
            )

    def clean_source_file(self):
        """
        Check if the uploaded file is a valid image for the mosaic.
        """
        upload = self.cleaned_data.get("source_file")
        if not upload or "source_file" not in self.changed_data:
            return upload

        import rasterio
        from rasterio.errors import NotGeoreferencedWarning, RasterioIOError
        from rasterio.io import MemoryFile

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", NotGeoreferencedWarning)
                if hasattr(upload, "temporary_file_path"):
                    # Large uploads are already on disk; only the header is read
                    with rasterio.open(upload.temporary_file_path()):
                        pass
                else:
                    upload.seek(0)
                    with MemoryFile(upload.read()) as memfile, memfile.open():
                        pass
        except RasterioIOError:
            raise forms.ValidationError(
                f'"{upload.name}" isn\'t an image format that can be used. '
                "Use a PNG, JPEG, WebP or GeoTIFF."
            )
        finally:
            upload.seek(0)
        return upload

    def clean_georeference(self):
        raw = self.cleaned_data.get("georeference")
        if not raw:
            return None
        try:
            data = json.loads(raw)
            bounds = [float(v) for v in data["bounds"]]
            epsg = int(data.get("epsg", 3857))
        except (ValueError, KeyError, TypeError):
            raise forms.ValidationError(
                "Couldn't read the image placement. Try placing it again."
            )
        if len(bounds) != 4:
            raise forms.ValidationError(
                f"The image placement needs 4 values, but got {len(bounds)}. Try again."
            )
        min_x, min_y, max_x, max_y = bounds
        if min_x == max_x or min_y == max_y:
            raise forms.ValidationError(
                "The image placement has no width or height. Try placing it again."
            )
        if min_x >= max_x or min_y >= max_y:
            raise forms.ValidationError(
                "The image placement is flipped. Try placing it again."
            )
        return {"epsg": epsg, "bounds": bounds}

    @property
    def georeference_changed(self):
        geo_reference_data = self.cleaned_data.get("georeference")
        return (
            bool(geo_reference_data)
            and (geo_reference_data["epsg"], geo_reference_data["bounds"])
            != self._saved_georeference
        )

    @property
    def needs_regeneration(self):
        """Determine if saving will change the mosaic."""
        if not self.has_changed() and not self.instance.pk:
            return False  # an empty extra row
        return (
            "source_file" in self.changed_data
            or "order" in self.changed_data
            or self.georeference_changed
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        geo_reference_data = self.cleaned_data.get("georeference")
        if geo_reference_data:
            instance.georeference_epsg = geo_reference_data["epsg"]
            instance.georeference_bounds = geo_reference_data["bounds"]
        elif "source_file" in self.changed_data:
            # A new file without a placement: don't keep the old file's placement
            instance.georeference_epsg = None
            instance.georeference_bounds = None
        if commit:
            instance.save()
        return instance


class BasemapCaptureForm(forms.ModelForm):
    dask_scheduler = forms.ModelChoiceField(
        queryset=DaskScheduler.objects.all(),
        required=False,
        label="Dask Scheduler",
    )
    max_requests_per_second = forms.IntegerField(
        required=False,
        label="Max Requests Per Second",
        max_value=settings.BASEMAP_CAPTURE_SECURE_MAX_RATE,
        min_value=1,
        help_text="For server downloads only. Helps avoid hitting rate limits. Leave blank for no limit.",
        widget=forms.NumberInput(attrs={"step": 1, "placeholder": "No limit"}),
    )

    class Meta:
        model = BasemapCapture
        fields = ("name", "min_zoom", "max_zoom")
