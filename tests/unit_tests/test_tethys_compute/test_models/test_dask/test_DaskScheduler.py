"""
********************************************************************************
* Name: test_DaskScheduler
* Author: nswain
* Created On: October 02, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""

from tethys_apps.base.testing.testing import TethysTestCase
from tethys_compute.models import Scheduler, DaskScheduler
from unittest import mock


class DaskSchedulerTest(TethysTestCase):
    def set_up(self):
        self.scheduler = DaskScheduler(
            name="test_dask_scheduler",
            host="localhost",
            timeout=10,
            heartbeat_interval=5,
            dashboard="test_dashboard",
        )
        self.scheduler.save()

        self.scheduler1 = DaskScheduler(
            name="test_dask_scheduler_2",
            host="localhost",
            timeout=0,
            heartbeat_interval=0,
            dashboard="test_dashboard",
        )

        self.scheduler1.save()

    def tear_down(self):
        self.scheduler.delete()
        self.scheduler1.delete()

    def test_DaskScheduler(self):
        ret = DaskScheduler.objects.get(name="test_dask_scheduler")

        # Check result
        self.assertIsInstance(ret, DaskScheduler)
        self.assertEqual("test_dask_scheduler", ret.name)
        self.assertEqual("localhost", ret.host)
        self.assertEqual(10, ret.timeout)
        self.assertEqual(5, ret.heartbeat_interval)
        self.assertEqual("test_dashboard", ret.dashboard)
        self.assertEqual("Dask Scheduler", ret._meta.verbose_name)
        self.assertEqual("Dask Schedulers", ret._meta.verbose_name_plural)

    def test_DaskScheduler_inheritance(self):
        ret = Scheduler.objects.get_subclass(name="test_dask_scheduler")

        # Check result
        self.assertIsInstance(ret, DaskScheduler)
        self.assertEqual("test_dask_scheduler", ret.name)
        self.assertEqual("localhost", ret.host)
        self.assertEqual(10, ret.timeout)
        self.assertEqual(5, ret.heartbeat_interval)
        self.assertEqual("test_dashboard", ret.dashboard)

    @mock.patch("tethys_compute.models.dask.dask_scheduler.Client")
    def test_client_prop(self, mock_client):
        mock_client.return_value = "test_client"

        dask_scheduler = Scheduler.objects.get_subclass(name="test_dask_scheduler")

        # Execute
        ret = dask_scheduler.client

        # Check result
        self.assertEqual("test_client", ret)

        # Check result
        self.assertEqual("test_client", ret)
        mock_client.assert_called_with(
            address="localhost", heartbeat_interval=5, timeout=10
        )

    @mock.patch("tethys_compute.models.dask.dask_scheduler.Client")
    def test_client_prop_no_heartbeat_and_timeout(self, mock_client):
        mock_client.return_value = "test_client"

        dask_scheduler = Scheduler.objects.get_subclass(name="test_dask_scheduler_2")

        # Execute
        ret = dask_scheduler.client

        # Check result
        self.assertEqual("test_client", ret)

        # Check result
        self.assertEqual("test_client", ret)

        mock_client.assert_called_with(
            address="localhost", heartbeat_interval=None, timeout="__no_default__"
        )

    @mock.patch("tethys_compute.models.dask.dask_scheduler.log")
    @mock.patch("tethys_compute.models.dask.dask_scheduler.Client")
    def test_client_error_prop(self, mock_client, mock_log):
        mock_client.side_effect = Exception("test error message")

        dask_scheduler = Scheduler.objects.get_subclass(name="test_dask_scheduler")

        # Execute
        raised_dask_job_exception = False

        try:
            dask_scheduler.client
        except Exception:
            raised_dask_job_exception = True

        # Check result
        self.assertTrue(raised_dask_job_exception)
        mock_log.exception.assert_called_with("Dask Client Init Error")
