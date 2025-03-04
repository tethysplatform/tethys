import unittest
from unittest import mock
from tethys_compute.views.dask_dashboard_view import dask_dashboard


class TestDaskDashBoard(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch("tethys_compute.views.dask_dashboard_view.render")
    @mock.patch("tethys_compute.views.dask_dashboard_view.DaskScheduler")
    def test_dask_status_link(self, mock_dask_scheduler, mock_render):
        mock_dask_object = mock.MagicMock()
        mock_dask_object.name = "test_name"
        mock_dask_object.dashboard = "test_dashboard"
        mock_dask_scheduler.objects.get.return_value = mock_dask_object
        request = mock.MagicMock()

        # Execute
        dask_dashboard(request, "test_dask_id", page="status")

        # Check render call
        rts_call_args = mock_render.call_args_list
        self.assertEqual(
            "tethys_compute/dask_scheduler_dashboard.html", rts_call_args[0][0][1]
        )
        self.assertEqual(
            "/admin/dask-dashboard/status/test_dask_id/",
            rts_call_args[0][0][2]["status_link"],
        )

    @mock.patch("tethys_compute.views.dask_dashboard_view.render")
    @mock.patch("tethys_compute.views.dask_dashboard_view.DaskScheduler")
    def test_dask_workers_link(self, mock_dask_scheduler, mock_render):
        mock_dask_object = mock.MagicMock()
        mock_dask_object.name = "test_name"
        mock_dask_object.dashboard = "test_dashboard"
        mock_dask_scheduler.objects.get.return_value = mock_dask_object
        request = mock.MagicMock()

        # Execute
        dask_dashboard(request, "test_dask_id", page="workers")

        # Check render call
        rts_call_args = mock_render.call_args_list
        self.assertEqual(
            "tethys_compute/dask_scheduler_dashboard.html", rts_call_args[0][0][1]
        )
        self.assertEqual(
            "/admin/dask-dashboard/workers/test_dask_id/",
            rts_call_args[0][0][2]["workers_link"],
        )

    @mock.patch("tethys_compute.views.dask_dashboard_view.render")
    @mock.patch("tethys_compute.views.dask_dashboard_view.DaskScheduler")
    def test_dask_tasks_link(self, mock_dask_scheduler, mock_render):
        mock_dask_object = mock.MagicMock()
        mock_dask_object.name = "test_name"
        mock_dask_object.dashboard = "test_dashboard"
        mock_dask_scheduler.objects.get.return_value = mock_dask_object
        request = mock.MagicMock()

        # Execute
        dask_dashboard(request, "test_dask_id", page="tasks")

        # Check render call
        rts_call_args = mock_render.call_args_list
        self.assertEqual(
            "tethys_compute/dask_scheduler_dashboard.html", rts_call_args[0][0][1]
        )
        self.assertEqual(
            "/admin/dask-dashboard/tasks/test_dask_id/",
            rts_call_args[0][0][2]["tasks_link"],
        )

    @mock.patch("tethys_compute.views.dask_dashboard_view.render")
    @mock.patch("tethys_compute.views.dask_dashboard_view.DaskScheduler")
    def test_dask_profile_link(self, mock_dask_scheduler, mock_render):
        mock_dask_object = mock.MagicMock()
        mock_dask_object.name = "test_name"
        mock_dask_object.dashboard = "test_dashboard"
        mock_dask_scheduler.objects.get.return_value = mock_dask_object
        request = mock.MagicMock()

        # Execute
        dask_dashboard(request, "test_dask_id", page="profile")

        # Check render call
        rts_call_args = mock_render.call_args_list
        self.assertEqual(
            "tethys_compute/dask_scheduler_dashboard.html", rts_call_args[0][0][1]
        )
        self.assertEqual(
            "/admin/dask-dashboard/profile/test_dask_id/",
            rts_call_args[0][0][2]["profile_link"],
        )

    @mock.patch("tethys_compute.views.dask_dashboard_view.render")
    @mock.patch("tethys_compute.views.dask_dashboard_view.DaskScheduler")
    def test_dask_graph_link(self, mock_dask_scheduler, mock_render):
        mock_dask_object = mock.MagicMock()
        mock_dask_object.name = "test_name"
        mock_dask_object.dashboard = "test_dashboard"
        mock_dask_scheduler.objects.get.return_value = mock_dask_object
        request = mock.MagicMock()

        # Execute
        dask_dashboard(request, "test_dask_id", page="graph")

        # Check render call
        rts_call_args = mock_render.call_args_list
        self.assertEqual(
            "tethys_compute/dask_scheduler_dashboard.html", rts_call_args[0][0][1]
        )
        self.assertEqual(
            "/admin/dask-dashboard/graph/test_dask_id/",
            rts_call_args[0][0][2]["graph_link"],
        )

    @mock.patch("tethys_compute.views.dask_dashboard_view.render")
    @mock.patch("tethys_compute.views.dask_dashboard_view.DaskScheduler")
    def test_dask_system_link(self, mock_dask_scheduler, mock_render):
        mock_dask_object = mock.MagicMock()
        mock_dask_object.name = "test_name"
        mock_dask_object.dashboard = "test_dashboard"
        mock_dask_scheduler.objects.get.return_value = mock_dask_object
        request = mock.MagicMock()

        # Execute
        dask_dashboard(request, "test_dask_id", page="system")

        # Check render call
        rts_call_args = mock_render.call_args_list
        self.assertEqual(
            "tethys_compute/dask_scheduler_dashboard.html", rts_call_args[0][0][1]
        )
        self.assertEqual(
            "/admin/dask-dashboard/system/test_dask_id/",
            rts_call_args[0][0][2]["systems_link"],
        )

    @mock.patch("tethys_compute.views.dask_dashboard_view.render")
    @mock.patch("tethys_compute.views.dask_dashboard_view.DaskScheduler")
    def test_dask_groups_link(self, mock_dask_scheduler, mock_render):
        mock_dask_object = mock.MagicMock()
        mock_dask_object.name = "test_name"
        mock_dask_object.dashboard = "test_dashboard"
        mock_dask_scheduler.objects.get.return_value = mock_dask_object
        request = mock.MagicMock()

        # Execute
        dask_dashboard(request, "test_dask_id", page="groups")

        # Check render call
        rts_call_args = mock_render.call_args_list
        self.assertEqual(
            "tethys_compute/dask_scheduler_dashboard.html", rts_call_args[0][0][1]
        )
        self.assertEqual(
            "/admin/dask-dashboard/groups/test_dask_id/",
            rts_call_args[0][0][2]["groups_link"],
        )
