import importlib
from unittest import mock
from django.apps import apps

from tethys_tenants import apps as tenant_apps


def test_tethys_tenants_config():
    app_config = apps.get_app_config("tethys_tenants")
    name = app_config.name
    verbose_name = app_config.verbose_name

    assert "tethys_tenants" == name
    assert "Tethys Tenants" == verbose_name
    assert isinstance(app_config, tenant_apps.TethysTenantsConfig)


@mock.patch("tethys_portal.optional_dependencies.has_module", return_value=False)
def test_tethys_tenants_config_unavailable(mock_hm):
    importlib.reload(tenant_apps)

    # Verify has_module was called
    mock_hm.assert_called()
