import io
import json
from unittest import mock

from rasterio.enums import ColorInterp

from tethys_basemaps import views
from tethys_basemaps.capture_sources import BrowserOnlySource
from tethys_basemaps.models import BasemapCapture, BasemapImage, PortalBasemap
from tethys_compute.models import DaskScheduler
from tethys_services.models import SecureMapService

UPLOAD_POST = {
    "index": json.dumps([[0, 0, 0, 10]]),
    "bbox": "0,0,1,1",
    "name": "Test Capture",
    "source": "",
}

SERVER_PLAN = {
    "name": "Test Capture",
    "source": "Test Source",
    "bbox": [0, 0, 1, 1],
    "min_zoom": 0,
    "max_zoom": 1,
    "tile_size": 256,
    "dask_scheduler": 1,
}


@mock.patch("tethys_basemaps.views._tile_style", return_value={"bands": [1]})
@mock.patch("large_image_source_rasterio.open")
def test_open_tile_source_with_style(mock_rio_open, mock_tile_style):
    views._open_tile_source.cache_clear()

    result = views._open_tile_source("/data/test.tif", 1.0)

    mock_rio_open.assert_called_once_with(
        "/data/test.tif",
        projection="EPSG:3857",
        encoding="PNG",
        style=json.dumps({"bands": [1]}),
    )
    assert result == mock_rio_open.return_value


@mock.patch("tethys_basemaps.views._tile_style", return_value=None)
@mock.patch("large_image_source_rasterio.open")
def test_open_tile_source_no_style(mock_rio_open, mock_tile_style):
    views._open_tile_source.cache_clear()

    views._open_tile_source("/data/test.tif", 1.0)

    mock_rio_open.assert_called_once_with(
        "/data/test.tif", projection="EPSG:3857", encoding="PNG"
    )


@mock.patch("tethys_basemaps.views._open_tile_source")
@mock.patch("tethys_basemaps.views.os.path.getmtime", return_value=123.0)
def test_get_tile_source(mock_getmtime, mock_open_tile_source):
    result = views._get_tile_source("/data/test.tif")

    mock_open_tile_source.assert_called_once_with("/data/test.tif", 123.0)
    assert result == mock_open_tile_source.return_value


@mock.patch("rasterio.open")
def test_tile_style(mock_rasterio_open):
    mock_dataset = mock_rasterio_open.return_value.__enter__.return_value
    mock_dataset.colorinterp = [
        ColorInterp.red,
        ColorInterp.green,
        ColorInterp.blue,
        ColorInterp.alpha,
    ]

    result = views._tile_style("/data/test.tif")

    assert result == {
        "bands": [
            {"band": 1, "palette": "#f00", "min": 0, "max": 255},
            {"band": 2, "palette": "#0f0", "min": 0, "max": 255},
            {"band": 3, "palette": "#00f", "min": 0, "max": 255},
            {
                "band": 4,
                "palette": ["#ffffff00", "#ffffffff"],
                "min": 0,
                "max": 255,
                "composite": "multiply",
            },
        ]
    }


@mock.patch("rasterio.open")
def test_tile_style_no_color_bands(mock_rasterio_open):
    mock_dataset = mock_rasterio_open.return_value.__enter__.return_value
    mock_dataset.colorinterp = [ColorInterp.gray]

    assert views._tile_style("/data/test.tif") is None


def test_capture_layer():
    result = views._capture_layer(
        mock.MagicMock(), ["https://test/{z}/{x}/{y}"], {}, None
    )

    assert result == {
        "basemap_type": "xyz",
        "urls": ["https://test/{z}/{x}/{y}"],
        "opacity": 1,
    }


def test_capture_layer_headers_and_rate():
    result = views._capture_layer(
        mock.MagicMock(),
        ["https://test/{z}/{x}/{y}"],
        {"Authorization": "Bearer t"},
        20,
    )

    assert result["headers"] == {"Authorization": "Bearer t"}
    assert result["fetch"] == {"max_requests_per_second": 20}


def test_capture_layer_secure_source():
    source = SecureMapService(name="Test Secure")

    result = views._capture_layer(source, ["https://test/wms?BBOX={bbox}"], {}, 20)

    assert result["fetch"] == {
        **views.SECURE_CAPTURE_FETCH,
        "max_requests_per_second": 20,
    }
    assert views.SECURE_CAPTURE_FETCH["max_requests_per_second"] == 50  # not changed


def test_concurrency_for(settings):
    settings.BASEMAP_CAPTURE_CONCURRENCY = 16

    assert views._concurrency_for(None) == 16
    assert views._concurrency_for(1) == 2
    assert views._concurrency_for(50) == 5
    assert views._concurrency_for(1000) == 16


@mock.patch("tethys_basemaps.views.BasemapImage.objects")
def test_image_tile_not_found(mock_images):
    mock_images.get.side_effect = BasemapImage.DoesNotExist

    response = views.image_tile(mock.MagicMock(), 1, 0, 0, 0)

    assert response.status_code == 404


@mock.patch("tethys_basemaps.views._get_tile_source")
@mock.patch("tethys_basemaps.views.BasemapImage.objects")
def test_image_tile(mock_images, mock_get_tile_source):
    mock_get_tile_source.return_value.getTile.return_value = b"tile bytes"

    response = views.image_tile(mock.MagicMock(), 1, 2, 3, 4)

    mock_get_tile_source.return_value.getTile.assert_called_once_with(3, 4, 2)
    assert response.status_code == 200
    assert response.content == b"tile bytes"
    assert response["Content-Type"] == "image/png"


