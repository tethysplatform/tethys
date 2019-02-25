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
from tethys_apps.models import (TethysApp,
                                TethysExtension,
                                CustomSetting,
                                DatasetServiceSetting,
                                SpatialDatasetServiceSetting,
                                WebProcessingServiceSetting,
                                PersistentStoreConnectionSetting,
                                PersistentStoreDatabaseSetting)


class TethysAppSettingInline(admin.TabularInline):
    template = 'tethys_portal/admin/edit_inline/tabular.html'

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class CustomSettingInline(TethysAppSettingInline):
    readonly_fields = ('name', 'description', 'type', 'required')
    fields = ('name', 'description', 'type', 'value', 'required')
    model = CustomSetting


class DatasetServiceSettingInline(TethysAppSettingInline):
    readonly_fields = ('name', 'description', 'required', 'engine')
    fields = ('name', 'description', 'dataset_service', 'engine', 'required')
    model = DatasetServiceSetting


class SpatialDatasetServiceSettingInline(TethysAppSettingInline):
    readonly_fields = ('name', 'description', 'required', 'engine')
    fields = ('name', 'description', 'spatial_dataset_service', 'engine', 'required')
    model = SpatialDatasetServiceSetting


class WebProcessingServiceSettingInline(TethysAppSettingInline):
    readonly_fields = ('name', 'description', 'required')
    fields = ('name', 'description', 'web_processing_service', 'required')
    model = WebProcessingServiceSetting


# TODO: Figure out how to initialize persistent stores with button in admin
# Consider: https://medium.com/@hakibenita/how-to-add-custom-action-buttons-to-django-admin-8d266f5b0d41
class PersistentStoreConnectionSettingInline(TethysAppSettingInline):
    readonly_fields = ('name', 'description', 'required')
    fields = ('name', 'description', 'persistent_store_service', 'required')
    model = PersistentStoreConnectionSetting


class PersistentStoreDatabaseSettingInline(TethysAppSettingInline):
    readonly_fields = ('name', 'description', 'required', 'spatial', 'initialized')
    fields = ('name', 'description', 'spatial', 'initialized', 'persistent_store_service', 'required')
    model = PersistentStoreDatabaseSetting

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(dynamic=False)


class TethysAppAdmin(GuardedModelAdmin):
    readonly_fields = ('package',)
    fields = ('package', 'name', 'description', 'tags', 'enabled', 'show_in_apps_library', 'enable_feedback')
    inlines = [CustomSettingInline,
               PersistentStoreConnectionSettingInline,
               PersistentStoreDatabaseSettingInline,
               DatasetServiceSettingInline,
               SpatialDatasetServiceSettingInline,
               WebProcessingServiceSettingInline]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class TethysExtensionAdmin(GuardedModelAdmin):
    readonly_fields = ('package', 'name', 'description')
    fields = ('package', 'name', 'description', 'enabled')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


admin.site.register(TethysApp, TethysAppAdmin)
admin.site.register(TethysExtension, TethysExtensionAdmin)
