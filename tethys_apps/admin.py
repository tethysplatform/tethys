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
from tethys_apps.models import TethysApp


class TethysAppAdmin(GuardedModelAdmin):
    readonly_fields = ('package',)
    fields = ('package', 'name', 'description', 'enabled', 'show_in_apps_library', 'enable_feedback', 'feedback_emails')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

admin.site.register(TethysApp, TethysAppAdmin)
