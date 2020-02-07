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
            name='test_ps',
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
        self.assertEqual(13, len(ret))

        for r in ret:
            self.assertIsInstance(r, TethysAppSetting)

    def test_custom_settings_prop(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(name='default_name')
        custom_setting.value = 'foo'
        custom_setting.save()

        ret = self.test_app.custom_settings

        for r in ret:
            self.assertIsInstance(r, TethysAppSetting)
            if r.name == 'default_name':
                self.assertEqual('foo', r.value)

    def test_dataset_service_settings_prop(self):
        ds_setting = self.test_app.settings_set.select_subclasses().get(name='primary_ckan')
        ds_setting.dataset_service = self.ds
        ds_setting.save()

        ret = self.test_app.dataset_service_settings

        for r in ret:
            self.assertIsInstance(r, TethysAppSetting)
            if r.name == 'primary_ckan':
                self.assertEqual('test_ds', r.dataset_service.name)
                self.assertEqual('foo', r.dataset_service.apikey)
                self.assertEqual('http://localhost/api/3/action/', r.dataset_service.endpoint)

    def test_spatial_dataset_service_settings_prop(self):
        sds_setting = self.test_app.settings_set.select_subclasses().get(name='primary_geoserver')
        sds_setting.spatial_dataset_service = self.sds
        sds_setting.save()

        ret = self.test_app.spatial_dataset_service_settings

        for r in ret:
            self.assertIsInstance(r, TethysAppSetting)
            if r.name == 'primary_geoserver':
                self.assertEqual('test_sds', r.spatial_dataset_service.name)
                self.assertEqual('http://localhost/geoserver/rest/', r.spatial_dataset_service.endpoint)
                self.assertEqual('foo', r.spatial_dataset_service.username)
                self.assertEqual('password', r.spatial_dataset_service.password)

    def test_wps_services_settings_prop(self):
        wps_setting = self.test_app.settings_set.select_subclasses().get(name='primary_52n')
        wps_setting.web_processing_service = self.wps
        wps_setting.save()

        ret = self.test_app.wps_services_settings

        for r in ret:
            self.assertIsInstance(r, TethysAppSetting)
            if r.name == 'primary_52n':
                self.assertEqual('test_wps', r.web_processing_service.name)
                self.assertEqual('http://localhost/wps/WebProcessingService', r.web_processing_service.endpoint)
                self.assertEqual('foo', r.web_processing_service.username)
                self.assertEqual('password', r.web_processing_service.password)

    def test_persistent_store_connection_settings_prop(self):
        ps_setting = self.test_app.settings_set.select_subclasses().get(name='primary')
        ps_setting.persistent_store_service = self.ps
        ps_setting.save()

        ret = self.test_app.persistent_store_connection_settings

        for r in ret:
            self.assertIsInstance(r, TethysAppSetting)
            if r.name == 'primary':
                self.assertEqual('test_ps', r.persistent_store_service.name)
                self.assertEqual('localhost', r.persistent_store_service.host)
                self.assertEqual(5432, r.persistent_store_service.port)
                self.assertEqual('foo', r.persistent_store_service.username)
                self.assertEqual('password', r.persistent_store_service.password)

    def test_persistent_store_database_settings_prop(self):
        ps_setting = self.test_app.settings_set.select_subclasses().get(name='spatial_db')
        ps_setting.persistent_store_service = self.ps
        ps_setting.save()

        ret = self.test_app.persistent_store_database_settings

        for r in ret:
            self.assertIsInstance(r, TethysAppSetting)
            if r.name == 'spatial_db':
                self.assertEqual('test_ps', r.persistent_store_service.name)
                self.assertEqual('localhost', r.persistent_store_service.host)
                self.assertEqual(5432, r.persistent_store_service.port)
                self.assertEqual('foo', r.persistent_store_service.username)
                self.assertEqual('password', r.persistent_store_service.password)

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

        ps_db_setting = self.test_app.settings_set.select_subclasses().get(name='spatial_db')
        ps_db_setting.persistent_store_service = self.ps
        ps_db_setting.save()

        ret = self.test_app.configured

        self.assertTrue(ret)

    def test_configured_prop_required_no_value(self):
        # See: test_app.app for expected settings configuration
        # Set required settings
        custom_setting = self.test_app.settings_set.select_subclasses().get(name='default_name')
        custom_setting.value = ''  # <-- NOT SET / NO VALUE
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

        psd_setting = self.test_app.settings_set.select_subclasses().get(name='spatial_db')
        psd_setting.persistent_store_service = self.ps
        psd_setting.save()

        ret = self.test_app.configured
        self.assertFalse(ret)

    def test_configured_prop_not_assigned_exception(self):
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
