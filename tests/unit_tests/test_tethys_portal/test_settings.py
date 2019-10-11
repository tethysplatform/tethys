from importlib import reload
from unittest import mock, TestCase
from tethys_portal import settings


class TestSettings(TestCase):

    def set_up(self):
        pass

    def tear_down(self):
        pass

    @mock.patch('tethys_portal.settings.yaml.safe_load', return_value={'settings': {'test': 'test'}})
    def test_local_settings(self, mock_local_settings):
        reload(settings)
        self.assertDictEqual(settings.local_settings, mock_local_settings.return_value['settings'])

    @mock.patch('tethys_portal.settings.yaml.safe_load', side_effect=FileNotFoundError())
    @mock.patch('tethys_portal.settings.logging.getLogger')
    def test_local_settings_file_not_found_error(self, mock_log, _):
        reload(settings)
        mock_log.return_value.info.assert_called()

    @mock.patch('tethys_portal.settings.yaml.safe_load', side_effect=RuntimeError())
    @mock.patch('tethys_portal.settings.logging.getLogger')
    def test_local_settings_exception(self, mock_log, _):
        reload(settings)
        mock_log.return_value.exception.assert_called()

    @mock.patch('tethys_portal.settings.yaml.safe_load',
                return_value={'settings': {'OAUTH_CONFIGS': {'test_oauth_key': 'test'}}})
    def test_oauth_configs(self, _):
        reload(settings)
        self.assertEqual(settings.test_oauth_key, 'test')

    @mock.patch('tethys_portal.settings.yaml.safe_load',
                return_value={'settings': {'CAPTCHA_CONFIG': {'test_captcha': 'test'}}})
    def test_captcha_config(self, _):
        reload(settings)
        self.assertEqual(settings.test_captcha, 'test')

    @mock.patch('tethys_portal.settings.yaml.safe_load',
                return_value={'settings': {'ANALYTICS_CONFIGS': {'test_analytic': 'test'}}})
    def test_analytics_configs(self, _):
        reload(settings)
        self.assertEqual(settings.test_analytic, 'test')

    @mock.patch('tethys_portal.settings.yaml.safe_load',
                return_value={'settings': {'TEST_SETTING': 'test'}})
    def test_other_settings(self, _):
        reload(settings)
        self.assertEqual(settings.test_oauth_key, 'test')
