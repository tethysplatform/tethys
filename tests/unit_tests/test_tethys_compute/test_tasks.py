import unittest
from unittest import mock

import tethys_compute.tasks as tethys_compute_tasks


async def noop():
    pass


def raise_error():
    raise Exception()


class TestTasks(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch("tethys_compute.tasks._run_after_delay", new_callable=mock.MagicMock)
    @mock.patch("tethys_compute.tasks.asyncio.create_task")
    def test_create_task(self, mock_aio_ct, mock_run_delay):
        mock_func = mock.MagicMock()
        mock_coro = mock.MagicMock()
        mock_run_delay.return_value = mock_coro
        tethys_compute_tasks.create_task(mock_func)
        mock_aio_ct.assert_called_with(mock_coro)
        mock_run_delay.assert_called_with(
            mock_func, delay=0, periodic=False, count=None
        )

    @mock.patch("tethys_compute.tasks.logger")
    async def test_run_after_delay(self, mock_log):
        await tethys_compute_tasks._run_after_delay(
            noop, delay=0, periodic=False, count=None
        )
        mock_log.info.assert_called()

    @mock.patch("tethys_compute.tasks.logger")
    @mock.patch("tethys_compute.tasks.asyncio.sleep")
    async def test_run_after_delay_periodic(self, mock_sleep, mock_log):
        await tethys_compute_tasks._run_after_delay(
            noop, delay=30, periodic=True, count=2
        )
        mock_sleep.assert_called_with(30)
        mock_log.info.assert_called()

    @mock.patch("tethys_compute.tasks.logger")
    async def test_run_after_delay_exception(self, mock_log):
        await tethys_compute_tasks._run_after_delay(
            raise_error, delay=0, periodic=False, count=None
        )
        self.assertEqual(mock_log.info.call_count, 2)
