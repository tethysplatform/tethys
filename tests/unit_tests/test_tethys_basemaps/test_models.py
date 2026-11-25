from unittest import mock

import pytest

import tethys_basemaps.mbtiles_utilities as mbtiles
from tethys_basemaps import models
from tethys_basemaps.models import (
    BasemapCapture,
    BasemapImage,
    PortalBasemap,
    PortalBasemapSource,
    _delete_basemap_files,
    remove_files,
)

PNG = b"\x89PNG\r\n\x1a\ntest png"


def test_original_basemap_upload_path():
    image = BasemapImage(name="Test Image")

    result = models.original_basemap_upload_path(image, "test.png")

    assert result == "basemaps/images/original/Test Image/test.png"


def test_generated_basemap_upload_path():
    image = BasemapImage(name="Test Image")

    result = models.generated_basemap_upload_path(image, "test.tif")

    assert result == "basemaps/images/generated/Test Image/test.tif"


def test_basemap_capture_upload_path():
    assert models.basemap_capture_upload_path(None, "test.mbtiles") == (
        "basemaps/captures/test.mbtiles"
    )


def test_portal_basemap_str():
    assert str(PortalBasemap(name="Test Basemap")) == "Test Basemap"


def test_portal_basemap_source_format_options():
    source = PortalBasemapSource(
        name="Test Source",
        basemap_type="XYZ",
        options={"url": "https://example.com/{z}/{x}/{y}.png"},
    )

    assert source.format_options() == {
        "XYZ": {
            "url": "https://example.com/{z}/{x}/{y}.png",
            "control_label": "Test Source",
        }
    }


def test_portal_basemap_source_format_options_no_options():
    source = PortalBasemapSource(name="Test Source", basemap_type="ESRI", options=None)

    assert source.format_options() == {"ESRI": {"control_label": "Test Source"}}


def test_portal_basemap_source_as_basemap():
    source = PortalBasemapSource(name="Test Source", basemap_type="CartoDB")

    assert source.as_basemap() == source.format_options()


@mock.patch("django.core.files.storage.default_storage")
def test_basemap_image_unique_output_name(mock_storage):
    image = BasemapImage(name="Test Image", source_file="original/test.png")
    mock_storage.exists.return_value = False

    result = image.unique_output_name()

    assert result == "basemaps/images/generated/Test Image/test_cog_run_1.tif"


@mock.patch("django.core.files.storage.default_storage")
def test_basemap_image_unique_output_name_skips_used_run(mock_storage):
    image = BasemapImage(name="Test Image", source_file="original/test.png")
    mock_storage.exists.side_effect = lambda name: name.endswith("_run_1.tif.cancel")

    result = image.unique_output_name()

    assert result == "basemaps/images/generated/Test Image/test_cog_run_2.tif"


def test_basemap_image_as_basemap_not_ready():
    image = BasemapImage(name="Test Image", status=BasemapImage.StatusChoices.PENDING)

    with pytest.raises(ValueError, match='The "Test Image" image is not ready.'):
        image.as_basemap()


@mock.patch("django.urls.reverse", return_value="/basemaps/image/1/0/0/0")
def test_basemap_image_as_basemap(mock_reverse):
    image = BasemapImage(
        pk=1,
        name="Test Image",
        status=BasemapImage.StatusChoices.READY,
        attribution="Test Attribution",
        min_x=0,
        min_y=0,
        max_x=1,
        max_y=1,
    )
    result = image.as_basemap()

    options = result["XYZ"]
    assert str(options["url"]) == "/basemaps/image/1/{z}/{x}/{y}"
    assert options["control_label"] == "Test Image"
    assert options["minZoom"] == 0
    assert options["maxZoom"] == 22
    assert options["attributions"] == "Test Attribution"
    assert options["layer_extent"] == [0, 0, 1, 1]
    mock_reverse.assert_called_once_with(
        "basemaps:image_tile", kwargs={"image_id": 1, "z": 0, "x": 0, "y": 0}
    )


