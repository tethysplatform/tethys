"""
********************************************************************************
* Name: admin.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    DatasetService,
    SecureImageryService,
    SpatialDatasetService,
    WebProcessingService,
    PersistentStoreService,
)
from django.forms import ModelForm, PasswordInput
from tethys_portal.optional_dependencies import (
    optional_import,
    has_module,
    MissingOptionalDependency,
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


class PersistentStoreServiceForm(ModelForm):
    class Meta:
        model = PersistentStoreService
        fields = ("name", "engine", "host", "port", "username", "password")
        widgets = {
            "password": PasswordInput(),
        }

class SecureImageryServiceForm(ModelForm):
    class Meta:
        model = SecureImageryService
        fields = "__all__"
        labels = {
            "name": _("Name"), 
            "endpoint": _("Endpoint"), 
            "api_key": _("API Key"), 
            "params": _("Parameters")
        }
        

        widgets = {
            "authentication_key": PasswordInput(render_value=True),
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


class PersistentStoreServiceAdmin(admin.ModelAdmin):
    """
    Admin model for Persistent Store Service Model
    """

    form = PersistentStoreServiceForm
    fields = ("name", "engine", "host", "port", "username", "password")

class SecureImageryServiceAdmin(admin.ModelAdmin):
    """
    Admin model for Secure Imagery Service Model
    """

    form = SecureImageryServiceForm
    fields = ("name", "endpoint", "authentication_method", "authentication_key", "api_key", "params")

    class Media:
        js = ("tethys_services/js/secure_imagery_service_admin.js",)


admin.site.register(DatasetService, DatasetServiceAdmin)
admin.site.register(SpatialDatasetService, SpatialDatasetServiceAdmin)
admin.site.register(WebProcessingService, WebProcessingServiceAdmin)
admin.site.register(PersistentStoreService, PersistentStoreServiceAdmin)
admin.site.register(SecureImageryService, SecureImageryServiceAdmin)