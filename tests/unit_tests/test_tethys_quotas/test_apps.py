import warnings

import pytest
from unittest import mock
from unittest.mock import MagicMock
from tethys_quotas.apps import TethysQuotasConfig
import django
from django.db.backends.utils import CursorWrapper
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


@pytest.mark.skipif(
    django.VERSION < (5, 0),
    reason="app initialization warning introduced in Django 5.0",
)
@pytest.mark.django_db
def test_ready_suppresses_db_init_warning(config):
    # syncing quota handlers intentionally queries the database during app
    # initialization, so Django's RuntimeWarning about it should be suppressed
    # (see issue #1060)
    with mock.patch(
        "tethys_quotas.apps.sync_resource_quota_handlers",
        side_effect=lambda: warnings.warn(
            CursorWrapper.APPS_NOT_READY_WARNING_MSG,
            category=RuntimeWarning,
            stacklevel=2,
        ),
    ):
        with warnings.catch_warnings(record=True) as recorded:
            warnings.simplefilter("always")
            config.ready()
    assert recorded == []


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
