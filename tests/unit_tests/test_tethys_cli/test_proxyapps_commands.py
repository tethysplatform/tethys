import pytest
from tethys_apps.models import ProxyApp

from unittest import mock
from tethys_cli.proxyapps_commands import (
    add_proxyapp,
    update_proxyapp,
    list_proxyapps,
)

import unittest


class TestProxyAppsCommand(unittest.TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.app_name = "My_Proxy_App_for_Testing"
        self.endpoint = "http://foo.example.com/my-proxy-app"
        self.back_url = "http://bar.example.com/apps/"
        self.logo = "http://foo.example.com/my-proxy-app/logo.png"
        self.description = "This is an app that is not here."
        self.tags = '"Water","Earth","Fire","Air"'
        self.open_in_new_tab = True
        self.order = 0
        self.display_external_icon = False
        self.enabled = True
        self.show_in_apps_library = True
        self.maxDiff = None
        self.proxy_app = ProxyApp(
            name=self.app_name,
            endpoint=self.endpoint,
            icon=self.logo,
            back_url=self.back_url,
            description=self.description,
            tags=self.tags,
            open_in_new_tab=self.open_in_new_tab,
            order=self.order,
            display_external_icon=self.display_external_icon,
            enabled=self.enabled,
            show_in_apps_library=self.show_in_apps_library,
        )
        self.proxy_app.save()

    @pytest.mark.django_db
    def tearDown(self):
        self.proxy_app.delete()

    @mock.patch("tethys_cli.proxyapps_commands.write_info")
    @mock.patch("tethys_cli.proxyapps_commands.print")
    @pytest.mark.django_db
    def test_list_proxy_apps(self, mock_print, mock_write_info):
        mock_args = mock.Mock()
        mock_args.verbose = False
        list_proxyapps(mock_args)
        rts_call_args = mock_print.call_args_list
        check_list = []

        for i in range(len(rts_call_args)):
            check_list.append(rts_call_args[i][0][0])

        mock_write_info.assert_called_with("Proxy Apps:")
        self.assertIn(f"  {self.app_name}: {self.endpoint}", check_list)

    @mock.patch("tethys_cli.proxyapps_commands.write_info")
    @mock.patch("tethys_cli.proxyapps_commands.print")
    @pytest.mark.django_db
    def test_list_proxy_apps_verbose(self, mock_print, mock_write_info):
        mock_args = mock.Mock()
        mock_args.verbose = True
        list_proxyapps(mock_args)
        rts_call_args = mock_print.call_args_list

        expected_output = (
            f"  {self.app_name}:\n"
            f"    endpoint: {self.endpoint}\n"
            f"    description: {self.description}\n"
            f"    icon: {self.logo}\n"
            f"    tags: {self.tags}\n"
            f"    enabled: {self.enabled}\n"
            f"    show_in_apps_library: {self.show_in_apps_library}\n"
            f"    back_url: {self.back_url}\n"
            f"    open_in_new_tab: {self.open_in_new_tab}\n"
            f"    display_external_icon: {self.display_external_icon}\n"
            f"    order: {self.order}"
        )

        mock_write_info.assert_called_with("Proxy Apps:")
        self.assertEqual(rts_call_args[0][0][0], expected_output)

    @mock.patch("tethys_cli.proxyapps_commands.write_error")
    @mock.patch("tethys_cli.proxyapps_commands.exit", side_effect=SystemExit)
    @pytest.mark.django_db
    def test_update_proxy_apps_no_app(self, mock_exit, mock_write_error):
        mock_args = mock.Mock()
        mock_args.name = "non_existing_proxy_app"
        mock_args.set_kwargs = [["non_existing_key", "https://fake.com"]]

        self.assertRaises(
            SystemExit,
            update_proxyapp,
            mock_args,
        )

        mock_write_error.assert_called_with(
            "Proxy app named 'non_existing_proxy_app' does not exist"
        )
        mock_exit.assert_called_with(1)

    @mock.patch("tethys_cli.proxyapps_commands.write_success")
    @mock.patch("tethys_cli.proxyapps_commands.write_warning")
    @mock.patch("tethys_cli.proxyapps_commands.exit", side_effect=SystemExit)
    @pytest.mark.django_db
    def test_update_proxy_apps_no_correct_key(
        self, mock_exit, mock_write_warning, mock_write_success
    ):
        mock_args = mock.Mock()
        mock_args.name = self.app_name
        mock_args.set_kwargs = [["non_existing_key", "https://fake.com"]]
        mock_args.proxy_app_key = "non_existing_key"
        mock_args.proxy_app_key_value = "https://fake.com"

        self.assertRaises(
            SystemExit,
            update_proxyapp,
            mock_args,
        )

        mock_write_warning.assert_called_with(
            "Attribute non_existing_key does not exist"
        )
        mock_write_success.assert_called_with(
            f"Proxy app '{self.app_name}' was updated successfully"
        )
        mock_exit.assert_called_with(0)

    @mock.patch("tethys_cli.proxyapps_commands.write_info")
    @mock.patch("tethys_cli.proxyapps_commands.write_success")
    @mock.patch("tethys_cli.proxyapps_commands.exit", side_effect=SystemExit)
    @pytest.mark.django_db
    def test_update_proxy_apps(self, mock_exit, mock_write_success, mock_write_info):
        mock_args = mock.Mock()
        mock_args.name = self.app_name
        mock_args.set_kwargs = [["icon", "https://fake.com"]]

        self.assertRaises(
            SystemExit,
            update_proxyapp,
            mock_args,
        )

        try:
            proxy_app_updated = ProxyApp.objects.get(
                name=self.app_name, icon="https://fake.com"
            )
            self.assertEqual(proxy_app_updated.icon, "https://fake.com")
        except ProxyApp.DoesNotExist:
            self.fail(
                f"ProxyApp.DoesNotExist was raised, ProxyApp with name {self.app_name} was never updated"
            )

        mock_write_info.assert_called_with(
            "Attribute icon was updated successfully with https://fake.com"
        )
        mock_write_success.assert_called_with(
            f"Proxy app '{self.app_name}' was updated successfully"
        )
        mock_exit.assert_called_with(0)

    @mock.patch("tethys_cli.proxyapps_commands.write_error")
    @mock.patch("tethys_cli.proxyapps_commands.exit", side_effect=SystemExit)
    @pytest.mark.django_db
    def test_add_proxy_apps_with_existing_proxy_app(self, mock_exit, mock_write_error):
        mock_args = mock.Mock()
        mock_args.name = self.app_name
        mock_args.endpoint = "http://foo.example.com/my-proxy-app"

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
    @pytest.mark.django_db
    def test_add_proxyapp_integrity_error(self, mock_exit, mock_write_error):
        app_name_mock = "My_Proxy_App_for_Testing_2"
        mock_args = mock.Mock()
        mock_args.name = app_name_mock
        mock_args.endpoint = "http://foo.example.com/my-proxy-app"
        mock_args.description = None
        mock_args.icon = None
        mock_args.tags = None
        mock_args.enabled = None
        mock_args.show_in_apps_library = None
        mock_args.back_url = None
        mock_args.open_new_tab = None
        mock_args.display_external_icon = None
        mock_args.order = None

        self.assertRaises(
            SystemExit,
            add_proxyapp,
            mock_args,
        )
        mock_write_error.assert_called_with(
            f'Not possible to add the proxy app "{app_name_mock}" because one or more values of the wrong type were provided. Run "tethys proxyapp add --help" to see examples for each argument.'
        )
        mock_exit.assert_called_with(1)

    @mock.patch("tethys_cli.proxyapps_commands.write_success")
    @mock.patch("tethys_cli.proxyapps_commands.exit", side_effect=SystemExit)
    @pytest.mark.django_db
    def test_add_proxyapp_success(self, mock_exit, mock_write_success):
        app_name_mock = "My_Proxy_App_for_Testing_2"
        mock_args = mock.Mock()
        mock_args.name = app_name_mock
        mock_args.endpoint = "http://foo.example.com/my-proxy-app"
        mock_args.description = ""
        mock_args.icon = ""
        mock_args.tags = ""
        mock_args.enabled = True
        mock_args.show_in_apps_library = True
        mock_args.back_url = ""
        mock_args.open_new_tab = True
        mock_args.display_external_icon = False
        mock_args.order = 0

        self.assertRaises(
            SystemExit,
            add_proxyapp,
            mock_args,
        )

        try:
            proxy_app_added = ProxyApp.objects.get(name=app_name_mock)
            self.assertEqual(proxy_app_added.name, app_name_mock)
            proxy_app_added.delete()

        except ProxyApp.DoesNotExist:
            self.fail(
                f"ProxyApp.DoesNotExist was raised, ProxyApp with name {app_name_mock} was never added"
            )

        mock_write_success.assert_called_with(f"Proxy app {app_name_mock} added")
        mock_exit.assert_called_with(0)

    @mock.patch("tethys_cli.proxyapps_commands.write_success")
    @mock.patch("tethys_cli.proxyapps_commands.exit", side_effect=SystemExit)
    @pytest.mark.django_db
    def test_add_proxyapp_non_default_values_success(
        self, mock_exit, mock_write_success
    ):
        app_name_mock = "My_Proxy_App_for_Testing_non_default"
        app_endpoint_mock = "http://foo.example.com/my-proxy-app"
        app_description_mock = "Mock description for proxy app"
        app_icon_mock = "http://logo-url.foo.example.com/my-proxy-app"
        app_tags_mock = '"tag one", "tag two", "tag three"'
        app_enabled_mock = False
        app_show_in_apps_library_mock = False
        app_back_url_mock = "http://back-url.foo.example.com/my-proxy-app"
        app_open_new_tab_mock = False
        app_display_external_icon_mock = True
        app_order_mock = 1

        mock_args = mock.Mock()
        mock_args.name = app_name_mock
        mock_args.endpoint = app_endpoint_mock
        mock_args.description = app_description_mock
        mock_args.icon = app_icon_mock
        mock_args.tags = app_tags_mock
        mock_args.enabled = app_enabled_mock
        mock_args.show_in_apps_library = app_show_in_apps_library_mock
        mock_args.back_url = app_back_url_mock
        mock_args.open_new_tab = app_open_new_tab_mock
        mock_args.display_external_icon = app_display_external_icon_mock
        mock_args.order = app_order_mock

        self.assertRaises(
            SystemExit,
            add_proxyapp,
            mock_args,
        )
        try:
            proxy_app_added = ProxyApp.objects.get(
                name=app_name_mock,
                endpoint=app_endpoint_mock,
                description=app_description_mock,
                icon=app_icon_mock,
                tags=app_tags_mock,
                enabled=app_enabled_mock,
                show_in_apps_library=app_show_in_apps_library_mock,
                back_url=app_back_url_mock,
                open_in_new_tab=app_open_new_tab_mock,
                display_external_icon=app_display_external_icon_mock,
                order=app_order_mock,
            )
            self.assertEqual(proxy_app_added.name, app_name_mock)
            self.assertEqual(proxy_app_added.endpoint, app_endpoint_mock)
            self.assertEqual(proxy_app_added.description, app_description_mock)
            self.assertEqual(proxy_app_added.icon, app_icon_mock)
            self.assertEqual(proxy_app_added.tags, app_tags_mock)
            self.assertEqual(proxy_app_added.enabled, app_enabled_mock)
            self.assertEqual(
                proxy_app_added.show_in_apps_library, app_show_in_apps_library_mock
            )
            self.assertEqual(proxy_app_added.back_url, app_back_url_mock)
            self.assertEqual(proxy_app_added.open_in_new_tab, app_open_new_tab_mock)
            self.assertEqual(proxy_app_added.order, app_order_mock)
            self.assertEqual(
                proxy_app_added.display_external_icon, app_display_external_icon_mock
            )
            proxy_app_added.delete()

        except ProxyApp.DoesNotExist:
            self.fail(
                f"ProxyApp.DoesNotExist was raised, ProxyApp with name {app_name_mock} was never added"
            )

        mock_write_success.assert_called_with(f"Proxy app {app_name_mock} added")
        mock_exit.assert_called_with(0)

    @mock.patch("tethys_cli.proxyapps_commands.write_success")
    @mock.patch("tethys_cli.proxyapps_commands.exit", side_effect=SystemExit)
    @pytest.mark.django_db
    def test_add_proxyapp_one_tag_success(self, mock_exit, mock_write_success):
        app_name_mock = "My_Proxy_App_for_Testing_non_default"
        app_endpoint_mock = "http://foo.example.com/my-proxy-app"
        app_description_mock = "Mock description for proxy app"
        app_icon_mock = "http://logo-url.foo.example.com/my-proxy-app"
        app_tags_mock = "tag with space"
        app_enabled_mock = False
        app_show_in_apps_library_mock = False
        app_back_url_mock = "http://back-url.foo.example.com/my-proxy-app"
        app_open_new_tab_mock = False
        app_display_external_icon_mock = True
        app_order_mock = 1

        mock_args = mock.Mock()
        mock_args.name = app_name_mock
        mock_args.endpoint = app_endpoint_mock
        mock_args.description = app_description_mock
        mock_args.icon = app_icon_mock
        mock_args.tags = app_tags_mock
        mock_args.enabled = app_enabled_mock
        mock_args.show_in_apps_library = app_show_in_apps_library_mock
        mock_args.back_url = app_back_url_mock
        mock_args.open_new_tab = app_open_new_tab_mock
        mock_args.display_external_icon = app_display_external_icon_mock
        mock_args.order = app_order_mock

        self.assertRaises(
            SystemExit,
            add_proxyapp,
            mock_args,
        )
        try:
            proxy_app_added = ProxyApp.objects.get(
                name=app_name_mock,
                endpoint=app_endpoint_mock,
                description=app_description_mock,
                icon=app_icon_mock,
                tags=app_tags_mock,
                enabled=app_enabled_mock,
                show_in_apps_library=app_show_in_apps_library_mock,
                back_url=app_back_url_mock,
                open_in_new_tab=app_open_new_tab_mock,
                display_external_icon=app_display_external_icon_mock,
                order=app_order_mock,
            )
            self.assertEqual(proxy_app_added.name, app_name_mock)
            self.assertEqual(proxy_app_added.endpoint, app_endpoint_mock)
            self.assertEqual(proxy_app_added.description, app_description_mock)
            self.assertEqual(proxy_app_added.icon, app_icon_mock)
            self.assertEqual(proxy_app_added.tags, app_tags_mock)
            self.assertEqual(proxy_app_added.enabled, app_enabled_mock)
            self.assertEqual(
                proxy_app_added.show_in_apps_library, app_show_in_apps_library_mock
            )
            self.assertEqual(proxy_app_added.back_url, app_back_url_mock)
            self.assertEqual(proxy_app_added.open_in_new_tab, app_open_new_tab_mock)
            self.assertEqual(proxy_app_added.order, app_order_mock)
            self.assertEqual(
                proxy_app_added.display_external_icon, app_display_external_icon_mock
            )
            proxy_app_added.delete()

        except ProxyApp.DoesNotExist:
            self.fail(
                f"ProxyApp.DoesNotExist was raised, ProxyApp with name {app_name_mock} was never added"
            )

        mock_write_success.assert_called_with(f"Proxy app {app_name_mock} added")
        mock_exit.assert_called_with(0)
