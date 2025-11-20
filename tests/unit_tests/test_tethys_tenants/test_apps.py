import importlib
from unittest import mock
from django.test import TestCase
from django.apps import apps

from tethys_tenants import apps as tenant_apps


class TethysTenantsAppsTest(TestCase):
    def test_tethys_tenants_config(self):
        app_config = apps.get_app_config("tethys_tenants")
        name = app_config.name
        verbose_name = app_config.verbose_name

        self.assertEqual("tethys_tenants", name)
        self.assertEqual("Tethys Tenants", verbose_name)
        self.assertTrue(isinstance(app_config, tenant_apps.TethysTenantsConfig))

    @mock.patch("tethys_portal.optional_dependencies.has_module", return_value=False)
    def test_tethys_tenants_config_unavailable(self, mock_has_module):
        importlib.reload(tenant_apps)

        # Verify has_module was called
        mock_has_module.assert_called()
