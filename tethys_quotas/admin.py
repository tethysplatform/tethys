"""
********************************************************************************
* Name: admin.py
* Author: tbayer
* Created On: February 12, 2019
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""

from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from django.contrib import admin
from django.contrib.auth.models import User
from tethys_apps.models import TethysApp
from tethys_quotas.models import ResourceQuota, UserQuota, TethysAppQuota


@admin.register(ResourceQuota)
class ResourceQuotaAdmin(admin.ModelAdmin):
    readonly_fields = ("codename", "name", "description", "units", "applies_to")
    fields = (
        "name",
        "description",
        "default",
        "units",
        "codename",
        "applies_to",
        "help",
        "active",
        "impose_default",
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class TethysQuotasSettingInline(admin.TabularInline):
    template = "tethys_quotas/admin/edit_inline/tabular.html"

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class UserQuotasSettingInline(TethysQuotasSettingInline):
    readonly_fields = ("name", "description", "default", "units")
    fields = ("name", "description", "value", "default", "units")
    model = UserQuota

    def get_queryset(self, request):
        qs = super(UserQuotasSettingInline, self).get_queryset(request)

        resource_quota_qs = ResourceQuota.objects.filter(
            applies_to="django.contrib.auth.models.User"
        )
        if resource_quota_qs.exists():
            resource_quota = resource_quota_qs.first()

            if not resource_quota.active:
                return None

            user_id = request.resolver_match.kwargs.get("object_id")

            user = User.objects.get(id=user_id)

            qs = qs.filter(entity=user)
            if not qs.exists() and resource_quota.impose_default:
                user_quota = UserQuota(
                    resource_quota=resource_quota,
                    entity=user,
                    value=None,
                )
                user_quota.save()

        return qs

    def name(*args):
        # Sets the name field as a link to the resource quota admin change page
        rq = None
        for arg in args:
            if isinstance(arg, UserQuota):
                rq = arg.resource_quota

        content_type = ContentType.objects.get_for_model(rq.__class__)
        admin_url = reverse(
            "admin:%s_%s_change" % (content_type.app_label, content_type.model),
            args=(rq.id,),
        )
        return format_html("""<a href="{}">{}</a>""".format(admin_url, rq.name))

    def description(*args):
        for arg in args:
            if isinstance(arg, UserQuota):
                return arg.resource_quota.description

    def default(*args):
        # Sets the name field as a link to the resource quota admin change page
        rq = None
        for arg in args:
            if isinstance(arg, UserQuota):
                rq = arg.resource_quota
                if rq.impose_default:
                    return rq.default
                else:
                    return "--"

    def units(*args):
        for arg in args:
            if isinstance(arg, UserQuota):
                return arg.resource_quota.units


class TethysAppQuotasSettingInline(TethysQuotasSettingInline):
    readonly_fields = ("name", "description", "default", "units")
    fields = ("name", "description", "value", "default", "units")
    model = TethysAppQuota

    def get_queryset(self, request):
        qs = super(TethysAppQuotasSettingInline, self).get_queryset(request)

        resource_quota_qs = ResourceQuota.objects.filter(
            applies_to="tethys_apps.models.TethysApp"
        )
        if resource_quota_qs.exists():
            resource_quota = resource_quota_qs.first()

            if not resource_quota.active:
                return None

            tethys_app_id = request.resolver_match.kwargs["object_id"]
            tethys_app = TethysApp.objects.get(id=tethys_app_id)

            qs = qs.filter(entity=tethys_app)
            if not qs.exists() and resource_quota.impose_default:
                app_quota = TethysAppQuota(
                    resource_quota=resource_quota,
                    entity=tethys_app,
                    value=None,
                )
                app_quota.save()

        return qs

    def name(*args):
        # Sets the name field as a link to the resource quota admin change page
        rq = None
        for arg in args:
            if isinstance(arg, TethysAppQuota):
                rq = arg.resource_quota

        content_type = ContentType.objects.get_for_model(rq.__class__)
        admin_url = reverse(
            "admin:{}_{}_change".format(content_type.app_label, content_type.model),
            args=(rq.id,),
        )
        return format_html("""<a href="{}">{}</a>""".format(admin_url, rq.name))

    def description(*args):
        for arg in args:
            if isinstance(arg, TethysAppQuota):
                return arg.resource_quota.description

    def default(*args):
        # Sets the name field as a link to the resource quota admin change page
        rq = None
        for arg in args:
            if isinstance(arg, TethysAppQuota):
                rq = arg.resource_quota
                if rq.impose_default:
                    return rq.default
                else:
                    return "--"

    def units(*args):
        for arg in args:
            if isinstance(arg, TethysAppQuota):
                return arg.resource_quota.units
