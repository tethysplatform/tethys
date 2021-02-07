import unittest
import tethys_gizmos.views.gizmo_showcase as gizmo_showcase
from unittest import mock
from django.test import RequestFactory
from ... import UserFactory


class TestGizmoShowcase(unittest.TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.request_factory = RequestFactory()

    def tearDown(self):
        pass

    def test_get_geoserver_wms(self):
        expected_endpoint = 'https://demo.geo-solutions.it/geoserver/wms'
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
    @mock.patch('tethys_gizmos.views.gizmo_showcase.CondorWorkflow')
    def test_create_sample_jobs(self, mock_cw, mock_bj):
        mock_bj().return_value = mock.MagicMock()
        request = self.request_factory.get('/jobs')
        request.user = self.user
        gizmo_showcase.create_sample_jobs(request)

        # Check BasicJob Call
        mock_bj.assert_called_with(_status='VCP', description='Completed multi-process job with some errors',
                                   label='gizmos_showcase', name='job_21', user=request.user, status_message=None)
        mock_cw.assert_called_once()
        mock_cw.assert_called_with(name='job_22', user=request.user, description='Workflow job with multiple nodes.',
                                   label='gizmos_showcase', _status='VAR', status_message=None)

    @mock.patch('tethys_gizmos.views.gizmo_showcase.render')
    def test_cesium_map_view_home(self, mock_render):
        request = self.request_factory.get('/jobs')
        request.user = self.user

        # Execute
        gizmo_showcase.cesium_map_view(request, 'home')

        # Check render
        render_call_args = mock_render.call_args_list
        self.assertIn('/developer/gizmos/map_layers/cesium-map-view', render_call_args[0][0][2]['map_layers_link'])
        self.assertIn('home', render_call_args[0][0][2]['page_type'])
        self.assertIn('/developer/gizmos/model/cesium-map-view', render_call_args[0][0][2]['model_link'])
        self.assertIn('/developer/gizmos/home/cesium-map-view', render_call_args[0][0][2]['home_link'])

    @mock.patch('tethys_gizmos.views.gizmo_showcase.render')
    def test_cesium_map_view_map_layers(self, mock_render):
        request = self.request_factory.get('/jobs')
        request.user = self.user

        # Execute
        gizmo_showcase.cesium_map_view(request, 'map_layers')

        # Check render
        render_call_args = mock_render.call_args_list
        self.assertIn('map_layers', render_call_args[0][0][2]['page_type'])

    @mock.patch('tethys_gizmos.views.gizmo_showcase.render')
    def test_cesium_map_view_map_token(self, mock_render):
        request = self.request_factory.get('/jobs', data={'cesium-ion-token': 'cesium-token-goes-here'})
        request.user = self.user

        # Execute
        gizmo_showcase.cesium_map_view(request, 'map_layers')

        # Check render
        render_call_args = mock_render.call_args_list

        self.assertIn('cesium-token-goes-here', render_call_args[0][0][2]['home_link'])
        self.assertIn('cesium-token-goes-here', render_call_args[0][0][2]['map_layers_link'])
        self.assertIn('cesium-token-goes-here', render_call_args[0][0][2]['terrain_link'])
        self.assertIn('cesium-token-goes-here', render_call_args[0][0][2]['czml_link'])
        self.assertIn('cesium-token-goes-here', render_call_args[0][0][2]['geojson_link'])
        self.assertIn('cesium-token-goes-here', render_call_args[0][0][2]['model_link'])
        self.assertIn('cesium-token-goes-here', render_call_args[0][0][2]['model2_link'])

    @mock.patch('tethys_gizmos.views.gizmo_showcase.render')
    def test_cesium_map_view_terrain(self, mock_render):
        request = self.request_factory.get('/jobs')
        request.user = self.user

        # Execute
        gizmo_showcase.cesium_map_view(request, 'terrain')

        # Check render
        render_call_args = mock_render.call_args_list
        self.assertIn('terrain', render_call_args[0][0][2]['page_type'])

    @mock.patch('tethys_gizmos.views.gizmo_showcase.render')
    def test_cesium_map_view_czml(self, mock_render):
        request = self.request_factory.get('/jobs')
        request.user = self.user

        # Execute
        gizmo_showcase.cesium_map_view(request, 'czml')

        # Check render
        render_call_args = mock_render.call_args_list
        self.assertIn('czml', render_call_args[0][0][2]['page_type'])

    @mock.patch('tethys_gizmos.views.gizmo_showcase.render')
    def test_cesium_map_view_geojson(self, mock_render):
        request = self.request_factory.get('/jobs')
        request.user = self.user

        # Execute
        gizmo_showcase.cesium_map_view(request, 'geojson')

        # Check render
        render_call_args = mock_render.call_args_list
        self.assertIn('geojson', render_call_args[0][0][2]['page_type'])

    @mock.patch('tethys_gizmos.views.gizmo_showcase.render')
    def test_cesium_map_view_model(self, mock_render):
        request = self.request_factory.get('/jobs')
        request.user = self.user

        # Execute
        gizmo_showcase.cesium_map_view(request, 'model')

        # Check render
        render_call_args = mock_render.call_args_list
        self.assertIn('model', render_call_args[0][0][2]['page_type'])
        self.assertIn('clock', render_call_args[0][0][2]['cesium_map_view'])
        self.assertIn('globe', render_call_args[0][0][2]['cesium_map_view'])

    @mock.patch('tethys_gizmos.views.gizmo_showcase.render')
    def test_cesium_map_view_models(self, mock_render):
        request = self.request_factory.get('/jobs')
        request.user = self.user

        # Execute
        gizmo_showcase.cesium_map_view(request, 'model2')

        # Check render
        render_call_args = mock_render.call_args_list
        self.assertIn('model2', render_call_args[0][0][2]['page_type'])

    @mock.patch('tethys_gizmos.views.gizmo_showcase.messages')
    def test_cesium_map_view_geometry(self, mock_messages):
        request = self.request_factory.get('/jobs')
        request.user = self.user
        mock_post = mock.MagicMock()
        request.POST = mock_post
        mock_post.get.return_value = 'test_submitted_geometry'

        # Execute
        gizmo_showcase.cesium_map_view(request, 'home')

        # Check geometry submit
        mock_post.get.assert_called_with('geometry', None)
        mock_messages.info.assert_called_with(request, 'test_submitted_geometry')

    @mock.patch('tethys_gizmos.views.gizmo_showcase.render')
    @mock.patch('tethys_gizmos.views.gizmo_showcase.JobsTable')
    @mock.patch('tethys_gizmos.views.gizmo_showcase.TethysJob')
    def test_jobs_table_demo(self, mock_TethysJob, mock_JobsTable, mock_render):
        request = self.request_factory.get('/jobs')
        request.user = self.user

        result = gizmo_showcase.jobs_table_demo(request)

        mock_JobsTable.assert_called_with(
            jobs=mock_TethysJob.objects.filter().order_by().select_subclasses(),
            column_fields=('id', 'name', 'description', 'creation_time'),
            hover=True,
            striped=False,
            bordered=False,
            condensed=False,
            monitor_url='gizmos:results',
            results_url='gizmos:results',
            refresh_interval=10000,
            run_btn=True,
            delete_btn=True,
            show_detailed_status=True,
            actions=['run', 'resubmit', 'log', 'monitor', 'results', 'terminate', 'delete'],
        )

        mock_render.assert_called_with(request, 'tethys_gizmos/gizmo_showcase/jobs_table.html',
                                       {'jobs_table': mock_JobsTable()})
        self.assertEqual(mock_render(), result)