@mock.patch("tethys_basemaps.views._get_tile_source")
@mock.patch("tethys_basemaps.views.BasemapImage.objects")
def test_image_tile_outside_image(mock_images, mock_get_tile_source):
    mock_get_tile_source.return_value.getTile.side_effect = Exception("Test error")

    response = views.image_tile(mock.MagicMock(), 1, 2, 3, 4)

    assert response.status_code == 204


@mock.patch("tethys_basemaps.views.BasemapImage.objects")
def test_original_image_not_found(mock_images):
    mock_images.get.side_effect = BasemapImage.DoesNotExist

    response = views.original_image(mock.MagicMock(), 1)

    assert response.status_code == 404


@mock.patch("tethys_basemaps.views.BasemapImage.objects")
def test_original_image_no_source_file(mock_images):
    mock_images.get.return_value.source_file = None

    response = views.original_image(mock.MagicMock(), 1)

    assert response.status_code == 404


@mock.patch("tethys_basemaps.views.BasemapImage.objects")
def test_original_image(mock_images):
    mock_image = mock_images.get.return_value
    mock_image.source_file.name = "basemaps/images/original/test/test.png"
    mock_image.source_file.open.return_value = io.BytesIO(b"image bytes")

    response = views.original_image(mock.MagicMock(), 1)

    assert response.status_code == 200
    assert response["Content-Type"] == "image/png"
    assert b"".join(response.streaming_content) == b"image bytes"


@mock.patch("tethys_basemaps.views.PortalBasemap.objects")
def test_basemap_status_not_found(mock_basemaps):
    mock_basemaps.select_related.return_value.get.side_effect = (
        PortalBasemap.DoesNotExist
    )

    response = views.basemap_status(mock.MagicMock(), 1)

    assert response.status_code == 404


@mock.patch("tethys_basemaps.views.PortalBasemap.objects")
def test_basemap_status_source(mock_basemaps):
    mock_basemap = mock_basemaps.select_related.return_value.get.return_value
    mock_basemap.basemapcapture = None
    mock_basemap.basemapimage = None

    response = views.basemap_status(mock.MagicMock(), 1)

    assert response.status_code == 404


@mock.patch("tethys_basemaps.views.PortalBasemap.objects")
def test_basemap_status_capture_progress(mock_basemaps, tmp_path):
    progress_path = tmp_path / "test.progress.json"
    progress_path.write_text(json.dumps({"done": 1, "total": 2}))
    mock_capture = (
        mock_basemaps.select_related.return_value.get.return_value.basemapcapture
    )
    mock_capture.pk = 1
    mock_capture.error_message = ""
    mock_capture.progress_path = str(progress_path)
    mock_capture.refresh_status.return_value = "processing"

    response = views.basemap_status(mock.MagicMock(), 1)

    assert json.loads(response.content) == {
        "id": 1,
        "status": "processing",
        "error": "",
        "done": 1,
        "total": 2,
    }


@mock.patch("tethys_basemaps.views.PortalBasemap.objects")
def test_basemap_status_image(mock_basemaps):
    mock_basemap = mock_basemaps.select_related.return_value.get.return_value
    mock_basemap.basemapcapture = None
    mock_image = mock_basemap.basemapimage
    mock_image.pk = 1
    mock_image.error_message = ""
    mock_image.progress_path = None
    mock_image.refresh_status.return_value = "ready"

    response = views.basemap_status(mock.MagicMock(), 1)

    assert json.loads(response.content) == {"id": 1, "status": "ready", "error": ""}


@mock.patch("tethys_basemaps.views.reverse", return_value="/test/url/")
def test_capture_response_processing(mock_reverse):
    mock_capture = mock.MagicMock(
        pk=1, status=BasemapCapture.StatusChoices.PROCESSING, error_message=""
    )
    mock_capture.name = "Test Capture"

    response = views._capture_response(mock_capture, 5)

    assert response.status_code == 202
    assert json.loads(response.content) == {
        "id": 1,
        "name": "Test Capture",
        "tiles": 5,
        "status": "processing",
        "error": "",
        "status_url": "/test/url/",
        "change_url": "/test/url/",
        "basemap_capture_list_url": "/test/url/",
    }


@mock.patch("tethys_basemaps.views.reverse", return_value="/test/url/")
def test_capture_response_ready(mock_reverse):
    mock_capture = mock.MagicMock(
        pk=1, status=BasemapCapture.StatusChoices.READY, error_message=""
    )
    mock_capture.name = "Test Capture"

    response = views._capture_response(mock_capture, 5)

    assert response.status_code == 200


def test_capture_upload_no_tiles():
    mock_request = mock.MagicMock(method="POST", FILES={}, POST=UPLOAD_POST)

    response = views.capture_upload(mock_request)

    assert response.status_code == 400
    assert response.content == b"No tiles were provided."


def test_capture_upload_invalid_bbox_value():
    mock_request = mock.MagicMock(
        method="POST",
        FILES={"tiles": mock.MagicMock(size=10)},
        POST={**UPLOAD_POST, "bbox": "a,b,c,d"},
    )

    response = views.capture_upload(mock_request)

    assert response.content == b"Invalid tile index or bbox."


