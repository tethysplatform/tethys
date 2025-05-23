import sys

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import unittest
from unittest import mock

from argparse import ArgumentParser
from tethys_apps.management.commands import tethys_app_uninstall
from tethys_apps.models import TethysApp, TethysExtension


class ManagementCommandsTethysAppUninstallTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_tethys_app_uninstall_add_arguments(self):
        parser = ArgumentParser("foo_parser")
        cmd = tethys_app_uninstall.Command()
        cmd.add_arguments(parser)
        self.assertIn("foo_parser", parser.format_usage())
        self.assertIn("app_or_extension", parser.format_usage())
        self.assertIn("[-e]", parser.format_usage())
        self.assertIn("--extension", parser.format_help())

    @mock.patch("tethys_apps.management.commands.tethys_app_uninstall.exit")
    @mock.patch("sys.stdout", new_callable=StringIO)
    @mock.patch("tethys_apps.management.commands.tethys_app_uninstall.input")
    @mock.patch(
        "tethys_apps.management.commands.tethys_app_uninstall.get_installed_tethys_items"
    )
    def test_tethys_app_uninstall_handle_apps_cancel(
        self, mock_installed_items, mock_input, mock_stdout, mock_exit
    ):
        mock_installed_items.return_value = ["foo_app"]
        mock_input.side_effect = ["foo", "no"]
        mock_exit.side_effect = SystemExit

        cmd = tethys_app_uninstall.Command()
        self.assertRaises(
            SystemExit,
            cmd.handle,
            app_or_extension=["tethysapp.foo_app"],
            is_extension=False,
            is_forced=False,
        )

        mock_installed_items.assert_called_with(apps=True, extensions=False)
        self.assertIn("Uninstall cancelled by user.", mock_stdout.getvalue())

    @mock.patch("tethys_apps.management.commands.tethys_app_uninstall.ContentType")
    @mock.patch("site.getsitepackages", return_value="foo")
    @mock.patch("tethys_apps.management.commands.tethys_app_uninstall.Group.objects")
    @mock.patch(
        "tethys_apps.management.commands.tethys_app_uninstall.Permission.objects"
    )
    @mock.patch("tethys_apps.management.commands.tethys_app_uninstall.Path.unlink")
    @mock.patch("tethys_apps.management.commands.tethys_app_uninstall.subprocess.Popen")
    @mock.patch("warnings.warn")
    @mock.patch("sys.stdout", new_callable=StringIO)
    @mock.patch("tethys_apps.management.commands.tethys_app_uninstall.input")
    @mock.patch(
        "tethys_apps.management.commands.tethys_app_uninstall.get_installed_tethys_items"
    )
    @mock.patch("tethys_apps.models.TethysExtension")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_tethys_app_uninstall_handle_apps_delete_rmtree_Popen_remove_exceptions(
        self,
        mock_app,
        mock_extension,
        mock_installed_items,
        mock_input,
        mock_stdout,
        mock_warnings,
        mock_popen,
        mock_unlink,
        mock_permissions,
        mock_groups,
        _,
        __,
    ):
        mock_app.objects.get.return_value = mock.MagicMock()
        mock_app.objects.get().delete.return_value = True
        mock_extension.objects.get.return_value = mock.MagicMock()
        mock_extension.objects.get().delete.return_value = True
        mock_installed_items.return_value = {"foo_app": "/foo/foo_app"}
        mock_input.side_effect = ["yes"]
        mock_popen.side_effect = KeyboardInterrupt
        mock_unlink.side_effect = [True, Exception]
        mock_permission = mock.MagicMock(delete=mock.MagicMock())
        mock_permissions.filter().filter().all.return_value = [mock_permission]
        mock_group = mock.MagicMock(delete=mock.MagicMock())
        mock_groups.filter().all.return_value = [mock_group]

        cmd = tethys_app_uninstall.Command()
        cmd.handle(
            app_or_extension=["tethysapp.foo_app"], is_extension=False, is_forced=False
        )

        mock_installed_items.assert_called_with(apps=True, extensions=False)
        mock_permission.delete.assert_called_once()
        mock_group.delete.assert_called_once()
        self.assertIn("successfully uninstalled", mock_stdout.getvalue())
        mock_warnings.assert_not_called()  # Don't do the TethysModel.DoesNotExist exception this test
        mock_app.objects.get.assert_called()
        mock_app.objects.get().delete.assert_called_once()
        mock_extension.objects.get.assert_called()
        mock_extension.objects.get().delete.assert_not_called()
        mock_popen.assert_called_once_with(
            [sys.executable, "-m", "pip", "uninstall", "-y", "tethysapp-foo_app"],
            stderr=-2,
            stdout=-1,
        )

    @mock.patch("warnings.warn")
    @mock.patch("tethys_apps.management.commands.tethys_app_uninstall.exit")
    @mock.patch("sys.stdout", new_callable=StringIO)
    @mock.patch(
        "tethys_apps.management.commands.tethys_app_uninstall.get_installed_tethys_items"
    )
    @mock.patch("tethys_apps.models.TethysExtension")
    @mock.patch("tethys_apps.models.TethysApp")
    def test_tethys_app_uninstall_handle_module_and_db_not_found(
        self,
        mock_app,
        mock_extension,
        mock_installed_items,
        mock_stdout,
        mock_exit,
        mock_warn,
    ):
        # Raise DoesNotExist on db query
        mock_app.objects.get.return_value = mock.MagicMock()
        mock_app.DoesNotExist = TethysApp.DoesNotExist
        mock_extension.DoesNotExist = TethysExtension.DoesNotExist
        mock_app.objects.get.side_effect = TethysApp.DoesNotExist
        mock_extension.objects.get.return_value = mock.MagicMock()
        mock_extension.objects.get.side_effect = TethysExtension.DoesNotExist

        # No installed apps or extensions returned
        mock_installed_items.return_value = {}
        mock_exit.side_effect = SystemExit

        cmd = tethys_app_uninstall.Command()
        self.assertRaises(
            SystemExit,
            cmd.handle,
            app_or_extension=["tethysext.foo_extension"],
            is_extension=True,
            is_forced=False,
        )

        mock_installed_items.assert_called_with(apps=False, extensions=True)
        mock_warn.assert_called_once()
