"""
********************************************************************************
* Name: admin.py
* Author: Jacob Johnson
* Created On: 2026
* Copyright: (c) Aquaveo 2026
********************************************************************************
"""

from django.contrib import admin, messages
from django.db.models import JSONField
from django.urls import reverse
from django.utils.html import format_html

from tethys_apps.admin import TethysAppAdmin
from tethys_apps.models import TethysApp
from tethys_basemaps.forms import TethysAppBasemapsForm, BasemapImageForm
from tethys_basemaps.models import PortalBasemapSource, BasemapImage
from tethys_portal.dependencies import vendor_static_dependencies
from tethys_portal.optional_dependencies import has_module, optional_import

from pathlib import Path

BROWSER_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
OPENLAYERS = vendor_static_dependencies["openlayers"]

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

@admin.register(BasemapImage)
class BasemapImageAdmin(admin.ModelAdmin):
    form = BasemapImageForm
    change_form_template = "tethys_basemaps/admin/basemap_image_change_form.html"
    list_display = ("name", "status")
    list_filter = ("status",)
    search_fields = ("name",)
    fields = ("name", "attribution", "source_file", "dask_scheduler", "georeference", "status", "error_message")
    readonly_fields = ("status", "error_message")

    class Media:
        css = {"all": (OPENLAYERS.get_custom_version_url(url_type="css", version=OPENLAYERS.version),)}
        js = (OPENLAYERS.get_custom_version_url(url_type="js", version=OPENLAYERS.version),)

    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Check if there is a new source file or if the georeferencing on an existing basemap image has changed
        if "source_file" in form.changed_data or form.georeference_changed:
            try:
                obj.start_generation(request.user, dask_scheduler=form.cleaned_data.get("dask_scheduler"))
            except Exception:
                # Refresh the object from the database to get the latest status and error message set in start_generation
                obj.refresh_from_db()
                self.message_user(
                    request,
                    "There was an error processing the uploaded image. See its error message for more details.",
                    level=messages.ERROR,
                )
                return
            if obj.status == BasemapImage.StatusChoices.PROCESSING:
                request._basemap_note = ("It is being processed.", messages.SUCCESS)


    def message_user(self, request, message, level=messages.INFO, *args, **kwargs):
        # Add extra information to Django's messages
        # ex: adding to the "Successfully added" message
        note = getattr(request, "_basemap_note", None)
        if note and level == messages.SUCCESS:
            message = format_html("{} {}", message, note[0])
            level = note[1]
        super().message_user(request, message, level, *args, **kwargs)


    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        overlay = {}
        # Check if this is an existing image object being edited
        image = self.get_object(request, object_id) if object_id else None
        if image is not None:
            image.refresh_status()
            if image.georeference_bounds:
                overlay["bounds"] = image.georeference_bounds
                overlay["epsg"] = image.georeference_epsg or 3857
            elif None not in (image.min_x, image.min_y, image.max_x, image.max_y):
                overlay["bounds"] = [image.min_x, image.min_y, image.max_x, image.max_y]
                overlay["epsg"] = 3857

            if image.source_file and Path(image.source_file.name).suffix.lower() in BROWSER_IMAGE_EXTENSIONS:
                # Use the original source file to make changes rather than the processed COG file
                overlay["image_url"] = reverse("basemaps:original_image", args=[image.pk])
            elif image.status == BasemapImage.StatusChoices.READY:
                # If the image is a file format that isn't in BROWSER_IMAGE_EXTENSIONS, (ex: GeoTIFF),
                # then use the processed tiled version of the image
                overlay["tile_url"] = str(image.as_basemap()["XYZ"]["url"])

        extra_context = {
            **(extra_context or {}),
            "image_overlay": overlay,
        }
        return super().changeform_view(request, object_id, form_url, extra_context)

# Add basemap picker to TethysApp settings
admin.site.unregister(TethysApp)

@admin.register(TethysApp)
class TethysAppBasemapsAdmin(TethysAppAdmin):
    form = TethysAppBasemapsForm
    fields = TethysAppAdmin.fields + ("portal_basemaps",)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.portal_basemaps.set(form.cleaned_data.get("portal_basemaps", []))