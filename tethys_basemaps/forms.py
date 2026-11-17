"""
********************************************************************************
* Name: forms.py
* Author: Jacob Johnson
* Created On: 2026
* Copyright: (c) Aquaveo 2026
********************************************************************************
"""
import json
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from tethys_apps.models import TethysApp
from tethys_basemaps.models import PortalBasemap, BasemapImage
from tethys_compute.models import DaskScheduler



class TethysAppBasemapsForm(forms.ModelForm):
    portal_basemaps = forms.ModelMultipleChoiceField(
        queryset=PortalBasemap.objects.order_by("name"),
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
    georeference = forms.CharField(required=False, widget=forms.HiddenInput)
    dask_scheduler = forms.ModelChoiceField(
        queryset=DaskScheduler.objects.all(),
        required=False,
        label="Dask Scheduler",
    )

    class Meta:
        model = BasemapImage
        fields = ("name", "attribution", "source_file")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store the current georeference so we can check changes later
        # Remember the saved placement so we can tell whether the user moved it
        self._saved_georeference = (self.instance.georeference_epsg, self.instance.georeference_bounds)
        if self.instance.georeference_bounds:
            self.initial["georeference"] = json.dumps({
                "epsg": self.instance.georeference_epsg or 3857,
                "bounds": self.instance.georeference_bounds,
            })

    def clean_georeference(self):
        raw = self.cleaned_data.get("georeference")
        if not raw:
            return None
        try:
            data = json.loads(raw)
            bounds = [float(v) for v in data["bounds"]]
            epsg = int(data.get("epsg", 3857))
        except (ValueError, KeyError, TypeError):
            raise forms.ValidationError("Couldn't read the image placement. Try placing it again.")
        if len(bounds) != 4:
            raise forms.ValidationError(f"The image placement needs 4 values, but got {len(bounds)}. Try again.")
        min_x, min_y, max_x, max_y = bounds
        if min_x == max_x or min_y == max_y:
            raise forms.ValidationError("The image placement has no width or height. Try placing it again.")
        if min_x >= max_x or min_y >= max_y:
            raise forms.ValidationError("The image placement is flipped. Try placing it again.")
        return {"epsg": epsg, "bounds": bounds}

    @property
    def georeference_changed(self):
        geo_reference_data = self.cleaned_data.get("georeference")
        return bool(geo_reference_data) and (geo_reference_data["epsg"], geo_reference_data["bounds"]) != self._saved_georeference

    def save(self, commit=True):
        instance = super().save(commit=False)
        geo_reference_data = self.cleaned_data.get("georeference")
        if geo_reference_data:
            instance.georeference_epsg = geo_reference_data["epsg"]
            instance.georeference_bounds = geo_reference_data["bounds"]
        if commit:
            instance.save()
        return instance