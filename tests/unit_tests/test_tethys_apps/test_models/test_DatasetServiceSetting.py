from tethys_sdk.testing import TethysTestCase
from tethys_apps.models import TethysApp, DatasetServiceSetting
from tethys_apps.exceptions import TethysAppSettingNotAssigned
from django.core.exceptions import ValidationError
from tethys_services.models import DatasetService


class DatasetServiceSettingTests(TethysTestCase):
    def set_up(self):
        self.test_app = TethysApp.objects.get(package="test_app")

        pass

    def tear_down(self):
        pass

    def test_clean_empty_validation_error(self):
        ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="primary_ckan"
        )
        ds_setting.dataset_service = None
        ds_setting.save()
        # Check ValidationError
        self.assertRaises(
            ValidationError,
            DatasetServiceSetting.objects.get(name="primary_ckan").clean,
        )

    def test_get_value_NotAssigned(self):
        ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="primary_ckan"
        )
        ds_setting.dataset_service = None
        ds_setting.save()
        self.assertRaises(
            TethysAppSettingNotAssigned,
            DatasetServiceSetting.objects.get(name="primary_ckan").get_value,
        )

    def test_get_value(self):
        ds = DatasetService(
            name="test_ds",
            endpoint="http://localhost/api/3/action/",
            public_endpoint="http://publichost/api/3/action/",
        )
        ds.save()
        ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="primary_ckan"
        )
        ds_setting.dataset_service = ds
        ds_setting.save()

        ret = DatasetServiceSetting.objects.get(name="primary_ckan").get_value()

        self.assertEqual("CKAN", ret.get_engine().type)
        self.assertEqual("test_ds", ret.name)
        self.assertEqual("http://localhost/api/3/action/", ret.endpoint)
        self.assertEqual("http://publichost/api/3/action/", ret.public_endpoint)

    def test_get_value_check_if(self):
        ds = DatasetService(
            name="test_ds",
            endpoint="http://localhost/api/3/action/",
            public_endpoint="http://publichost/api/3/action/",
        )
        ds.save()
        ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="primary_ckan"
        )
        ds_setting.dataset_service = ds
        ds_setting.save()

        # Check as_engine
        ret = DatasetServiceSetting.objects.get(name="primary_ckan").get_value(
            as_engine=True
        )
        self.assertEqual("CKAN", ret.type)

        # Check as_enpoint
        ret = DatasetServiceSetting.objects.get(name="primary_ckan").get_value(
            as_endpoint=True
        )
        self.assertEqual("http://localhost/api/3/action/", ret)

        # Check as_public_endpoint
        ret = DatasetServiceSetting.objects.get(name="primary_ckan").get_value(
            as_public_endpoint=True
        )
        self.assertEqual("http://publichost/api/3/action/", ret)
