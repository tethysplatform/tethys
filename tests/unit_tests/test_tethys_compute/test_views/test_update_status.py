import unittest
from unittest import mock

import tethys_compute.views.update_status as tethys_compute_update_status


class TestUpdateStatus(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch("tethys_compute.views.update_status.TethysJob.objects.get_subclass")
    async def test_get_job(self, mock_tj):
        mock_user = mock.MagicMock(is_staff=False, is_anonymous=False)
        mock_user.has_perm.return_value = False
        await tethys_compute_update_status.get_job("job_id", mock_user)
        mock_tj.assert_called_with(id="job_id", user=mock_user)

    @mock.patch("tethys_compute.views.update_status.TethysJob.objects.get_subclass")
    async def test_get_job_staff(self, mock_tj):
        mock_user = mock.MagicMock(is_staff=True, is_anonymous=False)
        await tethys_compute_update_status.get_job("job_id", mock_user)
        mock_tj.assert_called_with(id="job_id")

    @mock.patch("tethys_compute.views.update_status.TethysJob.objects.get_subclass")
    async def test_get_job_has_permission(self, mock_tj):
        mock_user = mock.MagicMock(is_staff=False, is_anonymous=False)
        mock_user.has_perm.return_value = True
        await tethys_compute_update_status.get_job("job_id", mock_user)
        mock_tj.assert_called_with(id="job_id")

    @mock.patch("tethys_compute.views.update_status.get_anonymous_user")
    @mock.patch("tethys_compute.views.update_status.TethysJob.objects.get_subclass")
    async def test_get_job_anonymous_user(self, mock_tj, mock_get_anonymous_user):
        mock_user = mock.MagicMock(is_staff=False, is_anonymous=True)
        mock_user.has_perm.return_value = False
        mock_anonymous_user = mock.MagicMock(is_staff=False)
        mock_anonymous_user.has_perm.return_value = False
        mock_get_anonymous_user.return_value = mock_anonymous_user
        await tethys_compute_update_status.get_job("job_id", mock_user)
        mock_get_anonymous_user.assert_called_once()
        mock_tj.assert_called_with(id="job_id", user=mock_anonymous_user)

    @mock.patch("tethys_compute.views.update_status.logger")
    @mock.patch("tethys_compute.views.update_status.JsonResponse")
    @mock.patch("tethys_compute.views.update_status.TethysJob")
    async def test_update_job_status(self, mock_tethysjob, mock_json_response, _):
        mock_request = mock.MagicMock(GET={})
        mock_job_id = mock.MagicMock()
        mock_job1 = mock.MagicMock()
        mock_job1.status = True
        mock_tethysjob.objects.get_subclass.return_value = mock_job1

        await tethys_compute_update_status.update_job_status(mock_request, mock_job_id)
        mock_tethysjob.objects.get_subclass.assert_called_once_with(id=mock_job_id)
        mock_json_response.assert_called_once_with({"success": True})

    @mock.patch("tethys_compute.views.update_status.create_task")
    @mock.patch("tethys_compute.views.update_status.logger")
    @mock.patch("tethys_compute.views.update_status.JsonResponse")
    async def test_update_job_status_with_delay(
        self, mock_json_response, mock_log, mock_ct
    ):
        mock_request = mock.MagicMock(GET={"delay": "1"})
        mock_job_id = mock.MagicMock()

        await tethys_compute_update_status.update_job_status(mock_request, mock_job_id)
        mock_json_response.assert_called_once_with({"success": "scheduled"})
        mock_log.debug.assert_called_once()
        mock_ct.assert_called_with(
            tethys_compute_update_status._update_job_status, mock_job_id, delay=1
        )

    @mock.patch("tethys_compute.views.update_status.create_task")
    @mock.patch("tethys_compute.views.update_status.logger")
    @mock.patch("tethys_compute.views.update_status.JsonResponse")
    async def test_update_job_status_with_delay_exception(
        self, mock_json_response, mock_log, mock_ct
    ):
        mock_request = mock.MagicMock(GET={"delay": "1"})
        mock_job_id = mock.MagicMock()
        mock_ct.side_effect = Exception

        await tethys_compute_update_status.update_job_status(mock_request, mock_job_id)
        mock_json_response.assert_called_once_with({"success": False})
        mock_log.warning.assert_called_once()

    @mock.patch("tethys_compute.views.update_status.logger")
    @mock.patch("tethys_compute.views.update_status.JsonResponse")
    @mock.patch("tethys_compute.views.update_status.TethysJob")
    async def test_update_job_statusException(
        self, mock_tethysjob, mock_json_response, mock_log
    ):
        mock_request = mock.MagicMock(GET={})
        mock_job_id = mock.MagicMock()
        mock_tethysjob.objects.get_subclass.side_effect = Exception

        await tethys_compute_update_status.update_job_status(mock_request, mock_job_id)
        mock_tethysjob.objects.get_subclass.assert_called_once_with(id=mock_job_id)
        mock_json_response.assert_called_once_with({"success": False})
        mock_log.warning.assert_called_once()

    @mock.patch("tethys_compute.views.update_status.JsonResponse")
    @mock.patch("tethys_compute.views.update_status.DaskJob")
    def test_update_dask_job_status(self, mock_daskjob, mock_json_response):
        mock_request = mock.MagicMock()
        mock_job_key = mock.MagicMock()
        mock_job1 = mock.MagicMock()
        mock_job1.status = True
        mock_job2 = mock.MagicMock()
        mock_daskjob.objects.filter.return_value = [mock_job1, mock_job2]

        # Call the method
        tethys_compute_update_status.update_dask_job_status(mock_request, mock_job_key)

        # check results
        mock_daskjob.objects.filter.assert_called_once_with(key=mock_job_key)
        mock_json_response.assert_called_once_with({"success": True})

    @mock.patch("tethys_compute.views.update_status.JsonResponse")
    @mock.patch("tethys_compute.views.update_status.DaskJob")
    def test_update_dask_job_statusException(self, mock_daskjob, mock_json_response):
        mock_request = mock.MagicMock()
        mock_job_key = mock.MagicMock()
        mock_daskjob.objects.filter.side_effect = Exception

        tethys_compute_update_status.update_dask_job_status(mock_request, mock_job_key)
        mock_daskjob.objects.filter.assert_called_once_with(key=mock_job_key)
        mock_json_response.assert_called_once_with({"success": False})
