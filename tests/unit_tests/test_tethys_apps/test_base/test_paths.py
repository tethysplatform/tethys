import tempfile
from pathlib import Path
import pytest
from unittest import mock

import sys

from django.conf import settings
from django.http import HttpRequest
from django.test import override_settings
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

import tethys_apps.base.app_base as tethys_app_base
from tethys_apps.base import paths
from tethys_apps.base.paths import TethysPath, _check_app_quota, _check_user_quota


@mock.patch("tethys_apps.base.paths.Path")
def test_tethyspath_init_value_error(mock_path):
    mock_file = mock.MagicMock()
    mock_file.is_file.return_value = True
    mock_path().resolve.return_value = mock_file
    with pytest.raises(ValueError):
        TethysPath(mock.MagicMock())
    mock_file.is_file.assert_called_once()


def test_tethyspath_repr():
    with tempfile.TemporaryDirectory() as temp_dir:
        tethys_path = TethysPath(temp_dir)
        string_path = tethys_path.path
        assert repr(tethys_path) == f'<TethysPath path="{string_path}">'  # noqa: E501


def test_tethyspath_read_only():
    with tempfile.TemporaryDirectory() as temp_dir:
        tethys_path = TethysPath(temp_dir)
        assert not tethys_path.read_only
        tethys_path = TethysPath(temp_dir, read_only=True)
        assert tethys_path.read_only


def test_tethyspath_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir).resolve()
        for i in range(1, 4):
            with (temp_dir / f"file{i}.txt").open("w") as temp_file:
                temp_file.write(f"This is file {i}")
        tethys_path = TethysPath(temp_dir)
        tethys_path_files_names_only = tethys_path.files(names_only=True)
        tethys_path_files = tethys_path.files()
        assert "file1.txt" in tethys_path_files_names_only
        assert "file2.txt" in tethys_path_files_names_only
        assert "file3.txt" in tethys_path_files_names_only
        assert len(tethys_path_files) == 3
        assert temp_dir / "file1.txt" in tethys_path_files
        assert temp_dir / "file2.txt" in tethys_path_files
        assert temp_dir / "file3.txt" in tethys_path_files
        assert len(tethys_path_files) == 3


def test_tethyspath_directories():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir).resolve()
        for i in range(1, 4):
            (temp_dir / f"dir{i}").mkdir(parents=True)
        tethys_path = TethysPath(temp_dir)
        tethys_path_directories_names_only = tethys_path.directories(names_only=True)
        tethys_path_directories = tethys_path.directories()
        assert "dir1" in tethys_path_directories_names_only
        assert "dir2" in tethys_path_directories_names_only
        assert "dir3" in tethys_path_directories_names_only
        assert len(tethys_path_directories) == 3
        assert temp_dir / "dir1" in tethys_path_directories
        assert temp_dir / "dir2" in tethys_path_directories
        assert temp_dir / "dir3" in tethys_path_directories
        assert len(tethys_path_directories) == 3


def test_tethyspath_clear():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir).resolve()
        with (temp_dir / "file1.txt").open("w") as temp_file:
            temp_file.write("This is file 1")
        for i in range(1, 4):
            new_dir = temp_dir / f"dir{i}"
            new_dir.mkdir(parents=True)
            for j in range(1, 3):
                with (new_dir / f"file{j}.txt").open("w") as temp_file:
                    temp_file.write(f"This is file {j} in dir{i}")
            sub_dir = new_dir / "subdir"
            sub_dir.mkdir(parents=True)
            with (sub_dir / "file1.txt").open("w") as temp_file:
                temp_file.write("This is file 1 in subdir of dir{i}")
        tethys_path_read_only = TethysPath(temp_dir, read_only=True)
        fs = tethys_path_read_only.files()
        ds = tethys_path_read_only.directories()
        assert len(fs) == 1
        assert len(ds) == 3
        with pytest.raises(RuntimeError):
            tethys_path_read_only.clear()
        assert len(fs) == 1
        assert len(ds) == 3
        tethys_path = TethysPath(temp_dir)
        fs2 = tethys_path.files()
        ds2 = tethys_path.directories()
        assert len(fs2) == 1
        assert len(ds2) == 3
        tethys_path.clear()
        fs3 = tethys_path.files()
        ds3 = tethys_path.directories()
        assert len(fs3) == 0
        assert len(ds3) == 0


