import pytest
from unittest import mock
from unittest.mock import MagicMock
from tethys_quotas.apps import TethysQuotasConfig
from django.db.utils import ProgrammingError, OperationalError


@pytest.fixture
def config():
    mock_module = MagicMock()
    mock_module.__file__ = "/fake/path/tethys_quotas/__init__.py"
    return TethysQuotasConfig("tethys_quotas", mock_module)


@pytest.mark.django_db
def test_ready_calls_sync_resource_quota_handlers(config):
    with mock.patch("tethys_quotas.apps.sync_resource_quota_handlers") as mock_sync:
        config.ready()
        mock_sync.assert_called_once()


@pytest.mark.django_db
def test_ready_programming_error_logs_warning(config):
    with (
        mock.patch(
            "tethys_quotas.apps.sync_resource_quota_handlers",
            side_effect=ProgrammingError(),
        ),
        mock.patch("tethys_quotas.apps.log") as mock_log,
    ):
        config.ready()
        mock_log.warning.assert_called_with(
            "Unable to sync resource quota handlers: Resource Quota table does not exist"
        )


@pytest.mark.django_db
def test_ready_operational_error_logs_warning(config):
    with (
        mock.patch(
            "tethys_quotas.apps.sync_resource_quota_handlers",
            side_effect=OperationalError(),
        ),
        mock.patch("tethys_quotas.apps.log") as mock_log,
    ):
        config.ready()
        mock_log.warning.assert_called_with(
            "Unable to sync resource quota handlers: No database found"
        )
