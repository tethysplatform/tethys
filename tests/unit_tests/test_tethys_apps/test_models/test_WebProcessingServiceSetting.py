from tethys_sdk.testing import TethysTestCase
from tethys_apps.models import TethysApp, WebProcessingServiceSetting
from tethys_apps.exceptions import TethysAppSettingNotAssigned
from django.core.exceptions import ValidationError
from unittest import mock


class WebProcessingServiceSettingTests(TethysTestCase):
    def set_up(self):
        self.test_app = TethysApp.objects.get(package="test_app")

        pass

    def tear_down(self):
        pass

    def test_clean_empty_validation_error(self):
        wps_setting = self.test_app.settings_set.select_subclasses().get(
            name="primary_52n"
        )
        wps_setting.web_processing_service = None
        wps_setting.save()
        # Check ValidationError
        self.assertRaises(
            ValidationError,
            WebProcessingServiceSetting.objects.get(name="primary_52n").clean,
        )

    def test_get_value_NotAssigned(self):
        wps_setting = self.test_app.settings_set.select_subclasses().get(
            name="primary_52n"
        )
        wps_setting.web_processing_service = None
        wps_setting.save()
        self.assertRaises(
            TethysAppSettingNotAssigned,
            WebProcessingServiceSetting.objects.get(name="primary_52n").get_value,
        )

    @mock.patch("tethys_apps.models.WebProcessingServiceSetting.web_processing_service")
    def test_get_value(self, mock_wps):
        mock_wps.get_engine.return_value = "test_wps_engine"
        mock_wps.endpoint = "test_endpoint"
        mock_wps.public_endpoint = "test_public_endpoint"
        mock_wps.name = "test_wps_name"

        ret = WebProcessingServiceSetting.objects.get(name="primary_52n").get_value()
        self.assertEqual("test_wps_engine", ret.get_engine())
        self.assertEqual("test_wps_name", ret.name)
        self.assertEqual("test_endpoint", ret.endpoint)
        self.assertEqual("test_public_endpoint", ret.public_endpoint)

    @mock.patch("tethys_apps.models.WebProcessingServiceSetting.web_processing_service")
    def test_get_value_check_if(self, mock_wps):
        mock_wps.get_engine.return_value = "test_wps_engine"
        mock_wps.endpoint = "test_endpoint"
        mock_wps.public_endpoint = "test_public_endpoint"

        # Check if as_engine
        ret = WebProcessingServiceSetting.objects.get(name="primary_52n").get_value(
            as_engine=True
        )
        self.assertEqual("test_wps_engine", ret)

        # Check if as_endpoint
        ret = WebProcessingServiceSetting.objects.get(name="primary_52n").get_value(
            as_endpoint=True
        )
        self.assertEqual("test_endpoint", ret)

        # Check if as_public_endpoint
        ret = WebProcessingServiceSetting.objects.get(name="primary_52n").get_value(
            as_public_endpoint=True
        )
        self.assertEqual("test_public_endpoint", ret)
