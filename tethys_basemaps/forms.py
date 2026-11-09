"""
********************************************************************************
* Name: forms.py
* Author: Jacob Johnson
* Created On: 2026
* Copyright: (c) Aquaveo 2026
********************************************************************************
"""

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from tethys_apps.models import TethysApp
from tethys_basemaps.models import PortalBasemap


class TethysAppBasemapsForm(forms.ModelForm):
    portal_basemaps = forms.ModelMultipleChoiceField(
        queryset=PortalBasemap.objects.order_by("name"),
        required=False,
        widget=FilteredSelectMultiple("basemaps", is_stacked=False),
        help_text="Portal basemaps to include in this app's maps.",
    )

    class Meta:
        model = TethysApp
        fields = "__all__"  # the admin's `fields` decides what's rendered

        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["portal_basemaps"].initial = self.instance.portal_basemaps.all()