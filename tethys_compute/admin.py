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
from tethys_compute.models import Scheduler, TethysJob


@admin.register(Scheduler)
class SchedulerAdmin(admin.ModelAdmin):
    list_display = ['name', 'host', 'username', 'password', 'private_key_path', 'private_key_pass']


@admin.register(TethysJob)
class JobAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'label', 'user', 'creation_time', 'execute_time', 'completion_time',
                    'status']
    list_display_links = ('name',)

    def has_add_permission(self, request):
        return False
