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
from guardian.admin import GuardedModelAdmin
from tethys_services.models import DatasetService
from tethys_apps.models import (TethysApp,
                                CustomTethysAppSetting,
                                DatasetServiceSetting,
                                SpatialDatasetServiceSetting,
                                WebProcessingServiceSetting)


class TethysAppSettingInline(admin.TabularInline):
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

class CustomTethysAppSettingInline(TethysAppSettingInline):
    readonly_fields = ('name', 'description', 'required')
    fields = ('name', 'description', 'value', 'required')
    model = CustomTethysAppSetting

class DatasetServiceSettingInline(TethysAppSettingInline):
    readonly_fields = ('name', 'description', 'required', 'engine')
    fields = ('name', 'description', 'dataset_service', 'engine', 'required')
    model = DatasetServiceSetting

#    def formfield_for_foreignkey(self, db_field, request, **kwargs):
#        """
#        Filter by dataset service engine
#        """
#        if db_field.name == "dataset_service":
#            kwargs['queryset'] = DatasetService.objects.filter(engine=DatasetService.CKAN)
#        return super(DatasetServiceSettingInline, self) \
#            .formfield_for_foreignkey(db_field, request, **kwargs)

class SpatialDatasetServiceSettingInline(TethysAppSettingInline):
    readonly_fields = ('name', 'description', 'required', 'engine')
    fields = ('name', 'description', 'spatial_dataset_service', 'engine', 'required')
    model = SpatialDatasetServiceSetting

class WebProcessingServiceSettingInline(TethysAppSettingInline):
    readonly_fields = ('name', 'description', 'required')
    fields = ('name', 'description', 'web_processing_service', 'required')
    model = WebProcessingServiceSetting

class TethysAppAdmin(GuardedModelAdmin):
    readonly_fields = ('package',)
    fields = ('package', 'name', 'description', 'tags', 'enabled', 'show_in_apps_library', 'enable_feedback')
    inlines = [CustomTethysAppSettingInline,
               DatasetServiceSettingInline,
               SpatialDatasetServiceSettingInline,
               WebProcessingServiceSettingInline]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

admin.site.register(TethysApp, TethysAppAdmin)
