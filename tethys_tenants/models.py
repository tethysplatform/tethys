from django.db import models
from tethys_portal.optional_dependencies import optional_import, has_module

TenantMixin = optional_import("TenantMixin", from_module="django_tenants.models")
DomainMixin = optional_import("DomainMixin", from_module="django_tenants.models")

if has_module(TenantMixin):

    class Tenant(TenantMixin):
        name = models.CharField(max_length=100)
        created_on = models.DateField(auto_now_add=True)

        # Schema will be automatically created and synced on save when True
        auto_create_schema = True


if has_module(DomainMixin):

    class Domain(DomainMixin):
        pass


if has_module("django_tenants"):

    class App(models.Model):
        """Model to associate apps with specific tenants"""

        tenant = models.ForeignKey(
            Tenant, on_delete=models.CASCADE, related_name="tenant_apps"
        )
        app_package = models.CharField(max_length=200)
        enabled = models.BooleanField(default=True)

        class Meta:
            app_label = "tethys_tenants"  # The Django app this belongs to
            verbose_name = "Tenant App"
            verbose_name_plural = "Tenant Apps"
            unique_together = ("tenant", "app_package")

        def __str__(self):
            return f"{self.tenant.schema_name}: {self.app_package}"
