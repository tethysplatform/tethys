import importlib
from unittest import mock

from tethys_tenants import models


def test_tenant_model_exists():
    assert hasattr(models.Tenant, "name")
    assert hasattr(models.Tenant, "created_on")
    assert hasattr(models.Tenant, "auto_create_schema")
    assert models.Tenant.auto_create_schema


def test_domain_model_exists():
    # Domain inherits from DomainMixin, so just checking it exists
    assert models.Domain is not None


@mock.patch("tethys_portal.optional_dependencies.has_module", return_value=False)
def test_models_not_imported_when_django_tenants_unavailable(mock_hm):
    importlib.reload(models)

    mock_hm.assert_called()