def test_capture_upload_flipped_bbox():
    mock_request = mock.MagicMock(
        method="POST",
        FILES={"tiles": mock.MagicMock(size=10)},
        POST={**UPLOAD_POST, "bbox": "1,1,0,0"},
    )

    response = views.capture_upload(mock_request)

    assert response.content == b"Invalid bbox."


def test_capture_upload_empty_index():
    mock_request = mock.MagicMock(
        method="POST",
        FILES={"tiles": mock.MagicMock(size=10)},
        POST={**UPLOAD_POST, "index": "[]"},
    )

    response = views.capture_upload(mock_request)

    assert response.content == b"No tiles were provided."


def test_capture_upload_index_not_numbers():
    mock_request = mock.MagicMock(
        method="POST",
        FILES={"tiles": mock.MagicMock(size=10)},
        POST={**UPLOAD_POST, "index": json.dumps([["a", 0, 0, 10]])},
    )

    response = views.capture_upload(mock_request)

    assert response.content == b"Invalid tile index."


def test_capture_upload_index_wrong_length():
    mock_request = mock.MagicMock(
        method="POST",
        FILES={"tiles": mock.MagicMock(size=10)},
        POST={**UPLOAD_POST, "index": json.dumps([[0, 0, 0]])},
    )

    response = views.capture_upload(mock_request)

    assert response.content == b"Invalid tile index."


def test_capture_upload_index_out_of_range():
    mock_request = mock.MagicMock(
        method="POST",
        FILES={"tiles": mock.MagicMock(size=10)},
        POST={**UPLOAD_POST, "index": json.dumps([[0, 1, 0, 10]])},
    )

    response = views.capture_upload(mock_request)

    assert response.content == b"Invalid tile index."


def test_capture_upload_size_mismatch():
    mock_request = mock.MagicMock(
        method="POST", FILES={"tiles": mock.MagicMock(size=99)}, POST=UPLOAD_POST
    )

    response = views.capture_upload(mock_request)

    assert response.content == b"The tile index does not match the uploaded tiles."


def test_capture_upload_no_name():
    mock_request = mock.MagicMock(
        method="POST",
        FILES={"tiles": mock.MagicMock(size=10)},
        POST={**UPLOAD_POST, "name": "  "},
    )

    response = views.capture_upload(mock_request)

    assert response.content == b"Enter a name for the capture."


@mock.patch("tethys_basemaps.views.PortalBasemap.objects")
def test_capture_upload_name_exists(mock_basemaps):
    mock_basemaps.filter.return_value.exists.return_value = True
    mock_request = mock.MagicMock(
        method="POST", FILES={"tiles": mock.MagicMock(size=10)}, POST=UPLOAD_POST
    )

    response = views.capture_upload(mock_request)

    assert response.content == b"A basemap with this name already exists."


@mock.patch("tethys_basemaps.views._capture_response")
@mock.patch("tethys_basemaps.views.run_basemap_task", return_value=None)
@mock.patch("tethys_basemaps.views.BasemapCapture.objects")
@mock.patch(
    "tethys_basemaps.views.BasemapCapture.unique_output_name",
    return_value="basemaps/captures/test-capture.mbtiles",
)
@mock.patch("tethys_basemaps.views.default_storage")
@mock.patch("tethys_basemaps.views.PortalBasemap.objects")
def test_capture_upload(
    mock_basemaps,
    mock_storage,
    mock_unique_output_name,
    mock_captures,
    mock_run,
    mock_capture_response,
):
    mock_basemaps.filter.return_value.exists.return_value = False
    mock_storage.save.return_value = "basemaps/captures/staging/test.tiles"
    mock_storage.path.side_effect = lambda name: f"/media/{name}"
    mock_request = mock.MagicMock(
        method="POST", FILES={"tiles": mock.MagicMock(size=10)}, POST=UPLOAD_POST
    )
    mock_capture = mock_captures.create.return_value

    response = views.capture_upload(mock_request)

    mock_captures.create.assert_called_once_with(
        name="Test Capture",
        source=None,
        secure_source=None,
        status=BasemapCapture.StatusChoices.PROCESSING,
        mbtiles_file="basemaps/captures/test-capture.mbtiles",
        min_zoom=0,
        max_zoom=0,
        min_x=0.0,
        min_y=0.0,
        max_x=1.0,
        max_y=1.0,
    )
    mock_run.assert_called_once_with(
        views.build_mbtiles,
        mock_capture.pk,
        "/media/basemaps/captures/staging/test.tiles",
        [[0, 0, 0, 10]],
        [0.0, 0.0, 1.0, 1.0],
        "Test Capture",
        "",
        "/media/basemaps/captures/test-capture.mbtiles",
        name=f"Build basemap capture {mock_capture.pk}",
        user=mock_request.user,
        result_path=mock_capture.result_path,
        non_dask_result_handler=mock_capture.apply_build_result,
        cancel_path=mock_capture.cancel_path,
    )
    mock_captures.filter.return_value.update.assert_not_called()
    mock_capture.refresh_from_db.assert_called_once()
    mock_capture_response.assert_called_once_with(mock_capture, 1)
    assert response == mock_capture_response.return_value


