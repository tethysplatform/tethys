"""
********************************************************************************
* Name: admin.py
* Author: Scott Christensen
* Created On: 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""

from django.contrib import admin
from django.utils.html import format_html
from django import forms
from tethys_compute.models import TethysJob
from tethys_compute.models.condor.condor_scheduler import CondorScheduler
from tethys_compute.models.dask.dask_scheduler import DaskScheduler


@admin.register(DaskScheduler)
class DaskSchedulerAdmin(admin.ModelAdmin):
    list_display = ["name", "host", "timeout", "heartbeat_interval", "append_link"]
    list_display_links = ["name", "append_link"]

    def append_link(self, obj):
        if obj.dashboard:
            dask_status_link = '<a href="%s" target="_blank">%s</a>' % (
                "../../dask-dashboard/status/" + str(obj.id),
                "Launch DashBoard",
            )
            return format_html(dask_status_link)

    append_link.allow_tags = True
    append_link.short_description = "dashboard"


class CondorSchedulerAdminForm(forms.ModelForm):
    class Meta:
        model = CondorScheduler
        fields = (
            "name",
            "host",
            "port",
            "username",
            "password",
            "private_key_path",
            "private_key_pass",
        )
        widgets = {
            "password": forms.PasswordInput(),
            "private_key_pass": forms.PasswordInput(),
        }


@admin.register(CondorScheduler)
class CondorSchedulerAdmin(admin.ModelAdmin):
    form = CondorSchedulerAdminForm
    list_display = ["name", "host", "port", "username", "private_key_path"]


@admin.register(TethysJob)
class JobAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "description",
        "label",
        "user",
        "creation_time",
        "execute_time",
        "completion_time",
        "status",
    ]
    list_display_links = ("name",)

    def has_add_permission(self, request, obj=None):
        return False
