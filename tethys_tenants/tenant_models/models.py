from django.db import models
from tethys_tenants.models import Tenant
from tethys_portal.optional_dependencies import has_module


if has_module("django_tenants"):
    class App(models.Model):
        """Model to associate apps with specific tenants"""
        tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='tenant_apps')
        app_package = models.CharField(max_length=200)  # e.g., "tethysapp.my_app"
        enabled = models.BooleanField(default=True)
        
        class Meta:
            app_label = 'tenant_models'  # This tells Django which app this belongs to
            verbose_name = "Tenant App"
            verbose_name_plural = "Tenant Apps"
            unique_together = ('tenant', 'app_package')
            
        def __str__(self):
            return f"{self.tenant.schema_name}: {self.app_package}"
