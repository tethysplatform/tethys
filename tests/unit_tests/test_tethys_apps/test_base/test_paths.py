from pathlib import Path
import tempfile
import unittest
from unittest import mock

import sys

from django.conf import settings
from django.http import HttpRequest
from django.test import override_settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

import tethys_apps.base.app_base as tethys_app_base
from tethys_apps.base import paths
from tethys_apps.base.paths import TethysPath, _check_app_quota, _check_user_quota


class TestTethysPath(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch("tethys_apps.base.paths.Path")
    def test__init__value_error(self, mock_path):
        mock_file = mock.MagicMock()
        mock_file.is_file.return_value = True
        mock_path().resolve.return_value = mock_file
        self.assertRaises(ValueError, TethysPath, mock.MagicMock())
        mock_file.is_file.assert_called_once()

    def test_repr(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tethys_path = TethysPath(temp_dir)
        string_path = tethys_path.path
        self.assertEqual(repr(tethys_path), f'<TethysPath path="{string_path}">')

    def test_read_only(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tethys_path = TethysPath(temp_dir)
            self.assertFalse(tethys_path.read_only)

            tethys_path = TethysPath(temp_dir, read_only=True)
            self.assertTrue(tethys_path.read_only)

    def test_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir).resolve()
            for i in range(1, 4):
                with (temp_dir / f"file{i}.txt").open("w") as temp_file:
                    temp_file.write(f"This is file {i}")

            # List the files in the directory to verify they were created
            tethys_path = TethysPath(temp_dir)

            tethys_path_files_names_only = tethys_path.files(names_only=True)
            tethys_path_files = tethys_path.files()

            self.assertTrue("file1.txt" in tethys_path_files_names_only)
            self.assertTrue("file2.txt" in tethys_path_files_names_only)
            self.assertTrue("file3.txt" in tethys_path_files_names_only)
            self.assertEqual(len(tethys_path_files), 3)

            self.assertTrue(temp_dir / "file1.txt" in tethys_path_files)
            self.assertTrue(temp_dir / "file2.txt" in tethys_path_files)
            self.assertTrue(temp_dir / "file3.txt" in tethys_path_files)
            self.assertEqual(len(tethys_path_files), 3)

    def test_directories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir).resolve()
            for i in range(1, 4):
                (temp_dir / f"dir{i}").mkdir(parents=True)

            tethys_path = TethysPath(temp_dir)

            tethys_path_directories_names_only = tethys_path.directories(
                names_only=True
            )
            tethys_path_directories = tethys_path.directories()

            self.assertTrue("dir1" in tethys_path_directories_names_only)
            self.assertTrue("dir2" in tethys_path_directories_names_only)
            self.assertTrue("dir3" in tethys_path_directories_names_only)
            self.assertEqual(len(tethys_path_directories), 3)

            self.assertTrue(temp_dir / "dir1" in tethys_path_directories)
            self.assertTrue(temp_dir / "dir2" in tethys_path_directories)
            self.assertTrue(temp_dir / "dir3" in tethys_path_directories)
            self.assertEqual(len(tethys_path_directories), 3)

    def test_clear(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir).resolve()
            # Create three directories in the temporary directory
            with (temp_dir / "file1.txt").open("w") as temp_file:
                temp_file.write("This is file 1")
            for i in range(1, 4):
                new_dir = temp_dir / f"dir{i}"
                new_dir.mkdir(parents=True)

                # Create two files in each new directory
                for j in range(1, 3):
                    with (new_dir / f"file{j}.txt").open("w") as temp_file:
                        temp_file.write(f"This is file {j} in dir{i}")

                # Create a subdirectory in each new directory
                sub_dir = new_dir / "subdir"
                sub_dir.mkdir(parents=True)

                # Create one file in the subdirectory
                with (sub_dir / "file1.txt").open("w") as temp_file:
                    temp_file.write("This is file 1 in subdir of dir{i}")

            tethys_path_read_only = TethysPath(temp_dir, read_only=True)
            fs = tethys_path_read_only.files()
            ds = tethys_path_read_only.directories()

            self.assertEqual(len(fs), 1)  # This should probably be 10
            self.assertEqual(len(ds), 3)  # This should probably be 6

            with self.assertRaises(RuntimeError):
                tethys_path_read_only.clear()

            self.assertEqual(len(fs), 1)
            self.assertEqual(len(ds), 3)

            tethys_path = TethysPath(temp_dir)

            fs2 = tethys_path.files()
            ds2 = tethys_path.directories()

            self.assertEqual(len(fs2), 1)
            self.assertEqual(len(ds2), 3)

            tethys_path.clear()

            fs3 = tethys_path.files()
            ds3 = tethys_path.directories()

            self.assertEqual(len(fs3), 0)
            self.assertEqual(len(ds3), 0)

    def test_remove(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir).resolve()
            # Create three directories in the temporary directory
            with (temp_dir / "file1.txt").open("w") as temp_file:
                temp_file.write("This is file 1")
            for i in range(1, 4):
                new_dir = temp_dir / f"dir{i}"
                new_dir.mkdir(parents=True)

                # Create two files in each new directory
                for j in range(1, 3):
                    with (new_dir / f"file{j}.txt").open("w") as temp_file:
                        temp_file.write(f"This is file {j} in dir{i}")

            # test read only
            tethys_path_read_only = TethysPath(temp_dir, read_only=True)
            with self.assertRaises(RuntimeError):
                tethys_path_read_only.remove(f"{temp_dir}/file1.txt")

            tethys_path = TethysPath(temp_dir)
            fs = tethys_path.files()
            ds = tethys_path.directories()
            self.assertEqual(len(fs), 1)
            self.assertEqual(len(ds), 3)

            # test relative to
            with self.assertRaises(ValueError):
                tethys_path.remove(f"{temp_dir}/../test.txt")

            tethys_path.remove(f"{temp_dir}/file1.txt")
            fs2 = tethys_path.files()
            ds2 = tethys_path.directories()

            self.assertEqual(len(fs2), 0)
            self.assertEqual(len(ds2), 3)

            tethys_path.remove(f"{temp_dir}/dir1")
            fs3 = tethys_path.files()
            ds3 = tethys_path.directories()
            self.assertEqual(len(fs3), 0)
            self.assertEqual(len(ds3), 2)

    def test_get_size(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir).resolve()
            # Create three directories in the temporary directory
            with (temp_dir / "file1.txt").open("w") as temp_file:
                temp_file.write("This is file 1")
            for i in range(1, 4):
                new_dir = temp_dir / f"dir{i}"
                new_dir.mkdir(parents=True)

                # Create two files in each new directory
                for j in range(1, 3):
                    with (new_dir / f"file{j}.txt").open("w") as temp_file:
                        temp_file.write(f"This is file {j} in dir{i}")

            tethys_path = TethysPath(temp_dir)

            # Check size in bites (b)
            size = tethys_path.get_size()
            self.assertEqual(size, 14.0)

            # Check size in kilobytes (kb)
            size = tethys_path.get_size("kb")
            self.assertEqual(size, 0.013671875)


class TestTethysPathHelpers(unittest.TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        from tethys_apps.models import TethysApp

        self.mock_app_base_class = tethys_app_base.TethysAppBase()
        self.mock_request = mock.Mock(spec=HttpRequest)
        self.mock_app = TethysApp(name="test_app", package="test_app_package")
        self.user = User(username="tester")

        self.mock_request.user = self.user

    def tearDown(self):
        pass

    @mock.patch("tethys_apps.utilities.get_app_class")
    @mock.patch("tethys_apps.utilities.get_active_app")
    def test_resolve_app_class(self, mock_get_active_app, mock_get_app_class):
        mock_get_app_class.return_value = self.mock_app
        mock_get_active_app.return_value = self.mock_app

        a1 = paths._resolve_app_class(self.mock_app_base_class)
        self.assertEqual(a1, self.mock_app_base_class)
        mock_get_app_class.assert_not_called()
        mock_get_active_app.assert_not_called()

        a2 = paths._resolve_app_class(self.mock_request)
        self.assertEqual(a2, self.mock_app)
        mock_get_active_app.assert_called_with(self.mock_request, get_class=True)

        a3 = paths._resolve_app_class(self.mock_app)
        self.assertEqual(a3, self.mock_app)
        mock_get_app_class.assert_called_with(self.mock_app)

        with self.assertRaises(ValueError):
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
    def test___get_app_workspace_old(self, mock_ac, mock_am, mock_tw):
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

    @mock.patch("tethys_apps.base.paths._get_app_media_root")
    @mock.patch("tethys_apps.base.paths._resolve_app_class")
    @mock.patch("tethys_apps.base.paths.passes_quota")
    @mock.patch("tethys_apps.base.paths._resolve_user")
    @mock.patch("tethys_apps.base.paths.TethysPath")
    def test_add_path_decorator(self, mock_TethysPath, mock_ru, mock_pq, _, __):
        def fake_controller(request, user_media, *args, **kwargs):
            return user_media

        mock_TethysPath.return_value = "user_media_path"

        User = get_user_model()
        user = User(username="test_user")
        mock_ru.return_value = user

        mock_pq.return_value = True

        wrapped_controller = paths._add_path_decorator("user_media")(fake_controller)
        user_media = wrapped_controller(self.mock_request)
        self.assertEqual(user_media, "user_media_path")

    @mock.patch("tethys_apps.base.paths._get_app_media_root")
    @mock.patch("tethys_apps.base.paths._resolve_user")
    @mock.patch("tethys_apps.base.paths._resolve_app_class")
    @mock.patch("tethys_apps.base.paths.TethysPath")
    def test_add_path_decorator_no_user(self, mock_TethysPath, _, __, ___):
        def fake_controller(request, user_media, *args, **kwargs):
            return user_media

        mock_TethysPath.return_value = "user_media_return"

        wrapped_controller = paths._add_path_decorator("user_media")(fake_controller)

        with self.assertRaises(PermissionDenied):
            wrapped_controller(self.mock_request)

    def test_add_path_decorator_no_request(self):
        def fake_controller(request, user_media, *args, **kwargs):
            return user_media

        mock_user_media_func = mock.MagicMock()
        mock_user_media_func.return_value = "user_media_return"

        wrapped_controller_no_request = paths._add_path_decorator("user_media")(
            fake_controller
        )

        with self.assertRaises(ValueError) as exc:
            wrapped_controller_no_request(None)
        self.assertEqual(
            str(exc.exception),
            "No request given. The user_media decorator only works on controllers.",
        )