@mock.patch("tethys_basemaps.views._capture_response")
@mock.patch("tethys_basemaps.views.run_basemap_task", return_value=None)
@mock.patch("tethys_basemaps.views.BasemapCapture.objects")
@mock.patch("tethys_basemaps.views.BasemapCapture.unique_output_name")
@mock.patch("tethys_basemaps.views.default_storage")
@mock.patch("tethys_basemaps.views.PortalBasemap.objects")
@mock.patch("tethys_basemaps.views.PortalBasemapSource.objects")
def test_capture_upload_portal_source(
    mock_sources,
    mock_basemaps,
    mock_storage,
    mock_unique_output_name,
    mock_captures,
    mock_run,
    mock_capture_response,
):
    mock_source = mock_sources.filter.return_value.first.return_value
    mock_basemaps.filter.return_value.exists.return_value = False
    mock_request = mock.MagicMock(
        method="POST",
        FILES={"tiles": mock.MagicMock(size=10)},
        POST={**UPLOAD_POST, "source": "Test Source"},
    )

    views.capture_upload(mock_request)

    mock_sources.filter.assert_called_once_with(name="Test Source")
    assert mock_captures.create.call_args.kwargs["source"] == mock_source
    assert mock_captures.create.call_args.kwargs["secure_source"] is None


@mock.patch("tethys_basemaps.views._capture_response")
@mock.patch("tethys_basemaps.views.run_basemap_task", return_value=None)
@mock.patch("tethys_basemaps.views.BasemapCapture.objects")
@mock.patch("tethys_basemaps.views.BasemapCapture.unique_output_name")
@mock.patch("tethys_basemaps.views.default_storage")
@mock.patch("tethys_basemaps.views.PortalBasemap.objects")
@mock.patch("tethys_basemaps.views.SecureMapService.objects")
@mock.patch("tethys_basemaps.views.PortalBasemapSource.objects")
def test_capture_upload_secure_source(
    mock_sources,
    mock_secure_services,
    mock_basemaps,
    mock_storage,
    mock_unique_output_name,
    mock_captures,
    mock_run,
    mock_capture_response,
):
    mock_sources.filter.return_value.first.return_value = None
    mock_secure = mock_secure_services.filter.return_value.first.return_value
    mock_basemaps.filter.return_value.exists.return_value = False
    mock_request = mock.MagicMock(
        method="POST",
        FILES={"tiles": mock.MagicMock(size=10)},
        POST={**UPLOAD_POST, "source": "Test Secure"},
    )

    views.capture_upload(mock_request)

    assert mock_captures.create.call_args.kwargs["source"] is None
    assert mock_captures.create.call_args.kwargs["secure_source"] == mock_secure


@mock.patch("tethys_basemaps.views._capture_response")
@mock.patch("tethys_basemaps.views.run_basemap_task")
@mock.patch("tethys_basemaps.views.BasemapCapture.objects")
@mock.patch("tethys_basemaps.views.BasemapCapture.unique_output_name")
@mock.patch("tethys_basemaps.views.default_storage")
@mock.patch("tethys_basemaps.views.PortalBasemap.objects")
def test_capture_upload_with_job(
    mock_basemaps,
    mock_storage,
    mock_unique_output_name,
    mock_captures,
    mock_run,
    mock_capture_response,
):
    mock_basemaps.filter.return_value.exists.return_value = False
    mock_request = mock.MagicMock(
        method="POST", FILES={"tiles": mock.MagicMock(size=10)}, POST=UPLOAD_POST
    )
    mock_capture = mock_captures.create.return_value

    views.capture_upload(mock_request)

    mock_captures.filter.assert_called_once_with(pk=mock_capture.pk)
    mock_captures.filter.return_value.update.assert_called_once_with(
        job=mock_run.return_value
    )


@mock.patch("tethys_basemaps.views._capture_response")
@mock.patch(
    "tethys_basemaps.views.run_basemap_task", side_effect=Exception("Test error")
)
@mock.patch("tethys_basemaps.views.BasemapCapture.objects")
@mock.patch("tethys_basemaps.views.BasemapCapture.unique_output_name")
@mock.patch("tethys_basemaps.views.default_storage")
@mock.patch("tethys_basemaps.views.PortalBasemap.objects")
def test_capture_upload_build_error(
    mock_basemaps,
    mock_storage,
    mock_unique_output_name,
    mock_captures,
    mock_run,
    mock_capture_response,
):
    mock_basemaps.filter.return_value.exists.return_value = False
    mock_request = mock.MagicMock(
        method="POST", FILES={"tiles": mock.MagicMock(size=10)}, POST=UPLOAD_POST
    )

    views.capture_upload(mock_request)

    mock_captures.filter.return_value.update.assert_called_once_with(
        status=BasemapCapture.StatusChoices.FAILED, error_message="Test error"
    )


def test_capture_server_invalid_json():
    mock_request = mock.MagicMock(method="POST", body="not json")

    response = views.capture_server(mock_request)

    assert response.content == b"Invalid capture plan."


def test_capture_server_plan_not_dict():
    mock_request = mock.MagicMock(method="POST", body=json.dumps([1, 2]))

    response = views.capture_server(mock_request)

    assert response.content == b"Invalid capture plan."


def test_capture_server_no_name():
    mock_request = mock.MagicMock(
        method="POST", body=json.dumps({**SERVER_PLAN, "name": ""})
    )

    response = views.capture_server(mock_request)

    assert response.content == b"Enter a name for the capture."


def test_capture_server_invalid_zoom_value():
    mock_request = mock.MagicMock(
        method="POST", body=json.dumps({**SERVER_PLAN, "min_zoom": "a"})
    )

    response = views.capture_server(mock_request)

    assert response.content == b"Invalid bbox, zoom range or tile size."


