import unittest
import mock

from tethys_compute.admin import SchedulerAdmin, JobAdmin


class TestTethysComputeAdmin(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_scheduler_admin(self):
        mock_admin = mock.MagicMock()
        mock_admin2 = mock.MagicMock()

        sa = SchedulerAdmin(mock_admin, mock_admin2)
        self.assertListEqual(['name', 'host', 'username', 'password', 'private_key_path', 'private_key_pass'],
                             sa.list_display)

    def test_job_admin(self):
        mock_admin = mock.MagicMock()
        mock_admin2 = mock.MagicMock()

        ja = JobAdmin(mock_admin, mock_admin2)
        self.assertListEqual(['name', 'description', 'label', 'user', 'creation_time', 'execute_time',
                              'completion_time', 'status'], ja.list_display)
        self.assertEquals(('name',), ja.list_display_links)

    def test_job_admin_has_add_permission(self):
        mock_admin = mock.MagicMock()
        mock_admin2 = mock.MagicMock()
        mock_request = mock.MagicMock()

        ja = JobAdmin(mock_admin, mock_admin2)
        self.assertFalse(ja.has_add_permission(mock_request))

    def test_admin_site_register(self):
        from django.contrib import admin
        from tethys_compute.models import Scheduler, TethysJob
        registry = admin.site._registry
        self.assertIn(Scheduler, registry)
        self.assertIsInstance(registry[Scheduler], SchedulerAdmin)

        self.assertIn(TethysJob, registry)
        self.assertIsInstance(registry[TethysJob], JobAdmin)
