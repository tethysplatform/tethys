from tethys_basemaps.permissions import can_capture
from unittest import mock


def test_can_capture_no_user():
    assert can_capture(None) is False


def test_can_capture_unauthenticated_user():
    mock_user = mock.MagicMock()
    mock_user.is_authenticated = False
    assert can_capture(mock_user) is False


def test_can_capture_inactive_user():
    mock_user = mock.MagicMock()
    mock_user.is_authenticated = True
    mock_user.is_active = False
    assert can_capture(mock_user) is False


def test_can_capture_is_staff():
    mock_user = mock.MagicMock()
    mock_user.is_authenticated = True
    mock_user.is_active = True
    mock_user.is_staff = True
    assert can_capture(mock_user) is True


def test_can_capture_user_has_permission():
    mock_user = mock.MagicMock()
    mock_user.is_authenticated = True
    mock_user.is_active = True
    mock_user.is_staff = False
    mock_user.has_perm.return_value = True
    assert can_capture(mock_user) is True


def test_can_capture_user_without_permission():
    mock_user = mock.MagicMock()
    mock_user.is_authenticated = True
    mock_user.is_active = True
    mock_user.is_staff = False
    mock_user.has_perm.return_value = False
    assert can_capture(mock_user) is False
