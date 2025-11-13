"""
********************************************************************************
* Name: admin.py
* Author: Michael Souffront
* Created On: 2025
* License: BSD 2-Clause
********************************************************************************
"""

from django.db import models
from tethys_portal.optional_dependencies import has_module


if has_module("django_tenants"):

    from django_tenants.models import TenantMixin, DomainMixin

    class Tenant(TenantMixin):
        name = models.CharField(max_length=100)
        created_on = models.DateField(auto_now_add=True)

        # Schema will be automatically created and synced on save when True
        auto_create_schema = True

    class Domain(DomainMixin):
        pass