def test_capture_server_invalid_bbox():
    mock_request = mock.MagicMock(
        method="POST", body=json.dumps({**SERVER_PLAN, "bbox": [1, 1, 0, 0]})
    )

    response = views.capture_server(mock_request)

    assert response.content == b"Invalid bbox."


def test_capture_server_invalid_zoom_range():
    mock_request = mock.MagicMock(
        method="POST", body=json.dumps({**SERVER_PLAN, "min_zoom": 5, "max_zoom": 1})
    )

    response = views.capture_server(mock_request)

    assert response.content == b"Invalid zoom range."


def test_capture_server_invalid_tile_size():
    mock_request = mock.MagicMock(
        method="POST", body=json.dumps({**SERVER_PLAN, "tile_size": 100})
    )

    response = views.capture_server(mock_request)

    assert response.content == b"Invalid tile size."


@mock.patch("tethys_basemaps.views.DaskScheduler.objects")
def test_capture_server_scheduler_not_found(mock_schedulers):
    mock_schedulers.get.side_effect = DaskScheduler.DoesNotExist
    mock_request = mock.MagicMock(method="POST", body=json.dumps(SERVER_PLAN))

    response = views.capture_server(mock_request)

    assert response.content == b"Invalid Dask scheduler."


@mock.patch("tethys_basemaps.views.DaskScheduler.objects")
def test_capture_server_scheduler_blank(mock_schedulers):
    mock_schedulers.get.side_effect = ValueError
    mock_request = mock.MagicMock(
        method="POST", body=json.dumps({**SERVER_PLAN, "dask_scheduler": ""})
    )

    response = views.capture_server(mock_request)

    assert response.content == b"Invalid Dask scheduler."


@mock.patch("tethys_basemaps.views.SecureMapService.objects")
@mock.patch("tethys_basemaps.views.PortalBasemapSource.objects")
@mock.patch("tethys_basemaps.views.DaskScheduler.objects")
def test_capture_server_source_not_found(
    mock_schedulers, mock_sources, mock_secure_services
):
    mock_sources.filter.return_value.first.return_value = None
    mock_secure_services.filter.return_value.first.return_value = None
    mock_request = mock.MagicMock(method="POST", body=json.dumps(SERVER_PLAN))

    response = views.capture_server(mock_request)

    assert response.status_code == 400
    assert json.loads(response.content)["browser_only"] is True


@mock.patch(
    "tethys_basemaps.views.source_tile_templates",
    side_effect=BrowserOnlySource("Test error"),
)
@mock.patch("tethys_basemaps.views.PortalBasemapSource.objects")
@mock.patch("tethys_basemaps.views.DaskScheduler.objects")
def test_capture_server_browser_only_source(
    mock_schedulers, mock_sources, mock_templates
):
    mock_request = mock.MagicMock(method="POST", body=json.dumps(SERVER_PLAN))

    response = views.capture_server(mock_request)

    assert response.status_code == 400
    assert json.loads(response.content) == {"error": "Test error", "browser_only": True}


@mock.patch(
    "tethys_basemaps.views.source_tile_templates", side_effect=ValueError("Test error")
)
@mock.patch("tethys_basemaps.views.PortalBasemapSource.objects")
@mock.patch("tethys_basemaps.views.DaskScheduler.objects")
def test_capture_server_source_error(mock_schedulers, mock_sources, mock_templates):
    mock_request = mock.MagicMock(method="POST", body=json.dumps(SERVER_PLAN))

    response = views.capture_server(mock_request)

    assert response.content == b"Test error"


@mock.patch("tethys_basemaps.views.count_tiles", return_value=0)
@mock.patch("tethys_basemaps.views.source_tile_templates", return_value=([], {}))
@mock.patch("tethys_basemaps.views.PortalBasemapSource.objects")
@mock.patch("tethys_basemaps.views.DaskScheduler.objects")
def test_capture_server_outside_map(
    mock_schedulers, mock_sources, mock_templates, mock_count_tiles
):
    mock_request = mock.MagicMock(method="POST", body=json.dumps(SERVER_PLAN))

    response = views.capture_server(mock_request)

    assert response.content == b"The selected area is outside the map."


@mock.patch("tethys_basemaps.views.PortalBasemap.objects")
@mock.patch("tethys_basemaps.views.count_tiles", return_value=2)
@mock.patch("tethys_basemaps.views.source_tile_templates", return_value=([], {}))
@mock.patch("tethys_basemaps.views.PortalBasemapSource.objects")
@mock.patch("tethys_basemaps.views.DaskScheduler.objects")
def test_capture_server_name_exists(
    mock_schedulers, mock_sources, mock_templates, mock_count_tiles, mock_basemaps
):
    mock_basemaps.filter.return_value.exists.return_value = True
    mock_request = mock.MagicMock(method="POST", body=json.dumps(SERVER_PLAN))

    response = views.capture_server(mock_request)

    assert response.content == b'A basemap named "Test Capture" already exists.'


@mock.patch("tethys_basemaps.views.PortalBasemap.objects")
@mock.patch("tethys_basemaps.views.count_tiles", return_value=2)
@mock.patch("tethys_basemaps.views.source_tile_templates", return_value=([], {}))
@mock.patch("tethys_basemaps.views.PortalBasemapSource.objects")
@mock.patch("tethys_basemaps.views.DaskScheduler.objects")
def test_capture_server_invalid_rate(
    mock_schedulers, mock_sources, mock_templates, mock_count_tiles, mock_basemaps
):
    mock_basemaps.filter.return_value.exists.return_value = False
    mock_request = mock.MagicMock(
        method="POST", body=json.dumps({**SERVER_PLAN, "max_requests_per_second": "a"})
    )

    response = views.capture_server(mock_request)

    assert response.content == b"Invalid max requests per second."


