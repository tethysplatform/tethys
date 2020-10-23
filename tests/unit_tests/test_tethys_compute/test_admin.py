import unittest
from unittest import mock

from django import forms

from tethys_compute.admin import JobAdmin, CondorSchedulerAdmin, DaskSchedulerAdmin, CondorSchedulerAdminForm
from tethys_compute.models.condor.condor_scheduler import CondorScheduler


class TestTethysComputeAdmin(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dask_scheduler_admin(self):
        mock_admin = mock.MagicMock()
        mock_admin2 = mock.MagicMock()

        sa = DaskSchedulerAdmin(mock_admin, mock_admin2)
        self.assertListEqual(['name', 'host', 'timeout', 'heartbeat_interval', 'append_link'],
                             sa.list_display)

    def test_CondorSchedulerAdminForm(self):
        mock_args = mock.MagicMock()
        expected_fields = ('name', 'host', 'username', 'password', 'private_key_path', 'private_key_pass')

        ret = CondorSchedulerAdminForm(mock_args)
        self.assertEqual(CondorScheduler, ret.Meta.model)
        self.assertEqual(expected_fields, ret.Meta.fields)
        self.assertTrue('password' in ret.Meta.widgets)
        self.assertIsInstance(ret.Meta.widgets['password'], forms.PasswordInput)
        self.assertTrue('private_key_pass' in ret.Meta.widgets)
        self.assertIsInstance(ret.Meta.widgets['private_key_pass'], forms.PasswordInput)

    def test_condor_scheduler_admin(self):
        mock_admin = mock.MagicMock()
        mock_admin2 = mock.MagicMock()

        sa = CondorSchedulerAdmin(mock_admin, mock_admin2)
        self.assertListEqual(['name', 'host', 'username', 'password', 'private_key_path', 'private_key_pass'],
                             sa.list_display)

    def test_job_admin(self):
        mock_admin = mock.MagicMock()
        mock_admin2 = mock.MagicMock()

        ja = JobAdmin(mock_admin, mock_admin2)
        self.assertListEqual(['name', 'description', 'label', 'user', 'creation_time', 'execute_time',
                              'completion_time', 'status'], ja.list_display)
        self.assertEqual(('name',), ja.list_display_links)

    def test_job_admin_has_add_permission(self):
        mock_admin = mock.MagicMock()
        mock_admin2 = mock.MagicMock()
        mock_request = mock.MagicMock()

        ja = JobAdmin(mock_admin, mock_admin2)
        self.assertFalse(ja.has_add_permission(mock_request))

    def test_admin_site_register(self):
        from django.contrib import admin
        from tethys_compute.models.tethys_job import TethysJob
        from tethys_compute.models.condor.condor_scheduler import CondorScheduler
        from tethys_compute.models.dask.dask_scheduler import DaskScheduler

        registry = admin.site._registry
        self.assertIn(DaskScheduler, registry)
        self.assertIn(CondorScheduler, registry)
        self.assertIn(TethysJob, registry)
        self.assertIsInstance(registry[DaskScheduler], DaskSchedulerAdmin)
        self.assertIsInstance(registry[CondorScheduler], CondorSchedulerAdmin)
        self.assertIsInstance(registry[TethysJob], JobAdmin)

    def test_append_link(self):
        mock_admin = mock.MagicMock()
        mock_admin2 = mock.MagicMock()

        sa = DaskSchedulerAdmin(mock_admin, mock_admin2)

        mock_object = mock.MagicMock(dashboard='test_daskboard', id='123')

        res = sa.append_link(mock_object)

        self.assertEqual('<a href="../../dask-dashboard/status/123" target="_blank">Launch DashBoard</a>', res)
