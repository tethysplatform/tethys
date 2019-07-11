from unittest import mock
from tethys_sdk.testing import TethysTestCase
from tethys_compute.models import Scheduler
from tethys_compute.scheduler_manager import list_schedulers, get_scheduler, \
    create_condor_scheduler, create_dask_scheduler, create_scheduler


class SchedulerManagerTests(TethysTestCase):

    def set_up(self):
        self.scheduler = Scheduler(
            name='test_scheduler',
            host='localhost',
        )
        self.scheduler.save()

    def tear_down(self):
        self.scheduler.delete()

    @mock.patch('tethys_compute.scheduler_manager.Scheduler')
    def test_list_schedulers(self, mock_scheduler):
        mock_scheduler.objects.all.return_value = ['foo']
        ret = list_schedulers()
        self.assertListEqual(['foo'], ret)
        mock_scheduler.objects.all.assert_called()

    def test_get_scheduler(self):
        ret = get_scheduler('test_scheduler')
        self.assertEqual(self.scheduler, ret)

    def test_get_scheduler_none(self):
        ret = get_scheduler('foo')
        self.assertIsNone(ret)

    @mock.patch('tethys_compute.scheduler_manager.CondorScheduler')
    def test_create_condor_scheduler(self, mock_cs):
        name = 'foo'
        host = 'localhost'
        username = 'bob'
        password = 'pass'
        private_key_path = 'key'
        private_key_pass = 'keypass'
        mock_sch = mock.MagicMock()

        mock_cs.return_value = mock_sch

        self.assertEqual(mock_sch, create_condor_scheduler(
            name, host,
            username=username,
            password=password,
            private_key_path=private_key_path,
            private_key_pass=private_key_pass,
        ))

        mock_cs.assert_called_once_with('foo', 'localhost',
                                        username=username,
                                        password=password,
                                        private_key_path=private_key_path,
                                        private_key_pass=private_key_pass)

    @mock.patch('tethys_compute.scheduler_manager.DaskScheduler')
    def test_create_dask_scheduler(self, mock_ds):
        name = 'foo'
        host = 'localhost'
        timeout = 10
        heartbeat_interval = 5
        dashboard = 'test_dashboard'

        mock_sch = mock.MagicMock()

        mock_ds.return_value = mock_sch

        self.assertEqual(
            mock_sch,
            create_dask_scheduler(
                name, host,
                timeout=timeout,
                heartbeat_interval=heartbeat_interval,
                dashboard=dashboard
            )
        )
        mock_ds.assert_called_once_with('foo', 'localhost', timeout=timeout,
                                        heartbeat_interval=heartbeat_interval,
                                        dashboard=dashboard)

    def test_create_scheduler_invalid_type(self):
        self.assertRaises(ValueError, create_scheduler, 'foo', 'localhost', 'invalid')

    @mock.patch('tethys_compute.scheduler_manager.create_dask_scheduler')
    def test_create_scheduler_dask(self, mock_cds):
        ret = create_scheduler('foo', 'localhost', 'dask')
        self.assertEqual(mock_cds(), ret)

    @mock.patch('tethys_compute.scheduler_manager.create_condor_scheduler')
    def test_create_scheduler_condor(self, mock_ccs):
        ret = create_scheduler('foo', 'localhost', 'condor')
        self.assertEqual(mock_ccs(), ret)

    def test_create_scheulder_invalid_kwargs(self):
        self.assertRaises(ValueError, create_scheduler, 'foo', 'localhost', 'dask', foo='bar')
