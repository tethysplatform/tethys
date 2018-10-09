import unittest
import mock

from tethys_services.base import DatasetService, SpatialDatasetService, WpsService


class TethysServicesBaseTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # Data Services

    @mock.patch('tethys_services.base.pretty_output')
    def test_DatasetService_init_valid_engine(self, mock_pretty_output):
        expected_name = 'DataServices'
        expected_type = 'ckan'
        expected_endpoint = 'tethys_dataset_services.engines.CkanDatasetEngine'
        ret = DatasetService(name=expected_name, type=expected_type, endpoint=expected_endpoint)
        self.assertEquals(expected_name, ret.name)
        self.assertEquals(expected_type, ret.type)
        self.assertEquals(expected_endpoint, ret.endpoint)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn('DEPRECATION WARNING', po_call_args[0][0][0])

    @mock.patch('tethys_services.base.pretty_output')
    @mock.patch('tethys_services.base.len')
    @mock.patch('tethys_services.base.list')
    def test_DatasetService_init_with_more_than_two(self, mock_list, mock_len, mock_pretty_output):
        mock_len.return_value = 3
        mock_list.return_value = ['ckan', 'hydroshare', 'geoserver']
        expected_name = 'DataServices'
        expected_type = 'foo'
        expected_endpoint = 'tethys_dataset_services.engines.CkanDatasetEngine'

        self.assertRaises(ValueError, DatasetService, name=expected_name, type=expected_type,
                          endpoint=expected_endpoint)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEquals(0, len(po_call_args))

    @mock.patch('tethys_services.base.pretty_output')
    def test_DatasetService_init_with_two(self, mock_pretty_output):
        expected_name = 'DataServices'
        expected_type = 'foo'
        expected_endpoint = 'tethys_dataset_services.engines.CkanDatasetEngine'
        self.assertRaises(ValueError, DatasetService, name=expected_name, type=expected_type,
                          endpoint=expected_endpoint)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEquals(0, len(po_call_args))

    @mock.patch('tethys_services.base.pretty_output')
    @mock.patch('tethys_services.base.len')
    @mock.patch('tethys_services.base.list')
    def test_DatasetService_init_with_less_than_two(self, mock_list, mock_len, mock_pretty_output):
        mock_len.return_value = 1
        mock_list.return_value = ['ckan']
        expected_name = 'DataServices'
        expected_type = 'foo'
        expected_endpoint = 'tethys_dataset_services.engines.CkanDatasetEngine'
        self.assertRaises(ValueError, DatasetService, name=expected_name, type=expected_type,
                          endpoint=expected_endpoint)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEquals(0, len(po_call_args))

    @mock.patch('tethys_services.base.pretty_output')
    def test_DatasetService_repr(self, mock_pretty_output):
        expected_name = 'DataServices'
        expected_type = 'ckan'
        expected_endpoint = 'tethys_dataset_services.engines.CkanDatasetEngine'
        ret = DatasetService(name=expected_name, type=expected_type, endpoint=expected_endpoint)
        self.assertEquals('<DatasetService: type=ckan, api_endpoint=tethys_dataset_services.engines.CkanDatasetEngine>',
                          ret.__repr__())
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEquals(1, len(po_call_args))
        self.assertIn('DEPRECATION WARNING', po_call_args[0][0][0])

    # Spatial Data Services

    @mock.patch('tethys_services.base.pretty_output')
    def test_SpatialDatasetService_init_with_valid_spatial_engine(self, mock_pretty_output):
        expected_name = 'SpatialDataServices'
        expected_type = 'geoserver'
        expected_endpoint = 'tethys_dataset_services.engines.GeoServerSpatialDatasetEngine'
        ret = SpatialDatasetService(name=expected_name, type=expected_type, endpoint=expected_endpoint)
        self.assertEquals(expected_name, ret.name)
        self.assertEquals(expected_type, ret.type)
        self.assertEquals(expected_endpoint, ret.endpoint)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn('DEPRECATION WARNING', po_call_args[0][0][0])

    @mock.patch('tethys_services.base.pretty_output')
    @mock.patch('tethys_services.base.len')
    @mock.patch('tethys_services.base.list')
    def test_SpatialDatasetService_init_with_invalid_spatial_engine_more_than_two(self, mock_list,
                                                                                  mock_len,
                                                                                  mock_pretty_output):
        mock_len.return_value = 3
        mock_list.return_value = ['ckan', 'hydroshare', 'geoserver']
        expected_name = 'SpatialDataServices'
        expected_type = 'foo'
        expected_endpoint = 'end-point'
        self.assertRaises(ValueError, SpatialDatasetService, name=expected_name, type=expected_type,
                          endpoint=expected_endpoint)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEquals(0, len(po_call_args))

    @mock.patch('tethys_services.base.pretty_output')
    @mock.patch('tethys_services.base.len')
    @mock.patch('tethys_services.base.list')
    def test_SpatialDatasetService_init_with_valid_spatial_engine_equals_two(self, mock_list,
                                                                             mock_len,
                                                                             mock_pretty_output):
        mock_len.return_value = 2
        mock_list.return_value = ['hydroshare', 'geoserver']
        expected_name = 'SpatialDataServices'
        expected_type = 'foo'
        expected_endpoint = 'end-point'
        self.assertRaises(ValueError, SpatialDatasetService, name=expected_name, type=expected_type,
                          endpoint=expected_endpoint)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEquals(0, len(po_call_args))

    @mock.patch('tethys_services.base.pretty_output')
    @mock.patch('tethys_services.base.len')
    @mock.patch('tethys_services.base.list')
    def test_SpatialDatasetService_init_with_valid_spatial_engine_less_than_two(self, mock_list,
                                                                                mock_len,
                                                                                mock_pretty_output):
        mock_len.return_value = 1
        mock_list.return_value = ['geoserver']
        expected_name = 'SpatialDataServices'
        expected_type = 'foo'
        expected_endpoint = 'end-point'
        self.assertRaises(ValueError, SpatialDatasetService, name=expected_name, type=expected_type,
                          endpoint=expected_endpoint)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEquals(0, len(po_call_args))

    @mock.patch('tethys_services.base.pretty_output')
    def test_SpatialDatasetService_repr(self, mock_pretty_output):
        expected_name = 'SpatialDataServices'
        expected_type = 'geoserver'
        expected_endpoint = 'tethys_dataset_services.engines.GeoServerSpatialDatasetEngine'
        ret = SpatialDatasetService(name=expected_name, type=expected_type, endpoint=expected_endpoint)
        self.assertEquals('<SpatialDatasetService: type=geoserver, '
                          'api_endpoint=tethys_dataset_services.engines.GeoServerSpatialDatasetEngine>', ret.__repr__())
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEquals(1, len(po_call_args))
        self.assertIn('DEPRECATION WARNING', po_call_args[0][0][0])

    # WpsService

    @mock.patch('tethys_services.base.pretty_output')
    def test_WpsService_init(self, mock_pretty_output):
        expected_name = 'foo'
        expected_endpoint = 'end_point'
        ret = WpsService(name=expected_name, endpoint=expected_endpoint)
        self.assertEquals(expected_name, ret.name)
        self.assertEquals(expected_endpoint, ret.endpoint)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEquals(1, len(po_call_args))
        self.assertIn('DEPRECATION WARNING', po_call_args[0][0][0])

    @mock.patch('tethys_services.base.pretty_output')
    def test_WpsService_repr(self, mock_pretty_output):
        expected_name = 'foo'
        expected_endpoint = 'end_point'
        self.assertEquals('<WpsService: name=foo, endpoint=end_point>',
                          WpsService(name=expected_name, endpoint=expected_endpoint).__repr__())
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEquals(1, len(po_call_args))
        self.assertIn('DEPRECATION WARNING', po_call_args[0][0][0])
