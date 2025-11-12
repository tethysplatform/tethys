import importlib
from unittest import mock
from django.test import TestCase

from tethys_tenants import models


class TethysTenantsModelsTest(TestCase):
    def test_tenant_model_exists(self):
        self.assertTrue(hasattr(models.Tenant, "name"))
        self.assertTrue(hasattr(models.Tenant, "created_on"))
        self.assertTrue(hasattr(models.Tenant, "auto_create_schema"))
        self.assertTrue(models.Tenant.auto_create_schema)

    def test_domain_model_exists(self):
        # Domain inherits from DomainMixin, so just checking it exists
        self.assertIsNotNone(models.Domain)

    @mock.patch("tethys_portal.optional_dependencies.has_module", return_value=False)
    def test_models_not_imported_when_django_tenants_unavailable(self, mock_has_module):
        importlib.reload(models)

        mock_has_module.assert_called()
