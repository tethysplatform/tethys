from django.db import models
from tethys_portal.optional_dependencies import optional_import, has_module

TenantMixin = optional_import("TenantMixin", from_module="django_tenants.models")
DomainMixin = optional_import("DomainMixin", from_module="django_tenants.models")

if has_module(TenantMixin):
    class Tenant(TenantMixin):
        name = models.CharField(max_length=100)
        created_on = models.DateField(auto_now_add=True)

        # default true, schema will be automatically created and synced when it is saved
        auto_create_schema = True

if has_module(DomainMixin):
    class Domain(DomainMixin):
        pass
