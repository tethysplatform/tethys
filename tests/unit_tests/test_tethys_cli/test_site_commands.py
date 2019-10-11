import unittest
import os
from unittest import mock

from tethys_cli.site_commands import gen_site_content


class CLISiteCommandsTest(unittest.TestCase):
    def setUp(self):
        self.src_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.root_app_path = os.path.join(self.src_dir, 'apps', 'tethysapp-test_app')

    def tearDown(self):
        pass

    @mock.patch('tethys_config.models.Setting.objects.filter')
    @mock.patch('tethys_cli.site_commands.timezone.now')
    @mock.patch('tethys_cli.site_commands.load_apps')
    def test_gen_site_content(self, mock_load_apps, mock_now, mock_filter):

        mock_args = mock.MagicMock(title="New Title", restore_defaults=False, from_file=False)

        gen_site_content(mock_args)

        mock_load_apps.assert_called()
        mock_filter.assert_called_with(name="Brand Text")

        call_args = mock_filter(name="Brand Text").update.call_args_list
        self.assertEqual("New Title", call_args[0][1]['content'])
        self.assertEqual(mock_now.return_value, call_args[0][1]['date_modified'])

    @mock.patch('tethys_config.init.setting_defaults')
    @mock.patch('tethys_config.models.SettingsCategory.objects.get')
    @mock.patch('tethys_config.models.Setting.objects.all')
    @mock.patch('tethys_cli.site_commands.load_apps')
    def test_gen_site_content_restore_defaults(self, mock_load_apps, mock_all, mock_get, mock_setting_defaults):
        mock_args = mock.MagicMock(from_file=False)

        gen_site_content(mock_args)

        mock_load_apps.assert_called()

        mock_all().delete.assert_called()

        call_args = mock_get.call_args_list
        self.assertEqual("General Settings", call_args[0][1]['name'])
        self.assertEqual("Home Page", call_args[1][1]['name'])

        self.assertEqual(2, mock_setting_defaults.call_count)

    @mock.patch('tethys_cli.site_commands.Path')
    @mock.patch('tethys_config.models.Setting.objects.filter')
    @mock.patch('tethys_cli.site_commands.timezone.now')
    @mock.patch('tethys_cli.site_commands.load_apps')
    def test_gen_site_content_with_yaml(self, mock_load_apps, mock_now, mock_filter, mock_path):
        file_path = os.path.join(self.root_app_path, 'test-portal_config.yml')
        mock_file_path = mock.MagicMock()
        mock_path.return_value = mock_file_path
        mock_file_path.__truediv__().exists.return_value = True
        mock_file_path.__truediv__().open.return_value = open(file_path)

        mock_args = mock.MagicMock(from_file=True, restore_defaults=False)

        gen_site_content(mock_args)

        mock_load_apps.assert_called()
        mock_filter.assert_called_with(name="Brand Text")

        call_args = mock_filter(name="Brand Text").update.call_args_list
        self.assertEqual("New Title", call_args[0][1]['content'])
        self.assertEqual(mock_now.return_value, call_args[0][1]['date_modified'])

    @mock.patch('builtins.input', side_effect=['x', 'n', 'y'])
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    @mock.patch('tethys_cli.site_commands.exit')
    @mock.patch('tethys_cli.site_commands.call')
    @mock.patch('tethys_cli.site_commands.Path')
    def test_gen_site_content_with_create_yaml(self, mock_path, mock_call, mock_exit, mock_pretty_output, _):
        mock_args = mock.MagicMock(restore_defaults=False)
        mock_file_path = mock.MagicMock()
        mock_path.return_value = mock_file_path
        mock_file_path.__truediv__().exists.return_value = False

        gen_site_content(mock_args)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn('Generation of portal_config.yml file cancelled', po_call_args[0][0][0])

        gen_site_content(mock_args)
        self.assertIn('portal', mock_call.call_args_list[0][0][0])
        mock_exit.assert_called_with(0)
