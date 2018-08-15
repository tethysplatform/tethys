"""
********************************************************************************
* Name: test_TethysApp
* Author: nswain
* Created On: August 15, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""
from tethys_sdk.testing import TethysTestCase
from tethys_apps.models import TethysApp, TethysAppSetting
from tethys_services.models import PersistentStoreService, SpatialDatasetService, DatasetService, WebProcessingService


class TethysAppTests(TethysTestCase):

    def set_up(self):
        self.test_app = TethysApp.objects.get(package='test_app')
        self.wps = WebProcessingService(
            name='test_wps',
            endpoint='http://localhost/wps/WebProcessingService',
            username='foo',
            password='password'

        )
        self.wps.save()

        self.sds = SpatialDatasetService(
            name='test_sds',
            endpoint='http://localhost/geoserver/rest/',
            username='foo',
            password='password'
        )
        self.sds.save()

        self.ds = DatasetService(
            name='test_ds',
            endpoint='http://localhost/api/3/action/',
            apikey='foo',
        )
        self.ds.save()

        self.ps = PersistentStoreService(
            name='test_sds',
            host='localhost',
            port='5432',
            username='foo',
            password='password'
        )
        self.ps.save()

    def tear_down(self):
        self.wps.delete()
        self.ps.delete()
        self.ds.delete()
        self.sds.delete()

    def test_unicode(self):
        ret = unicode(self.test_app)
        self.assertEqual('Test App', ret)

    def test_str(self):
        ret = str(self.test_app)
        self.assertEqual('Test App', ret)

    def test_add_settings(self):
        new_setting = TethysAppSetting(
            name='new_setting',
            required=False
        )

        self.test_app.add_settings([new_setting])

        app = TethysApp.objects.get(package='test_app')
        settings = app.settings_set.filter(name='new_setting')
        self.assertEqual(1, len(settings))

    def test_add_settings_add_same_setting_twice(self):
        new_setting = TethysAppSetting(
            name='new_setting',
            required=False
        )
        new_setting_same_name = TethysAppSetting(
            name='new_setting',
            required=False
        )

        self.test_app.add_settings([new_setting, new_setting_same_name])

        app = TethysApp.objects.get(package='test_app')
        settings = app.settings_set.filter(name='new_setting')
        self.assertEqual(1, len(settings))


    def test_settings_prop(self):
        ret = self.test_app.settings
        self.assertEqual(12, len(ret))

        for r in ret:
            self.assertIsInstance(r, TethysAppSetting)

    def test_custom_settings_prop(self):
        pass

    def test_dataset_service_settings_prop(self):
        pass

    def test_spatial_dataset_service_settings_prop(self):
        pass

    def test_wps_services_settings_prop(self):
        pass

    def test_persistent_store_connection_settings_prop(self):
        pass

    def test_persistent_store_database_settings_prop(self):
        pass

    def test_configured_prop_required_and_set(self):
        # See: test_app.app for expected settings configuration
        # Set required settings
        custom_setting = self.test_app.settings_set.select_subclasses().get(name='default_name')
        custom_setting.value = 'foo'
        custom_setting.save()

        ds_setting = self.test_app.settings_set.select_subclasses().get(name='primary_ckan')
        ds_setting.dataset_service = self.ds
        ds_setting.save()

        sds_setting = self.test_app.settings_set.select_subclasses().get(name='primary_geoserver')
        sds_setting.spatial_dataset_service = self.sds
        sds_setting.save()

        wps_setting = self.test_app.settings_set.select_subclasses().get(name='primary_52n')
        wps_setting.web_processing_service = self.wps
        wps_setting.save()

        ps_setting = self.test_app.settings_set.select_subclasses().get(name='primary')
        ps_setting.persistent_store_service = self.ps
        ps_setting.save()

        ret = self.test_app.configured

        self.assertTrue(ret)

    def test_configured_prop_required_no_value(self):
        # See: test_app.app for expected settings configuration
        # Set required settings
        custom_setting = self.test_app.settings_set.select_subclasses().get(name='default_name')
        custom_setting.value = ''
        custom_setting.save()

        ds_setting = self.test_app.settings_set.select_subclasses().get(name='primary_ckan')
        ds_setting.dataset_service = self.ds
        ds_setting.save()

        sds_setting = self.test_app.settings_set.select_subclasses().get(name='primary_geoserver')
        sds_setting.spatial_dataset_service = self.sds
        sds_setting.save()

        wps_setting = self.test_app.settings_set.select_subclasses().get(name='primary_52n')
        wps_setting.web_processing_service = self.wps
        wps_setting.save()

        ps_setting = self.test_app.settings_set.select_subclasses().get(name='primary')
        ps_setting.persistent_store_service = self.ps
        ps_setting.save()

        ret = self.test_app.configured
        self.assertFalse(ret)

    def test_configured_prop_not_assigned_exception(self):
        # See: test_app.app for expected settings configuration
        custom_setting = self.test_app.settings_set.select_subclasses().get(name='default_name')
        custom_setting.value = ''
        custom_setting.save()

        ds_setting = self.test_app.settings_set.select_subclasses().get(name='primary_ckan')
        ds_setting.dataset_service = None
        ds_setting.save()

        sds_setting = self.test_app.settings_set.select_subclasses().get(name='primary_geoserver')
        sds_setting.spatial_dataset_service = None
        sds_setting.save()

        wps_setting = self.test_app.settings_set.select_subclasses().get(name='primary_52n')
        wps_setting.web_processing_service = None
        wps_setting.save()

        ps_setting = self.test_app.settings_set.select_subclasses().get(name='primary')
        ps_setting.persistent_store_service = None
        ps_setting.save()

        ret = self.test_app.configured
        self.assertFalse(ret)


class TethysAppNoSettingsTests(TethysTestCase):

    def set_up(self):
        self.test_app = TethysApp.objects.get(package='test_app')

        # See: test_app.app for expected settings configuration
        for setting in self.test_app.settings_set.all():
            setting.delete()

    def test_configured_prop_no_settings(self):
        ret = self.test_app.configured
        self.assertTrue(ret)

