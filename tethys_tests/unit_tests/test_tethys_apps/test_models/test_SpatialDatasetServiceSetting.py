from tethys_sdk.testing import TethysTestCase
from tethys_apps.models import TethysApp
from django.core.exceptions import ValidationError
from tethys_services.models import SpatialDatasetService


class SpatialDatasetServiceTests(TethysTestCase):
    def set_up(self):
        self.test_app = TethysApp.objects.get(package='test_app')

        pass

    def tear_down(self):
        pass

    def test_clean(self):
        sds_setting = self.test_app.settings_set.select_subclasses().get(name='primary_geoserver')
        sds_setting.spatial_dataset_service = None
        sds_setting.save()
        # Check ValidationError
        self.assertRaises(ValidationError, self.test_app.settings_set.select_subclasses().
                          get(name='primary_geoserver').clean)

    def test_get_value(self):
        sds = SpatialDatasetService(
            name='test_sds',
            endpoint='http://localhost/geoserver/rest/',
            public_endpoint='http://publichost/geoserver/rest/',
            apikey='test_api',
            username='foo',
            password='password',
        )
        sds.save()
        sds_setting = self.test_app.settings_set.select_subclasses().get(name='primary_geoserver')
        sds_setting.spatial_dataset_service = sds
        sds_setting.save()

        ret = self.test_app.settings_set.select_subclasses().get(name='primary_geoserver').get_value()

        # Check result
        self.assertEqual('test_sds', ret.name)
        self.assertEqual('http://localhost/geoserver/rest/', ret.endpoint)
        self.assertEqual('http://publichost/geoserver/rest/', ret.public_endpoint)
        self.assertEqual('test_api', ret.apikey)
        self.assertEqual('foo', ret.username)
        self.assertEqual('password', ret.password)

    def test_get_value_none(self):
        sds_setting = self.test_app.settings_set.select_subclasses().get(name='primary_geoserver')
        sds_setting.spatial_dataset_service = None
        sds_setting.save()

        ret = self.test_app.settings_set.select_subclasses().get(name='primary_geoserver').get_value()
        self.assertIsNone(ret)

    def test_get_value_check_if(self):
        sds = SpatialDatasetService(
            name='test_sds',
            endpoint='http://localhost/geoserver/rest/',
            public_endpoint='http://publichost/geoserver/rest/',
            apikey='test_api',
            username='foo',
            password='password',
        )
        sds.save()
        sds_setting = self.test_app.settings_set.select_subclasses().get(name='primary_geoserver')
        sds_setting.spatial_dataset_service = sds
        sds_setting.save()

        # Check as_engine
        ret = self.test_app.settings_set.select_subclasses().get(name='primary_geoserver').get_value(as_engine=True)
        # Check result
        self.assertEqual('GEOSERVER', ret.type)
        self.assertEqual('http://localhost/geoserver/rest/', ret.endpoint)

        # Check as wms
        ret = self.test_app.settings_set.select_subclasses().get(name='primary_geoserver').get_value(as_wms=True)
        # Check result
        self.assertEqual('http://localhost/geoserver/wms', ret)

        # Check as wfs
        ret = self.test_app.settings_set.select_subclasses().get(name='primary_geoserver').get_value(as_wfs=True)
        # Check result
        self.assertEqual('http://localhost/geoserver/ows', ret)

        # Check as_endpoint
        ret = self.test_app.settings_set.select_subclasses().get(name='primary_geoserver').get_value(as_endpoint=True)
        # Check result
        self.assertEqual('http://localhost/geoserver/rest/', ret)

        # Check as_endpoint
        ret = self.test_app.settings_set.select_subclasses().get(name='primary_geoserver').\
            get_value(as_public_endpoint=True)
        # Check result
        self.assertEqual('http://publichost/geoserver/rest/', ret)
