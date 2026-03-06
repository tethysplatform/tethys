"""
********************************************************************************
* Name: admin.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

import json
import logging
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group, Permission
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.utils import ProgrammingError, OperationalError
from django.utils.html import format_html
from django.shortcuts import reverse
from django.db import models
from tethys_quotas.admin import TethysAppQuotasSettingInline, UserQuotasSettingInline
from guardian.admin import GuardedModelAdmin
from guardian.shortcuts import assign_perm, remove_perm
from guardian.models import GroupObjectPermission
from tethys_quotas.utilities import get_quota, _convert_storage_units
from tethys_quotas.handlers.workspace import WorkspaceQuotaHandler
from tethys_apps.models import (
    TethysApp,
    TethysExtension,
    CustomSetting,
    SecretCustomSetting,
    JSONCustomSetting,
    DatasetServiceSetting,
    SpatialDatasetServiceSetting,
    WebProcessingServiceSetting,
    SchedulerSetting,
    PersistentStoreConnectionSetting,
    PersistentStoreDatabaseSetting,
    ProxyApp,
)
from tethys_portal.optional_dependencies import (
    optional_import,
    has_module,
    MissingOptionalDependency,
)

# optional imports
MFAApp = optional_import("myAppNameConfig", from_module="mfa.apps")
User_Keys = optional_import("User_Keys", from_module="mfa.models")
JSONEditorWidget = optional_import(
    "JSONEditorWidget", from_module="django_json_widget.widgets"
)

tethys_log = logging.getLogger("tethys." + __name__)


class TethysAppSettingInline(admin.TabularInline):
    template = "tethys_portal/admin/edit_inline/tabular.html"

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class CustomSettingInline(TethysAppSettingInline):
    readonly_fields = ("name", "description", "type", "required")
    fields = ("name", "description", "type", "value", "include_in_api", "required")
    model = CustomSetting


class SecretCustomSettingForm(forms.ModelForm):
    value = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "input-text with-border",
                "placeholder": "secret custom setting",
            }
        )
    )

    class Meta:
        model = SecretCustomSetting
        fields = ["value", "include_in_api"]


class SecretCustomSettingInline(TethysAppSettingInline):
    readonly_fields = ("name", "description", "required")
    fields = ("name", "description", "value", "include_in_api", "required")
    model = SecretCustomSetting
    form = SecretCustomSettingForm


class JSONCustomSettingInline(TethysAppSettingInline):
    readonly_fields = ("name", "description", "required")
    fields = ("name", "description", "value", "include_in_api", "required")
    model = JSONCustomSetting
    options_default = {
        "modes": ["code", "text"],
        "search": False,
        "navigationBar": False,
    }

    width_default = "100%"
    height_default = "300px"
    if has_module(JSONEditorWidget):
        formfield_overrides = {
            models.JSONField: {
                "widget": JSONEditorWidget(
                    width=width_default, height=height_default, options=options_default
                )
            },
        }


class DatasetServiceSettingInline(TethysAppSettingInline):
    readonly_fields = ("name", "description", "required", "engine")
    fields = ("name", "description", "dataset_service", "engine", "required")
    model = DatasetServiceSetting


class SpatialDatasetServiceSettingInline(TethysAppSettingInline):
    readonly_fields = ("name", "description", "required", "engine")
    fields = ("name", "description", "spatial_dataset_service", "engine", "required")
    model = SpatialDatasetServiceSetting


class WebProcessingServiceSettingInline(TethysAppSettingInline):
    readonly_fields = ("name", "description", "required")
    fields = ("name", "description", "web_processing_service", "required")
    model = WebProcessingServiceSetting


class SchedulerSettingInline(TethysAppSettingInline):
    readonly_fields = ("name", "description", "required", "engine")
    fields = ("name", "description", "scheduler_service", "engine", "required")
    model = SchedulerSetting


# TODO: Figure out how to initialize persistent stores with button in admin
# Consider: https://medium.com/@hakibenita/how-to-add-custom-action-buttons-to-django-admin-8d266f5b0d41
class PersistentStoreConnectionSettingInline(TethysAppSettingInline):
    readonly_fields = ("name", "description", "required")
    fields = ("name", "description", "persistent_store_service", "required")
    model = PersistentStoreConnectionSetting


class PersistentStoreDatabaseSettingInline(TethysAppSettingInline):
    readonly_fields = ("name", "description", "required", "spatial", "initialized")
    fields = (
        "name",
        "description",
        "spatial",
        "initialized",
        "persistent_store_service",
        "required",
    )
    model = PersistentStoreDatabaseSetting

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(dynamic=False)


class TethysAppAdmin(GuardedModelAdmin):
    obj_perms_manage_template = "tethys_apps/guardian/extend_obj_perms_manage.html"
    readonly_fields = (
        "package",
        "manage_app_storage",
        "remove_app",
    )
    fields = (
        "package",
        "name",
        "description",
        "icon",
        "color",
        "tags",
        "back_url",
        "order",
        "enabled",
        "show_in_apps_library",
        "enable_feedback",
        "manage_app_storage",
        "remove_app",
    )
    inlines = [
        CustomSettingInline,
        JSONCustomSettingInline,
        SecretCustomSettingInline,
        PersistentStoreConnectionSettingInline,
        PersistentStoreDatabaseSettingInline,
        DatasetServiceSettingInline,
        SpatialDatasetServiceSettingInline,
        WebProcessingServiceSettingInline,
        SchedulerSettingInline,
        TethysAppQuotasSettingInline,
    ]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def manage_app_storage(self, app):
        codename = "tethysapp_workspace_quota"
        rqh = WorkspaceQuotaHandler(app)
        current_use = _convert_storage_units(rqh.units, rqh.get_current_use())
        quota = get_quota(app, codename)
        if quota["quota"]:
            quota = _convert_storage_units(quota["units"], quota["quota"])
        else:
            quota = "&#8734;"

        url = reverse("admin:clear_workspace", kwargs={"app_id": app.id})

        return format_html(
            """
        <span>{} of {}</span>
        <a id="clear-workspace" class="btn btn-danger btn-sm"
        href="{url}">
        Clear Workspace</a>
        """.format(
                current_use, quota, url=url
            )
        )

    def remove_app(self, app):
        url = reverse("admin:remove_app", kwargs={"app_id": app.id})
        return format_html(
            f"""
            <a
                id="remove-app" class="btn btn-danger btn-sm"
                href="{url}"
            >
                Remove App
            </a>
        """
        )


class TethysExtensionAdmin(GuardedModelAdmin):
    readonly_fields = ("package", "name", "description")
    fields = ("package", "name", "description", "enabled")

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class CustomUser(UserAdmin):
    def change_view(self, *args, **kwargs):
        if not isinstance(self.inlines, list):
            self.inlines = list(self.inlines)
        if UserQuotasSettingInline not in self.inlines:
            self.inlines.append(UserQuotasSettingInline)
        response = super().change_view(*args, **kwargs)

        # remove inline so it does not interfere with other models that relate to User
        self.inlines.remove(UserQuotasSettingInline)
        return response


class GOPAppAccessForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = "__all__"

    class Media:
        js = ("tethys_apps/js/group_admin.js",)

    # Override default permissions field to exclude the "Can Access App" permissions,
    # which are handled via the "proxy_apps" and "apps" fields
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.exclude(name__iendswith="Can Access App"),
        required=False,
        widget=FilteredSelectMultiple(verbose_name="permissions", is_stacked=False),
    )

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(verbose_name="Users", is_stacked=False),
    )

    proxy_apps = forms.ModelMultipleChoiceField(
        queryset=ProxyApp.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(verbose_name="Proxy Apps", is_stacked=False),
    )

    apps = forms.ModelMultipleChoiceField(
        queryset=TethysApp.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name="Apps",
            is_stacked=False,
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # set the apps widget attrs to ensure that the JavaScript can map between the app name and the app package
        # needs to be set here so the queryset is not loaded on import
        apps = self.fields["apps"]
        name_to_package = json.dumps({a.name: a.package for a in apps.queryset})
        apps.widget.attrs = {"data-app-packages": name_to_package}

        if self.instance.pk:
            # initialize the app and proxy apps fields
            for field, model in (
                (apps, TethysApp),
                (self.fields["proxy_apps"], ProxyApp),
            ):
                app_pks = [
                    int(g.object_pk)
                    for g in GroupObjectPermission.objects.filter(
                        group_id=self.instance.pk,
                        content_type_id=model.get_content_type().id,
                    ).distinct()
                ]
                field.initial = model.objects.filter(pk__in=app_pks)

            # initialize users field
            self.initial["users"] = self.instance.user_set.values_list("pk", flat=True)

            # initialize dynamic app fields
            for field in self.fields:
                if "_permissions" in field:
                    perms_pks = (
                        GroupObjectPermission.objects.values_list(
                            "permission_id", flat=True
                        )
                        .filter(group_id=self.instance.pk)
                        .distinct()
                    )
                    self.fields[field].initial = Permission.objects.filter(
                        pk__in=perms_pks,
                        codename__icontains=f'{field.split("_permissions")[0]}:',
                    ).exclude(codename__icontains=":access_app")
                elif "_groups" in field:
                    app_pk = TethysApp.objects.get(package=field.split("_groups")[0]).pk

                    included_groups_pks = []

                    groups_pks = (
                        GroupObjectPermission.objects.values_list("group_id", flat=True)
                        .filter(object_pk=app_pk)
                        .distinct()
                    )

                    current_group_perm_list = (
                        GroupObjectPermission.objects.values_list(
                            "permission_id", flat=True
                        )
                        .filter(object_pk=app_pk, group_id=self.instance.pk)
                        .distinct()
                        .exclude(permission__codename__icontains=":access_app")
                    )

                    for gpk in groups_pks:
                        group_perm_list = (
                            GroupObjectPermission.objects.values_list(
                                "permission_id", flat=True
                            )
                            .filter(group_id=gpk)
                            .distinct()
                        )
                        if set(group_perm_list).issubset(current_group_perm_list):
                            included_groups_pks.append(gpk)

                    if self.fields[field].queryset is not None:
                        self.fields[field].queryset = self.fields[
                            field
                        ].queryset.exclude(pk=self.instance.pk)

                    self.fields[field].initial = Group.objects.filter(
                        pk__in=included_groups_pks
                    ).exclude(pk=self.instance.pk)

    def clean(self):
        for field in self.fields:
            if "_permissions" in field:
                self.cleaned_data[field] = Permission.objects.filter(
                    pk__in=self.data.getlist(field)
                )
            elif "_groups" in field:
                self.cleaned_data[field] = Group.objects.filter(
                    pk__in=self.data.getlist(field)
                )

    def save(self, commit=True):
        group = super().save(commit=False)

        if not group.pk:
            group.save()

        # users
        self.instance.user_set.clear()
        self.instance.user_set.add(*self.cleaned_data["users"])

        # apps
        for field in ("apps", "proxy_apps"):
            assign_query = self.cleaned_data[field]
            if self.fields[field].initial:
                remove_query = self.fields[field].initial.difference(assign_query)

                for app in remove_query:
                    remove_perm(f"{app.package}:access_app", group, app)

            for app in assign_query:
                assign_perm(f"{app.package}:access_app", group, app)

        for field in self.fields:
            # permissions
            if "_permissions" in field:
                assign_perms_query = self.cleaned_data[field]
                if initial := self.fields[field].initial:
                    remove_perms_query = set(initial).difference(
                        set(assign_perms_query)
                    )
                    for perm in remove_perms_query:
                        remove_perm(
                            perm.codename,
                            group,
                            TethysApp.objects.filter(
                                package=field.split("_permissions")[0]
                            ),
                        )
                for perm in assign_perms_query:
                    assign_perm(
                        perm.codename,
                        group,
                        TethysApp.objects.filter(
                            package=field.split("_permissions")[0]
                        ),
                    )
            elif "_groups" in field:
                assign_groups_pks = (
                    self.cleaned_data[field].values_list("pk", flat=True).distinct()
                )
                assign_gperms_pks = (
                    GroupObjectPermission.objects.filter(group_id__in=assign_groups_pks)
                    .values_list("permission_id", flat=True)
                    .distinct()
                )
                assign_gperms_query = Permission.objects.filter(
                    pk__in=assign_gperms_pks
                )
                if self.fields[field].initial:
                    remove_groups_pks = (
                        self.fields[field]
                        .initial.difference(assign_gperms_pks)
                        .values_list("pk", flat=True)
                        .distinct()
                    )
                    remove_gperms_pks = (
                        GroupObjectPermission.objects.filter(
                            group_id__in=remove_groups_pks
                        )
                        .values_list("permission_id", flat=True)
                        .distinct()
                    )
                    remove_gperms_query = Permission.objects.filter(
                        pk__in=remove_gperms_pks
                    )

                    for gperm in remove_gperms_query:
                        remove_perm(
                            gperm.codename,
                            group,
                            TethysApp.objects.filter(package=field.split("_groups")[0]),
                        )
                for gperm in assign_gperms_query:
                    assign_perm(
                        gperm.codename,
                        group,
                        TethysApp.objects.filter(package=field.split("_groups")[0]),
                    )

        return group


def make_gop_app_access_form():
    """
    Create the group form dynamically, adding fields for permissions and groups for each app.
    """
    all_apps = TethysApp.objects.all()

    properties = {}

    for app_qs in all_apps:
        all_permissions_queryset = Permission.objects.filter(
            codename__icontains=app_qs.package
        ).exclude(codename__icontains=":access_app")

        properties[f"{app_qs.package}_permissions"] = forms.ModelMultipleChoiceField(
            queryset=all_permissions_queryset,
            required=False,
            widget=FilteredSelectMultiple(
                verbose_name=f"{app_qs.name} Permissions", is_stacked=False
            ),
        )

        group_with_app_perms = []
        for g in (
            GroupObjectPermission.objects.filter(object_pk=app_qs.pk)
            .values("group_id")
            .distinct()
        ):
            group_with_app_perms.append(int(g["group_id"]))
        all_groups_queryset = Group.objects.filter(pk__in=group_with_app_perms)

        properties[f"{app_qs.package}_groups"] = forms.ModelMultipleChoiceField(
            queryset=all_groups_queryset,
            required=False,
            widget=FilteredSelectMultiple(
                verbose_name=f"{app_qs.name} Groups", is_stacked=False
            ),
        )

    GOPAppAccessFormDynamic = type(
        "GOPAppAccessFormDynamic", (GOPAppAccessForm,), properties
    )

    return GOPAppAccessFormDynamic


class UserKeyAdmin(admin.ModelAdmin):
    fields = ("username", "added_on", "key_type", "enabled", "last_used")
    readonly_fields = ("username", "added_on", "key_type", "last_used")
    list_display = ("username", "added_on", "key_type", "enabled", "last_used")
    list_filter = ("username",)
    model = User_Keys


def register_custom_group():
    try:

        class CustomGroup(GroupAdmin):
            form = make_gop_app_access_form()

        admin.site.unregister(Group)
        admin.site.register(Group, CustomGroup)
    except (ProgrammingError, TypeError, OperationalError):
        tethys_log.warning("Unable to register CustomGroup.")


def register_user_keys_admin():
    try:
        MFAApp.verbose_name = "Multi-Factor Authentication"
        User_Keys._meta.verbose_name = "Users MFA Key"
        User_Keys._meta.verbose_name_plural = "Users MFA Keys"
        admin.site.register(User_Keys, UserKeyAdmin)
    except (ProgrammingError, MissingOptionalDependency):
        tethys_log.warning("Unable to register UserKeys.")


class ProxyAppAdmin(GuardedModelAdmin):
    obj_perms_manage_template = "tethys_apps/guardian/extend_obj_perms_manage.html"


register_custom_group()
admin.site.unregister(User)
admin.site.register(User, CustomUser)
if has_module(User_Keys):
    register_user_keys_admin()
admin.site.register(ProxyApp, ProxyAppAdmin)
admin.site.register(TethysApp, TethysAppAdmin)
admin.site.register(TethysExtension, TethysExtensionAdmin)
