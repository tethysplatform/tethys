import pytest
from tethys_quotas.apps import TethysQuotasConfig


@pytest.fixture(scope="function")
def load_quotas(test_app):
    c = TethysQuotasConfig(TethysQuotasConfig.name, "tethys_quotas")
    c.ready()
