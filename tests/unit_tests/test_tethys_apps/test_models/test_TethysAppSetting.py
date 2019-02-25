from tethys_sdk.testing import TethysTestCase
from tethys_apps.models import TethysAppSetting
from unittest import mock


class TethysAppSettingTests(TethysTestCase):
    def set_up(self):
        self.test_app_setting = TethysAppSetting.objects.get(name='primary_ckan')

    def tear_down(self):
        pass

    def test_str(self):
        ret = str(self.test_app_setting)
        self.assertEqual('primary_ckan', ret)

    @mock.patch('tethys_apps.models.TethysFunctionExtractor')
    def test_initializer_function_prop(self, mock_tfe):
        mock_tfe.return_value = mock.MagicMock(function='test_function')
        ret = self.test_app_setting.initializer_function

        self.assertEqual('test_function', ret)

    @mock.patch('tethys_apps.models.TethysAppSetting.initializer_function')
    def test_initialize(self, mock_if):
        self.test_app_setting.initialize()
        mock_if.assert_called_with(False)

    def test_get_value(self):
        self.assertRaises(NotImplementedError, self.test_app_setting.get_value, 'test')
