import unittest
import os
from unittest import mock
from django.core.exceptions import ObjectDoesNotExist

from tethys_cli.site_commands import (
    gen_site_content,
    update_site_settings_content,
    uncodify,
    update_site_settings_if_standalone_mode,
)


class CLISiteCommandsTest(unittest.TestCase):
    def setUp(self):
        self.src_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.root_app_path = os.path.join(self.src_dir, "apps", "tethysapp-test_app")

    def tearDown(self):
        pass

    @mock.patch("tethys_cli.site_commands.update_site_settings_content")
    @mock.patch("tethys_cli.site_commands.setup_django")
    def test_gen_site_content(self, mock_setup_django, mock_update_settings):
        mock_args = mock.MagicMock(
            brand_text="New Title", restore_defaults=False, from_file=False
        )

        gen_site_content(mock_args)

        mock_setup_django.assert_called()
        mock_update_settings.assert_called_once_with(vars(mock_args))

    @mock.patch("tethys_cli.site_commands.update_site_settings_content")
    @mock.patch("tethys_config.init.setting_defaults")
    @mock.patch("tethys_config.models.SettingsCategory.objects.get")
    @mock.patch("tethys_config.models.Setting.objects.all")
    @mock.patch("tethys_cli.site_commands.setup_django")
    def test_gen_site_content_restore_defaults(
        self,
        mock_setup_django,
        mock_all,
        mock_get,
        mock_setting_defaults,
        mock_update_settings,
    ):
        mock_args = mock.MagicMock(from_file=False, restore_defaults=True)

        gen_site_content(mock_args)

        mock_setup_django.assert_called()

        mock_all().delete.assert_called()

        call_args = mock_get.call_args_list
        self.assertEqual("General Settings", call_args[0][1]["name"])
        self.assertEqual("Home Page", call_args[1][1]["name"])
        self.assertEqual("Custom Styles", call_args[2][1]["name"])
        self.assertEqual("Custom Templates", call_args[3][1]["name"])

        self.assertEqual(4, mock_setting_defaults.call_count)
        mock_update_settings.assert_called_once_with(vars(mock_args))

    @mock.patch("tethys_cli.site_commands.update_site_settings_content")
    @mock.patch("tethys_cli.site_commands.Path")
    @mock.patch("tethys_cli.site_commands.setup_django")
    def test_gen_site_content_with_yaml(
        self, mock_setup_django, mock_path, mock_update_settings
    ):
        file_path = os.path.join(self.root_app_path, "test-portal_config.yml")
        mock_file_path = mock.MagicMock()
        mock_path.return_value = mock_file_path
        mock_file_path.__truediv__().exists.return_value = True
        mock_file_path.__truediv__().open.return_value = open(file_path)

        mock_args = mock.MagicMock(from_file=True, restore_defaults=False)

        gen_site_content(mock_args)

        mock_setup_django.assert_called()

        self.assertEqual(5, mock_update_settings.call_count)
        mock_update_settings.assert_called_with(vars(mock_args))

    @mock.patch("tethys_cli.site_commands.write_warning")
    @mock.patch("tethys_cli.site_commands.yaml.safe_load")
    @mock.patch("tethys_cli.site_commands.update_site_settings_content")
    @mock.patch("tethys_cli.site_commands.Path")
    @mock.patch("tethys_cli.site_commands.setup_django")
    def test_gen_site_content_with_yaml_invalid_category(
        self,
        mock_setup_django,
        mock_path,
        mock_update_settings,
        mock_load_yaml,
        mock_warn,
    ):
        mock_file_path = mock.MagicMock()
        mock_path.return_value = mock_file_path
        mock_file_path.__truediv__().exists.return_value = True
        mock_load_yaml.return_value = {"site_settings": {"INVALID_CATEGORY": {}}}

        mock_args = mock.MagicMock(from_file=True, restore_defaults=False)

        gen_site_content(mock_args)

        mock_setup_django.assert_called()

        self.assertEqual(5, mock_update_settings.call_count)
        mock_update_settings.assert_called_with(vars(mock_args))
        mock_warn.assert_called_once()

    @mock.patch("tethys_cli.site_commands.update_site_settings_content")
    @mock.patch("builtins.input", side_effect=["x", "n", "y"])
    @mock.patch("tethys_cli.cli_colors.pretty_output")
    @mock.patch("tethys_cli.site_commands.exit")
    @mock.patch("tethys_cli.site_commands.call")
    @mock.patch("tethys_cli.site_commands.Path")
    def test_gen_site_content_with_create_yaml(
        self, mock_path, mock_call, mock_exit, mock_pretty_output, _, __
    ):
        mock_args = mock.MagicMock(restore_defaults=False)
        mock_file_path = mock.MagicMock()
        mock_path.return_value = mock_file_path
        mock_file_path.__truediv__().exists.return_value = False

        gen_site_content(mock_args)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn(
            "Generation of portal_config.yml file cancelled", po_call_args[0][0][0]
        )

        gen_site_content(mock_args)
        self.assertIn("portal", mock_call.call_args_list[0][0][0])
        mock_exit.assert_called_with(0)

    @mock.patch("tethys_cli.site_commands.timezone.now")
    @mock.patch("tethys_config.models.Setting.objects.filter")
    def test_update_site_settings_content(self, mock_filter, mock_now):
        update_site_settings_content({"brand_text": "New Title"})
        mock_filter.assert_called_with(name="Brand Text")
        call_args = mock_filter(name="Brand Text").update.call_args_list
        self.assertEqual("New Title", call_args[0][1]["content"])
        self.assertEqual(mock_now.return_value, call_args[0][1]["date_modified"])

    @mock.patch("tethys_cli.site_commands.write_warning")
    @mock.patch("tethys_config.models.Setting.objects.filter")
    def test_update_site_settings_content_invalid_setting(self, mock_filter, mock_warn):
        mock_filter.return_value = None
        update_site_settings_content(
            {"invalid_setting": "content"}, warn_if_setting_not_found=True
        )
        mock_filter.assert_called_with(name="Invalid Setting")
        mock_warn.assert_called_once()

    def test_uncodify(self):
        result = uncodify("my_css_to_render")
        self.assertEqual("My CSS to Render", result)

    def test_update_site_settings_if_standalone_mode_no_settings(self):
        portal_config_json = {
            "version": 2.0,
            "name": None,
            "apps": None,
            "settings": None,
            "site_settings": {"GENERAL_SETTINGS": {"BRAND_TEXT": "New Title"}},
        }

        updated_portal_config_json = update_site_settings_if_standalone_mode(
            portal_config_json
        )

        expected_portal_config_json = {
            "version": 2.0,
            "name": None,
            "apps": None,
            "settings": None,
            "site_settings": {"GENERAL_SETTINGS": {"BRAND_TEXT": "New Title"}},
        }
        self.assertTrue(updated_portal_config_json == expected_portal_config_json)

    def test_update_site_settings_if_standalone_mode_no_portal_config(self):
        portal_config_json = {
            "version": 2.0,
            "name": None,
            "apps": None,
            "settings": {"TETHYS_PORTAL_CONFIG": None},
            "site_settings": {"GENERAL_SETTINGS": {"BRAND_TEXT": "New Title"}},
        }

        updated_portal_config_json = update_site_settings_if_standalone_mode(
            portal_config_json
        )

        expected_portal_config_json = {
            "version": 2.0,
            "name": None,
            "apps": None,
            "settings": {"TETHYS_PORTAL_CONFIG": None},
            "site_settings": {"GENERAL_SETTINGS": {"BRAND_TEXT": "New Title"}},
        }
        self.assertTrue(updated_portal_config_json == expected_portal_config_json)

    def test_update_site_settings_if_standalone_mode_no_standalone(self):
        portal_config_json = {
            "version": 2.0,
            "name": None,
            "apps": None,
            "settings": {"TETHYS_PORTAL_CONFIG": {"STANDALONE_APP": None}},
            "site_settings": {"GENERAL_SETTINGS": {"BRAND_TEXT": "New Title"}},
        }

        updated_portal_config_json = update_site_settings_if_standalone_mode(
            portal_config_json
        )

        expected_portal_config_json = {
            "version": 2.0,
            "name": None,
            "apps": None,
            "settings": {"TETHYS_PORTAL_CONFIG": {"STANDALONE_APP": None}},
            "site_settings": {"GENERAL_SETTINGS": {"BRAND_TEXT": "New Title"}},
        }
        self.assertTrue(updated_portal_config_json == expected_portal_config_json)

    @mock.patch("tethys_apps.models.TethysApp")
    def test_update_site_settings_if_standalone_mode_standalone(self, mock_tethysapp):
        portal_config_json = {
            "version": 2.0,
            "name": None,
            "apps": None,
            "settings": {
                "TETHYS_PORTAL_CONFIG": {"STANDALONE_APP": "standalone_app_test"}
            },
            "site_settings": None,
        }
        mock_app = mock.MagicMock()
        mock_app.name = "Standalone App Test"
        mock_tethysapp.objects.get.return_value = mock_app
        updated_portal_config_json = update_site_settings_if_standalone_mode(
            portal_config_json
        )

        expected_portal_config_json = {
            "version": 2.0,
            "name": None,
            "apps": None,
            "settings": {
                "TETHYS_PORTAL_CONFIG": {"STANDALONE_APP": "standalone_app_test"}
            },
            "site_settings": {
                "GENERAL_SETTINGS": {
                    "STANDALONE_APP_MODE": "true",
                    "APPS_LIBRARY_TITLE": "Standalone App Test",
                }
            },
        }
        self.assertTrue(updated_portal_config_json == expected_portal_config_json)

    @mock.patch("tethys_apps.models.TethysApp")
    def test_update_site_settings_if_standalone_mode_app_dne(self, mock_tethysapp):
        portal_config_json = {
            "version": 2.0,
            "name": None,
            "apps": None,
            "settings": {
                "TETHYS_PORTAL_CONFIG": {"STANDALONE_APP": "standalone_app_test"}
            },
            "site_settings": None,
        }
        mock_tethysapp.objects.get.side_effect = [ObjectDoesNotExist]
        with self.assertRaises(Exception) as context:
            update_site_settings_if_standalone_mode(portal_config_json)

        self.assertTrue(
            'Could not locate app with package "standalone_app_test".'
            in context.exception.args
        )
