import json
from unittest import mock

import pytest

import tethys_basemaps.jobs as jobs
from tethys_basemaps.tasks import dask_task_state


def test_run_basemap_task_inline():
    mock_func = mock.MagicMock()
    mock_handler = mock.MagicMock()

    result = jobs.run_basemap_task(
        mock_func,
        1,
        2,
        name="Test Task",
        user=None,
        result_path="/data/test.result.json",
        non_dask_result_handler=mock_handler,
        cancel_path="/data/test.cancel",
    )

    mock_func.assert_called_once_with(1, 2, cancel_path="/data/test.cancel")
    mock_handler.assert_called_once_with(mock_func.return_value)
    assert result is None


@mock.patch("tethys_compute.models.DaskJob")
@mock.patch("cloudpickle.register_pickle_by_value")
def test_run_basemap_task_dask(mock_register, mock_dask_job):
    mock_func = mock.MagicMock()
    mock_handler = mock.MagicMock()
    mock_scheduler = mock.MagicMock()
    mock_user = mock.MagicMock()
    mock_job = mock_dask_job.return_value
    mock_job._status = "PEN"

    result = jobs.run_basemap_task(
        mock_func,
        1,
        2,
        name="Test Task",
        user=mock_user,
        result_path="/data/test.result.json",
        non_dask_result_handler=mock_handler,
        dask_scheduler=mock_scheduler,
        cancel_path="/data/test.cancel",
    )

    mock_register.assert_called_once()
    mock_dask_job.assert_called_once_with(
        name="Test Task",
        user=mock_user,
        label="tethys_basemaps",
        scheduler=mock_scheduler,
        forget=True,
    )
    mock_job.save.assert_called_once()
    mock_job.client.submit.assert_called_once_with(
        mock_func,
        1,
        2,
        result_path="/data/test.result.json",
        pure=False,
        cancel_path="/data/test.cancel",
    )
    mock_job.execute.assert_called_once_with(mock_job.client.submit.return_value)
    mock_func.assert_not_called()
    mock_handler.assert_not_called()
    assert result == mock_job


@mock.patch("tethys_compute.models.DaskJob")
@mock.patch("cloudpickle.register_pickle_by_value")
def test_run_basemap_task_dask_error(mock_register, mock_dask_job):
    mock_dask_job.return_value._status = "ERR"

    with pytest.raises(RuntimeError, match='Could not submit "Test Task"'):
        jobs.run_basemap_task(
            mock.MagicMock(),
            name="Test Task",
            user=None,
            result_path="/data/test.result.json",
            non_dask_result_handler=mock.MagicMock(),
            dask_scheduler=mock.MagicMock(),
        )


@mock.patch("tethys_basemaps.jobs.os.remove")
def test_delete_safely(mock_remove):
    jobs.delete_safely("/data/test.result.json")

    mock_remove.assert_called_once_with("/data/test.result.json")


@mock.patch("tethys_basemaps.jobs.os.remove")
def test_delete_safely_no_path(mock_remove):
    jobs.delete_safely(None)

    mock_remove.assert_not_called()


@mock.patch("tethys_basemaps.jobs.os.remove", side_effect=FileNotFoundError)
def test_delete_safely_missing_file(mock_remove):
    jobs.delete_safely("/data/test.result.json")

    mock_remove.assert_called_once_with("/data/test.result.json")


def test_dask_task_state_no_key():
    mock_job = mock.MagicMock(key="")

    assert jobs._dask_task_state(mock_job) == ("unknown", None)


def test_dask_task_state_no_scheduler():
    mock_job = mock.MagicMock(key="test-key", scheduler=None)

    assert jobs._dask_task_state(mock_job) == ("unknown", None)


@mock.patch("tethys_basemaps.jobs.log")
def test_dask_task_state_no_connection(mock_log):
    mock_job = mock.MagicMock(key="test-key")
    type(mock_job.scheduler).client = mock.PropertyMock(side_effect=Exception("down"))

    assert jobs._dask_task_state(mock_job) == ("unknown", None)
    mock_log.exception.assert_called_once()


def test_dask_task_state():
    mock_job = mock.MagicMock(key="test-key")
    mock_client = mock_job.scheduler.client
    mock_client.run_on_scheduler.return_value = ["erred", "Test error"]

    result = jobs._dask_task_state(mock_job)

    mock_client.run_on_scheduler.assert_called_once_with(
        dask_task_state, key="test-key"
    )
    mock_client.close.assert_called_once()
    assert result == ("erred", "Test error")


@mock.patch("tethys_basemaps.jobs.log")
def test_dask_task_state_run_error(mock_log):
    mock_job = mock.MagicMock(key="test-key")
    mock_client = mock_job.scheduler.client
    mock_client.run_on_scheduler.side_effect = Exception("Test error")

    assert jobs._dask_task_state(mock_job) == ("unknown", None)
    mock_log.exception.assert_called_once()
    mock_client.close.assert_called_once()


