import unittest
from unittest import mock

from tethys_compute.views.dask_dashboard import dask_dashboard


class TestDaskDashBoard(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_compute.views.dask_dashboard.server_document')
    @mock.patch('tethys_compute.views.dask_dashboard.render')
    @mock.patch('tethys_compute.views.dask_dashboard.DaskScheduler')
    def test_dask_status_link(self, mock_dask_scheduler, mock_render, mock_bokeh_server):
        mock_dask_object = mock.MagicMock()
        mock_dask_object.name = 'test_name'
        mock_dask_object.dashboard = 'test_dashboard'
        mock_dask_scheduler.objects.get.return_value = mock_dask_object
        request = mock.MagicMock()
        mock_bokeh_server.return_value = '\n<script id="c2701686-24f8-47e0-9f22-b909ac04cabb"></script>'

        # Execute
        dask_dashboard(request, 'test_dask_id', page='status')

        rts_call_args = mock_render.call_args_list

        # Check render call
        self.assertEqual('tethys_compute/dask_scheduler_status.html', rts_call_args[0][0][1])
        self.assertEqual('/admin/dask-dashboard/status/test_dask_id/', rts_call_args[0][0][2]['status_link'])
        rts_bokeh_call_args = mock_bokeh_server.call_args_list

        # Check link passed to server_document
        self.assertEqual('http://test_dashboard/individual-nbytes', rts_bokeh_call_args[0][0][0])
        self.assertEqual('http://test_dashboard/individual-nprocessing', rts_bokeh_call_args[1][0][0])
        self.assertEqual('http://test_dashboard/individual-task-stream', rts_bokeh_call_args[2][0][0])
        self.assertEqual('http://test_dashboard/individual-progress', rts_bokeh_call_args[3][0][0])

    @mock.patch('tethys_compute.views.dask_dashboard.render')
    @mock.patch('tethys_compute.views.dask_dashboard.DaskScheduler')
    def test_dask_workers_link(self, mock_dask_scheduler, mock_render):
        mock_dask_object = mock.MagicMock()
        mock_dask_object.name = 'test_name'
        mock_dask_object.dashboard = 'test_dashboard'
        mock_dask_scheduler.objects.get.return_value = mock_dask_object
        request = mock.MagicMock()

        # Execute
        dask_dashboard(request, 'test_dask_id', page='workers')

        # Check render call
        rts_call_args = mock_render.call_args_list
        self.assertEqual('tethys_compute/dask_scheduler_workers.html', rts_call_args[0][0][1])
        self.assertEqual('/admin/dask-dashboard/workers/test_dask_id/', rts_call_args[0][0][2]['workers_link'])

    @mock.patch('tethys_compute.views.dask_dashboard.render')
    @mock.patch('tethys_compute.views.dask_dashboard.DaskScheduler')
    def test_dask_tasks_link(self, mock_dask_scheduler, mock_render):
        mock_dask_object = mock.MagicMock()
        mock_dask_object.name = 'test_name'
        mock_dask_object.dashboard = 'test_dashboard'
        mock_dask_scheduler.objects.get.return_value = mock_dask_object
        request = mock.MagicMock()

        # Execute
        dask_dashboard(request, 'test_dask_id', page='tasks')

        # Check render call
        rts_call_args = mock_render.call_args_list
        self.assertEqual('tethys_compute/dask_scheduler_tasks.html', rts_call_args[0][0][1])
        self.assertEqual('/admin/dask-dashboard/tasks/test_dask_id/', rts_call_args[0][0][2]['tasks_link'])

    @mock.patch('tethys_compute.views.dask_dashboard.render')
    @mock.patch('tethys_compute.views.dask_dashboard.DaskScheduler')
    def test_dask_profile_link(self, mock_dask_scheduler, mock_render):
        mock_dask_object = mock.MagicMock()
        mock_dask_object.name = 'test_name'
        mock_dask_object.dashboard = 'test_dashboard'
        mock_dask_scheduler.objects.get.return_value = mock_dask_object
        request = mock.MagicMock()

        # Execute
        dask_dashboard(request, 'test_dask_id', page='profile')

        # Check render call
        rts_call_args = mock_render.call_args_list
        self.assertEqual('tethys_compute/dask_scheduler_profile.html', rts_call_args[0][0][1])
        self.assertEqual('/admin/dask-dashboard/profile/test_dask_id/', rts_call_args[0][0][2]['profile_link'])

    @mock.patch('tethys_compute.views.dask_dashboard.render')
    @mock.patch('tethys_compute.views.dask_dashboard.DaskScheduler')
    def test_dask_graph_link(self, mock_dask_scheduler, mock_render):
        mock_dask_object = mock.MagicMock()
        mock_dask_object.name = 'test_name'
        mock_dask_object.dashboard = 'test_dashboard'
        mock_dask_scheduler.objects.get.return_value = mock_dask_object
        request = mock.MagicMock()

        # Execute
        dask_dashboard(request, 'test_dask_id', page='graph')

        # Check render call
        rts_call_args = mock_render.call_args_list
        self.assertEqual('tethys_compute/dask_scheduler_graph.html', rts_call_args[0][0][1])
        self.assertEqual('/admin/dask-dashboard/graph/test_dask_id/', rts_call_args[0][0][2]['graph_link'])

    @mock.patch('tethys_compute.views.dask_dashboard.pull_session')
    @mock.patch('tethys_compute.views.dask_dashboard.components')
    @mock.patch('tethys_compute.views.dask_dashboard.render')
    @mock.patch('tethys_compute.views.dask_dashboard.DaskScheduler')
    def test_dask_system_link(self, mock_dask_scheduler, mock_render, mock_bokeh_com, mock_pull_session):
        mock_dask_object = mock.MagicMock()
        mock_dask_object.name = 'test_name'
        mock_dask_object.dashboard = 'test_dashboard'
        mock_dask_scheduler.objects.get.return_value = mock_dask_object
        request = mock.MagicMock()
        mock_session = mock.MagicMock()
        mock_pull_session.__enter__ = mock_session
        mock_bokeh_com.return_value = ('\n<script id="c2701686-24f8-47e0-9f22-b909ac04cabb"></script>',
                                       {'CPU': '\n<div class="bk-root" id="CPU_ID"></div>'})

        # Execute
        dask_dashboard(request, 'test_dask_id', page='system')

        rts_call_args = mock_render.call_args_list

        # Check render call
        self.assertEqual('tethys_compute/dask_scheduler_system.html', rts_call_args[0][0][1])
        self.assertEqual('/admin/dask-dashboard/status/test_dask_id/', rts_call_args[0][0][2]['status_link'])
        self.assertEqual('CPU_ID', rts_call_args[0][0][2]['the_divs']['CPU']['id'])
