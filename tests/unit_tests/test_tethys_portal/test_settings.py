import datetime as dt
from importlib import reload
from unittest import mock, TestCase
from tethys_portal import settings


class TestSettings(TestCase):

    def set_up(self):
        pass

    def tear_down(self):
        pass

    @mock.patch('tethys_portal.settings.yaml.safe_load', return_value={'settings': {'test': 'test'}})
    def test_portal_config_settings(self, mock_local_settings):
        reload(settings)
        self.assertDictEqual(settings.portal_config_settings, mock_local_settings.return_value['settings'])

    @mock.patch('tethys_portal.settings.yaml.safe_load', side_effect=FileNotFoundError())
    @mock.patch('tethys_portal.settings.logging.getLogger')
    def test_portal_config_file_not_found_error(self, mock_log, _):
        reload(settings)
        mock_log.return_value.info.assert_called()

    @mock.patch('tethys_portal.settings.yaml.safe_load', side_effect=RuntimeError())
    @mock.patch('tethys_portal.settings.logging.getLogger')
    def test_portal_config_exception(self, mock_log, _):
        reload(settings)
        mock_log.return_value.exception.assert_called()

    @mock.patch('tethys_portal.settings.yaml.safe_load',
                return_value={'settings': {'TETHYS_PORTAL_CONFIG': {'test_portal_key': 'test'}}})
    def test_tethys_portal_config(self, _):
        reload(settings)
        self.assertEqual(settings.test_portal_key, 'test')

    @mock.patch('tethys_portal.settings.yaml.safe_load',
                return_value={'settings': {'EMAIL_CONFIG': {'test_email_key': 'test'}}})
    def test_email_config(self, _):
        reload(settings)
        self.assertEqual(settings.test_email_key, 'test')

    @mock.patch('tethys_portal.settings.yaml.safe_load',
                return_value={'settings': {'OAUTH_CONFIG': {'test_oauth_key': 'test'}}})
    def test_oauth_config(self, _):
        reload(settings)
        self.assertEqual(settings.test_oauth_key, 'test')

    @mock.patch('tethys_portal.settings.yaml.safe_load',
                return_value={'settings': {'CAPTCHA_CONFIG': {'test_captcha': 'test'}}})
    def test_captcha_config(self, _):
        reload(settings)
        self.assertEqual(settings.test_captcha, 'test')

    @mock.patch('tethys_portal.settings.yaml.safe_load',
                return_value={'settings': {'ANALYTICS_CONFIG': {'test_analytic': 'test'}}})
    def test_analytics_config(self, _):
        reload(settings)
        self.assertEqual(settings.test_analytic, 'test')

    @mock.patch('tethys_portal.settings.yaml.safe_load',
                return_value={'settings': {'MFA_CONFIG': {'MFA_REQUIRED': True}}})
    def test_mfa_config(self, _):
        reload(settings)
        self.assertEqual(settings.MFA_REQUIRED, True)

    @mock.patch('tethys_portal.settings.yaml.safe_load',
                return_value={'settings': {'LOCKOUT_CONFIG': {'AXES_COOLOFF_TIME': 1}}})
    def test_lockout_config__cooloff_int(self, _):
        reload(settings)
        self.assertEqual(settings.AXES_COOLOFF_TIME, 1)

    @mock.patch('tethys_portal.settings.yaml.safe_load',
                return_value={'settings': {'LOCKOUT_CONFIG': {'AXES_COOLOFF_TIME': 'PT45M'}}})
    def test_lockout_config__cooloff_iso_str(self, _):
        reload(settings)
        self.assertEqual(settings.AXES_COOLOFF_TIME, dt.timedelta(minutes=45))

    @mock.patch('tethys_portal.settings.yaml.safe_load',
                return_value={'settings': {'LOCKOUT_CONFIG': {'AXES_COOLOFF_TIME': 'foo'}}})
    def test_lockout_config__cooloff_bad_str(self, _):
        reload(settings)
        self.assertEqual(settings.AXES_COOLOFF_TIME, 'foo')

    @mock.patch('tethys_portal.settings.yaml.safe_load',
                return_value={'settings': {'SESSION_CONFIG': {'SESSION_EXPIRES_AT_BROWSER_CLOSE': True}}})
    def test_session_config(self, _):
        reload(settings)
        self.assertEqual(settings.SESSION_EXPIRES_AT_BROWSER_CLOSE, True)

    @mock.patch('tethys_portal.settings.yaml.safe_load',
                return_value={'settings': {'TEST_SETTING': 'test'}})
    def test_other_settings(self, _):
        reload(settings)
        self.assertEqual(settings.test_oauth_key, 'test')
