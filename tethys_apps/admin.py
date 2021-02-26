"""
********************************************************************************
* Name: admin.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
import logging
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group, Permission
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.utils import ProgrammingError
from django.utils.html import format_html
from django.shortcuts import reverse
from tethys_quotas.admin import TethysAppQuotasSettingInline, UserQuotasSettingInline
from guardian.admin import GuardedModelAdmin
from guardian.shortcuts import assign_perm, remove_perm
from guardian.models import GroupObjectPermission
from mfa.models import User_Keys
from tethys_quotas.utilities import get_quota, _convert_storage_units
from tethys_quotas.handlers.workspace import WorkspaceQuotaHandler
from tethys_apps.models import (TethysApp,
                                TethysExtension,
                                CustomSetting,
                                DatasetServiceSetting,
                                SpatialDatasetServiceSetting,
                                WebProcessingServiceSetting,
                                PersistentStoreConnectionSetting,
                                PersistentStoreDatabaseSetting,
                                ProxyApp)

tethys_log = logging.getLogger('tethys.' + __name__)


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
    obj_perms_manage_template = \
        "tethys_apps/guardian/extend_obj_perms_manage.html"
    readonly_fields = ('package', 'manage_app_storage',)
    fields = ('package', 'name', 'description', 'icon', 'color', 'tags', 'enabled', 'show_in_apps_library',
              'enable_feedback', 'manage_app_storage',)
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
        rqh = WorkspaceQuotaHandler(app)
        current_use = _convert_storage_units(rqh.units, rqh.get_current_use())
        quota = get_quota(app, codename)
        if quota['quota']:
            quota = _convert_storage_units(quota['units'], quota['quota'])
        else:
            quota = "&#8734;"

        url = reverse('admin:clear_workspace', kwargs={'app_id': app.id})

        return format_html("""
        <span>{} of {}</span>
        <a id="clear-workspace" class="btn btn-danger btn-sm"
        href="{url}">
        Clear Workspace</a>
        """.format(current_use, quota, url=url))


class TethysExtensionAdmin(GuardedModelAdmin):
    readonly_fields = ('package', 'name', 'description')
    fields = ('package', 'name', 'description', 'enabled')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class CustomUser(UserAdmin):
    def add_view(self, *args, **kwargs):
        if UserQuotasSettingInline in self.inlines:
            self.inlines.pop(self.inlines.index(UserQuotasSettingInline))
        return super().add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        if UserQuotasSettingInline not in self.inlines:
            self.inlines.append(UserQuotasSettingInline)
        return super().change_view(*args, **kwargs)


class GOPAppAccessForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = "__all__"

    class Media:
        js = ('tethys_apps/js/group_admin.js',)

    apps = forms.ModelMultipleChoiceField(
        queryset=TethysApp.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name='Apps',
            is_stacked=False
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            app_pks = []
            for gop in GroupObjectPermission.objects.values('object_pk').distinct().filter(group_id=self.instance.pk):
                app_pks.append(int(gop['object_pk']))
            self.fields['apps'].initial = TethysApp.objects.filter(pk__in=app_pks)

            for field in self.fields:
                if '_permissions' in field:
                    perms_pks = GroupObjectPermission.objects.values_list('permission_id', flat=True) \
                        .filter(group_id=self.instance.pk).distinct()
                    self.fields[field].initial = Permission.objects \
                        .filter(pk__in=perms_pks, codename__icontains=f'{field.split("_permissions")[0]}:') \
                        .exclude(codename__icontains=':access_app')
                elif '_groups' in field:
                    app_pk = TethysApp.objects.get(package=field.split('_groups')[0]).pk

                    included_groups_pks = []

                    groups_pks = GroupObjectPermission.objects.values_list('group_id', flat=True) \
                        .filter(object_pk=app_pk).distinct()

                    current_group_perm_list = GroupObjectPermission.objects.values_list('permission_id', flat=True) \
                        .filter(object_pk=app_pk, group_id=self.instance.pk).distinct() \
                        .exclude(permission__codename__icontains=':access_app')

                    for gpk in groups_pks:
                        group_perm_list = GroupObjectPermission.objects.values_list('permission_id', flat=True) \
                            .filter(group_id=gpk).distinct()
                        if set(group_perm_list).issubset(current_group_perm_list):
                            included_groups_pks.append(gpk)

                    if self.fields[field].queryset is not None:
                        self.fields[field].queryset = self.fields[field].queryset.exclude(pk=self.instance.pk)

                    self.fields[field].initial = Group.objects \
                        .filter(pk__in=included_groups_pks) \
                        .exclude(pk=self.instance.pk)

    def clean(self):
        for field in self.fields:
            if '_permissions' in field:
                self.cleaned_data[field] = Permission.objects.filter(pk__in=self.data.getlist(field))
            elif '_groups' in field:
                self.cleaned_data[field] = Group.objects.filter(pk__in=self.data.getlist(field))

    def save(self, commit=True):
        group = super().save(commit=False)

        if not group.pk:
            group.save()

        # apps
        assign_apps_query = self.cleaned_data['apps']
        if self.fields['apps'].initial:
            remove_apps_query = self.fields['apps'].initial.difference(assign_apps_query)

            for app in remove_apps_query:
                remove_perm(f'{app.package}:access_app', group, app)

        for app in assign_apps_query:
            assign_perm(f'{app.package}:access_app', group, app)

        for field in self.fields:
            # permissions
            if '_permissions' in field:
                assign_perms_query = self.cleaned_data[field]
                if self.fields[field].initial:
                    remove_perms_query = self.fields[field].initial.difference(assign_perms_query)

                    for perm in remove_perms_query:
                        remove_perm(perm.codename, group,
                                    TethysApp.objects.filter(package=field.split('_permissions')[0]))
                for perm in assign_perms_query:
                    assign_perm(perm.codename, group, TethysApp.objects.filter(package=field.split('_permissions')[0]))
            elif '_groups' in field:
                assign_groups_pks = self.cleaned_data[field].values_list('pk', flat=True).distinct()
                assign_gperms_pks = GroupObjectPermission.objects.filter(group_id__in=assign_groups_pks) \
                    .values_list('permission_id', flat=True) \
                    .distinct()
                assign_gperms_query = Permission.objects.filter(pk__in=assign_gperms_pks)
                if self.fields[field].initial:
                    remove_groups_pks = self.fields[field].initial.difference(assign_gperms_pks) \
                        .values_list('pk', flat=True).distinct()
                    remove_gperms_pks = GroupObjectPermission.objects.filter(group_id__in=remove_groups_pks) \
                        .values_list('permission_id', flat=True) \
                        .distinct()
                    remove_gperms_query = Permission.objects.filter(pk__in=remove_gperms_pks)

                    for gperm in remove_gperms_query:
                        remove_perm(gperm.codename, group,
                                    TethysApp.objects.filter(package=field.split('_groups')[0]))
                for gperm in assign_gperms_query:
                    assign_perm(gperm.codename, group, TethysApp.objects.filter(package=field.split('_groups')[0]))

        return group


def make_gop_app_access_form():
    """
    Create the group form dynamically, adding fields for permissions and groups for each app.
    """
    all_apps = TethysApp.objects.all()

    properties = {}

    for app_qs in all_apps:
        all_permissions_queryset = Permission.objects \
            .filter(codename__icontains=app_qs.package) \
            .exclude(codename__icontains=':access_app')

        properties[f'{app_qs.package}_permissions'] = forms.ModelMultipleChoiceField(
            queryset=all_permissions_queryset,
            required=False,
            widget=FilteredSelectMultiple(
                verbose_name=f'{app_qs.name} Permissions',
                is_stacked=False
            )
        )

        group_with_app_perms = []
        for g in GroupObjectPermission.objects.filter(object_pk=app_qs.pk).values('group_id').distinct():
            group_with_app_perms.append(int(g['group_id']))
        all_groups_queryset = Group.objects.filter(pk__in=group_with_app_perms)

        properties[f'{app_qs.package}_groups'] = forms.ModelMultipleChoiceField(
            queryset=all_groups_queryset,
            required=False,
            widget=FilteredSelectMultiple(
                verbose_name=f'{app_qs.name} Groups',
                is_stacked=False
            )
        )

    GOPAppAccessFormDynamic = type(
        'GOPAppAccessFormDynamic',
        (GOPAppAccessForm,),
        properties
    )

    return GOPAppAccessFormDynamic


class UserKeyAdmin(admin.ModelAdmin):
    fields = ('username', 'added_on', 'key_type', 'enabled', 'last_used')
    readonly_fields = ('username', 'added_on', 'key_type', 'last_used')
    list_display = ('username', 'added_on', 'key_type', 'enabled', 'last_used')
    list_filter = ('username', )
    model = User_Keys


def register_custom_group():
    try:
        class CustomGroup(GroupAdmin):
            form = make_gop_app_access_form()

        admin.site.unregister(Group)
        admin.site.register(Group, CustomGroup)
    except ProgrammingError:
        tethys_log.warning("Unable to register CustomGroup.")


def register_user_keys_admin():
    try:
        User_Keys._meta.verbose_name = 'Users MFA Key'
        User_Keys._meta.verbose_name_plural = 'Users MFA Keys'
        admin.site.register(User_Keys, UserKeyAdmin)
    except ProgrammingError:
        tethys_log.warning("Unable to register UserKeys.")


register_custom_group()
admin.site.unregister(User)
admin.site.register(User, CustomUser)
register_user_keys_admin()
admin.site.register(ProxyApp)
admin.site.register(TethysApp, TethysAppAdmin)
admin.site.register(TethysExtension, TethysExtensionAdmin)
