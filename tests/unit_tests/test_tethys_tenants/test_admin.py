import importlib
from unittest import mock
from django.test import TestCase, RequestFactory
from django.contrib import admin
from django.http import Http404
from django.contrib.admin.sites import AdminSite

from tethys_tenants import models
from tethys_tenants import admin as tethys_tenants_admin


class TethysTenantsAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()

    def test_is_public_schema_function(self):
        # Mock request with public tenant
        public_request = mock.MagicMock()
        public_request.tenant.schema_name = "public"
        self.assertTrue(tethys_tenants_admin.is_public_schema(public_request))

        # Mock request with non-public tenant
        tenant_request = mock.MagicMock()
        tenant_request.tenant.schema_name = "tenant1"
        self.assertFalse(tethys_tenants_admin.is_public_schema(tenant_request))

    def test_public_schema_only_decorator(self):
        @tethys_tenants_admin.public_schema_only
        def dummy_view(self, request):
            return "success"

        # Test with public schema
        public_request = mock.MagicMock()
        public_request.tenant.schema_name = "public"
        result = dummy_view(None, public_request)
        self.assertEqual(result, "success")

        # Test with tenant schema - should raise Http404
        tenant_request = mock.MagicMock()
        tenant_request.tenant.schema_name = "tenant1"
        with self.assertRaises(Http404):
            dummy_view(None, tenant_request)

    def test_domain_admin_registration(self):
        registry = admin.site._registry
        self.assertIn(models.Domain, registry)
        self.assertIsInstance(registry[models.Domain], tethys_tenants_admin.DomainAdmin)

    def test_tenant_admin_registration(self):
        registry = admin.site._registry
        self.assertIn(models.Tenant, registry)
        self.assertIsInstance(registry[models.Tenant], tethys_tenants_admin.TenantAdmin)

    def test_tenant_admin_configuration(self):
        admin_instance = tethys_tenants_admin.TenantAdmin(models.Tenant, self.site)
        self.assertEqual(admin_instance.list_display, ("name",))

    def test_domain_admin_has_module_permission(self):
        admin_instance = tethys_tenants_admin.DomainAdmin(models.Domain, self.site)

        # Test with public schema
        public_request = mock.MagicMock()
        public_request.tenant.schema_name = "public"
        self.assertTrue(admin_instance.has_module_permission(public_request))

        # Test with tenant schema
        tenant_request = mock.MagicMock()
        tenant_request.tenant.schema_name = "tenant1"
        self.assertFalse(admin_instance.has_module_permission(tenant_request))

    def test_tenant_admin_has_module_permission(self):
        admin_instance = tethys_tenants_admin.TenantAdmin(models.Tenant, self.site)

        # Test with public schema
        public_request = mock.MagicMock()
        public_request.tenant.schema_name = "public"
        self.assertTrue(admin_instance.has_module_permission(public_request))

        # Test with tenant schema
        tenant_request = mock.MagicMock()
        tenant_request.tenant.schema_name = "tenant1"
        self.assertFalse(admin_instance.has_module_permission(tenant_request))

    def test_domain_admin_changelist_view_public_schema(self):
        admin_instance = tethys_tenants_admin.DomainAdmin(models.Domain, self.site)

        public_request = mock.MagicMock()
        public_request.tenant.schema_name = "public"

        with mock.patch(
            "django.contrib.admin.ModelAdmin.changelist_view"
        ) as mock_super:
            mock_super.return_value = "success"
            result = admin_instance.changelist_view(public_request)
            self.assertEqual(result, "success")
            mock_super.assert_called_once_with(public_request, None)

    def test_domain_admin_changelist_view_tenant_schema(self):
        admin_instance = tethys_tenants_admin.DomainAdmin(models.Domain, self.site)

        tenant_request = mock.MagicMock()
        tenant_request.tenant.schema_name = "tenant1"

        with self.assertRaises(Http404):
            admin_instance.changelist_view(tenant_request)

    @mock.patch("tethys_portal.optional_dependencies.has_module", return_value=False)
    def test_admin_graceful_handling_without_django_tenants(self, mock_has_module):
        importlib.reload(tethys_tenants_admin)

        # Verify has_module was called
        mock_has_module.assert_called()
