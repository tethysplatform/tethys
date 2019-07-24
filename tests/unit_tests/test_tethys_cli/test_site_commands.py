import unittest
from unittest import mock

from tethys_cli.site_commands import gen_site_content


class CLISiteCommandsTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_config.models.Setting.objects.filter')
    @mock.patch('tethys_cli.site_commands.timezone.now')
    @mock.patch('tethys_cli.site_commands.load_apps')
    def test_gen_site_content(self, mock_load_apps, mock_now, mock_filter):

        mock_args = mock.MagicMock(title="New Title", restore_defaults=False)

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
        mock_args = mock.MagicMock()

        gen_site_content(mock_args)

        mock_load_apps.assert_called()

        mock_all().delete.assert_called()

        call_args = mock_get.call_args_list
        self.assertEqual("General Settings", call_args[0][1]['name'])
        self.assertEqual("Home Page", call_args[1][1]['name'])

        self.assertEqual(2, mock_setting_defaults.call_count)