def test_tethyspath_remove():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir).resolve()
        with (temp_dir / "file1.txt").open("w") as temp_file:
            temp_file.write("This is file 1")
        for i in range(1, 4):
            new_dir = temp_dir / f"dir{i}"
            new_dir.mkdir(parents=True)
            for j in range(1, 3):
                with (new_dir / f"file{j}.txt").open("w") as temp_file:
                    temp_file.write(f"This is file {j} in dir{i}")
        tethys_path_read_only = TethysPath(temp_dir, read_only=True)
        with pytest.raises(RuntimeError):
            tethys_path_read_only.remove(f"{temp_dir}/file1.txt")
        tethys_path = TethysPath(temp_dir)
        fs = tethys_path.files()
        ds = tethys_path.directories()
        assert len(fs) == 1
        assert len(ds) == 3
        with pytest.raises(ValueError):
            tethys_path.remove(f"{temp_dir}/../test.txt")
        tethys_path.remove(f"{temp_dir}/file1.txt")
        fs2 = tethys_path.files()
        ds2 = tethys_path.directories()
        assert len(fs2) == 0
        assert len(ds2) == 3
        tethys_path.remove(f"{temp_dir}/dir1")
        fs3 = tethys_path.files()
        ds3 = tethys_path.directories()
        assert len(fs3) == 0
        assert len(ds3) == 2


def test_tethyspath_get_size():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir).resolve()
        with (temp_dir / "file1.txt").open("w") as temp_file:
            temp_file.write("This is file 1")
        for i in range(1, 4):
            new_dir = temp_dir / f"dir{i}"
            new_dir.mkdir(parents=True)
            for j in range(1, 3):
                with (new_dir / f"file{j}.txt").open("w") as temp_file:
                    temp_file.write(f"This is file {j} in dir{i}")
        tethys_path = TethysPath(temp_dir)
        size = tethys_path.get_size()
        assert size == 14.0
        size = tethys_path.get_size("kb")
        assert size == 0.013671875


@pytest.fixture()
@pytest.mark.django_db
def tethys_path_helpers():
    from django.contrib.auth.models import User
    from tethys_apps.models import TethysApp

    mock_app_base_class = tethys_app_base.TethysAppBase()
    mock_request = mock.Mock(spec=HttpRequest)
    mock_app_class = TethysApp
    mock_app = TethysApp(name="test_app", package="test_app")
    user = User(username="tester")
    mock_request.user = user
    mock_app.package = "app_package"
    return {
        "mock_app_base_class": mock_app_base_class,
        "mock_request": mock_request,
        "mock_app_class": mock_app_class,
        "mock_app": mock_app,
        "user": user,
    }


@mock.patch("tethys_apps.utilities.get_app_class")
@mock.patch("tethys_apps.utilities.get_active_app")
@pytest.mark.django_db
def test_resolve_app_class(
    mock_get_active_app, mock_get_app_class, tethys_path_helpers
):
    mock_app = tethys_path_helpers["mock_app"]
    mock_app_base_class = tethys_path_helpers["mock_app_base_class"]
    mock_request = tethys_path_helpers["mock_request"]
    mock_app_class = tethys_path_helpers["mock_app_class"]
    mock_get_app_class.return_value = mock_app
    mock_get_active_app.return_value = mock_app
    a1 = paths._resolve_app_class(mock_app_base_class)
    assert a1 == mock_app_base_class
    mock_get_app_class.assert_not_called()
    mock_get_active_app.assert_not_called()
    a2 = paths._resolve_app_class(mock_request)
    assert a2 == mock_app
    mock_get_active_app.assert_called_with(mock_request, get_class=True)
    a3 = paths._resolve_app_class(mock_app)
    assert a3 == mock_app
    mock_get_app_class.assert_called_with(mock_app)
    with pytest.raises(ValueError):
        paths._resolve_app_class(None)

def test_resolve_user(self):
    user = paths._resolve_user(self.user).username
    self.assertEqual(user, "tester")

    request_user = paths._resolve_user(self.mock_request).username
    self.assertEqual(request_user, "tester")

    with self.assertRaises(ValueError):
        paths._resolve_user(None)

