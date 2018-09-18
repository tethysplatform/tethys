import unittest
import tethys_gizmos.views.gizmo_showcase as gizmo_showcase
from requests.exceptions import ConnectionError
import mock
from django.test import RequestFactory
from tests.factories.django_user import UserFactory


class TestGizmoShowcase(unittest.TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.request_factory = RequestFactory()

    def tearDown(self):
        pass

    @mock.patch('tethys_gizmos.views.gizmo_showcase.list_spatial_dataset_engines')
    def test_get_geoserver_wms(self, mock_list_sdes):
        endpoint = 'http://localhost:8080/geoserver/rest'
        expected_endpoint = 'http://localhost:8080/geoserver/wms'
        mock_sde = mock.MagicMock(type='GEOSERVER',
                                  endpoint=endpoint)
        mock_list_sdes.return_value = [mock_sde]
        result = gizmo_showcase.get_geoserver_wms()

        # Check Result
        self.assertEqual(expected_endpoint, result)

    @mock.patch('tethys_gizmos.views.gizmo_showcase.list_spatial_dataset_engines')
    def test_get_geoserver_wms_connection_error(self, mock_list_sdes):
        # Connection Error Case
        endpoint = 'http://localhost:8080/geoserver/rest'
        expected_endpoint = 'http://ciwmap.chpc.utah.edu:8080/geoserver/wms'
        mock_sde = mock.MagicMock(type='GEOSERVER',
                                  endpoint=endpoint)
        mock_sde.validate.side_effect = ConnectionError
        mock_list_sdes.return_value = [mock_sde]
        result = gizmo_showcase.get_geoserver_wms()

        # Check Result
        self.assertEqual(expected_endpoint, result)

    def test_index(self):
        request = self.request_factory.post('/jobs', {'editable_map_submit': '1', 'geometry': '[100, 40]'})
        request.user = self.user
        result = gizmo_showcase.index(request)

        self.assertEqual(200, result.status_code)

    def test_get_kml(self):
        request = self.request_factory
        result = gizmo_showcase.get_kml(request)

        self.assertIn('kml_link', result._container[0].decode())
        self.assertEqual(200, result.status_code)

    def test_swap_kml(self):
        request = self.request_factory
        result = gizmo_showcase.swap_kml(request)

        self.assertIn('.kml', result._container[0].decode())
        self.assertEqual(200, result.status_code)

    def test_swap_overlays(self):
        request = self.request_factory
        result = gizmo_showcase.swap_overlays(request)

        self.assertIn('"type": "GeometryCollection"', result._container[0].decode())
        self.assertEqual(200, result.status_code)

    @mock.patch('tethys_gizmos.views.gizmo_showcase.messages')
    def test_google_map_view(self, mock_messages):
        mock_mi = mock_messages.info
        request = self.request_factory.post('/jobs', {'editable_map_submit': '1', 'geometry': '[100, 40]'})
        request.user = self.user
        # Need this to fix the You cannot add messages without installing
        #  django.contrib.messages.middleware.MessageMiddleware
        result = gizmo_showcase.google_map_view(request)

        # Check result
        mock_mi.assert_called_with(request, '[100, 40]')
        self.assertEqual(200, result.status_code)

    @mock.patch('tethys_gizmos.views.gizmo_showcase.messages')
    def test_map_view(self, mock_messages):
        mock_mi = mock_messages.info
        request = self.request_factory.post('/jobs', {'editable_map_submit': '1', 'geometry': '[100, 40]'})
        request.user = self.user
        # Need this to fix the You cannot add messages without installing
        #  django.contrib.messages.middleware.MessageMiddleware
        result = gizmo_showcase.map_view(request)

        # Check result
        mock_mi.assert_called_with(request, '[100, 40]')
        self.assertEqual(200, result.status_code)

    def test_esri_map(self):
        request = self.request_factory.post('/jobs', {'editable_map_submit': '1', 'geometry': '[100, 40]'})
        request.user = self.user
        result = gizmo_showcase.esri_map(request)

        self.assertEqual(200, result.status_code)

    def test_jobs_table_result(self):
        request = self.request_factory.post('/jobs', {'editable_map_submit': '1', 'geometry': '[100, 40]'})
        request.user = self.user
        result = gizmo_showcase.jobs_table_results(request=request, job_id='1')

        self.assertEqual(302, result.status_code)

    @mock.patch('tethys_gizmos.views.gizmo_showcase.BasicJob')
    def test_create_sample_jobs(self, mock_bj):
        mock_bj().return_value = mock.MagicMock()
        request = self.request_factory
        request.user = 'test_user'
        gizmo_showcase.create_sample_jobs(request)

        # Check BasicJob Call
        mock_bj.assert_called_with(_status='VCP', description='Completed multi-process job with some errors',
                                   label='gizmos_showcase', name='job_8', user='test_user')
