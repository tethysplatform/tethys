from tethys_apps.models import ProxyApp

from unittest import mock
from tethys_cli.proxyapps_commands import (
    add_proxyapp,
    update_proxyapp,
    list_proxyapps,
    get_engine,
)

from django.test import TestCase
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

    @mock.patch("tethys_cli.proxyapps_commands.write_error")
    @mock.patch("tethys_cli.proxyapps_commands.read_settings")
    def test_get_engine_no_db_settings_error(self, mock_settings, mock_write_error):
        mock_settings.return_value = {}
        get_engine()
        mock_write_error.assert_called_with(
            "No database settings defined in the portal_config.yml file"
        )

    @mock.patch("tethys_cli.proxyapps_commands.write_error")
    @mock.patch("tethys_cli.proxyapps_commands.read_settings")
    def test_get_engine_no_default_db_settings_error(
        self, mock_settings, mock_write_error
    ):
        mock_settings.return_value = {"DATABASES": {}}
        get_engine()
        mock_write_error.assert_called_with(
            "No default database defined in the portal_config.yml file"
        )

    @mock.patch("tethys_cli.proxyapps_commands.write_error")
    @mock.patch("tethys_cli.proxyapps_commands.read_settings")
    def test_get_engine_connection_error(self, mock_settings, mock_write_error):
        # database settings is empty here, so it will cause an error
        mock_settings.return_value = {
            "DATABASES": {"default": {"ENGINE": "django.db.backends.postgresql"}}
        }
        get_engine()
        mock_write_error.assert_called_with("Error when connecting to the database")

    @mock.patch("tethys_cli.proxyapps_commands.create_engine")
    @mock.patch("tethys_cli.proxyapps_commands.read_settings")
    def test_get_engine_sqlite(self, mock_settings, mock_create_engine):
        mock_settings.return_value = {
            "DATABASES": {
                "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "db_name"}
            }
        }
        mock_engine = mock_create_engine.return_value
        mock_engine.connect.return_value = "Mocked SQLite Engine"

        # Call the function that uses create_engine
        engine = get_engine()

        # Assertions
        mock_create_engine.assert_called_once()
        mock_create_engine.assert_called_with("sqlite:///db_name", pool_pre_ping=True)

    @mock.patch("tethys_cli.proxyapps_commands.write_info")
    @mock.patch("tethys_cli.proxyapps_commands.print")
    def test_list_proxy_apps(self, mock_print, mock_write_info):
        list_proxyapps()
        rts_call_args = mock_print.call_args_list
        check_list = []

        for i in range(len(rts_call_args)):
            check_list.append(rts_call_args[i][0][0])

        mock_write_info.assert_called_with("Proxy Apps:")
        self.assertIn("  My_Proxy_App_for_Testing", check_list)

    @mock.patch("tethys_cli.proxyapps_commands.write_error")
    def test_update_proxy_apps_no_app_name(self, mock_write_error):
        mock_args = []
        update_proxyapp(mock_args)
        mock_write_error.assert_called_with("proxy_app_name cannot be empty")

    @mock.patch("tethys_cli.proxyapps_commands.write_error")
    def test_update_proxy_apps_no_app_key_name(self, mock_write_error):
        mock_args = [self.app_name]
        update_proxyapp(mock_args)
        mock_write_error.assert_called_with("proxy_app_key cannot be empty")

    @mock.patch("tethys_cli.proxyapps_commands.write_error")
    def test_update_proxy_apps_no_app_value_name(self, mock_write_error):
        mock_args = [self.app_name, "logo_url"]
        update_proxyapp(mock_args)
        mock_write_error.assert_called_with("proxy_app_value cannot be empty")

    @mock.patch("tethys_cli.proxyapps_commands.write_error")
    def test_update_proxy_apps_no_app(self, mock_write_error):
        mock_args = ["My_Proxy_App_for_Testing2", "logo_url", "https://fake.com"]
        update_proxyapp(mock_args)
        mock_write_error.assert_called_with(
            f"Proxy app My_Proxy_App_for_Testing2 does not exits"
        )

    @mock.patch("tethys_cli.proxyapps_commands.write_error")
    def test_update_proxy_apps_no_correct_key(self, mock_write_error):
        mock_args = [
            self.app_name,
            "non_existing_key",
            "https://fake.com",
        ]
        update_proxyapp(mock_args)
        mock_write_error.assert_called_with(
            f"Attribute non_existing_key does not exists in Proxy app {self.app_name}"
        )

    @mock.patch("tethys_cli.proxyapps_commands.write_success")
    def test_update_proxy_apps(self, mock_write_success):
        mock_args = [
            self.app_name,
            "logo_url",
            "https://fake.com",
        ]
        update_proxyapp(mock_args)
        mock_write_success.assert_called_with(f"Proxy app {self.app_name} was updated")

    @mock.patch("tethys_cli.proxyapps_commands.write_error")
    def test_add_proxy_apps_no_app_name(self, mock_write_error):
        mock_args = []
        add_proxyapp(mock_args)
        mock_write_error.assert_called_with(f"proxy_app_name argument cannot be empty")

    @mock.patch("tethys_cli.proxyapps_commands.write_error")
    def test_add_proxy_apps_no_endpoint(self, mock_write_error):
        mock_args = ["new_proxy_app"]
        add_proxyapp(mock_args)
        mock_write_error.assert_called_with(
            f"proxy_app_endpoint argument cannot be empty"
        )

    @mock.patch("tethys_cli.proxyapps_commands.write_error")
    def test_add_proxy_apps_with_existing_proxy_app(self, mock_write_error):
        mock_args = ["My_Proxy_App_for_Testing", "http://foo.example.com/my-proxy-app"]
        add_proxyapp(mock_args)
        mock_write_error.assert_called_with(
            f"There is already a proxy app with that name: {self.app_name}"
        )

    @mock.patch("tethys_cli.proxyapps_commands.write_success")
    def test_add_proxyapp_only_two_arguments(self, mock_write_success):
        app_name_mock = "My_Proxy_App_for_Testing_2"
        endpoint_mock = "http://foo.example.com/my-proxy-app"
        mock_args = [app_name_mock, endpoint_mock]
        add_proxyapp(mock_args)
        mock_write_success.assert_called_with(f"Proxy app {app_name_mock} added")
        new_proxy_app = ProxyApp.objects.get(name=app_name_mock)
        new_proxy_app.delete()