@mock.patch("tethys_apps.base.paths._resolve_user")
@mock.patch("tethys_apps.base.paths._resolve_app_class")
def test__get_user_workspace_unauthenticated(self, mock_ru, _):
    fake_user = mock.Mock()
    fake_user.is_anonymous = True
    mock_ru.return_value = fake_user
    with self.assertRaises(PermissionDenied) as err:
        paths._get_user_workspace(self.mock_request, self.mock_request.user)

    self.assertEqual(str(err.exception), "User is not authenticated.")

def test_get_app_workspace_root(self):
    p = paths._get_app_workspace_root(self.mock_app)
    self.assertEqual(p, Path(settings.TETHYS_WORKSPACES_ROOT + "/test_app_package"))

@override_settings(USE_OLD_WORKSPACES_API=True)
@override_settings(DEBUG=True)
def test_old_get_app_workspace_root(self):
    p = paths._get_app_workspace_root(self.mock_app)
    self.assertEqual(p, Path(sys.modules[self.mock_app.__module__].__file__).parent)

@override_settings(USE_OLD_WORKSPACES_API=True)
@override_settings(DEBUG=True)
@mock.patch("tethys_apps.base.workspace.TethysWorkspace")
@mock.patch("tethys_apps.utilities.get_app_model")
@mock.patch("tethys_apps.utilities.get_app_class")
def test____get_app_workspace_old(self, mock_ac, mock_am, mock_tw):
    mock_ac.return_value = self.mock_app
    mock_am.return_value = self.mock_app
    p = paths._get_app_workspace(self.mock_app_base_class, bypass_quota=True)
    expected_path = mock_tw(
        Path(sys.modules[self.mock_app.__module__].__file__).parent
        / "workspaces"
        / "app_workspace"
    )
    self.assertEqual(p, expected_path)

@override_settings(USE_OLD_WORKSPACES_API=True)
@mock.patch("tethys_apps.base.paths._get_app_workspace_old")
@mock.patch("tethys_apps.utilities.get_app_model")
def test__get_app_workspace_old(
    self, mock_get_app_model, mock__get_app_workspace_old
):
    mock_get_app_model.return_value = self.mock_app_base_class
    mock_return = mock.MagicMock()
    mock__get_app_workspace_old.return_value = mock_return
    ws = paths.get_app_workspace(self.mock_request)

    mock__get_app_workspace_old.assert_called_once()
    self.assertEqual(ws, mock_return)

@override_settings(USE_OLD_WORKSPACES_API=True)
@override_settings(DEBUG=True)
@mock.patch("tethys_apps.base.workspace.TethysWorkspace")
@mock.patch("tethys_apps.utilities.get_app_model")
@mock.patch("tethys_apps.utilities.get_app_class")
def test___get_user_workspace_old(self, mock_ac, mock_am, mock_tw):
    mock_am.return_value = self.mock_app
    mock_ac.return_value = self.mock_app

    p = paths._get_user_workspace(
        self.mock_app_base_class, self.user, bypass_quota=True
    )
    expected_path = mock_tw(
        Path(sys.modules[self.mock_app.__module__].__file__).parent
        / "workspaces"
        / "tester"
    )
    self.assertEqual(p, expected_path)

@mock.patch("tethys_apps.base.paths._get_user_workspace_old")
@mock.patch("tethys_apps.utilities.get_active_app")
@override_settings(USE_OLD_WORKSPACES_API=True)
@pytest.mark.django_db
def test__get_user_workspace_old(
    self, mock_get_active_app, mock__get_user_workspace_old
):
    mock_get_active_app.return_value = self.mock_app
    mock_return = mock.MagicMock()
    mock__get_user_workspace_old.return_value = mock_return
    ws = paths.get_user_workspace(self.mock_request, self.user)

    mock__get_user_workspace_old.assert_called_once()
    self.assertEqual(ws, mock_return)

@override_settings(MEDIA_ROOT="media_root")
def test_get_app_media_root(self):
    p = paths._get_app_media_root(self.mock_app)
    self.assertEqual(p, Path(settings.MEDIA_ROOT + "/test_app_package"))

@mock.patch("tethys_apps.utilities.get_app_model")
@mock.patch("tethys_apps.base.paths.passes_quota", return_value=True)
def test__check_app_quota_passes(self, mock_passes_quota, mock_get_app_model):
    mock_get_app_model.return_value = self.mock_app_base_class
    try:
        _check_app_quota(mock_get_app_model(self.mock_request))
    except AssertionError:
        self.fail(
            "_check_app_quota() raised AssertionError when it shouldn't have."
        )

