import pytest
from unittest.mock import MagicMock, patch
from django.contrib.auth.models import User
from tethys_apps.models import TethysApp
from tethys_quotas.handlers.workspace import WorkspaceQuotaHandler


@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    return user


@pytest.fixture
def mock_app():
    app = MagicMock(spec=TethysApp)
    app.name = "TestApp"
    return app


@pytest.fixture
def mock_harvester_apps(mock_app):
    # Return a list with one app
    return [mock_app]


@pytest.fixture
def handler_user(mock_user):
    return WorkspaceQuotaHandler(entity=mock_user)


@pytest.fixture
def handler_app(mock_app):
    return WorkspaceQuotaHandler(entity=mock_app)


def test_get_current_use_user(handler_user, mock_user, mock_harvester_apps):
    workspace = MagicMock()
    media = MagicMock()
    workspace.get_size.return_value = 2
    media.get_size.return_value = 3
    with (
        patch("tethys_quotas.handlers.workspace.SingletonHarvester") as mock_harvester,
        patch(
            "tethys_quotas.handlers.workspace._get_user_workspace",
            return_value=workspace,
        ) as mock_get_user_workspace,
        patch(
            "tethys_quotas.handlers.workspace._get_user_media", return_value=media
        ) as mock_get_user_media,
    ):
        mock_harvester.return_value.apps = mock_harvester_apps
        result = handler_user.get_current_use()
        assert result == 5.0
        mock_get_user_workspace.assert_called_once_with(
            mock_harvester_apps[0], mock_user, bypass_quota=True
        )
        mock_get_user_media.assert_called_once_with(
            mock_harvester_apps[0], mock_user, bypass_quota=True
        )


def test_get_current_use_app(handler_app, mock_app, mock_harvester_apps):
    workspace = MagicMock()
    media = MagicMock()
    workspace.get_size.return_value = 4
    media.get_size.return_value = 6
    with (
        patch("tethys_quotas.handlers.workspace.SingletonHarvester") as mock_harvester,
        patch(
            "tethys_quotas.handlers.workspace._get_app_workspace",
            return_value=workspace,
        ) as mock_get_app_workspace,
        patch(
            "tethys_quotas.handlers.workspace._get_app_media", return_value=media
        ) as mock_get_app_media,
    ):
        mock_harvester.return_value.apps = mock_harvester_apps
        mock_app.name = "TestApp"
        result = handler_app.get_current_use()
        assert result == 10.0
        mock_get_app_workspace.assert_called_once_with(
            mock_harvester_apps[0], bypass_quota=True
        )
        mock_get_app_media.assert_called_once_with(
            mock_harvester_apps[0], bypass_quota=True
        )


def test_get_current_use_app_not_found(handler_app, mock_app):
    with patch("tethys_quotas.handlers.workspace.SingletonHarvester") as mock_harvester:
        mock_harvester.return_value.apps = []
        mock_app.name = "TestApp"
        result = handler_app.get_current_use()
        assert result == 0.0