@mock.patch("tethys_basemaps.views.PortalBasemap.objects")
@mock.patch("tethys_basemaps.views.count_tiles", return_value=2)
@mock.patch("tethys_basemaps.views.source_tile_templates", return_value=([], {}))
@mock.patch("tethys_basemaps.views.PortalBasemapSource.objects")
@mock.patch("tethys_basemaps.views.DaskScheduler.objects")
def test_capture_server_rate_too_low(
    mock_schedulers, mock_sources, mock_templates, mock_count_tiles, mock_basemaps
):
    mock_basemaps.filter.return_value.exists.return_value = False
    mock_request = mock.MagicMock(
        method="POST", body=json.dumps({**SERVER_PLAN, "max_requests_per_second": 0})
    )

    response = views.capture_server(mock_request)

    assert response.content.startswith(b"Requests per second must be between 1 and")


@mock.patch("tethys_basemaps.views._capture_response")
@mock.patch("tethys_basemaps.views._submit_server_download")
@mock.patch("tethys_basemaps.views.BasemapCapture.objects")
@mock.patch(
    "tethys_basemaps.views.BasemapCapture.unique_output_name",
    return_value="basemaps/captures/test-capture.mbtiles",
)
@mock.patch("tethys_basemaps.views.PortalBasemap.objects")
@mock.patch("tethys_basemaps.views.count_tiles", return_value=2)
@mock.patch("tethys_basemaps.views.source_tile_templates")
@mock.patch("tethys_basemaps.views.PortalBasemapSource.objects")
@mock.patch("tethys_basemaps.views.DaskScheduler.objects")
def test_capture_server(
    mock_schedulers,
    mock_sources,
    mock_templates,
    mock_count_tiles,
    mock_basemaps,
    mock_unique_output_name,
    mock_captures,
    mock_submit,
    mock_capture_response,
):
    mock_scheduler = mock_schedulers.get.return_value
    mock_source = mock_sources.filter.return_value.first.return_value
    mock_templates.return_value = (["https://test/{z}/{x}/{y}"], {})
    mock_basemaps.filter.return_value.exists.return_value = False
    mock_request = mock.MagicMock(
        method="POST", body=json.dumps({**SERVER_PLAN, "max_requests_per_second": 20})
    )
    mock_capture = mock_captures.create.return_value

    response = views.capture_server(mock_request)

    mock_schedulers.get.assert_called_once_with(pk=1)
    mock_templates.assert_called_once_with(mock_source, mock_request.user)
    mock_captures.create.assert_called_once_with(
        name="Test Capture",
        source=mock_source,
        secure_source=None,
        status=BasemapCapture.StatusChoices.PROCESSING,
        mbtiles_file="basemaps/captures/test-capture.mbtiles",
        max_requests_per_second=20,
        downloaded_on_server=True,
        dask_scheduler=mock_scheduler,
        tile_size=256,
        min_zoom=0,
        max_zoom=1,
        min_x=0.0,
        min_y=0.0,
        max_x=1.0,
        max_y=1.0,
    )
    mock_submit.assert_called_once_with(
        mock_capture, mock_source, ["https://test/{z}/{x}/{y}"], {}, mock_request.user
    )
    mock_capture_response.assert_called_once_with(mock_capture, 2)
    assert response == mock_capture_response.return_value


@mock.patch("tethys_basemaps.views._capture_response")
@mock.patch("tethys_basemaps.views._submit_server_download")
@mock.patch("tethys_basemaps.views.BasemapCapture.objects")
@mock.patch("tethys_basemaps.views.BasemapCapture.unique_output_name")
@mock.patch("tethys_basemaps.views.PortalBasemap.objects")
@mock.patch("tethys_basemaps.views.count_tiles", return_value=2)
@mock.patch("tethys_basemaps.views.source_tile_templates", return_value=([], {}))
@mock.patch("tethys_basemaps.views.SecureMapService.objects")
@mock.patch("tethys_basemaps.views.PortalBasemapSource.objects")
@mock.patch("tethys_basemaps.views.DaskScheduler.objects")
def test_capture_server_secure_source_default_rate(
    mock_schedulers,
    mock_sources,
    mock_secure_services,
    mock_templates,
    mock_count_tiles,
    mock_basemaps,
    mock_unique_output_name,
    mock_captures,
    mock_submit,
    mock_capture_response,
):
    secure_source = SecureMapService(name="Test Secure")
    mock_sources.filter.return_value.first.return_value = None
    mock_secure_services.filter.return_value.first.return_value = secure_source
    mock_basemaps.filter.return_value.exists.return_value = False
    mock_request = mock.MagicMock(method="POST", body=json.dumps(SERVER_PLAN))

    views.capture_server(mock_request)

    create_kwargs = mock_captures.create.call_args.kwargs
    assert create_kwargs["source"] is None
    assert create_kwargs["secure_source"] == secure_source
    assert create_kwargs["max_requests_per_second"] == 50


