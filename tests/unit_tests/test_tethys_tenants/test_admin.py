from unittest import mock
from django.test import RequestFactory
from django.contrib import admin
from django.http import Http404
from django.contrib.admin.sites import AdminSite

from tethys_tenants import models
from tethys_tenants import admin as tethys_tenants_admin
import pytest


@pytest.fixture
def setup_test():
    factory = RequestFactory()
    site = AdminSite()

    class InstanceProperties:
        pass

    props = InstanceProperties()
    props.factory = factory
    props.site = site
    yield props


def test_is_public_schema_function():
    # Mock request with public tenant
    public_request = mock.MagicMock()
    public_request.tenant.schema_name = "public"
    assert tethys_tenants_admin.is_public_schema(public_request)

    # Mock request with non-public tenant
    tenant_request = mock.MagicMock()
    tenant_request.tenant.schema_name = "tenant1"
    assert not tethys_tenants_admin.is_public_schema(tenant_request)


def test_public_schema_only_decorator():
    @tethys_tenants_admin.public_schema_only
    def dummy_view(self, request):
        return "success"

    # Test with public schema
    public_request = mock.MagicMock()
    public_request.tenant.schema_name = "public"
    result = dummy_view(None, public_request)
    assert result == "success"

    # Test with tenant schema - should raise Http404
    tenant_request = mock.MagicMock()
    tenant_request.tenant.schema_name = "tenant1"
    with pytest.raises(Http404):
        dummy_view(None, tenant_request)


def test_domain_admin_registration():
    registry = admin.site._registry
    assert models.Domain in registry
    assert isinstance(registry[models.Domain], tethys_tenants_admin.DomainAdmin)


def test_tenant_admin_registration():
    registry = admin.site._registry
    assert models.Tenant in registry
    assert isinstance(registry[models.Tenant], tethys_tenants_admin.TenantAdmin)


def test_tenant_admin_configuration(setup_test):
    admin_instance = tethys_tenants_admin.TenantAdmin(models.Tenant, setup_test.site)
    assert admin_instance.list_display == ("name",)


def test_domain_admin_has_module_permission(setup_test):
    admin_instance = tethys_tenants_admin.DomainAdmin(models.Domain, setup_test.site)

    public_request = mock.MagicMock()
    public_request.tenant.schema_name = "public"
    assert admin_instance.has_module_permission(public_request)

    tenant_request = mock.MagicMock()
    tenant_request.tenant.schema_name = "tenant1"
    assert not admin_instance.has_module_permission(tenant_request)


def test_tenant_admin_has_module_permission(setup_test):
    admin_instance = tethys_tenants_admin.TenantAdmin(models.Tenant, setup_test.site)

    public_request = mock.MagicMock()
    public_request.tenant.schema_name = "public"
    assert admin_instance.has_module_permission(public_request)

    tenant_request = mock.MagicMock()
    tenant_request.tenant.schema_name = "tenant1"
    assert not admin_instance.has_module_permission(tenant_request)


def test_domain_admin_changelist_view_public_schema(setup_test):
    admin_instance = tethys_tenants_admin.DomainAdmin(models.Domain, setup_test.site)

    public_request = mock.MagicMock()
    public_request.tenant.schema_name = "public"

    with mock.patch("django.contrib.admin.ModelAdmin.changelist_view") as mock_super:
        mock_super.return_value = "success"
        result = admin_instance.changelist_view(public_request)
        assert result == "success"
        mock_super.assert_called_once_with(public_request, None)


def test_domain_admin_changelist_view_tenant_schema(setup_test):
    admin_instance = tethys_tenants_admin.DomainAdmin(models.Domain, setup_test.site)

    tenant_request = mock.MagicMock()
    tenant_request.tenant.schema_name = "tenant1"

    with pytest.raises(Http404):
        admin_instance.changelist_view(tenant_request)


def test_domain_admin_change_view_public_schema(setup_test):
    admin_instance = tethys_tenants_admin.DomainAdmin(models.Domain, setup_test.site)

    public_request = mock.MagicMock()
    public_request.tenant.schema_name = "public"

    with mock.patch("django.contrib.admin.ModelAdmin.change_view") as mock_super:
        mock_super.return_value = "success"
        result = admin_instance.change_view(public_request, "123", "test_url")
        assert result == "success"
        mock_super.assert_called_once_with(public_request, "123", "test_url", None)


