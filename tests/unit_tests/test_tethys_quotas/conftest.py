import pytest
import tethys_quotas.apps as tqa


@pytest.fixture(scope="function")
def load_quotas(test_app):
    c = tqa.TethysQuotasConfig(tqa.TethysQuotasConfig.name, tqa)
    c.ready()
