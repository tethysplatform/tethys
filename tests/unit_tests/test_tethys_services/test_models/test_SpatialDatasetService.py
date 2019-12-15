from tethys_sdk.testing import TethysTestCase
import tethys_services.models as service_model
from unittest import mock


class SpatialDatasetServiceTests(TethysTestCase):
    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test__str__(self):
        sds = service_model.SpatialDatasetService(
            name='test_sds',
        )
        self.assertEqual('test_sds', sds.__str__())

    @mock.patch('tethys_services.models.GeoServerSpatialDatasetEngine')
    def test_get_engine_geo_server(self, mock_sds):
        sds = service_model.SpatialDatasetService(
            name='test_sds',
            engine=service_model.SpatialDatasetService.GEOSERVER,
            endpoint='http://localhost/geoserver/rest/',
            public_endpoint='http://publichost/geoserver/rest/',
            username='foo',
            password='password'
        )
        sds.save()
        ret = sds.get_engine()

        # Check result
        mock_sds.assert_called_with(endpoint='http://localhost/geoserver/rest/', password='password', username='foo')
        self.assertEqual('http://publichost/geoserver/rest/', ret.public_endpoint)

    @mock.patch('tethys_services.models.TDSCatalog')
    @mock.patch('tethys_services.models.session_manager')
    def test_get_engine_thredds(self, mock_session_manager, mock_TDSCatalog):
        sds = service_model.SpatialDatasetService(
            name='test_sds',
            engine=service_model.SpatialDatasetService.THREDDS,
            endpoint='http://localhost/thredds/catalog.xml',
            public_endpoint='http://publichost/thredds/catalog.xml',
            username='foo',
            password='password'
        )
        sds.save()
        ret = sds.get_engine()

        mock_session_manager.set_session_options.assert_called_with(auth=('foo', 'password'))
        mock_TDSCatalog.assert_called_with('http://localhost/thredds/catalog.xml')

        # Check result
        self.assertEqual(mock_TDSCatalog(), ret)