@mock.patch("django.urls.reverse", return_value="/unexpected/")
def test_basemap_image_as_basemap_unexpected_url(mock_reverse):
    image = BasemapImage(
        pk=1, name="Test Image", status=BasemapImage.StatusChoices.READY
    )

    result = image.as_basemap()

    assert "attributions" not in result["XYZ"]
    assert "layer_extent" not in result["XYZ"]
    with pytest.raises(ValueError, match="Unexpected tile URL shape: /unexpected/"):
        assert str(result["XYZ"]["url"])


@mock.patch("tethys_basemaps.models.refresh_from_result_file")
def test_basemap_image_refresh_status_processing(mock_refresh):
    image = BasemapImage(status=BasemapImage.StatusChoices.PROCESSING)

    result = image.refresh_status()

    mock_refresh.assert_called_once_with(
        image, image.apply_generation_result, "generation"
    )
    assert result == "processing"


@mock.patch("tethys_basemaps.models.refresh_from_result_file")
def test_basemap_image_refresh_status_ready(mock_refresh):
    image = BasemapImage(status=BasemapImage.StatusChoices.READY)

    assert image.refresh_status() == "ready"
    mock_refresh.assert_not_called()


def test_basemap_image_paths_no_file():
    image = BasemapImage()

    assert image.result_path is None
    assert image.cancel_path is None


