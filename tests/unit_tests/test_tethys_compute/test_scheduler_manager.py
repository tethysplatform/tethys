import unittest
import mock

from tethys_compute.scheduler_manager import list_schedulers, get_scheduler, create_scheduler


class SchedulerManagerTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_compute.scheduler_manager.Scheduler')
    def test_list_schedulers(self, mock_scheduler):
        mock_scheduler.objects.all.return_value = ['foo']
        ret = list_schedulers()
        self.assertListEqual(['foo'], ret)
        mock_scheduler.objects.all.assert_called()

    @mock.patch('tethys_compute.scheduler_manager.Scheduler')
    def test_get_scheduler(self, mock_scheduler):
        mock_filter_sche = mock.MagicMock()
        mock_filter_foo = mock.MagicMock()
        mock_filter_bar = mock.MagicMock()

        def my_filter(name):
            if name == 'foo':
                return [mock_filter_foo]
            elif name == 'bar':
                return [mock_filter_bar]
            else:
                return [mock_filter_sche]

        mock_scheduler.objects.filter.side_effect = my_filter

        self.assertEquals(mock_filter_foo, get_scheduler('foo'))
        self.assertEquals(mock_filter_bar, get_scheduler('bar'))
        self.assertEquals(mock_filter_sche, get_scheduler('asdf'))
        mock_scheduler.objects.filter.assert_any_call(name='foo')
        mock_scheduler.objects.filter.assert_any_call(name='bar')
        mock_scheduler.objects.filter.assert_any_call(name='asdf')

    @mock.patch('tethys_compute.scheduler_manager.Scheduler')
    def test_create_scheduler(self, mock_scheduler):
        name = 'foo'
        host = 'localhost'
        mock_sch = mock.MagicMock()

        mock_scheduler.return_value = mock_sch

        self.assertEquals(mock_sch, create_scheduler(name, host))
        mock_scheduler.assert_called_once_with('foo', 'localhost', None, None, None, None)
