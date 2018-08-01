import unittest
import tethys_gizmos.views.gizmo_showcase as gizmo_showcase
from requests.exceptions import ConnectionError
import mock
from django.test import RequestFactory
from tests.factories.django_user import UserFactory
from django.contrib.messages.storage.fallback import FallbackStorage


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

    def test_google_map_view(self):
        request = self.request_factory.post('/jobs', {'editable_map_submit': '1', 'geometry': '[100, 40]'})
        request.user = self.user
        # Need this to fix the You cannot add messages without installing
        #  django.contrib.messages.middleware.MessageMiddleware
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        result = gizmo_showcase.google_map_view(request)

        self.assertEqual(200, result.status_code)

    def test_map_view(self):
        request = self.request_factory.post('/jobs', {'editable_map_submit': '1', 'geometry': '[100, 40]'})
        request.user = self.user
        # Need this to fix the You cannot add messages without installing
        #  django.contrib.messages.middleware.MessageMiddleware
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        result = gizmo_showcase.map_view(request)

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

    def test_create_sample_jobs(self):
        request = self.request_factory
        request.user = self.user

        # import pdb
        # pdb.set_trace()
        # result = gizmo_showcase.create_sample_jobs(request)
        # TODO: Ask Nathan on save error message. Mock BasicJob and check Assert

    def test_get_kml(self):
        request = self.request_factory
        result = gizmo_showcase.get_kml(request)

        self.assertIn('kml_link', result._container[0])
        self.assertEqual(200, result.status_code)

    def test_swap_kml(self):
        request = self.request_factory
        result = gizmo_showcase.swap_kml(request)

        self.assertIn('.kml', result._container[0])
        self.assertEqual(200, result.status_code)

    def test_swap_overlays(self):
        request = self.request_factory
        result = gizmo_showcase.swap_overlays(request)

        self.assertIn('"type": "GeometryCollection"', result._container[0])
        self.assertEqual(200, result.status_code)