@mock.patch("tethys_apps.utilities.get_active_app")
@mock.patch("tethys_apps.base.paths.passes_quota", return_value=False)
def test__check_app_quota_fails(
    self,
    mock_passes_quota,
    mock_get_active_app,
):
    mock_get_active_app.return_value = self.mock_app
    with self.assertRaises(AssertionError):
        _check_app_quota(self.mock_request)

@mock.patch("tethys_apps.base.paths.passes_quota", return_value=True)
def test__check_user_quota_User(self, mock_passes_quota):
    try:
        _check_user_quota(self.user)
    except AssertionError:
        self.fail(
            "_check_user_quota() raised AssertionError when it shouldn't have."
        )

@mock.patch("tethys_apps.base.paths.passes_quota", return_value=True)
def test__check_user_quota_HttpRequest(self, mock_passes_quota):
    try:
        _check_user_quota(self.mock_request)
    except AssertionError:
        self.fail(
            "_check_user_quota() raised AssertionError when it shouldn't have."
        )

@mock.patch("tethys_apps.base.paths.passes_quota", return_value=True)
def test__check_user_quota_TethysApp(self, mock_passes_quota):
    with self.assertRaises(ValueError):
        _check_user_quota(self.mock_app)

@mock.patch("tethys_apps.base.paths.passes_quota", return_value=False)
def test__check_user_quota_fails(self, mock_passes_quota):
    with self.assertRaises(AssertionError):
        _check_user_quota(self.user)

@override_settings(MEDIA_ROOT="media_root")
def test_get_app_media_root(tethys_path_helpers):
    mock_app = tethys_path_helpers["mock_app"]
    p = paths._get_app_media_root(mock_app)
    assert p == Path(settings.MEDIA_ROOT + "/app_package")


@mock.patch("tethys_apps.utilities.get_active_app")
@mock.patch("tethys_apps.base.paths._get_app_media_root")
@mock.patch("tethys_apps.base.paths._resolve_app_class")
@mock.patch("tethys_apps.base.paths.passes_quota")
@mock.patch("tethys_apps.base.paths._resolve_user")
@mock.patch("tethys_apps.base.paths.TethysPath")
def test_add_path_decorator(mock_TethysPath, mock_ru, mock_pq, _, __, mock_get_active_app, tethys_path_helpers):
    def fake_controller(request, user_media, *args, **kwargs):
        return user_media

    mock_app = tethys_path_helpers["mock_app"]
    mock_request = tethys_path_helpers["mock_request"]
    user = tethys_path_helpers["user"]
    mock_get_active_app.return_value = mock_app

    mock_TethysPath.return_value = "user_media_path"
    mock_ru.return_value = user
    mock_pq.return_value = True

    wrapped_controller = paths._add_path_decorator("user_media")(fake_controller)
    user_media = wrapped_controller(mock_request)
    assert user_media == "user_media_path"


@mock.patch("tethys_apps.utilities.get_active_app")
@mock.patch("tethys_apps.base.paths._get_app_media_root")
@mock.patch("tethys_apps.base.paths._resolve_user")
@mock.patch("tethys_apps.base.paths._resolve_app_class")
@mock.patch("tethys_apps.base.paths.TethysPath")
def test_add_path_decorator_no_user(mock_TethysPath, _, __, ___, mock_get_active_app, tethys_path_helpers):
    def fake_controller(request, user_media, *args, **kwargs):
        return user_media

    mock_app = tethys_path_helpers["mock_app"]
    mock_request = tethys_path_helpers["mock_request"]
    mock_get_active_app.return_value = mock_app

    mock_TethysPath.return_value = "user_media_return"

    wrapped_controller = paths._add_path_decorator("user_media")(fake_controller)

    with pytest.raises(PermissionDenied) as exc:
        wrapped_controller(mock_request)

    assert str(exc.value) == "User is not authenticated."


def test_add_path_decorator_no_request():
    def fake_controller(request, user_media, *args, **kwargs):
        return user_media

    mock_user_media_func = mock.MagicMock()
    mock_user_media_func.return_value = "user_media_return"
    wrapped_controller_no_request = paths._add_path_decorator("user_media")(
        fake_controller
    )
    with pytest.raises(ValueError) as exc:
        wrapped_controller_no_request(None)
    assert (
        str(exc.value)
        == "No request given. The user_media decorator only works on controllers."
    )
