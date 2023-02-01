from tethys_sdk.testing import TethysTestCase
from tethys_compute.models.dask.dask_scheduler import Scheduler, DaskScheduler
from tethys_compute.models.dask.dask_job import DaskJob
from django.contrib.auth.models import User
import dask
from unittest import mock
import time


@dask.delayed
def inc(x):
    return x + 1


@dask.delayed
def double(x):
    return x + 2


@dask.delayed
def add(x, y):
    time.sleep(2)
    return x + y


class DaskJobTest(TethysTestCase):
    def set_up(self):
        self.user = User.objects.create_user("tethys_super", "user@example.com", "pass")

        self.scheduler = DaskScheduler(
            name="test_dask_scheduler",
            host="127.0.0.1:8000",
            timeout=10,
            heartbeat_interval=5,
            dashboard="test_dashboard",
        )
        self.scheduler.save()

    def tear_down(self):
        self.scheduler.delete()

    @mock.patch("tethys_compute.models.dask.dask_job.Client")
    def test_client_prop_with_invalid_scheduler(self, mock_client):
        mock_client.return_value = "test_client"

        djob = DaskJob(
            name="test_dj",
            user=self.user,
            key="test_key",
            label="label",
            scheduler=None,
        )

        # Execute
        ret = djob.client

        # Check result
        self.assertEqual("test_client", ret)
        mock_client.assert_called()

    @mock.patch("tethys_compute.models.dask.dask_scheduler.Client")
    def test_client_prop_with_valid_scheduler(self, mock_client):
        mock_client.return_value = "test_client"
        dask_scheduler = Scheduler.objects.get_subclass(name="test_dask_scheduler")

        djob = DaskJob(
            name="test_dj",
            user=self.user,
            key="test_key",
            label="label",
            scheduler=dask_scheduler,
        )

        # Execute
        ret = djob.client

        # Check result
        self.assertEqual("test_client", ret)
        mock_client.assert_called_with(
            address="127.0.0.1:8000", heartbeat_interval=5, timeout=10
        )

    @mock.patch("tethys_compute.models.dask.dask_job.Client")
    def test_client_no_scheduler_prop(self, mock_client):
        mock_client.return_value = "test_default_client"
        # Create DaskJob
        djob = DaskJob(name="test_dj", user=self.user, label="label")

        # Execute
        ret = djob.client

        # Check result
        self.assertEqual("test_default_client", ret)
        mock_client.assert_called_with()

    @mock.patch("tethys_compute.models.dask.dask_scheduler.Client")
    @mock.patch("tethys_compute.models.dask.dask_job.Future")
    def test_future_prop(self, mock_future, mock_client):
        mock_client_ret = mock.MagicMock()

        mock_client.return_value = mock_client_ret

        mock_client_ret.submit.return_value = mock.MagicMock(key="test_key")

        # Create DaskJob
        djob = DaskJob(
            name="test_dj", user=self.user, label="label", scheduler=self.scheduler
        )

        # Get Scheduler Client from DaskJob using client property
        client = djob.client

        # Use this Client to run rando function with a future handler
        future = client.submit(inc, 1)

        # Get the key from future handler and assign it to DaskJob key to keep track of this inc function
        djob.key = future.key

        # Use DaskJob future property to get back the inc function
        ret = djob.future

        # Check result
        mock_future.assert_called_with(key="test_key", client=mock_client_ret)
        self.assertEqual(mock_future(), ret)

    @mock.patch("tethys_compute.models.dask.dask_scheduler.Client")
    def test_future_prop_no_key(self, mock_client):
        mock_client_ret = mock.MagicMock()

        mock_client.return_value = mock_client_ret

        mock_client_ret.submit.return_value = mock.MagicMock(key="test_key")

        # Create DaskJob
        djob = DaskJob(
            name="test_dj", user=self.user, label="label", scheduler=self.scheduler
        )

        # Get Scheduler Client from DaskJob using client property
        client = djob.client

        # Use this Client to run inc function with a future handler
        client.submit(inc, 1)

        # Use DaskJob future property to get back the inc function
        ret = djob.future

        # Check result
        self.assertIsNone(ret)

    @mock.patch("tethys_compute.models.dask.dask_job.log")
    @mock.patch("tethys_compute.models.dask.dask_scheduler.Client")
    @mock.patch("tethys_compute.models.dask.dask_job.Future")
    def test_future_prop_exception(self, mock_future, mock_client, mock_log):
        mock_client_ret = mock.MagicMock()

        mock_client.return_value = mock_client_ret

        mock_client_ret.submit.return_value = mock.MagicMock(key="test_key")

        mock_future.side_effect = Exception("exception in creating future")

        # Create DaskJob
        djob = DaskJob(
            name="test_dj", user=self.user, label="label", scheduler=self.scheduler
        )

        # Get Scheduler Client from DaskJob using client property
        client = djob.client

        # Use this Client to run inc function with a future handler
        future = client.submit(inc, 1)

        # Get the key from future handler and assign it to DaskJob key to keep track of this inc function
        djob.key = future.key

        # Use DaskJob future property to get back the inc function
        ret = djob.future

        # Check result
        self.assertIsNone(ret)
        mock_log.exception.assert_called_with("Dask Future Init Error")

    @mock.patch("tethys_compute.models.dask.dask_job.fire_and_forget")
    @mock.patch("django.db.models.base.Model.save")
    @mock.patch("tethys_compute.models.dask.dask_scheduler.Client")
    def test_execute_delayed(self, mock_client, mock_save, mock_ff):
        mock_client_ret = mock.MagicMock()

        mock_client.return_value = mock_client_ret

        mock_future = mock.MagicMock(key="test_key")
        mock_client_ret.compute.return_value = mock_future

        # Create DaskJob
        djob = DaskJob(
            name="test_dj", user=self.user, label="label", scheduler=self.scheduler
        )

        # Delayed option
        delayed = dask.delayed(inc)(1)

        # _Execute
        djob._execute(delayed)

        # Check result
        mock_client_ret.compute.assert_called_with(delayed)
        self.assertEqual("test_key", djob.key)
        mock_save.assert_called()
        mock_ff.assert_called_with(mock_future)

    @mock.patch("tethys_compute.models.dask.dask_job.isinstance")
    @mock.patch("tethys_compute.models.dask.dask_job.fire_and_forget")
    @mock.patch("django.db.models.base.Model.save")
    @mock.patch("tethys_compute.models.dask.dask_scheduler.Client")
    def test_execute_future(self, mock_client, mock_save, mock_ff, mock_isinstance):
        mock_client.return_value = mock.MagicMock()

        mock_isinstance.side_effect = [True, False]

        # Create DaskJob
        djob = DaskJob(
            name="test_dj", user=self.user, label="label", scheduler=self.scheduler
        )

        # get client from DaskJob
        client = djob.client

        # Future option
        future = client.submit(inc, 2)

        # _Execute
        djob._execute(future)

        # Check result
        self.assertEqual(future.key, djob.key)
        mock_save.assert_called()
        mock_ff.assert_called_with(future)

    def test_execute_not_future_delayed(self):
        # Create DaskJob
        djob = DaskJob(
            name="test_dj", user=self.user, label="label", scheduler=self.scheduler
        )

        # _Execute
        self.assertRaises(ValueError, djob._execute, 1)

    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob.client")
    @mock.patch("django.db.models.base.Model.save")
    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob.future")
    def test_update_status(self, mock_future, mock_save, mock_client):
        mock_future.status = "finished"
        # Create DaskJob
        djob = DaskJob(
            name="test_dj", user=self.user, label="label", scheduler=self.scheduler
        )

        # call the function
        djob._update_status()

        # check the results
        mock_client.close.assert_called()
        mock_save.assert_called()

    def test_update_status_with_no_future(self):
        # Create DaskJob
        djob = DaskJob(
            name="test_dj", user=self.user, label="label", scheduler=self.scheduler
        )

        # check the results
        self.assertIsNone(djob._update_status())

    @mock.patch("tethys_compute.models.dask.dask_job.log")
    @mock.patch("django.db.models.base.Model.save")
    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob.future")
    def test_update_status_exception(self, mock_future, mock_save, mock_log):
        # Invalid status key
        mock_future.status = "foo"

        # Create DaskJob
        djob = DaskJob(
            name="test_dj", user=self.user, label="label", scheduler=self.scheduler
        )

        # call the function
        djob._update_status()

        # check the results
        mock_log.error.assert_called_with('Unknown Dask Status: "foo"')

    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob._acquire_pr_lock")
    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob._release_pr_lock")
    def test_process_result_with_failed_lock(self, mock_re_lock, mock_apl):
        mock_apl.return_value = False

        # Create DaskJob
        djob = DaskJob(
            name="test_dj",
            user=self.user,
            label="label",
            scheduler=self.scheduler,
            _process_results_function="test_function",
        )

        # call the function
        self.assertIsNone(djob._process_results())

        # check the result
        mock_re_lock.assert_not_called()

    @mock.patch(
        "tethys_compute.models.dask.dask_job.DaskJob.future",
        new_callable=mock.PropertyMock(return_value=None),
    )
    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob._acquire_pr_lock")
    def test_process_result_no_future(self, mock_apl, _):
        mock_apl.return_value = True

        # Create DaskJob
        djob = DaskJob(
            name="test_dj",
            user=self.user,
            label="label",
            scheduler=self.scheduler,
            _process_results_function="test_function",
        )

        # call the function
        self.assertIsNone(djob._process_results())

    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob.client")
    @mock.patch(
        "tethys_compute.models.dask.dask_job.DaskJob.future",
        new_callable=mock.PropertyMock(),
    )
    def test_process_result_forget(self, _, mock_client):
        # Create DaskJob
        djob = DaskJob(
            name="test_dj",
            user=self.user,
            label="label",
            scheduler=self.scheduler,
            forget=True,
        )

        # call the function
        ret = djob._process_results()

        # check the result
        mock_client.close.assert_called()
        self.assertIsNone(ret)

    @mock.patch("tethys_compute.models.tethys_job.TethysFunctionExtractor")
    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob.future")
    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob.client")
    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob._acquire_pr_lock")
    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob._release_pr_lock")
    def test_process_result_with_result_function(
        self, mock_re_lock, mock_apl, mock_client, mock_future, mock_tfe
    ):
        fake_key = "sum_faef"
        mock_function_extractor = mock.MagicMock()
        mock_function = mock.MagicMock(return_value="foo")
        mock_function_extractor.valid = True
        mock_function_extractor.function = mock_function
        mock_tfe.return_value = mock_function_extractor
        mock_apl.return_value = True

        # Create DaskJob
        djob = DaskJob(
            name="test_dj",
            user=self.user,
            label="label",
            scheduler=self.scheduler,
            _process_results_function="test_function",
        )
        djob.key = fake_key

        # call the function
        djob._process_results()

        # check the result
        mock_client.close.assert_called()
        mock_client.gather.assert_called_with(mock_future)
        mock_function.assert_called_with(mock_client.gather())
        mock_client.set_metadata.assert_called_with(fake_key, False)
        self.assertEqual("", djob.key)
        mock_re_lock.assert_called()

    @mock.patch("tethys_compute.models.tethys_job.TethysFunctionExtractor")
    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob.future")
    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob.client")
    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob._acquire_pr_lock")
    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob._release_pr_lock")
    @mock.patch("tethys_compute.models.dask.dask_job.log")
    def test_process_result_with_client_gather_exception(
        self, mock_logger, mock_re_lock, mock_apl, mock_client, mock_future, mock_tfe
    ):
        mock_function_extractor = mock.MagicMock()
        mock_function = mock.MagicMock(return_value="foo")
        mock_function_extractor.valid = True
        mock_function_extractor.function = mock_function
        mock_tfe.return_value = mock_function_extractor
        mock_apl.return_value = True
        gather_exception = Exception("Fake exception")
        mock_client.gather.side_effect = gather_exception

        # Create DaskJob
        djob = DaskJob(
            name="test_dj",
            user=self.user,
            label="label",
            scheduler=self.scheduler,
            _process_results_function="test_function",
        )

        # call the function
        djob._process_results()

        # check the result
        mock_client.gather.assert_called_with(mock_future)
        mock_logger.warning.assert_called()
        mock_function.assert_called_with(gather_exception)
        mock_re_lock.assert_called()

    @mock.patch("django.db.models.base.Model.save")
    @mock.patch("tethys_compute.models.dask.dask_job.log")
    @mock.patch("tethys_compute.models.tethys_job.TethysFunctionExtractor")
    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob.future")
    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob.client")
    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob._acquire_pr_lock")
    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob._release_pr_lock")
    def test_process_result_with_result_function_with_exception(
        self, mock_re_lock, mock_apl, _, mock_client, mock_tfe, mock_log, mock_save
    ):
        mock_function_extractor = mock.MagicMock()
        mock_function = mock.MagicMock()
        mock_function.side_effect = Exception
        mock_function_extractor.valid = True
        mock_function_extractor.function = mock_function
        mock_tfe.return_value = mock_function_extractor
        mock_apl.return_value = True

        # Create DaskJob
        djob = DaskJob(
            name="test_dj",
            user=self.user,
            label="label",
            scheduler=self.scheduler,
            _process_results_function="test_function",
        )

        # call the function
        djob._process_results()

        # check the result
        mock_log.exception.assert_called_with("Process Results Function Error")
        self.assertEqual("ERR", djob._status)
        mock_save.assert_called()
        mock_re_lock.assert_called()

    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob.future")
    def test_stop(self, mock_future):
        # Create DaskJob
        djob = DaskJob(
            name="test_dj", user=self.user, label="label", scheduler=self.scheduler
        )

        # call the stop function
        djob.stop()

        # Check result
        mock_future.cancel.assert_called()

    def test_pause(self):
        djob = DaskJob(
            name="test_dj",
            user=self.user,
            key="test_key",
            label="label",
            scheduler=self.scheduler,
        )

        # Execute and heck result
        self.assertRaises(NotImplementedError, djob.pause)

    def test_resume(self):
        djob = DaskJob(
            name="test_dj",
            user=self.user,
            key="test_key",
            label="label",
            scheduler=self.scheduler,
        )

        # Execute and heck result
        self.assertRaises(NotImplementedError, djob.resume)

    def test_result(self):
        # Create DaskJob
        djob = DaskJob(
            name="test_dj", user=self.user, label="label", scheduler=self.scheduler
        )
        # need to convert to string because it will convert to string when saving to the database
        djob.result = "serialized_results"

        # call the function
        ret = djob.result

        # Check result
        self.assertEqual("serialized_results", ret)

    def test_result_none(self):
        # Create DaskJob
        djob = DaskJob(
            name="test_dj", user=self.user, label="label", scheduler=self.scheduler
        )
        djob.result = None

        # call the function
        ret = djob.result

        # Check result
        self.assertIsNone(ret)

    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob.future")
    def test_done(self, mock_future):
        # Create DaskJob
        djob = DaskJob(
            name="test_dj", user=self.user, label="label", scheduler=self.scheduler
        )

        # call the done function
        ret = djob.done()

        # Check result
        mock_future.done.assert_called()
        self.assertEqual(mock_future.done(), ret)

    def test_done_with_no_future(self):
        # Create DaskJob
        djob = DaskJob(
            name="test_dj", user=self.user, label="label", scheduler=self.scheduler
        )

        # Check result
        self.assertIsNone(djob.done())

    def test_update_status_interval_prop(self):
        from datetime import timedelta

        # Create DaskJob
        djob = DaskJob(name="test_daskjob", user=self.user, label="label")
        djob.save()

        ret = DaskJob.objects.get(name="test_daskjob").update_status_interval

        # Check result
        self.assertIsInstance(ret, timedelta)
        self.assertEqual(timedelta(0, 0), ret)

        djob.delete()

    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob.future")
    def test_retry(self, mock_future):
        # Create DaskJob
        djob = DaskJob(
            name="test_dj", user=self.user, label="label", scheduler=self.scheduler
        )

        # call the done function
        djob.retry()

        # Check result
        mock_future.retry.assert_called()

    def test_retry_no_future(self):
        # Create DaskJob
        djob = DaskJob(
            name="test_dj", user=self.user, label="label", scheduler=self.scheduler
        )

        # call the done function
        self.assertIsNone(djob.retry())

    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob.future")
    def test__resubmit(self, mock_future):
        # Create DaskJob
        djob = DaskJob(
            name="test_dj", user=self.user, label="label", scheduler=self.scheduler
        )

        # call the done function
        djob._resubmit()

        # Check result
        mock_future.retry.assert_called()

    @mock.patch("tethys_compute.models.dask.dask_scheduler.Client")
    def test_get_logs(self, mock_client):
        mock_get_log = mock.MagicMock()
        mock_get_log.get_scheduler_logs.return_value = (
            ("INFO", "dask_scheduler_log1"),
            ("INFO", "dask_scheduler_log2"),
        )
        mock_get_log.get_worker_logs.return_value = {
            "worker1": (("INFO", "dask_worker1_log1"), ("INFO", "dask_worker1_log2"))
        }
        mock_client.return_value = mock_get_log
        # Create DaskJob
        djob = DaskJob(
            name="test_dj", user=self.user, label="label", scheduler=self.scheduler
        )
        expected_ret = {
            "Scheduler": '"INFO", "dask_scheduler_log1"\n"INFO", "dask_scheduler_log2"',
            "Worker-0": '"INFO", "dask_worker1_log1"\n"INFO", "dask_worker1_log2"',
        }
        ret = djob._get_logs()

        self.assertEqual(expected_ret, ret)

    @mock.patch("tethys_compute.models.dask.dask_job.log")
    def test_fail_acquire_pr_lock(self, mock_log):
        # Create DaskJob
        djob = DaskJob(
            name="test_dj", user=self.user, label="label", scheduler=self.scheduler
        )
        djob.extended_properties["processing_results"] = True
        self.assertFalse(djob._acquire_pr_lock())
        mock_log.warning.assert_called_with(
            "Unable to aquire lock. Processing results already occurring. Skipping..."
        )

    @mock.patch("django.db.models.base.Model.save")
    def test_fail_release_pr_lock(self, mock_save):
        # Create DaskJob
        djob = DaskJob(
            name="test_dj", user=self.user, label="label", scheduler=self.scheduler
        )
        djob.extended_properties["processing_results"] = True
        djob._release_pr_lock()
        self.assertFalse(djob.extended_properties["processing_results"])
        mock_save.assert_called()
