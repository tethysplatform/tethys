from django.contrib import admin
from .models import DatasetService, SpatialDatasetService, WebProcessingService
from django.forms import ModelForm, PasswordInput


class DatasetServiceForm(ModelForm):
    class Meta:
        model = DatasetService
        fields = ('name', 'engine', 'endpoint', 'apikey', 'username', 'password')
        widgets = {
            'password': PasswordInput(),
        }


class SpatialDatasetServiceForm(ModelForm):
    class Meta:
        model = SpatialDatasetService
        fields = ('name', 'engine', 'endpoint', 'apikey', 'username', 'password')
        widgets = {
            'password': PasswordInput(),
        }


class DatasetServiceAdmin(admin.ModelAdmin):
    """
    Admin model for Web Processing Service Model
    """
    form = DatasetServiceForm
    fields = ('name', 'engine', 'endpoint', 'apikey', 'username', 'password')


class SpatialDatasetServiceAdmin(admin.ModelAdmin):
    """
    Admin model for Spatial Dataset Service Model
    """
    form = SpatialDatasetServiceForm
    fields = ('name', 'engine', 'endpoint', 'apikey', 'username', 'password')


class WebProcessingServiceForm(ModelForm):
    class Meta:
        model = WebProcessingService
        fields = ('name', 'endpoint', 'username', 'password')
        widgets = {
            'password': PasswordInput(),
        }


class WebProcessingServiceAdmin(admin.ModelAdmin):
    """
    Admin model for Web Processing Service Model
    """
    form = WebProcessingServiceForm
    fields = ('name', 'endpoint', 'username', 'password')


admin.site.register(DatasetService, DatasetServiceAdmin)
admin.site.register(SpatialDatasetService, SpatialDatasetServiceAdmin)
admin.site.register(WebProcessingService, WebProcessingServiceAdmin)
