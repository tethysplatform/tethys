import unittest
from tethys_apps.models import TethysApp
import tethys_apps.base.workspace as base_workspace
import shutil
from pathlib import Path
from unittest import mock
from ... import UserFactory
from django.http import HttpRequest
from django.core.exceptions import PermissionDenied
import tethys_apps.base.app_base as tethys_app_base
from tethys_apps.base.workspace import (
    _get_user_workspace,
    _get_user_workspace_old,
    user_workspace,
    _get_app_workspace,
    _get_app_workspace_old,
    app_workspace,
)


@user_workspace
def user_dec_controller(request, user_workspace):
    return user_workspace


@app_workspace
def app_dec_controller(request, app_workspace):
    return app_workspace


class TethysAppChild(tethys_app_base.TethysAppBase):
    """
    Tethys app class for Test App.
    """

    name = "Test App"
    index = "home"
    icon = "test_app/images/icon.gif"
    package = "test_app"
    root_url = "test-app"
    color = "#2c3e50"
    description = "Place a brief description of your app here."


class TestUrlMap(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent.absolute()
        self.test_root = self.root / "test_workspace"
        self.test_root_a = self.test_root / "test_workspace_a"
        self.test_root2 = self.root / "test_workspace2"
        self.app_base = tethys_app_base.TethysAppBase()
        self.app = TethysApp(name="test_app", package="test_app")

        self.user = UserFactory()

    def tearDown(self):
        if self.test_root.is_dir():
            shutil.rmtree(self.test_root)
        if self.test_root2.is_dir():
            shutil.rmtree(self.test_root2)

    def test_TethysWorkspace(self):
        # Test Create new workspace folder test_workspace
        result = base_workspace.TethysWorkspace(path=str(self.test_root))
        workspace = '<TethysWorkspace path="{0}">'.format(self.test_root)

        # Create new folder inside test_workspace
        base_workspace.TethysWorkspace(path=str(self.test_root_a))

        # Create new folder test_workspace2
        base_workspace.TethysWorkspace(path=str(self.test_root2))

        self.assertEqual(result.__repr__(), workspace)
        self.assertEqual(result.path, str(self.test_root))

        # Create Files
        file_list = ["test1.txt", "test2.txt"]
        for file_name in file_list:
            # Create file
            (self.test_root / file_name).touch()

        # Test files with full path
        result = base_workspace.TethysWorkspace(path=str(self.test_root)).files(
            full_path=True
        )
        for file_name in file_list:
            self.assertIn(str(self.test_root / file_name), result)

        # Test files without full path
        result = base_workspace.TethysWorkspace(path=str(self.test_root)).files()
        for file_name in file_list:
            self.assertIn(file_name, result)

        # Test Directories with full path
        result = base_workspace.TethysWorkspace(path=str(self.root)).directories(
            full_path=True
        )
        self.assertIn(str(self.test_root), result)
        self.assertIn(str(self.test_root2), result)

        # Test Directories without full path
        result = base_workspace.TethysWorkspace(path=str(self.root)).directories()
        self.assertIn("test_workspace", result)
        self.assertIn("test_workspace2", result)
        self.assertNotIn(self.test_root, result)
        self.assertNotIn(self.test_root2, result)

        # Write to file
        (self.test_root / "test2.txt").write_text("Hello World")

        # Test size greater than zero
        workspace_size = base_workspace.TethysWorkspace(
            path=str(self.test_root)
        ).get_size()
        self.assertTrue(workspace_size > 0)

        # Test get size unit conversion
        workspace_size_kb = base_workspace.TethysWorkspace(
            path=self.test_root
        ).get_size("kb")
        self.assertEqual(workspace_size / 1024, workspace_size_kb)

        # Test Remove file
        base_workspace.TethysWorkspace(path=str(self.test_root)).remove("test2.txt")

        # Verify that the file has been remove
        self.assertFalse((self.test_root / "test2.txt").is_file())

        # Test Remove Directory
        base_workspace.TethysWorkspace(path=str(self.root)).remove(str(self.test_root2))

        # Verify that the Directory has been remove
        self.assertFalse(self.test_root2.is_dir())

        # Test Clear
        base_workspace.TethysWorkspace(path=str(self.test_root)).clear()

        # Test size equal to zero
        workspace_size = base_workspace.TethysWorkspace(
            path=str(self.test_root)
        ).get_size()
        self.assertTrue(workspace_size == 0)

        # Verify that the Directory has been remove
        self.assertFalse(self.test_root_a.is_dir())

        # Verify that the File has been remove
        self.assertFalse((self.test_root / "test1.txt").is_file())

        # Test don't allow overwriting the path property
        workspace = base_workspace.TethysWorkspace(path=str(self.test_root))
        workspace.path = "foo"
        self.assertEqual(str(self.test_root), workspace.path)

    @mock.patch("tethys_apps.base.workspace.TethysWorkspace")
    @mock.patch("tethys_apps.utilities.get_app_class")
    def test__get_user_workspace_user(self, mock_gac, mock_tws):
        mock_gac.return_value = self.app
        ret = _get_user_workspace(self.app_base, self.user)
        expected_path = Path("workspaces") / "user_workspaces" / self.user.username
        rts_call_args = mock_tws.call_args_list
        self.assertEqual(ret, mock_tws())
        self.assertIn(str(expected_path), rts_call_args[0][0][0])

    @mock.patch("tethys_apps.base.workspace.TethysWorkspace")
    @mock.patch("tethys_apps.utilities.get_app_class")
    def test__get_user_workspace_http(self, mock_gac, mock_tws):
        request = HttpRequest()
        request.user = self.user
        mock_gac.return_value = self.app
        ret = _get_user_workspace(self.app_base, request)
        expected_path = Path("workspaces") / "user_workspaces" / self.user.username
        rts_call_args = mock_tws.call_args_list
        self.assertEqual(ret, mock_tws())
        self.assertIn(str(expected_path), rts_call_args[0][0][0])

    @mock.patch("tethys_apps.base.workspace.TethysWorkspace")
    @mock.patch("tethys_apps.utilities.get_app_class")
    def test__get_user_workspace_none(self, mock_gac, mock_tws):
        mock_gac.return_value = self.app
        ret = _get_user_workspace(self.app_base, None)
        expected_path = Path("workspaces") / "user_workspaces" / "anonymous_user"
        rts_call_args = mock_tws.call_args_list
        self.assertEqual(ret, mock_tws())
        self.assertIn(str(expected_path), rts_call_args[0][0][0])

    def test__get_user_workspace_error(self):
        with self.assertRaises(ValueError) as context:
            _get_user_workspace(self.app_base, "not_user_or_request")

        self.assertEqual(
            str(context.exception),
            "Invalid type for argument 'user': must be either an User or HttpRequest object.",
        )

    @mock.patch("tethys_apps.utilities.get_app_model")
    def test__get_user_workspace_old_not_authenticated(self, mock_gam):
        request = HttpRequest()
        request.user = mock.MagicMock()
        request.user.is_anonymous = True
        mock_gam.return_value = self.app
        with self.assertRaises(PermissionDenied) as err:
            _get_user_workspace_old(self.app_base, request)

        self.assertEqual(str(err.exception), "User is not authenticated.")

    @mock.patch("tethys_apps.base.workspace.passes_quota", return_value=True)
    @mock.patch("tethys_apps.base.workspace._get_user_workspace")
    @mock.patch("tethys_apps.utilities.get_app_model")
    def test_get_user_workspace_aor_app_instance(self, mock_gam, mock_guw, mock_pq):
        mock_workspace = mock.MagicMock()
        mock_guw.return_value = mock_workspace
        mock_gam.return_value = self.app
        ret = _get_user_workspace_old(self.app_base, self.user)
        self.assertEqual(ret, mock_workspace)
        mock_pq.assert_called_with(self.user, "user_workspace_quota")
        mock_guw.assert_called_with(self.app, self.user)

    @mock.patch("tethys_apps.base.workspace.passes_quota", return_value=True)
    @mock.patch("tethys_apps.base.workspace._get_user_workspace")
    @mock.patch("tethys_apps.utilities.get_app_model")
    def test_get_user_workspace_aor_app_class(self, mock_gam, mock_guw, mock_pq):
        mock_workspace = mock.MagicMock()
        mock_guw.return_value = mock_workspace
        mock_gam.return_value = self.app
        ret = _get_user_workspace_old(TethysAppChild, self.user)
        self.assertEqual(ret, mock_workspace)
        mock_pq.assert_called_with(self.user, "user_workspace_quota")
        mock_guw.assert_called_with(self.app, self.user)

    @mock.patch("tethys_apps.utilities.get_app_model")
    @mock.patch("tethys_apps.base.workspace.passes_quota", return_value=True)
    @mock.patch("tethys_apps.base.workspace._get_user_workspace")
    def test_get_user_workspace_aor_request(self, mock_guw, mock_pq, mock_gam):
        request = HttpRequest()
        request.user = self.user
        mock_workspace = mock.MagicMock()
        mock_guw.return_value = mock_workspace
        mock_app = mock.MagicMock()
        mock_gam.return_value = mock_app
        ret = _get_user_workspace_old(request, self.user)
        self.assertEqual(ret, mock_workspace)
        mock_gam.assert_called_with(request)
        mock_pq.assert_called_with(self.user, "user_workspace_quota")
        mock_guw.assert_called_with(mock_app, self.user)

    def test_get_user_workspace_aor_error(self):
        with self.assertRaises(ValueError) as context:
            _get_user_workspace_old("not_app_or_request", self.user)

        self.assertEqual(
            str(context.exception),
            'Argument "app_or_request" must be of type HttpRequest, TethysAppBase, or TethysApp: "<class \'str\'>" given.',
        )

    @mock.patch("tethys_apps.base.workspace.passes_quota", return_value=True)
    @mock.patch("tethys_apps.base.workspace._get_user_workspace")
    def test_get_user_workspace_uor_user(self, mock_guw, mock_pq):
        mock_workspace = mock.MagicMock()
        mock_guw.return_value = mock_workspace
        ret = _get_user_workspace_old(self.app, self.user)
        self.assertEqual(ret, mock_workspace)
        mock_pq.assert_called_with(self.user, "user_workspace_quota")
        mock_guw.assert_called_with(self.app, self.user)

    @mock.patch("tethys_apps.base.workspace.passes_quota", return_value=True)
    @mock.patch("tethys_apps.base.workspace._get_user_workspace")
    @mock.patch("tethys_apps.utilities.get_app_model")
    def test_get_user_workspace_uor_request(self, mock_gam, mock_guw, mock_pq):
        request = HttpRequest()
        request.user = self.user
        mock_workspace = mock.MagicMock()
        mock_guw.return_value = mock_workspace
        mock_gam.return_value = self.app
        ret = _get_user_workspace_old(self.app_base, request)
        self.assertEqual(ret, mock_workspace)
        mock_pq.assert_called_with(self.user, "user_workspace_quota")
        mock_guw.assert_called_with(self.app, self.user)

    @mock.patch("tethys_apps.utilities.get_app_model")
    def test_get_user_workspace_uor_error(self, mock_gam):
        mock_gam.return_value = self.app
        with self.assertRaises(ValueError) as context:
            _get_user_workspace_old(self.app_base, "not_user_or_request")

        self.assertEqual(
            str(context.exception),
            'Argument "user_or_request" must be of type HttpRequest or User: "<class \'str\'>" given.',
        )

    @mock.patch("tethys_apps.base.workspace._get_user_workspace_old")
    def test_user_workspace_decorator_user(self, mock_guw):
        request = HttpRequest()
        request.user = self.user
        mock_workspace = mock.MagicMock()
        mock_guw.return_value = mock_workspace
        ret = user_dec_controller(request)
        self.assertEqual(ret, mock_workspace)
        mock_guw.assert_called_with(request, self.user)

    def test_user_workspace_decorator_HttpRequest_not_given(self):
        not_a_request = mock.MagicMock()
        with self.assertRaises(ValueError) as context:
            user_dec_controller(not_a_request)

        self.assertEqual(
            str(context.exception),
            "No request given. The user_workspace decorator only works on controllers.",
        )

    @mock.patch("tethys_apps.base.workspace.TethysWorkspace")
    @mock.patch("tethys_apps.utilities.get_app_class")
    def test__get_app_workspace(self, mock_ac, mock_tws):
        mock_ac.return_value = self.app_base.__class__
        ret = _get_app_workspace(self.app_base)
        self.assertEqual(ret, mock_tws(self.app_base))
        expected_workspace_path = Path("workspaces") / "app_workspace"
        rts_call_args = mock_tws.call_args_list
        self.assertIn(str(expected_workspace_path), rts_call_args[0][0][0])

    @mock.patch("tethys_apps.base.workspace.passes_quota", return_value=True)
    @mock.patch("tethys_apps.utilities.get_active_app")
    @mock.patch("tethys_apps.utilities.get_app_model")
    @mock.patch("tethys_apps.base.workspace._get_app_workspace")
    def test_get_app_workspace_app_instance(
        self, mock_gaw, mock_gam, mock_gaa, mock_pq
    ):
        mock_workspace = mock.MagicMock()
        mock_app = mock.MagicMock()
        mock_gaw.return_value = mock_workspace
        mock_gam.return_value = mock_app
        ret = _get_app_workspace_old(self.app_base)
        self.assertEqual(ret, mock_workspace)
        mock_gaa.assert_not_called()
        mock_pq.assert_called_with(mock_app, "tethysapp_workspace_quota")
        mock_gaw.assert_called_with(mock_app)

    @mock.patch("tethys_apps.base.workspace.passes_quota", return_value=True)
    @mock.patch("tethys_apps.utilities.get_active_app")
    @mock.patch("tethys_apps.utilities.get_app_model")
    @mock.patch("tethys_apps.base.workspace._get_app_workspace")
    def test_get_app_workspace_app_class(self, mock_gaw, mock_gam, mock_gaa, mock_pq):
        mock_workspace = mock.MagicMock()
        mock_app = mock.MagicMock()
        mock_gam.return_value = mock_app
        mock_gaw.return_value = mock_workspace
        ret = _get_app_workspace_old(TethysAppChild)
        self.assertEqual(ret, mock_workspace)
        mock_gaa.assert_not_called()
        mock_pq.assert_called_with(mock_app, "tethysapp_workspace_quota")
        mock_gaw.assert_called_with(mock_app)

    @mock.patch("tethys_apps.base.workspace.passes_quota", return_value=True)
    @mock.patch("tethys_apps.utilities.get_app_model")
    @mock.patch("tethys_apps.base.workspace._get_app_workspace")
    def test_get_app_workspace_http(self, mock_gaw, mock_gam, mock_pq):
        request = HttpRequest()
        mock_workspace = mock.MagicMock()
        mock_gaw.return_value = mock_workspace
        mock_app = mock.MagicMock()
        mock_gam.return_value = mock_app
        ret = _get_app_workspace_old(request)
        self.assertEqual(ret, mock_workspace)
        mock_gam.assert_called_with(request)
        mock_pq.assert_called_with(mock_app, "tethysapp_workspace_quota")
        mock_gaw.assert_called_with(mock_app)

    def test_get_app_workspace_error(self):
        with self.assertRaises(ValueError) as context:
            _get_app_workspace_old("not_app_or_request")

        self.assertEqual(
            str(context.exception),
            'Argument "app_or_request" must be of type HttpRequest, TethysAppBase, or TethysApp: "<class \'str\'>" given.',
        )

    @mock.patch("tethys_apps.utilities.get_active_app")
    @mock.patch("tethys_apps.base.workspace._get_app_workspace_old")
    def test_app_workspace_decorator(self, mock_gaw, mock_gaa):
        request = HttpRequest()
        mock_workspace = mock.MagicMock()
        mock_gaw.return_value = mock_workspace
        mock_app = mock.MagicMock()
        mock_gaa.return_value = mock_app
        ret = app_dec_controller(request)
        self.assertEqual(ret, mock_workspace)
        mock_gaw.assert_called_with(request)

    def test_app_workspace_decorator_HttpRequest_not_given(self):
        not_a_request = mock.MagicMock()

        with self.assertRaises(ValueError) as context:
            app_dec_controller(not_a_request)

        self.assertEqual(
            str(context.exception),
            "No request given. The app_workspace decorator only works on controllers.",
        )