def test_refresh_from_result_file_applies_result(tmp_path):
    result_path = tmp_path / "test.result.json"
    progress_path = tmp_path / "test.progress.json"
    result_path.write_text(json.dumps({"ok": True}))
    progress_path.write_text(json.dumps({"done": 1, "total": 2}))
    mock_record = mock.MagicMock(
        result_path=str(result_path), progress_path=str(progress_path)
    )
    mock_apply = mock.MagicMock()

    jobs.refresh_from_result_file(mock_record, mock_apply, "capture")

    mock_apply.assert_called_once_with({"ok": True})
    assert not result_path.exists()
    assert not progress_path.exists()


@mock.patch("tethys_basemaps.jobs._dask_task_state")
def test_refresh_from_result_file_no_job(mock_state):
    mock_record = mock.MagicMock(result_path=None, job_id=None)
    mock_apply = mock.MagicMock()

    jobs.refresh_from_result_file(mock_record, mock_apply, "capture")

    mock_apply.assert_not_called()
    mock_state.assert_not_called()


@mock.patch("tethys_basemaps.jobs._dask_task_state", return_value=("processing", None))
def test_refresh_from_result_file_still_running(mock_state):
    mock_record = mock.MagicMock(result_path=None, job_id=1)
    type(mock_record).objects = mock.MagicMock()

    jobs.refresh_from_result_file(mock_record, mock.MagicMock(), "capture")

    mock_state.assert_called_once_with(mock_record.job)
    type(mock_record).objects.filter.assert_not_called()


@mock.patch("tethys_basemaps.jobs.delete_safely")
@mock.patch(
    "tethys_basemaps.jobs._dask_task_state", return_value=("erred", "Test error")
)
def test_refresh_from_result_file_erred(mock_state, mock_delete):
    mock_record = mock.MagicMock(
        pk=1, result_path=None, progress_path="/data/test.progress.json", job_id=1
    )
    mock_objects = mock.MagicMock()
    type(mock_record).objects = mock_objects

    jobs.refresh_from_result_file(mock_record, mock.MagicMock(), "capture")

    mock_objects.filter.assert_called_once_with(pk=1, status="processing")
    mock_objects.filter.return_value.update.assert_called_once_with(
        status="failed",
        error_message="The capture job failed on the Dask worker.\nTest error",
    )
    mock_delete.assert_called_once_with("/data/test.progress.json")
    mock_record.refresh_from_db.assert_called_once()


@mock.patch("tethys_basemaps.jobs._dask_task_state", return_value=("erred", None))
def test_refresh_from_result_file_erred_no_error_text(mock_state):
    mock_record = mock.MagicMock(pk=1, result_path=None, progress_path=None, job_id=1)
    mock_objects = mock.MagicMock()
    type(mock_record).objects = mock_objects

    jobs.refresh_from_result_file(mock_record, mock.MagicMock(), "generation")

    mock_objects.filter.return_value.update.assert_called_once_with(
        status="failed",
        error_message="The generation job failed on the Dask worker.",
    )


@mock.patch("tethys_basemaps.jobs._dask_task_state", return_value=(None, None))
def test_refresh_from_result_file_finished_without_result(mock_state):
    mock_record = mock.MagicMock(pk=1, result_path=None, progress_path=None, job_id=1)
    mock_objects = mock.MagicMock()
    type(mock_record).objects = mock_objects

    jobs.refresh_from_result_file(mock_record, mock.MagicMock(), "capture")

    error_message = mock_objects.filter.return_value.update.call_args.kwargs[
        "error_message"
    ]
    assert error_message.startswith(
        "The capture job finished without writing a result file."
    )


@mock.patch("tethys_basemaps.jobs._dask_task_state")
def test_refresh_from_result_file_result_written_late(mock_state, tmp_path):
    result_path = tmp_path / "test.result.json"
    mock_record = mock.MagicMock(
        result_path=str(result_path), progress_path=None, job_id=1
    )
    mock_objects = mock.MagicMock()
    type(mock_record).objects = mock_objects
    mock_apply = mock.MagicMock()

    # The task finishes and writes its result file while the scheduler is being asked
    def finish_task(job):
        result_path.write_text(json.dumps({"ok": True}))
        return None, None

    mock_state.side_effect = finish_task

    jobs.refresh_from_result_file(mock_record, mock_apply, "capture")

    mock_apply.assert_called_once_with({"ok": True})
    mock_objects.filter.assert_not_called()


def test_cancel_dask_task_no_key():
    mock_job = mock.MagicMock(key="")

    jobs.cancel_dask_task(mock_job)

    mock_job.scheduler.client.cancel.assert_not_called()


@mock.patch("tethys_basemaps.jobs.log")
def test_cancel_dask_task_no_connection(mock_log):
    mock_job = mock.MagicMock(key="test-key")
    type(mock_job.scheduler).client = mock.PropertyMock(side_effect=Exception("down"))
