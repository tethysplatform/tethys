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
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.shortcuts import reverse
from tethys_quotas.admin import TethysAppQuotasSettingInline, UserQuotasSettingInline
from tethys_quotas.helpers import _convert_storage_units
from guardian.admin import GuardedModelAdmin
from tethys_quotas.helpers import get_quota, get_resource_available
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
    readonly_fields = ('package', 'manage_app_storage',)
    fields = ('package', 'name', 'description', 'tags', 'enabled', 'show_in_apps_library', 'enable_feedback',
              'manage_app_storage',)
    inlines = [CustomSettingInline,
               PersistentStoreConnectionSettingInline,
               PersistentStoreDatabaseSettingInline,
               DatasetServiceSettingInline,
               SpatialDatasetServiceSettingInline,
               WebProcessingServiceSettingInline,
               TethysAppQuotasSettingInline]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def manage_app_storage(self, app):
        codename = 'tethysapp_workspace_quota'
        quota = get_quota(app, codename)
        resource_available = None
        total_storage = None
        if quota:
            resource_available = get_resource_available(app, codename)
            total_storage = quota['quota'] - resource_available['resource_available']

        url = reverse('admin:clear_workspace', kwargs={'app_id': app.id})

        quota = _convert_storage_units(quota['units'], quota['quota'])
        total_storage = _convert_storage_units(resource_available['units'], total_storage)

        return mark_safe("""
        <span>{} of {}</span>
        <a id="clear-workspace" class="btn btn-danger btn-sm"
        href="{url}">
        Clear Workspace</a>
        """.format(total_storage, quota, url=url))


class TethysExtensionAdmin(GuardedModelAdmin):
    readonly_fields = ('package', 'name', 'description')
    fields = ('package', 'name', 'description', 'enabled')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class UserAdmin(BaseUserAdmin):
    inlines = (UserQuotasSettingInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(TethysApp, TethysAppAdmin)
admin.site.register(TethysExtension, TethysExtensionAdmin)