def test_basemap_image_paths(settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    image = BasemapImage(generated_file="generated/test.tif")

    assert image.result_path == str(tmp_path / "generated/test.tif.result.json")
    assert image.cancel_path == str(tmp_path / "generated/test.tif.cancel")


@mock.patch("tethys_basemaps.jobs.run_basemap_task", return_value=None)
@mock.patch.object(
    BasemapImage, "unique_output_name", return_value="generated/test_cog_run_1.tif"
)
def test_basemap_image_start_generation(
    mock_unique_output_name, mock_run, db, settings, tmp_path
):
    settings.MEDIA_ROOT = str(tmp_path)
    image = BasemapImage.objects.create(
        name="Test Image",
        source_file="original/test.png",
        georeference_bounds=[0, 0, 1, 1],
        georeference_epsg=4326,
    )
    mock_user = mock.MagicMock()

    image.start_generation(mock_user)

    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert args[1:] == (
        image.pk,
        str(tmp_path / "original/test.png"),
        str(tmp_path / "generated/test_cog_run_1.tif"),
    )
    assert kwargs["georeference_bounds"] == [0, 0, 1, 1]
    assert kwargs["georeference_epsg"] == 4326
    assert kwargs["user"] == mock_user
    assert kwargs["dask_scheduler"] is None
    assert kwargs["cancel_path"] == str(
        tmp_path / "generated/test_cog_run_1.tif.cancel"
    )
    assert image.status == BasemapImage.StatusChoices.PROCESSING
    assert image.generated_file.name == "generated/test_cog_run_1.tif"


def test_basemap_image_start_generation_already_processing(db):
    image = BasemapImage.objects.create(
        name="Test Image", status=BasemapImage.StatusChoices.PROCESSING
    )

    with pytest.raises(ValueError, match="is already processing"):
        image.start_generation(mock.MagicMock())


@mock.patch(
    "tethys_basemaps.jobs.run_basemap_task", side_effect=Exception("Test error")
)
@mock.patch.object(
    BasemapImage, "unique_output_name", return_value="generated/test_cog_run_1.tif"
)
def test_basemap_image_start_generation_error(
    mock_unique_output_name, mock_run, db, settings, tmp_path
):
    settings.MEDIA_ROOT = str(tmp_path)
    image = BasemapImage.objects.create(
        name="Test Image", source_file="original/test.png"
    )

    with pytest.raises(Exception, match="Test error"):
        image.start_generation(mock.MagicMock())

    image.refresh_from_db()
    assert image.status == BasemapImage.StatusChoices.FAILED
    assert image.error_message == "Test error"


@mock.patch("tethys_basemaps.jobs.run_basemap_task")
@mock.patch.object(
    BasemapImage, "unique_output_name", return_value="generated/test_cog_run_1.tif"
)
@mock.patch("tethys_basemaps.models.BasemapImage.objects.filter")
def test_basemap_image_start_generation_saves_job(
    mock_filter, mock_unique_output_name, mock_run, db, settings, tmp_path
):
    settings.MEDIA_ROOT = str(tmp_path)
    image = BasemapImage.objects.create(
        name="Test Image", source_file="original/test.png"
    )
    mock_job = mock.MagicMock()
    mock_run.return_value = mock_job

    image.start_generation(mock.MagicMock())

    mock_filter.assert_called_once_with(pk=image.pk)
    mock_filter.return_value.update.assert_called_once_with(job=mock_job)


def test_basemap_image_apply_generation_result(db, settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    image = BasemapImage.objects.create(
        name="Test Image", status=BasemapImage.StatusChoices.PROCESSING
    )
    result = {
        "ok": True,
        "output_path": str(tmp_path / "generated/test.tif"),
        "bounds": [0, 0, 1, 1],
        "srs": "3857",
        "wkt": "TEST WKT",
        "source_epsg": 4326,
    }

    image.apply_generation_result(result)

    assert image.status == BasemapImage.StatusChoices.READY
    assert image.generated_file.name == "generated/test.tif"
    assert [image.min_x, image.min_y, image.max_x, image.max_y] == [0, 0, 1, 1]
    assert image.srs == "3857"
    assert image.wkt == "TEST WKT"
    assert image.georeference_epsg == 4326
    assert image.error_message == ""


def test_basemap_image_apply_generation_result_keeps_georeference_epsg(
    db, settings, tmp_path
):
    settings.MEDIA_ROOT = str(tmp_path)
    image = BasemapImage.objects.create(
        name="Test Image",
        status=BasemapImage.StatusChoices.PROCESSING,
        georeference_epsg=26912,
    )
    result = {
        "ok": True,
        "output_path": str(tmp_path / "generated/test.tif"),
        "bounds": [0, 0, 1, 1],
        "srs": "3857",
        "wkt": "TEST WKT",
        "source_epsg": 4326,
    }

    image.apply_generation_result(result)

    assert image.georeference_epsg == 26912


def test_basemap_image_apply_generation_result_failed(db):
    image = BasemapImage.objects.create(
        name="Test Image", status=BasemapImage.StatusChoices.PROCESSING
    )

    image.apply_generation_result({"ok": False, "error": "Test error"})

    assert image.status == BasemapImage.StatusChoices.FAILED
    assert image.error_message == "Test error"


def test_basemap_image_apply_generation_result_not_processing(db):
    image = BasemapImage.objects.create(
        name="Test Image", status=BasemapImage.StatusChoices.CANCELLED
    )

    image.apply_generation_result({"ok": False, "error": "Test error"})

    assert image.status == BasemapImage.StatusChoices.CANCELLED


@mock.patch("tethys_basemaps.jobs.cancel_dask_task")
def test_basemap_image_stop_run_touches_cancel_flag(mock_cancel, settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    image = BasemapImage(generated_file="generated/test.tif")

    image._stop_run()

    assert (tmp_path / "generated/test.tif.cancel").exists()
    mock_cancel.assert_not_called()


@mock.patch("tethys_basemaps.jobs.cancel_dask_task")
def test_basemap_image_stop_run_no_cancel_path(mock_cancel):
    image = BasemapImage()

    image._stop_run()

    mock_cancel.assert_not_called()


@mock.patch("tethys_basemaps.jobs.cancel_dask_task")
def test_basemap_image_stop_run_cancels_dask_job(mock_cancel):
    image = BasemapImage(job_id=1)
    mock_job = mock.MagicMock()

    with mock.patch.object(
        BasemapImage, "job", new_callable=mock.PropertyMock, return_value=mock_job
    ):
        image._stop_run()

    mock_cancel.assert_called_once_with(mock_job)


def test_basemap_image_cancel_not_processing():
    image = BasemapImage(status=BasemapImage.StatusChoices.READY)

    assert image.cancel() is False


@mock.patch.object(BasemapImage, "_stop_run")
def test_basemap_image_cancel(mock_stop_run, db):
    image = BasemapImage.objects.create(
        name="Test Image", status=BasemapImage.StatusChoices.PROCESSING
    )

    with mock.patch.object(BasemapImage, "refresh_status", return_value="processing"):
        result = image.cancel("testuser")

    assert result is True
    assert image.status == BasemapImage.StatusChoices.CANCELLED
    assert image.error_message == "Cancelled by testuser."
    mock_stop_run.assert_called_once()


@mock.patch.object(BasemapImage, "_stop_run")
def test_basemap_image_cancel_no_user(mock_stop_run, db):
    image = BasemapImage.objects.create(
        name="Test Image", status=BasemapImage.StatusChoices.PROCESSING
    )

    with mock.patch.object(BasemapImage, "refresh_status", return_value="processing"):
        result = image.cancel()

    assert result is True
    assert image.error_message == "Cancelled."
    mock_stop_run.assert_called_once()


@mock.patch.object(BasemapImage, "_stop_run")
def test_basemap_image_cancel_finished_just_now(mock_stop_run, db):
    image = BasemapImage.objects.create(
        name="Test Image", status=BasemapImage.StatusChoices.READY
    )

    with mock.patch.object(BasemapImage, "refresh_status", return_value="processing"):
        result = image.cancel()

    assert result is False
    assert image.status == BasemapImage.StatusChoices.READY
    mock_stop_run.assert_not_called()


@mock.patch("tethys_basemaps.models.os.rmdir", side_effect=OSError)
@mock.patch("tethys_basemaps.models.remove_files")
@mock.patch.object(BasemapImage, "_stop_run")
def test_basemap_image_delete_files(
    mock_stop_run, mock_remove_files, mock_rmdir, settings, tmp_path
):
    settings.MEDIA_ROOT = str(tmp_path)
    image = BasemapImage(
        status=BasemapImage.StatusChoices.READY,
        source_file="original/test.png",
        generated_file="generated/test.tif",
    )
    cog = str(tmp_path / "generated/test.tif")

    image.delete_files()

    mock_stop_run.assert_not_called()
    mock_remove_files.assert_called_once_with(
        str(tmp_path / "original/test.png"),
        cog,
        cog + ".partial",
        cog + ".result.json",
        cog + ".cancel",
    )
    mock_rmdir.assert_has_calls(
        [mock.call(str(tmp_path / "original")), mock.call(str(tmp_path / "generated"))],
        any_order=True,
    )


@mock.patch("tethys_basemaps.models.os.rmdir")
@mock.patch("tethys_basemaps.models.remove_files")
@mock.patch.object(BasemapImage, "_stop_run")
def test_basemap_image_delete_files_processing(
    mock_stop_run, mock_remove_files, mock_rmdir, settings, tmp_path
):
    settings.MEDIA_ROOT = str(tmp_path)
    image = BasemapImage(
        status=BasemapImage.StatusChoices.PROCESSING,
        job_id=1,
        generated_file="generated/test.tif",
    )
    cog = str(tmp_path / "generated/test.tif")

    image.delete_files()

    mock_stop_run.assert_called_once()
    mock_remove_files.assert_called_once_with(
        cog, cog + ".partial", cog + ".result.json"
    )
    mock_rmdir.assert_called_once_with(str(tmp_path / "generated"))


@mock.patch("tethys_basemaps.models.os.rmdir")
@mock.patch("tethys_basemaps.models.remove_files")
def test_basemap_image_delete_files_no_files(mock_remove_files, mock_rmdir):
    image = BasemapImage(status=BasemapImage.StatusChoices.READY)

    image.delete_files()

    mock_remove_files.assert_called_once_with()
    mock_rmdir.assert_not_called()


def test_basemap_capture_tile_content_type():
    assert BasemapCapture(tile_format="jpg").tile_content_type == "image/jpeg"
    assert BasemapCapture(tile_format="tiff").tile_content_type == (
        "application/octet-stream"
    )


def test_basemap_capture_paths_no_file():
    capture = BasemapCapture()

    assert capture.result_path is None
    assert capture.progress_path is None
    assert capture.cancel_path is None


def test_basemap_capture_paths(settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    capture = BasemapCapture(mbtiles_file="captures/test.mbtiles")

    assert capture.result_path == str(tmp_path / "captures/test.mbtiles.result.json")
    assert capture.progress_path == str(
        tmp_path / "captures/test.mbtiles.progress.json"
    )
    assert capture.cancel_path == str(tmp_path / "captures/test.mbtiles.cancel")


@mock.patch("django.core.files.storage.default_storage")
def test_basemap_capture_unique_output_name(mock_storage):
    mock_storage.get_available_name.side_effect = lambda name: name
    mock_storage.exists.return_value = False

    result = BasemapCapture.unique_output_name("Test Capture")

    assert result == "basemaps/captures/test-capture.mbtiles"


@mock.patch("django.utils.crypto.get_random_string", return_value="abcdefg")
@mock.patch("django.core.files.storage.default_storage")
def test_basemap_capture_unique_output_name_skips_used_name(
    mock_storage, mock_random_string
):
    mock_storage.get_available_name.side_effect = lambda name: name
    mock_storage.exists.side_effect = lambda name: name == (
        "basemaps/captures/test-capture.mbtiles.cancel"
    )

    result = BasemapCapture.unique_output_name("Test Capture")

    assert result == "basemaps/captures/test-capture_abcdefg.mbtiles"


@mock.patch("django.core.files.storage.default_storage")
def test_basemap_capture_unique_output_name_no_slug(mock_storage):
    mock_storage.get_available_name.side_effect = lambda name: name
    mock_storage.exists.return_value = False

    assert (
        BasemapCapture.unique_output_name("!!!") == "basemaps/captures/basemap.mbtiles"
    )


@mock.patch.object(BasemapCapture, "save")
def test_basemap_capture_apply_build_result(mock_save, settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    capture = BasemapCapture(status=BasemapCapture.StatusChoices.PROCESSING)

    capture.apply_build_result(
        {
            "ok": True,
            "output_path": str(tmp_path / "captures/test.mbtiles"),
            "tile_format": "jpg",
        }
    )

    assert capture.mbtiles_file.name == "captures/test.mbtiles"
    assert capture.tile_format == "jpg"
    assert capture.status == BasemapCapture.StatusChoices.READY
    assert capture.error_message == ""
    mock_save.assert_called_once()


@mock.patch.object(BasemapCapture, "save")
def test_basemap_capture_apply_build_result_failed(mock_save):
    capture = BasemapCapture(status=BasemapCapture.StatusChoices.PROCESSING)

    capture.apply_build_result({"ok": False, "error": "Test error"})

    assert capture.status == BasemapCapture.StatusChoices.FAILED
    assert capture.error_message == "Test error"
    mock_save.assert_called_once()


@mock.patch("tethys_basemaps.models.refresh_from_result_file")
def test_basemap_capture_refresh_status_processing(mock_refresh):
    capture = BasemapCapture(status=BasemapCapture.StatusChoices.PROCESSING)

    result = capture.refresh_status()

    mock_refresh.assert_called_once_with(capture, capture.apply_build_result, "capture")
    assert result == "processing"


@mock.patch("tethys_basemaps.models.refresh_from_result_file")
def test_basemap_capture_refresh_status_ready(mock_refresh):
    capture = BasemapCapture(status=BasemapCapture.StatusChoices.READY)

    assert capture.refresh_status() == "ready"
    mock_refresh.assert_not_called()


@mock.patch("tethys_basemaps.jobs.cancel_dask_task")
def test_basemap_capture_cancel(mock_cancel_dask_task, db, settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    capture = BasemapCapture.objects.create(
        name="Test Capture",
        min_zoom=0,
        max_zoom=1,
        status=BasemapCapture.StatusChoices.PROCESSING,
        mbtiles_file="captures/test.mbtiles",
    )

    result = capture.cancel("testuser")

    assert result is True
    assert capture.status == BasemapCapture.StatusChoices.CANCELLED
    assert capture.error_message == "Cancelled by testuser."
    assert (tmp_path / "captures/test.mbtiles.cancel").exists()
    mock_cancel_dask_task.assert_not_called()


def test_basemap_capture_cancel_no_user(db, settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    capture = BasemapCapture.objects.create(
        name="Test Capture",
        min_zoom=0,
        max_zoom=1,
        status=BasemapCapture.StatusChoices.PROCESSING,
        mbtiles_file="captures/test.mbtiles",
    )

    capture.cancel()

    assert capture.error_message == "Cancelled."


def test_basemap_capture_cancel_already_finished(db):
    capture = BasemapCapture.objects.create(
        name="Test Capture",
        min_zoom=0,
        max_zoom=1,
        status=BasemapCapture.StatusChoices.READY,
    )

    assert capture.cancel() is False
    assert capture.status == BasemapCapture.StatusChoices.READY


def test_basemap_capture_cancel_finished_just_now(db):
    capture = BasemapCapture.objects.create(
        name="Test Capture",
        min_zoom=0,
        max_zoom=1,
        status=BasemapCapture.StatusChoices.READY,
    )
    with mock.patch.object(BasemapCapture, "refresh_status", return_value="processing"):
        result = capture.cancel()

    assert result is False
    assert capture.status == BasemapCapture.StatusChoices.READY


@mock.patch("tethys_basemaps.jobs.cancel_dask_task")
def test_basemap_capture_cancel_with_job(mock_cancel_dask_task, db, settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    capture = BasemapCapture.objects.create(
        name="Test Capture",
        min_zoom=0,
        max_zoom=1,
        status=BasemapCapture.StatusChoices.PROCESSING,
        mbtiles_file="captures/test.mbtiles",
    )
    capture.job_id = 1
    mock_job = mock.MagicMock(key=None)

    with mock.patch.object(
        BasemapCapture, "job", new_callable=mock.PropertyMock, return_value=mock_job
    ):
        result = capture.cancel("testuser")

    assert result is True
    assert capture.status == BasemapCapture.StatusChoices.CANCELLED
    mock_cancel_dask_task.assert_called_once_with(mock_job)


def test_basemap_capture_restart_problem_not_cancelled():
    capture = BasemapCapture(status=BasemapCapture.StatusChoices.READY)

    assert capture.restart_problem() == "Only a cancelled capture can be restarted."


def test_basemap_capture_restart_problem_browser_capture():
    capture = BasemapCapture(
        status=BasemapCapture.StatusChoices.CANCELLED, downloaded_on_server=False
    )

    assert capture.restart_problem().startswith(
        "Only captures downloaded on the server can be restarted."
    )


def test_basemap_capture_restart_problem_source_deleted():
    capture = BasemapCapture(
        status=BasemapCapture.StatusChoices.CANCELLED, downloaded_on_server=True
    )

    assert capture.restart_problem() == (
        "The basemap this capture was downloaded from no longer exists."
    )


def test_basemap_capture_restart_problem_none():
    capture = BasemapCapture(
        status=BasemapCapture.StatusChoices.CANCELLED,
        downloaded_on_server=True,
        source_id=1,
    )

    assert capture.restart_problem() is None


def test_basemap_capture_as_basemap_not_ready():
    capture = BasemapCapture(
        name="Test Capture", status=BasemapCapture.StatusChoices.PROCESSING
    )

    with pytest.raises(ValueError, match='The "Test Capture" capture is not ready.'):
        capture.as_basemap()


@mock.patch("django.urls.reverse", return_value="/basemaps/capture/1/0/0/0")
def test_basemap_capture_as_basemap(mock_reverse):
    capture = BasemapCapture(
        pk=1,
        name="Test Capture",
        status=BasemapCapture.StatusChoices.READY,
        attribution="Test Attribution",
        min_zoom=2,
        max_zoom=10,
        min_x=0,
        min_y=0,
        max_x=1,
        max_y=1,
    )

    result = capture.as_basemap()

    assert str(result["XYZ"]["url"]) == "/basemaps/capture/1/{z}/{x}/{y}"
    assert result["XYZ"]["control_label"] == "Test Capture"
    assert result["XYZ"]["minZoom"] == 2
    assert result["XYZ"]["maxZoom"] == 10
    assert result["XYZ"]["attributions"] == "Test Attribution"
    assert result["XYZ"]["layer_extent"] == [0, 0, 1, 1]
    mock_reverse.assert_called_once_with(
        "basemaps:capture_tile", kwargs={"capture_id": 1, "z": 0, "x": 0, "y": 0}
    )


@mock.patch("django.urls.reverse", return_value="/unexpected/")
def test_basemap_capture_as_basemap_unexpected_url(mock_reverse):
    capture = BasemapCapture(
        pk=1,
        name="Test Capture",
        status=BasemapCapture.StatusChoices.READY,
        min_zoom=0,
        max_zoom=1,
    )

    result = capture.as_basemap()

    assert "attributions" not in result["XYZ"]
    assert "layer_extent" not in result["XYZ"]
    with pytest.raises(ValueError, match="Unexpected tile URL shape: /unexpected/"):
        assert str(result["XYZ"]["url"])


def test_basemap_capture_get_tile(settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    (tmp_path / "captures").mkdir()
    conn = mbtiles.create_mbtiles(str(tmp_path / "captures/test.mbtiles"))
    mbtiles.insert_tile(conn, 1, 0, 1, PNG)
    conn.commit()
    conn.close()
    capture = BasemapCapture(
        status=BasemapCapture.StatusChoices.READY, mbtiles_file="captures/test.mbtiles"
    )

    assert capture.get_tile(1, 0, 1) == PNG
    assert capture.get_tile(1, 1, 1) is None


def test_basemap_capture_get_tile_not_ready():
    capture = BasemapCapture(
        status=BasemapCapture.StatusChoices.PROCESSING,
        mbtiles_file="captures/test.mbtiles",
    )

    assert capture.get_tile(0, 0, 0) is None


def test_basemap_capture_get_tile_no_file():
    capture = BasemapCapture(status=BasemapCapture.StatusChoices.READY)

    assert capture.get_tile(0, 0, 0) is None


@mock.patch("tethys_basemaps.models.os.remove")
def test_remove_files(mock_remove):
    path1 = "file1"
    path2 = "path/to/file2"
    remove_files(path1, path2)
    mock_remove.assert_has_calls([mock.call(path1), mock.call(path2)], any_order=True)
    assert mock_remove.call_count == 2


@mock.patch("tethys_basemaps.models.remove_files")
def test_basemap_capture_delete_files_no_file(mock_remove_files):
    capture = BasemapCapture()

    capture.delete_files()

    mock_remove_files.assert_not_called()


@mock.patch("tethys_basemaps.models.remove_files")
def test_basemap_capture_delete_files(mock_remove_files, settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    capture = BasemapCapture(
        status=BasemapCapture.StatusChoices.READY,
        mbtiles_file="captures/test.mbtiles",
    )
    base = str(tmp_path / "captures/test.mbtiles")

    capture.delete_files()

    mock_remove_files.assert_called_once_with(
        base, *(base + s for s in BasemapCapture.RUN_SUFFIXES)
    )


@mock.patch("tethys_basemaps.jobs.cancel_dask_task")
@mock.patch("tethys_basemaps.models.remove_files")
def test_basemap_capture_delete_files_processing(
    mock_remove_files, mock_cancel_dask_task, settings, tmp_path
):
    settings.MEDIA_ROOT = str(tmp_path)
    (tmp_path / "captures").mkdir()
    capture = BasemapCapture(
        status=BasemapCapture.StatusChoices.PROCESSING,
        job_id=1,
        mbtiles_file="captures/test.mbtiles",
    )
    mock_job = mock.MagicMock()

    with mock.patch.object(
        BasemapCapture, "job", new_callable=mock.PropertyMock, return_value=mock_job
    ):
        capture.delete_files()

    assert (tmp_path / "captures/test.mbtiles.cancel").exists()
    mock_cancel_dask_task.assert_called_once_with(mock_job)
    mock_remove_files.assert_called_once_with(capture.result_path)


@mock.patch("tethys_basemaps.models.transaction.on_commit")
def test_delete_basemap_files(mock_on_commit):
    instance = mock.MagicMock()

    _delete_basemap_files(BasemapImage, instance)

    mock_on_commit.assert_called_once_with(instance.delete_files)
