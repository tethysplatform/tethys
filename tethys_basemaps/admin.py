"""
********************************************************************************
* Name: admin.py
* Author: Jacob Johnson
* Created On: 2026
* Copyright: (c) Aquaveo 2026
********************************************************************************
"""

from pathlib import Path

from django.contrib import admin, messages
from django.db.models import JSONField
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html

from tethys_apps.admin import TethysAppAdmin
from tethys_apps.models import TethysApp
from tethys_basemaps.forms import (
    TethysAppBasemapsForm,
    BasemapCaptureForm,
    BasemapImageForm,
)
from tethys_basemaps.models import PortalBasemapSource, BasemapCapture, BasemapImage
from tethys_gizmos.gizmo_options import MapView, MVView, MVDraw
from tethys_portal.dependencies import vendor_static_dependencies
from tethys_portal.optional_dependencies import has_module, optional_import
from tethys_services.models import SecureMapService

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
    fields = (
        "name",
        "attribution",
        "source_file",
        "dask_scheduler",
        "georeference",
        "status",
        "error_message",
    )
    readonly_fields = ("status", "error_message")

    class Media:
        css = {
            "all": (
                OPENLAYERS.get_custom_version_url(
                    url_type="css", version=OPENLAYERS.version
                ),
            )
        }
        js = (
            OPENLAYERS.get_custom_version_url(
                url_type="js", version=OPENLAYERS.version
            ),
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        restart = change and obj.status == BasemapImage.StatusChoices.CANCELLED
        # Check if there is a new source file or if the georeferencing on an existing basemap image has changed
        if "source_file" in form.changed_data or form.georeference_changed or restart:
            try:
                obj.start_generation(
                    request.user, dask_scheduler=form.cleaned_data.get("dask_scheduler")
                )
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

    def response_add(self, request, obj, post_url_continue=None):
        response = super().response_add(request, obj, post_url_continue)
        return self._stay_while_processing(request, obj, response)

    def response_change(self, request, obj):
        response = super().response_change(request, obj)
        return self._stay_while_processing(request, obj, response)

    def _stay_while_processing(self, request, obj, response):
        """If the image is still processing, redirect back to its change page."""
        if (
            obj.status == BasemapImage.StatusChoices.PROCESSING
            and isinstance(response, HttpResponseRedirect)
            and "_addanother" not in request.POST
        ):
            response["Location"] = reverse(
                "admin:tethys_basemaps_basemapimage_change", args=[obj.pk]
            )
        return response

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
        image_urls = {"status": None, "cancel": None}
        # Check if this is an existing image object being edited
        image = self.get_object(request, object_id) if object_id else None
        if image is not None:
            status = image.refresh_status()
            if status == BasemapImage.StatusChoices.PROCESSING:
                image_urls["status"] = reverse(
                    "basemaps:basemap_status", args=[image.pk]
                )
                if image.job_id:  # only a Dask run can be stopped from here
                    image_urls["cancel"] = reverse(
                        "basemaps:image_cancel", args=[image.pk]
                    )
            if image.georeference_bounds:
                overlay["bounds"] = image.georeference_bounds
                overlay["epsg"] = image.georeference_epsg or 3857
            elif None not in (image.min_x, image.min_y, image.max_x, image.max_y):
                overlay["bounds"] = [image.min_x, image.min_y, image.max_x, image.max_y]
                overlay["epsg"] = 3857

            if (
                image.source_file
                and Path(image.source_file.name).suffix.lower()
                in BROWSER_IMAGE_EXTENSIONS
            ):
                # Use the original source file to make changes rather than the processed COG file
                overlay["image_url"] = reverse(
                    "basemaps:original_image", args=[image.pk]
                )
            elif image.status == BasemapImage.StatusChoices.READY:
                # If the image is a file format that isn't in BROWSER_IMAGE_EXTENSIONS, (ex: GeoTIFF),
                # then use the processed tiled version of the image
                overlay["tile_url"] = str(image.as_basemap()["XYZ"]["url"])

        extra_context = {
            **(extra_context or {}),
            "image_overlay": overlay,
            "image_urls": image_urls,
        }
        return super().changeform_view(request, object_id, form_url, extra_context)


@admin.register(BasemapCapture)
class BasemapCaptureAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "status",
    )
    search_fields = ("name",)
    change_form_template = "tethys_basemaps/admin/basemapcapture_change_form.html"
    fields = ("name", "min_zoom", "max_zoom")
    form = BasemapCaptureForm

    class Media:
        js = ("tethys_sdk/js/csrf.js",)

    def get_fields(self, request, obj=None):
        fields = list(self.fields)
        if obj is None:
            fields += ["dask_scheduler", "max_requests_per_second"]
        else:
            fields += ["status"]
            if obj.error_message:
                fields += ["error_message"]
            if obj.dask_scheduler is not None:
                fields += ["dask_scheduler", "rate_limit"]

        return fields

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ()
        return (
            "min_zoom",
            "max_zoom",
            "dask_scheduler",
            "rate_limit",
            "status",
            "error_message",
        )

    @admin.display(description="Max requests per second")
    def rate_limit(self, obj):
        rate = obj.max_requests_per_second
        if rate is None:
            return "No limit"
        return f"{rate:g} per second"

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        sources = PortalBasemapSource.objects.order_by("name")
        basemaps = [source.format_options() for source in sources]
        secure_map_services = SecureMapService.objects.order_by("name")
        for service in secure_map_services:
            basemaps.append(
                {
                    "WMS": {
                        "control_label": service.name,
                        "url": service._generate_request(),
                    }
                }
            )

        new_object = object_id is None

        # Get the urls the frontend needs for getting status, cancelling the capture, and restarting it1
        status_url = cancel_url = restart_url = None
        capture = None if new_object else self.get_object(request, object_id)
        if (
            capture is not None
            and capture.refresh_status() == BasemapCapture.StatusChoices.PROCESSING
        ):
            status_url = reverse("basemaps:basemap_status", args=[capture.pk])
            if capture.job_id:  # only a Dask job can be stopped from here
                cancel_url = reverse("basemaps:capture_cancel", args=[capture.pk])
        elif capture is not None and capture.restart_problem() is None:
            restart_url = reverse("basemaps:capture_restart", args=[capture.pk])

        capture_map = MapView(
            height="60vh",
            width="100%",
            basemap=basemaps,
            view=MVView(projection="EPSG:4326", center=[-98.5, 39.8], zoom=4),
            draw=(
                MVDraw(
                    controls=["Pan", "Box", "Delete"],
                    initial="Pan",
                    output_format="GeoJSON",
                )
                if new_object
                else None
            ),
        )

        extra_context = {
            **(extra_context or {}),
            "capture_map": capture_map,
            "capture_urls": {
                "upload": reverse("basemaps:capture_upload"),
                "server": reverse("basemaps:capture_server"),
                "status": status_url,
                "cancel": cancel_url,
                "restart": restart_url,
            },
            "gizmos_rendered": [],
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
