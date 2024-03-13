"""
********************************************************************************
* Name: test_DaskJobResult
* Author: nswain
* Created On: November 14, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""

from tethys_sdk.testing import TethysTestCase
from tethys_compute.models.dask.dask_scheduler import DaskScheduler
from tethys_compute.models.dask.dask_job import DaskJob
from django.contrib.auth.models import User
from unittest import mock


class DaskJobMockedResultsPropertyTests(TethysTestCase):
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
        pass

    @mock.patch("tethys_compute.models.tethys_job.TethysFunctionExtractor")
    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob.future")
    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob.client")
    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob._acquire_pr_lock")
    @mock.patch("tethys_compute.models.dask.dask_job.DaskJob._release_pr_lock")
    @mock.patch("tethys_compute.models.dask.dask_job.log")
    def test_process_result_serialize_exception(
        self, mock_log, mock_re_lock, mock_apl, mock_client, mock_future, mock_tfe
    ):
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

        # NOTE: To mock the "result" property, we must mock it on the type object, not the instance.
        # Unfortunately, this will persist for any test in the same test case that runs after this test.
        # That's why this test is pulled out in a separate test case (the other tests on "result" won't work
        # after this one runs).
        type(djob).result = mock.PropertyMock(side_effect=[Exception, "foo", "foo"])

        djob._process_results()

        # check the result
        mock_client.gather.assert_called_with(mock_future)
        mock_function.assert_called_with(mock_client.gather())
        mock_log.exception.assert_called_with("Results Serialization Error")
        mock_re_lock.assert_called()
        self.assertEqual("ERR", djob._status)
