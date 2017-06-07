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
from django.forms import Textarea
from django.db import models
from tethys_compute.models import SettingsCategory, Setting, Scheduler, TethysJob
# Register your models here.


class SettingInline(admin.TabularInline):
    fields = ('name', 'content', 'date_modified')
    readonly_fields = ('name', 'date_modified')
    model = Setting
    extra = 0

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 65})},
    }

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(SettingsCategory)
class SettingCategoryAdmin(admin.ModelAdmin):
    fields = ('name',)
    readonly_fields = ('name',)
    inlines = [SettingInline]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(Scheduler)
class SchedulerAdmin(admin.ModelAdmin):
    list_display = ['name', 'host', 'username', 'password', 'private_key_path', 'private_key_pass']


@admin.register(TethysJob)
class JobAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'label', 'user', 'creation_time', 'execute_time', 'completion_time', 'status']
    list_display_links = ('name',)

    def has_add_permission(self, request):
        return False