def test_domain_admin_change_view_tenant_schema(setup_test):
    admin_instance = tethys_tenants_admin.DomainAdmin(models.Domain, setup_test.site)

    tenant_request = mock.MagicMock()
    tenant_request.tenant.schema_name = "tenant1"

    with pytest.raises(Http404):
        admin_instance.change_view(tenant_request, "123", "test_url")


def test_domain_admin_add_view_public_schema(setup_test):
    admin_instance = tethys_tenants_admin.DomainAdmin(models.Domain, setup_test.site)

    public_request = mock.MagicMock()
    public_request.tenant.schema_name = "public"

    with mock.patch("django.contrib.admin.ModelAdmin.add_view") as mock_super:
        mock_super.return_value = "success"
        result = admin_instance.add_view(public_request, "test_url")
        assert result == "success"
        mock_super.assert_called_once_with(public_request, "test_url", None)


def test_domain_admin_add_view_tenant_schema(setup_test):
    admin_instance = tethys_tenants_admin.DomainAdmin(models.Domain, setup_test.site)

    tenant_request = mock.MagicMock()
    tenant_request.tenant.schema_name = "tenant1"

    with pytest.raises(Http404):
        admin_instance.add_view(tenant_request, "test_url")


def test_tenants_admin_changelist_view_public_schema(setup_test):
    admin_instance = tethys_tenants_admin.TenantAdmin(models.Tenant, setup_test.site)

    public_request = mock.MagicMock()
    public_request.tenant.schema_name = "public"

    with mock.patch("django.contrib.admin.ModelAdmin.changelist_view") as mock_super:
        mock_super.return_value = "success"
        result = admin_instance.changelist_view(public_request)
        assert result == "success"
        mock_super.assert_called_once_with(public_request, None)


def test_tenants_admin_changelist_view_tenant_schema(setup_test):
    admin_instance = tethys_tenants_admin.TenantAdmin(models.Tenant, setup_test.site)

    tenant_request = mock.MagicMock()
    tenant_request.tenant.schema_name = "tenant1"

    with pytest.raises(Http404):
        admin_instance.changelist_view(tenant_request)


def test_tenants_admin_change_view_public_schema(setup_test):
    admin_instance = tethys_tenants_admin.TenantAdmin(models.Tenant, setup_test.site)

    public_request = mock.MagicMock()
    public_request.tenant.schema_name = "public"

    with mock.patch("django.contrib.admin.ModelAdmin.change_view") as mock_super:
        mock_super.return_value = "success"
        result = admin_instance.change_view(public_request, "123", "test_url")
        assert result == "success"
        mock_super.assert_called_once_with(public_request, "123", "test_url", None)


def test_tenants_admin_change_view_tenant_schema(setup_test):
    admin_instance = tethys_tenants_admin.TenantAdmin(models.Tenant, setup_test.site)

    tenant_request = mock.MagicMock()
    tenant_request.tenant.schema_name = "tenant1"

    with pytest.raises(Http404):
        admin_instance.change_view(tenant_request, "123", "test_url")


def test_tenants_admin_add_view_public_schema(setup_test):
    admin_instance = tethys_tenants_admin.TenantAdmin(models.Tenant, setup_test.site)

    public_request = mock.MagicMock()
    public_request.tenant.schema_name = "public"

    with mock.patch("django.contrib.admin.ModelAdmin.add_view") as mock_super:
        mock_super.return_value = "success"
        result = admin_instance.add_view(public_request, "test_url")
        assert result == "success"
        mock_super.assert_called_once_with(public_request, "test_url", None)


def test_tenants_admin_add_view_tenant_schema(setup_test):
    admin_instance = tethys_tenants_admin.TenantAdmin(models.Tenant, setup_test.site)

    tenant_request = mock.MagicMock()
    tenant_request.tenant.schema_name = "tenant1"

    with pytest.raises(Http404):
        admin_instance.add_view(tenant_request, "test_url")
