import unittest
import tethys_gizmos.views.gizmo_showcase as gizmo_showcase
from requests.exceptions import ConnectionError
import mock
from mock import patch
import factory
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test.client import RequestFactory


# class FakeMessages:
#     ''' mocks the Django message framework, makes it easier to get
#     the messages out '''
#
#     messages = []
#
#     def add(self, level, message, extra_tags):
#         self.messages.append(str(message))
#
#     @property
#     def pop(self):
#         return self.messages.pop()
#
#
# def FakeRequestFactory(*args, **kwargs):
#     ''' FakeRequestFactory, FakeMessages and FakeRequestContext are good for
#     mocking out django views; they are MUCH faster than the Django test client.
#     '''
#
#     user = UserFactory()
#     if kwargs.get('authenticated'):
#         user.is_authenticated = lambda: True
#
#     request = HttpRequest()
#     request.user = user
#     request._messages = FakeMessages()
#     request.session = kwargs.get('session', {})
#     if kwargs.get('POST'):
#         request.method = 'POST'
#         request.POST = kwargs.get('POST')
#     else:
#         request.method = 'GET'
#         request.POST = kwargs.get('GET', {})
#
#     return request
#
#
class UserFactory(factory.Factory):
    ''' using the excellent factory_boy library '''
    FACTORY_FOR = User
    username = factory.Sequence(lambda i: 'test' + i)
    first_name = 'test'
    last_name = 'test2'
    email = factory.Sequence(lambda i: 'test@aquaveo.com' % i)


class TestGizmoShowcase(unittest.TestCase):
    def setUp(self):
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
        # user = User.objects.create(username='admin')
        # user.set_password('pass')
        # user.save()
        # from django.test import TestCase, Client
        # client = Client()
        # client.login(username='admin', password='pass')
        # request = RequestFactory()
        # import pdb
        # pdb.set_trace()
        # gizmo_showcase.index(request)
        pass

    def test_get_kml(self):
        request = RequestFactory()
        result = gizmo_showcase.get_kml(request)

        self.assertIn('kml_link', result._container[0])
        self.assertEqual(200, result.status_code)

    def test_swap_kml(self):
        request = RequestFactory()
        result = gizmo_showcase.swap_kml(request)

        self.assertIn('.kml', result._container[0])
        self.assertEqual(200, result.status_code)

    def test_swap_overlays(self):
        request = RequestFactory()
        result = gizmo_showcase.swap_overlays(request)

        self.assertIn('"type": "GeometryCollection"', result._container[0])
        self.assertEqual(200, result.status_code)

    def test_google_map_view(self):
        pass

    def test_map_view(self):
        pass

    def test_esri_map(self):
        pass

    def test_jobs_table_reuslt(self):
        pass

    def test_create_sample_jobs(self):
        # request = RequestFactory()
        # request.user = UserFactory()
        # result = gizmo_showcase.create_sample_jobs(request).create_job('id', 'des', 'status')
        #
        # import pdb
        # pdb.set_trace()
        pass
