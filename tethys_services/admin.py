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
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from .models import (
    DatasetService,
    SecureMapService,
    SpatialDatasetService,
    WebProcessingService,
    PostgresPersistentStoreService,
    SQLitePersistentStoreService,
)
from django.forms import ModelForm, PasswordInput, ChoiceField
from tethys_portal.optional_dependencies import (
    optional_import,
    has_module,
)

JSONEditorWidget = optional_import(
    "JSONEditorWidget", from_module="django_json_widget.widgets"
)


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
                width="60%",
                height="300px",
                options=options_default
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
    fields = ("name", "endpoint", "legend_title", "authentication_method", "api_key", "oauth_provider", "service_type", "use_proxy", "params")

    class Media:
        js = ("tethys_services/js/secure_map_service_admin.js",)


admin.site.register(DatasetService, DatasetServiceAdmin)
admin.site.register(SpatialDatasetService, SpatialDatasetServiceAdmin)
admin.site.register(WebProcessingService, WebProcessingServiceAdmin)
admin.site.register(PostgresPersistentStoreService, PostgresPersistentStoreServiceAdmin)
admin.site.register(SQLitePersistentStoreService, SQLitePersistentStoreServiceAdmin)
admin.site.register(SecureMapService, SecureMapServiceAdmin)
