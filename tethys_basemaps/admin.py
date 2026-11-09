"""
********************************************************************************
* Name: admin.py
* Author: Jacob Johnson
* Created On: 2026
* Copyright: (c) Aquaveo 2026
********************************************************************************
"""

from django.contrib import admin
from django.db.models import JSONField

from tethys_apps.admin import TethysAppAdmin
from tethys_apps.models import TethysApp
from tethys_basemaps.forms import TethysAppBasemapsForm
from tethys_basemaps.models import PortalBasemapSource
from tethys_portal.optional_dependencies import has_module, optional_import

JSONEditorWidget = optional_import(
    "JSONEditorWidget", from_module="django_json_widget.widgets"
)

@admin.register(PortalBasemapSource)
class PortalBasemapSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "basemap_type")
    search_fields = ("name", "basemap_type")
    fields = ("name", "basemap_type", "options")
    if has_module("django_json_widget"):
        formfield_overrides = {
            JSONField: {"widget": JSONEditorWidget},
        }

# Add basemap picker to TethysApp settings
admin.site.unregister(TethysApp)

@admin.register(TethysApp)
class TethysAppBasemapsAdmin(TethysAppAdmin):
    form = TethysAppBasemapsForm
    fields = TethysAppAdmin.fields + ("portal_basemaps",)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.portal_basemaps.set(form.cleaned_data.get("portal_basemaps", []))