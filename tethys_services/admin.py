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
from django.utils.translation import ugettext_lazy as _
from .models import DatasetService, SpatialDatasetService, WebProcessingService
from django.forms import ModelForm, PasswordInput


class DatasetServiceForm(ModelForm):
    class Meta:
        model = DatasetService
        fields = ('name', 'engine', 'endpoint', 'public_endpoint', 'apikey', 'username', 'password')
        widgets = {
            'password': PasswordInput(),
        }
        labels = {
            'public_endpoint': _('Public Endpoint')
        }


class SpatialDatasetServiceForm(ModelForm):
    class Meta:
        model = SpatialDatasetService
        fields = ('name', 'engine', 'endpoint', 'public_endpoint', 'apikey', 'username', 'password')
        widgets = {
            'password': PasswordInput(),
        }
        labels = {
            'public_endpoint': _('Public Endpoint')
        }


class DatasetServiceAdmin(admin.ModelAdmin):
    """
    Admin model for Web Processing Service Model
    """
    form = DatasetServiceForm
    fields = ('name', 'engine', 'endpoint', 'public_endpoint', 'apikey', 'username', 'password')


class SpatialDatasetServiceAdmin(admin.ModelAdmin):
    """
    Admin model for Spatial Dataset Service Model
    """
    form = SpatialDatasetServiceForm
    fields = ('name', 'engine', 'endpoint', 'public_endpoint', 'apikey', 'username', 'password')


class WebProcessingServiceForm(ModelForm):
    class Meta:
        model = WebProcessingService
        fields = ('name', 'endpoint', 'public_endpoint', 'username', 'password')
        widgets = {
            'password': PasswordInput(),
        }
        labels = {
            'public_endpoint': _('Public Endpoint')
        }


class WebProcessingServiceAdmin(admin.ModelAdmin):
    """
    Admin model for Web Processing Service Model
    """
    form = WebProcessingServiceForm
    fields = ('name', 'endpoint', 'public_endpoint', 'username', 'password')


admin.site.register(DatasetService, DatasetServiceAdmin)
admin.site.register(SpatialDatasetService, SpatialDatasetServiceAdmin)
admin.site.register(WebProcessingService, WebProcessingServiceAdmin)
