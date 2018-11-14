from django.test import Client
from django.contrib.auth import get_user_model
from tethys_services.models import PersistentStoreService, WebProcessingService, \
    SpatialDatasetService, DatasetService
from tethys_apps.models import TethysApp
from django.test import TestCase


class TethysTestAppTests(TestCase):

    def setUp(self):
        from tethys_apps.harvester import SingletonHarvester
        harvester = SingletonHarvester()
        harvester.harvest()

        self.persistent_service = PersistentStoreService(name="appdb")
        self.persistent_service.save()
        self.wps = WebProcessingService(name="wps", endpoint="http://example.com/wps/WebProcessingService")
        self.wps.save()
        self.geoserver = SpatialDatasetService(name="geoserver", endpoint="http://example.com/geoserver/rest")
        self.geoserver.save()
        self.ckan = DatasetService(name="ckan", endpoint="http://myckan.org/api/3/action")
        self.ckan.save()

        self.username = 'testuser'
        self.password = '12345'
        User = get_user_model()
        self.user = User.objects.create_user(username=self.username,
                                             password=self.password,
                                             email='foo_exist@aquaveo.com')
        self.client = Client()

    def tearDown(self):
        self.user.delete()

    def _get_app_by_name(self, app_name):
        app = TethysApp.objects.filter(name=app_name).first()
        return app

    def _get_app_setting_by_name(self, app_obj, setting_name):
        setting = app_obj.settings_set.filter(name=setting_name).\
            select_subclasses().first()
        return setting

    def test_testapp_configured(self):
        self.assertEquals(TethysApp.objects.filter(name="Test App").count(), 1)
        app = self._get_app_by_name("Test App")
        self.assertFalse(app.configured)

        primary_setting = self._get_app_setting_by_name(app, "primary")
        setattr(primary_setting, "persistent_store_service", self.persistent_service)
        primary_setting.save()
        self.assertFalse(app.configured)

        spatial_db_setting = self._get_app_setting_by_name(app, "spatial_db")
        setattr(spatial_db_setting, "persistent_store_service", self.persistent_service)
        spatial_db_setting.save()
        self.assertFalse(app.configured)

        wps_setting = self._get_app_setting_by_name(app, "primary_52n")
        setattr(wps_setting, "web_processing_service", self.wps)
        wps_setting.save()
        self.assertFalse(app.configured)

        geoserver_setting = self._get_app_setting_by_name(app, "primary_geoserver")
        setattr(geoserver_setting, "spatial_dataset_service", self.geoserver)
        geoserver_setting.save()
        self.assertFalse(app.configured)

        ckan_setting = self._get_app_setting_by_name(app, "primary_ckan")
        setattr(ckan_setting, "dataset_service", self.ckan)
        ckan_setting.save()
        self.assertFalse(app.configured)

        default_name_setting = self._get_app_setting_by_name(app, "default_name")
        setattr(default_name_setting, "value", "default name")
        default_name_setting.save()
        self.assertTrue(app.configured)

    def test_testapp_homepage(self):

        self.assertEquals(TethysApp.objects.filter(name="Test App").count(), 1)
        test_app_url = "/apps/test-app/1/2/"

        # without login
        response = self.client.get(test_app_url)
        self.assertNotEqual(response.status_code, 200)
        self.assertNotIn(b"Test App", response.content)
        self.assertNotIn(b"Heading 1", response.content)

        # login
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(test_app_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test App", response.content)
        self.assertIn(b"Heading 1", response.content)