@mock.patch("tethys_basemaps.views.run_basemap_task")
@mock.patch("tethys_basemaps.views.BasemapCapture.objects")
def test_submit_server_download(mock_captures, mock_run):
    mock_capture = mock.MagicMock(
        pk=1,
        min_x=0,
        min_y=0,
        max_x=1,
        max_y=1,
        min_zoom=0,
        max_zoom=1,
        tile_size=256,
        max_requests_per_second=None,
    )
    mock_capture.name = "Test Capture"
    mock_source = mock.MagicMock()
    mock_source.name = "Test Source"
    mock_user = mock.MagicMock()

    views._submit_server_download(
        mock_capture, mock_source, ["https://test/{z}/{x}/{y}"], {}, mock_user
    )

    mock_run.assert_called_once_with(
        views.fetch_and_build_mbtiles,
        1,
        [{"basemap_type": "xyz", "urls": ["https://test/{z}/{x}/{y}"], "opacity": 1}],
        [0, 0, 1, 1],
        0,
        1,
        256,
        "Test Capture",
        "Test Source",
        mock_capture.mbtiles_file.path,
        name="Download basemap capture 1",
        user=mock_user,
        result_path=mock_capture.result_path,
        non_dask_result_handler=mock_capture.apply_build_result,
        dask_scheduler=mock_capture.dask_scheduler,
        progress_path=mock_capture.progress_path,
        concurrency=views._concurrency_for(None),
        cancel_path=mock_capture.cancel_path,
    )
    mock_captures.filter.return_value.update.assert_called_once_with(
        job=mock_run.return_value
    )
    mock_capture.refresh_from_db.assert_called_once()


@mock.patch(
    "tethys_basemaps.views.run_basemap_task", side_effect=Exception("Test error")
)
@mock.patch("tethys_basemaps.views.BasemapCapture.objects")
def test_submit_server_download_error(mock_captures, mock_run):
    mock_capture = mock.MagicMock(pk=1, max_requests_per_second=None)

    views._submit_server_download(mock_capture, mock.MagicMock(), [], {}, None)

    mock_captures.filter.assert_called_once_with(pk=1)
    mock_captures.filter.return_value.update.assert_called_once_with(
        status=BasemapCapture.StatusChoices.FAILED, error_message="Test error"
    )
    mock_capture.refresh_from_db.assert_called_once()


@mock.patch("tethys_basemaps.views.BasemapCapture.objects")
def test_capture_cancel_not_found(mock_captures):
    mock_captures.get.side_effect = BasemapCapture.DoesNotExist

    response = views.capture_cancel(mock.MagicMock(method="POST"), 1)

    assert response.status_code == 404


@mock.patch("tethys_basemaps.views.BasemapCapture.objects")
def test_capture_cancel_no_job(mock_captures):
    mock_captures.get.return_value.job_id = None

    response = views.capture_cancel(mock.MagicMock(method="POST"), 1)

    assert response.status_code == 400


@mock.patch("tethys_basemaps.views.BasemapCapture.objects")
def test_capture_cancel_already_finished(mock_captures):
    mock_capture = mock_captures.get.return_value
    mock_capture.cancel.return_value = False
    mock_capture.status = "ready"
    mock_capture.get_status_display.return_value = "Ready"

    response = views.capture_cancel(mock.MagicMock(method="POST"), 1)

    assert response.status_code == 409
    assert json.loads(response.content) == {
        "error": "The capture has already finished (Ready).",
        "status": "ready",
    }


@mock.patch("tethys_basemaps.views.BasemapCapture.objects")
def test_capture_cancel(mock_captures):
    mock_capture = mock_captures.get.return_value
    mock_capture.pk = 1
    mock_capture.status = "cancelled"
    mock_capture.cancel.return_value = True
    mock_request = mock.MagicMock(method="POST")

    response = views.capture_cancel(mock_request, 1)

    mock_capture.cancel.assert_called_once_with(mock_request.user)
    assert response.status_code == 200
    assert json.loads(response.content) == {"id": 1, "status": "cancelled"}


@mock.patch("tethys_basemaps.views.BasemapCapture.objects")
def test_capture_tile_not_found(mock_captures):
    mock_captures.get.side_effect = BasemapCapture.DoesNotExist

    response = views.capture_tile(mock.MagicMock(), 1, 0, 0, 0)

    assert response.status_code == 404


@mock.patch("tethys_basemaps.views.BasemapCapture.objects")
def test_capture_tile_missing_tile(mock_captures):
    mock_captures.get.return_value.get_tile.return_value = None

    response = views.capture_tile(mock.MagicMock(), 1, 0, 0, 0)

    assert response.status_code == 204


@mock.patch("tethys_basemaps.views.BasemapCapture.objects")
def test_capture_tile(mock_captures):
    mock_capture = mock_captures.get.return_value
    mock_capture.get_tile.return_value = b"tile bytes"
    mock_capture.tile_content_type = "image/jpeg"

    response = views.capture_tile(mock.MagicMock(), 1, 2, 3, 4)

    mock_capture.get_tile.assert_called_once_with(2, 3, 4)
    assert response.content == b"tile bytes"
    assert response["Content-Type"] == "image/jpeg"


@mock.patch("tethys_basemaps.views.BasemapImage.objects")
def test_image_cancel_not_found(mock_images):
    mock_images.get.side_effect = BasemapImage.DoesNotExist

    response = views.image_cancel(mock.MagicMock(method="POST"), 1)

    assert response.status_code == 404


