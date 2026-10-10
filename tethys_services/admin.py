"""
********************************************************************************
* Name: admin.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, render
from django.urls import path, reverse
from django.utils.html import format_html, json_script
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from .models import (
    DatasetService,
    SecureMapService,
    SpatialDatasetService,
    WebProcessingService,
    PostgresPersistentStoreService,
    SQLitePersistentStoreService,
    BasemapCapture,
    BasemapImage,
    BasemapService,
)
from django.forms import ModelForm, PasswordInput, ChoiceField, CharField, HiddenInput
import json
from tethys_portal.optional_dependencies import (
    optional_import,
    has_module,
)

JSONEditorWidget = optional_import(
    "JSONEditorWidget", from_module="django_json_widget.widgets"
)

SUPPORTED_BASEMAP_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")

class DatasetServiceForm(ModelForm):
    class Meta:
        model = DatasetService
        fields = (
            "name",
            "engine",
            "endpoint",
            "public_endpoint",
            "apikey",
            "username",
            "password",
        )
        widgets = {
            "password": PasswordInput(),
        }
        labels = {"public_endpoint": _("Public Endpoint")}


class SpatialDatasetServiceForm(ModelForm):
    class Meta:
        model = SpatialDatasetService
        fields = (
            "name",
            "engine",
            "endpoint",
            "public_endpoint",
            "apikey",
            "username",
            "password",
        )
        widgets = {
            "password": PasswordInput(),
        }
        labels = {"public_endpoint": _("Public Endpoint")}


class WebProcessingServiceForm(ModelForm):
    class Meta:
        model = WebProcessingService
        fields = ("name", "endpoint", "public_endpoint", "username", "password")
        widgets = {
            "password": PasswordInput(),
        }
        labels = {"public_endpoint": _("Public Endpoint")}


class PostgresPersistentStoreServiceForm(ModelForm):
    class Meta:
        model = PostgresPersistentStoreService
        fields = ("name", "engine", "host", "port", "username", "password")
        widgets = {
            "password": PasswordInput(),
        }


class SQLitePersistentStoreServiceForm(ModelForm):
    class Meta:
        model = SQLitePersistentStoreService
        fields = ("name", "engine", "dir_path")


class SecureMapServiceForm(ModelForm):
    class Meta:
        model = SecureMapService
        fields = "__all__"
        labels = {
            "name": _("Name"),
            "endpoint": _("Endpoint"),
            "api_key": _("API Key"),
            "oauth_provider": _("OAuth Provider"),
            "params": _("Parameters"),
            "legend_title": _("Legend Title"),
            "service_type": _("Service Type"),
            "use_proxy": _("Use Proxy for Requests"),
        }

        widgets = {
            "api_key": PasswordInput(render_value=True),
        }

        options_default = {
            "modes": ["code", "text"],
            "search": False,
            "navigationBar": False,
        }

        if has_module("django_json_widget"):
            widgets["params"] = JSONEditorWidget(
                width="60%", height="300px", options=options_default
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = []
        if settings.AUTHENTICATION_BACKENDS:
            for backend in settings.AUTHENTICATION_BACKENDS:
                backend_class = import_string(backend)
                if hasattr(backend_class, "name"):
                    choices.append((backend_class.name, backend_class.name))
        self.fields["oauth_provider"] = ChoiceField(
            choices=choices,
            required=False,
        )

class BasemapServiceForm(ModelForm):
    class Meta:
        model = BasemapService
        fields = "__all__"



class DatasetServiceAdmin(admin.ModelAdmin):
    """
    Admin model for Web Processing Service Model
    """

    form = DatasetServiceForm
    fields = (
        "name",
        "engine",
        "endpoint",
        "public_endpoint",
        "apikey",
        "username",
        "password",
    )


class SpatialDatasetServiceAdmin(admin.ModelAdmin):
    """
    Admin model for Spatial Dataset Service Model
    """

    form = SpatialDatasetServiceForm
    fields = (
        "name",
        "engine",
        "endpoint",
        "public_endpoint",
        "apikey",
        "username",
        "password",
    )


class WebProcessingServiceAdmin(admin.ModelAdmin):
    """
    Admin model for Web Processing Service Model
    """

    form = WebProcessingServiceForm
    fields = ("name", "endpoint", "public_endpoint", "username", "password")


class PostgresPersistentStoreServiceAdmin(admin.ModelAdmin):
    """
    Admin model for Postgres Persistent Store Service Model
    """

    form = PostgresPersistentStoreServiceForm
    fields = ("name", "engine", "host", "port", "username", "password")


class SQLitePersistentStoreServiceAdmin(admin.ModelAdmin):
    """
    Admin model for SQLite Persistent Store Service Model
    """

    form = SQLitePersistentStoreServiceForm
    fields = ("name", "engine", "dir_path")


class SecureMapServiceAdmin(admin.ModelAdmin):
    """
    Admin model for Secure Map Service Model
    """

    form = SecureMapServiceForm
    fields = (
        "name",
        "endpoint",
        "legend_title",
        "authentication_method",
        "api_key",
        "oauth_provider",
        "service_type",
        "use_proxy",
        "params",
    )

    class Media:
        js = ("tethys_services/js/secure_map_service_admin.js",)


class BasemapImageInlineForm(ModelForm):
    georeference = CharField(widget=HiddenInput, required=False)

    class Meta:
        model = BasemapImage
        fields = ("source_file", "capture")
        help_texts = {
            "capture": "A basemap saved from a map view. Use instead of uploading a source file.",
        }

class BasemapImageInline(admin.StackedInline):
    model = BasemapImage
    form = BasemapImageInlineForm
    extra = 1  # one blank file input on a fresh service

    fields = (
        "source_file",
        "capture",
        "georeference",
        "display_status",
        "error_message",
        "generated_file",
        "srs",
        "min_x",
        "min_y",
        "max_x",
        "max_y",
        "map_data"
    )
    readonly_fields = (
        "display_status",
        "error_message",
        "generated_file",
        "srs",
        "min_x",
        "min_y",
        "max_x",
        "max_y",
        "map_data"
    )
    @admin.display(description="Status")
    def display_status(self, obj):
        if obj.pk is None:
            return "N/A"
        return obj.get_status_display()

    @admin.display(description="Map Data")
    def map_data(self, obj):
        if obj.pk is None or not obj.source_file or not obj.georeference_bounds:
            return ""
        if not obj.source_file.name.lower().endswith(SUPPORTED_BASEMAP_IMAGE_EXTENSIONS):
            return ""
        return json_script(
            {
                "url": obj.source_file.url,
                "bounds": list(obj.georeference_bounds),
                "epsg": obj.georeference_epsg,
            },
            element_id=f"basemap-image-{obj.pk}"
        )

class BasemapServiceAdmin(admin.ModelAdmin):
    """
    Admin model for Basemap Service Model
    """

    form = BasemapServiceForm
    fields = (
        "name",
        "attribution",
        "min_zoom",
        "max_zoom",
    )
    inlines = [BasemapImageInline]
    readonly_fields = ("min_zoom", "max_zoom")
    list_display = ("name", "image_count")

    @admin.display(description="Images")
    def image_count(self, obj):
        return obj.images.count()

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        for fs in formsets:
            if fs.model is not BasemapImage:
                continue

            for f in fs.forms:
                if f in fs.deleted_forms or not f.instance.pk:
                    continue
                raw = f.cleaned_data.get("georeference")
                replaced = "source_file" in f.changed_data or "capture" in f.changed_data
                updates = []

                if "source_file" in f.changed_data:
                    old = f.initial.get("source_file")
                    old_name = getattr(old, "name", old)
                    if old_name and old_name != f.instance.source_file.name:
                        f.instance.source_file.storage.delete(old_name)
                if raw:
                    data = json.loads(raw)
                    f.instance.georeference_epsg = data["epsg"]
                    f.instance.georeference_bounds = data["bounds"]
                    updates += ["georeference_bounds", "georeference_epsg"]

                if raw or replaced:
                    f.instance.status = BasemapImage.StatusChoices.PENDING
                    updates.append("status")

                if updates:
                    f.instance.save(update_fields=updates)

        pending = form.instance.images.filter(
            status=BasemapImage.StatusChoices.PENDING
        )
        for image in pending:
            try:
                image.generate()
            except Exception as e:
                print(f"Error generating basemap image {image.pk}: {e}")

    class Media:
        css = {"all": ("https://cdn.jsdelivr.net/npm/ol@9.2.4/ol.css",)}
        js = (
            "https://cdn.jsdelivr.net/npm/ol@9.2.4/dist/ol.js",
            "tethys_services/js/basemap_georeference.js",
        )
class BasemapImageAdmin(admin.ModelAdmin):
    list_display = ("__str__", "basemap_service", "status")
    list_filter = ("status", "basemap_service")

    def get_urls(self):
        custom = [
            path(
                "<int:image_id>/georeference/",
                self.admin_site.admin_view(self.georeference_view),
                name="basemap_georeference",
            ),
        ]
        return custom + super().get_urls()

    def georeference_view(self, request, image_id):
        image = get_object_or_404(BasemapImage, pk=image_id)
        context = {
            **self.admin_site.each_context(request),
            "title": f"Georeference {image}",
            "image": image,
            "source_url": reverse("basemap_source_file", kwargs={"image_id": image.pk}),
            "opts": self.model._meta,
        }

        return render(request, "tethys_services/basemap/basemap_georeference.html", context)


admin.site.register(DatasetService, DatasetServiceAdmin)
admin.site.register(SpatialDatasetService, SpatialDatasetServiceAdmin)
admin.site.register(WebProcessingService, WebProcessingServiceAdmin)
admin.site.register(PostgresPersistentStoreService, PostgresPersistentStoreServiceAdmin)
admin.site.register(SQLitePersistentStoreService, SQLitePersistentStoreServiceAdmin)
admin.site.register(SecureMapService, SecureMapServiceAdmin)
class BasemapCaptureAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "min_zoom", "max_zoom", "tile_format", "created_at", "service_count")
    list_filter = ("owner",)
    search_fields = ("name",)
    readonly_fields = (
        "owner", "mbtiles_file", "tile_format", "min_zoom", "max_zoom",
        "min_x", "min_y", "max_x", "max_y", "created_at", "services",
    )

    @admin.display(description="Services")
    def service_count(self, obj):
        return obj.images.values("basemap_service").distinct().count()

    @admin.display(description="Used by")
    def services(self, obj):
        names = obj.images.values_list("basemap_service__name", flat=True).distinct()
        return ", ".join(names) or "Not assigned to a basemap service"

    def has_add_permission(self, request):
        # Captures are created from a map view
        return False

    # Remove the MBTiles file once the row is gone (captures in use by a service are protected)
    def delete_model(self, request, obj):
        mbtiles_file = obj.mbtiles_file
        super().delete_model(request, obj)
        mbtiles_file.delete(save=False)

    def delete_queryset(self, request, queryset):
        mbtiles_files = [obj.mbtiles_file for obj in queryset]
        super().delete_queryset(request, queryset)
        for mbtiles_file in mbtiles_files:
            mbtiles_file.delete(save=False)


admin.site.register(BasemapService, BasemapServiceAdmin)
admin.site.register(BasemapCapture, BasemapCaptureAdmin)
admin.site.register(BasemapImage, BasemapImageAdmin)