from tethys_apps.models import ProxyApp

from unittest import mock
from tethys_cli.proxyapps_commands import (
    add_proxyapp,
    update_proxyapp,
    list_proxyapps,
)

import unittest


class TestProxyAppsCommand(unittest.TestCase):
    def setUp(self):
        self.app_name = "My_Proxy_App_for_Testing"
        self.endpoint = "http://foo.example.com/my-proxy-app"
        self.back_url = "http://bar.example.com/apps/"
        self.logo = "http://foo.example.com/my-proxy-app/logo.png"
        self.description = "This is an app that is not here."
        self.tags = '"Water","Earth","Fire","Air"'
        self.open_in_new_tab = True

        self.proxy_app = ProxyApp(
            name=self.app_name,
            endpoint=self.endpoint,
            logo_url=self.logo,
            back_url=self.back_url,
            description=self.description,
            tags=self.tags,
            open_in_new_tab=self.open_in_new_tab,
        )
        self.proxy_app.save()

    def tearDown(self):
        self.proxy_app.delete()

    @mock.patch("tethys_cli.proxyapps_commands.write_info")
    @mock.patch("tethys_cli.proxyapps_commands.print")
    def test_list_proxy_apps(self, mock_print, mock_write_info):
        mock_args = mock.Mock()
        list_proxyapps(mock_args)
        rts_call_args = mock_print.call_args_list
        check_list = []

        for i in range(len(rts_call_args)):
            check_list.append(rts_call_args[i][0][0])

        mock_write_info.assert_called_with("Proxy Apps:")
        self.assertIn("  My_Proxy_App_for_Testing", check_list)

    @mock.patch("tethys_cli.proxyapps_commands.write_error")
    @mock.patch("tethys_cli.proxyapps_commands.exit", side_effect=SystemExit)
    def test_update_proxy_apps_no_app(self, mock_exit, mock_write_error):
        mock_args = mock.Mock()
        mock_args.proxy_app_name = "non_existing_proxy_app"
        mock_args.proxy_app_key = "non_existing_key"
        mock_args.proxy_app_key_value = "https://fake.com"

        self.assertRaises(
            SystemExit,
            update_proxyapp,
            mock_args,
        )

        mock_write_error.assert_called_with(
            "Proxy app non_existing_proxy_app does not exits"
        )
        mock_exit.assert_called_with(1)

    @mock.patch("tethys_cli.proxyapps_commands.write_error")
    @mock.patch("tethys_cli.proxyapps_commands.exit", side_effect=SystemExit)
    def test_update_proxy_apps_no_correct_key(self, mock_exit, mock_write_error):
        mock_args = mock.Mock()
        mock_args.proxy_app_name = self.app_name
        mock_args.proxy_app_key = "non_existing_key"
        mock_args.proxy_app_key_value = "https://fake.com"

        self.assertRaises(
            SystemExit,
            update_proxyapp,
            mock_args,
        )

        mock_write_error.assert_called_with(
            f"Attribute non_existing_key does not exists in Proxy app {self.app_name}"
        )
        mock_exit.assert_called_with(1)

    @mock.patch("tethys_cli.proxyapps_commands.write_success")
    @mock.patch("tethys_cli.proxyapps_commands.exit", side_effect=SystemExit)
    def test_update_proxy_apps(self, mock_exit, mock_write_success):
        mock_args = mock.Mock()
        mock_args.proxy_app_name = self.app_name
        mock_args.proxy_app_key = "logo_url"
        mock_args.proxy_app_key_value = "https://fake.com"
        self.assertRaises(
            SystemExit,
            update_proxyapp,
            mock_args,
        )
        mock_write_success.assert_called_with(f"Proxy app {self.app_name} was updated")
        mock_exit.assert_called_with(0)

    @mock.patch("tethys_cli.proxyapps_commands.write_error")
    @mock.patch("tethys_cli.proxyapps_commands.exit", side_effect=SystemExit)
    def test_add_proxy_apps_with_existing_proxy_app(self, mock_exit, mock_write_error):
        mock_args = mock.Mock()
        mock_args.proxy_app_name = self.app_name
        mock_args.proxy_app_endpoint = "http://foo.example.com/my-proxy-app"

        self.assertRaises(
            SystemExit,
            add_proxyapp,
            mock_args,
        )
        mock_write_error.assert_called_with(
            f"There is already a proxy app with that name: {self.app_name}"
        )
        mock_exit.assert_called_with(1)

    @mock.patch("tethys_cli.proxyapps_commands.write_error")
    @mock.patch("tethys_cli.proxyapps_commands.exit", side_effect=SystemExit)
    def test_add_proxyapp_integrity_error(self, mock_exit, mock_write_error):
        app_name_mock = "My_Proxy_App_for_Testing_2"
        mock_args = mock.Mock()
        mock_args.proxy_app_name = app_name_mock
        mock_args.proxy_app_endpoint = "http://foo.example.com/my-proxy-app"
        mock_args.proxy_app_description = None
        mock_args.proxy_app_logo_url = None
        mock_args.proxy_app_tags = None
        mock_args.proxy_app_enabled = None
        mock_args.proxy_app_show_in_apps_library = None
        mock_args.proxy_app_back_url = None
        mock_args.proxy_app_open_new_tab = None
        mock_args.proxy_app_display_external_icon = None
        mock_args.proxy_app_order = None

        self.assertRaises(
            SystemExit,
            add_proxyapp,
            mock_args,
        )
        mock_write_error.assert_called_with(
            f"Not possible to add the proxy app: {app_name_mock}"
        )
        mock_exit.assert_called_with(1)

    @mock.patch("tethys_cli.proxyapps_commands.write_success")
    @mock.patch("tethys_cli.proxyapps_commands.exit", side_effect=SystemExit)
    def test_add_proxyapp_success(self, mock_exit, mock_write_success):
        app_name_mock = "My_Proxy_App_for_Testing_2"
        mock_args = mock.Mock()
        mock_args.proxy_app_name = app_name_mock
        mock_args.proxy_app_endpoint = "http://foo.example.com/my-proxy-app"
        mock_args.proxy_app_description = ""
        mock_args.proxy_app_logo_url = ""
        mock_args.proxy_app_tags = ""
        mock_args.proxy_app_enabled = True
        mock_args.proxy_app_show_in_apps_library = True
        mock_args.proxy_app_back_url = ""
        mock_args.proxy_app_open_new_tab = True
        mock_args.proxy_app_display_external_icon = False
        mock_args.proxy_app_order = 0

        self.assertRaises(
            SystemExit,
            add_proxyapp,
            mock_args,
        )
        new_proxy_app = ProxyApp.objects.get(name=app_name_mock)
        new_proxy_app.delete()
        mock_write_success.assert_called_with(f"Proxy app {app_name_mock} added")
        mock_exit.assert_called_with(0)
