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
from django.forms import Textarea
from django.db import models
from tethys_config.models import SettingsCategory, Setting
from tethys_apps.admin import TethysAppSettingInline


class SettingInline(TethysAppSettingInline):
    fields = ("name", "content", "date_modified")
    readonly_fields = ("name", "date_modified")
    model = Setting
    extra = 0

    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 2, "cols": 65})},
    }


class SettingCategoryAdmin(admin.ModelAdmin):
    fields = ("name",)
    readonly_fields = ("name",)
    inlines = [SettingInline]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(SettingsCategory, SettingCategoryAdmin)
