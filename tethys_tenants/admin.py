"""
********************************************************************************
* Name: admin.py
* Author: Michael Souffront
* Created On: 2025
* License: BSD 2-Clause
********************************************************************************
"""

from functools import wraps
from django.contrib import admin
from django.http import Http404
from tethys_portal.optional_dependencies import has_module
from tethys_tenants.models import Tenant, Domain


if has_module("django_tenants"):
    def is_public_schema(request):
        """Check if current request is from public schema"""
        return getattr(request.tenant, 'schema_name', None) == 'public'
    
    def public_schema_only(view_func):
        """Decorator to ensure view is only accessible from public schema"""
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            if not is_public_schema(request):
                raise Http404("Page not found")
            return view_func(self, request, *args, **kwargs)
        return wrapper

    @admin.register(Domain)
    class DomainAdmin(admin.ModelAdmin):
        list_display = ("domain", "tenant")

        def has_module_permission(self, request):
            return is_public_schema(request)

        @public_schema_only
        def changelist_view(self, request, extra_context=None):
            return super().changelist_view(request, extra_context)

        @public_schema_only
        def change_view(self, request, object_id, form_url='', extra_context=None):
            return super().change_view(request, object_id, form_url, extra_context)

        @public_schema_only
        def add_view(self, request, form_url='', extra_context=None):
            return super().add_view(request, form_url, extra_context)


    @admin.register(Tenant)
    class TenantAdmin(admin.ModelAdmin):
        list_display = ("name",)

        def has_module_permission(self, request):
            return is_public_schema(request)

        @public_schema_only
        def changelist_view(self, request, extra_context=None):
            return super().changelist_view(request, extra_context)

        @public_schema_only
        def change_view(self, request, object_id, form_url='', extra_context=None):
            return super().change_view(request, object_id, form_url, extra_context)

        @public_schema_only
        def add_view(self, request, form_url='', extra_context=None):
            return super().add_view(request, form_url, extra_context)