@mock.patch("tethys_basemaps.views.BasemapImage.objects")
def test_image_cancel_no_job(mock_images):
    mock_images.get.return_value.job_id = None

    response = views.image_cancel(mock.MagicMock(method="POST"), 1)

    assert response.status_code == 400


@mock.patch("tethys_basemaps.views.BasemapImage.objects")
def test_image_cancel_already_finished(mock_images):
    mock_image = mock_images.get.return_value
    mock_image.cancel.return_value = False
    mock_image.status = "ready"
    mock_image.get_status_display.return_value = "Ready"

    response = views.image_cancel(mock.MagicMock(method="POST"), 1)

    assert response.status_code == 409
    assert json.loads(response.content) == {
        "error": "The image has already finished (Ready).",
        "status": "ready",
    }


@mock.patch("tethys_basemaps.views.BasemapImage.objects")
def test_image_cancel(mock_images):
    mock_image = mock_images.get.return_value
    mock_image.pk = 1
    mock_image.status = "cancelled"
    mock_image.cancel.return_value = True
    mock_request = mock.MagicMock(method="POST")

    response = views.image_cancel(mock_request, 1)

    mock_image.cancel.assert_called_once_with(mock_request.user)
    assert response.status_code == 200
    assert json.loads(response.content) == {"id": 1, "status": "cancelled"}


@mock.patch("tethys_basemaps.views.BasemapCapture.objects")
def test_capture_restart_not_found(mock_captures):
    mock_captures.select_related.return_value.get.side_effect = (
        BasemapCapture.DoesNotExist
    )

    response = views.capture_restart(mock.MagicMock(method="POST"), 1)

    assert response.status_code == 404


@mock.patch("tethys_basemaps.views.BasemapCapture.objects")
def test_capture_restart_problem(mock_captures):
    mock_capture = mock_captures.select_related.return_value.get.return_value
    mock_capture.restart_problem.return_value = (
        "Only a cancelled capture can be restarted."
    )

    response = views.capture_restart(mock.MagicMock(method="POST"), 1)

    assert response.status_code == 400
    assert response.content == b"Only a cancelled capture can be restarted."


@mock.patch(
    "tethys_basemaps.views.source_tile_templates", side_effect=ValueError("Test error")
)
@mock.patch("tethys_basemaps.views.BasemapCapture.objects")
def test_capture_restart_source_error(mock_captures, mock_templates):
    mock_capture = mock_captures.select_related.return_value.get.return_value
    mock_capture.restart_problem.return_value = None

    response = views.capture_restart(mock.MagicMock(method="POST"), 1)

    assert response.status_code == 400
    assert response.content == b"Test error"
    mock_captures.filter.assert_not_called()


@mock.patch("tethys_basemaps.views._submit_server_download")
@mock.patch("tethys_basemaps.views.source_tile_templates", return_value=([], {}))
@mock.patch("tethys_basemaps.views.BasemapCapture.objects")
def test_capture_restart_not_claimed(mock_captures, mock_templates, mock_submit):
    mock_capture = mock_captures.select_related.return_value.get.return_value
    mock_capture.restart_problem.return_value = None
    mock_captures.filter.return_value.update.return_value = 0

    response = views.capture_restart(mock.MagicMock(method="POST"), 1)

    assert response.status_code == 409
    assert json.loads(response.content) == {
        "error": "The capture is no longer cancelled."
    }
    mock_submit.assert_not_called()


@mock.patch("tethys_basemaps.views._capture_response")
@mock.patch("tethys_basemaps.views.count_tiles", return_value=2)
@mock.patch("tethys_basemaps.views._submit_server_download")
@mock.patch("tethys_basemaps.views.source_tile_templates")
@mock.patch("tethys_basemaps.views.BasemapCapture.objects")
def test_capture_restart(
    mock_captures, mock_templates, mock_submit, mock_count_tiles, mock_capture_response
):
    mock_capture = mock_captures.select_related.return_value.get.return_value
    mock_capture.restart_problem.return_value = None
    mock_templates.return_value = (["https://test/{z}/{x}/{y}"], {"X-Test": "1"})
    mock_captures.filter.return_value.update.return_value = 1
    mock_request = mock.MagicMock(method="POST")

    response = views.capture_restart(mock_request, 1)

    mock_captures.select_related.assert_called_once_with("source", "secure_source")
    mock_templates.assert_called_once_with(mock_capture.source)
    mock_captures.filter.assert_called_once_with(
        pk=mock_capture.pk, status=BasemapCapture.StatusChoices.CANCELLED
    )
    mock_captures.filter.return_value.update.assert_called_once_with(
        status=BasemapCapture.StatusChoices.PROCESSING,
        error_message="",
        mbtiles_file=mock_capture.unique_output_name.return_value,
        job=None,
    )
    mock_capture.refresh_from_db.assert_called_once()
    mock_submit.assert_called_once_with(
        mock_capture,
        mock_capture.source,
        ["https://test/{z}/{x}/{y}"],
        {"X-Test": "1"},
        mock_request.user,
    )
    mock_count_tiles.assert_called_once_with(
        [
            mock_capture.min_x,
            mock_capture.min_y,
            mock_capture.max_x,
            mock_capture.max_y,
        ],
        mock_capture.min_zoom,
        mock_capture.max_zoom,
    )
    mock_capture_response.assert_called_once_with(mock_capture, 2)
    assert response == mock_capture_response.return_value
