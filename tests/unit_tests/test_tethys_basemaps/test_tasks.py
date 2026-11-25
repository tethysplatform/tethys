import io
import json
import sqlite3
from unittest import mock

import numpy
import pytest
import rasterio
import requests
from large_image.exceptions import TileSourceXYZRangeError
from PIL import Image
from rasterio.transform import from_bounds

import tethys_basemaps.mbtiles_utilities as mbtiles
import tethys_basemaps.tasks as tasks

HALF_WORLD = mbtiles.WEB_MERCATOR_HALF_WORLD
WORLD_BBOX = [-HALF_WORLD, -HALF_WORLD, HALF_WORLD, HALF_WORLD]
PNG = b"\x89PNG\r\n\x1a\ntest png"
JPG = b"\xff\xd8\xff\xe0test jpg"
WEBP = b"RIFF\x00\x00\x00\x00WEBPtest webp"


def test_tile_fetch_error_refused():
    response = mock.MagicMock(
        status_code=401,
        headers={"Content-Type": "text/plain", "retry-after": "5"},
        text="Invalid key supersecret123",
    )

    error = tasks.TileFetchError(
        "https://example.com/tile?key=supersecret123", response
    )

    assert error.status == 401
    assert str(error) == (
        "HTTP 401 from https://example.com/tile. The service refused the request. "
        "The credentials may be invalid or expired, or the key may have hit a rate "
        "or usage limit. {'retry-after': '5'} Response: Invalid key ***"
    )


def test_tile_fetch_error_server_error():
    response = mock.MagicMock(status_code=500, headers={}, text="")

    error = tasks.TileFetchError("https://example.com/tile", response)

    assert str(error) == (
        "HTTP 500 from https://example.com/tile. The service returned an error."
    )


def test_tile_fetch_error_scrubs_secrets():
    response = mock.MagicMock(
        status_code=403,
        headers={"Content-Type": "text/plain"},
        text="Token abcdefghij is expired",
    )

    error = tasks.TileFetchError(
        "https://example.com/tile", response, secrets=["abcdefghij"]
    )

    assert "abcdefghij" not in str(error)
    assert "Token *** is expired" in str(error)


def test_remove_url_params():
    result = tasks._remove_url_params("https://example.com/tile/1/2/3?key=secret")

    assert result == "https://example.com/tile/1/2/3"


def test_scrub():
    result = tasks._scrub(
        "key=secretkey123 short=abc token=tokenvalue",
        "https://example.com/tile?key=secretkey123&short=abc",
        secrets=["tokenvalue"],
    )

    assert result == "key=*** short=abc token=***"


def test_form_error_result_tile_fetch_error():
    response = mock.MagicMock(status_code=500, headers={}, text="")
    error = tasks.TileFetchError("https://example.com/tile", response)

    result = tasks._form_error_result("capture_id", 1, error)

    assert result == {"capture_id": 1, "ok": False, "error": str(error)}


def test_form_error_result_other_error():
    try:
        raise ValueError("Test error")
    except ValueError as e:
        result = tasks._form_error_result("image_id", 1, e)

    assert result["image_id"] == 1
    assert result["ok"] is False
    assert result["error"].startswith("Test error\nTraceback")


def test_write_json(tmp_path):
    path = tmp_path / "folder" / "test.json"

    tasks._write_json(str(path), {"done": 1})

    assert json.loads(path.read_text()) == {"done": 1}
    assert not (tmp_path / "folder" / "test.json.partial").exists()


def test_write_result(tmp_path):
    path = tmp_path / "test.result.json"

    result = tasks._write_result(str(path), {"ok": True})

    assert result == {"ok": True}
    assert json.loads(path.read_text()) == {"ok": True}


def test_write_result_no_path():
    assert tasks._write_result(None, {"ok": True}) == {"ok": True}


def test_form_cancelled_result():
    result = tasks._form_cancelled_result("capture_id", 1, done=2, total=3)

    assert result == {
        "capture_id": 1,
        "ok": False,
        "cancelled": True,
        "done": 2,
        "total": 3,
    }


def test_check_cancel_no_flag(tmp_path):
    tasks._check_cancel(None)
    tasks._check_cancel(str(tmp_path / "test.cancel"))


def test_check_cancel_flag(tmp_path):
    cancel_path = tmp_path / "test.cancel"
    cancel_path.touch()

    with pytest.raises(tasks.BasemapTaskCancelled):
        tasks._check_cancel(str(cancel_path))


def test_remove_files(tmp_path):
    path = tmp_path / "test.partial"
    path.touch()

    tasks._remove_files(str(path), str(tmp_path / "missing.json"), None)

    assert not path.exists()


@mock.patch("tethys_basemaps.tasks.traceback.print_exc")
@mock.patch("tethys_basemaps.tasks.os.remove", side_effect=PermissionError)
def test_remove_files_error(mock_remove, mock_print_exc):
    tasks._remove_files("/data/test.partial")

    mock_print_exc.assert_called_once()


def test_tile_format():
    assert tasks.tile_format(PNG) == "png"
    assert tasks.tile_format(JPG) == "jpg"
    assert tasks.tile_format(WEBP) == "webp"
    assert tasks.tile_format(b"<ServiceException/>") is None


def test_tile_ranges():
    result = list(tasks.tile_ranges(WORLD_BBOX, 0, 1))

    assert result == [(0, 0, 0, 0, 0), (1, 0, 1, 0, 1)]


def test_tile_ranges_outside_world():
    bbox = [HALF_WORLD + 1, 0, HALF_WORLD + 2, 1]

    assert list(tasks.tile_ranges(bbox, 0, 1)) == []


def test_count_tiles():
    assert tasks.count_tiles(WORLD_BBOX, 0, 1) == 5


def test_iter_coords():
    result = list(tasks._iter_coords(WORLD_BBOX, 0, 1))

    assert result == [(0, 0, 0), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]


def test_composite_one_layer():
    assert tasks._composite([JPG], [1], 256) == JPG


def test_composite_no_tiles():
    assert tasks._composite([None, None], [1, 1], 256) is None


def test_composite_layers():
    red = io.BytesIO()
    Image.new("RGBA", (4, 4), (255, 0, 0, 255)).save(red, "PNG")
    blue = io.BytesIO()
    Image.new("RGBA", (8, 8), (0, 0, 255, 255)).save(blue, "PNG")

    result = tasks._composite([red.getvalue(), None, blue.getvalue()], [1, 1, 0.5], 4)

    image = Image.open(io.BytesIO(result))
    assert image.size == (4, 4)
    red_value, green_value, blue_value, alpha_value = image.getpixel((0, 0))
    assert red_value == pytest.approx(128, abs=1)
    assert green_value == 0
    assert blue_value == pytest.approx(128, abs=1)
    assert alpha_value == 255


def test_make_reader_xyz():
    layer = {
        "basemap_type": "xyz",
        "urls": ["https://example.com/{z}/{x}/{y}.png"],
        "headers": {"Authorization": "Bearer token"},
        "fetch": {"max_requests_per_second": 10, "max_attempts": 3, "max_wait": 60},
    }

    reader = tasks._make_reader(layer, 30)

    assert isinstance(reader, tasks._XYZReader)
    assert reader.urls == ["https://example.com/{z}/{x}/{y}.png"]
    assert reader.timeout == 30
    assert reader.headers == {"Authorization": "Bearer token"}
    assert reader.max_attempts == 3
    assert reader.max_wait == 60
    assert reader._min_interval == 0.1


def test_make_reader_mbtiles():
    reader = tasks._make_reader(
        {"basemap_type": "mbtiles", "path": "/data/a.mbtiles"}, 30
    )

    assert isinstance(reader, tasks._MBTilesReader)
    assert reader.path == "/data/a.mbtiles"


def test_make_reader_cog():
    layer = {"basemap_type": "cog", "path": "/data/a.tif", "style": {"bands": []}}

    reader = tasks._make_reader(layer, 30)

    assert isinstance(reader, tasks._COGReader)
    assert reader.style == {"bands": []}


def test_make_reader_unknown():
    with pytest.raises(ValueError, match="Unknown layer basemap_type: wms"):
        tasks._make_reader({"basemap_type": "wms"}, 30)


def test_xyz_reader_init():
    reader = tasks._XYZReader(
        ["https://example.com/{z}/{x}/{y}.png"],
        30,
        headers={"Authorization": "Bearer token"},
    )

    assert reader.secrets == ["Bearer token", "token"]
    assert reader.retry_statuses == tasks.DEFAULT_RETRY_STATUSES
    assert reader._min_interval == 0


def test_xyz_reader_tile_url():
    reader = tasks._XYZReader(["https://example.com/{z}/{x}/{y}.png"], 30)

    assert reader._tile_url(2, 1, 3) == "https://example.com/2/1/3.png"


def test_xyz_reader_tile_url_flipped_y():
    reader = tasks._XYZReader(["https://example.com/{z}/{x}/{-y}.png"], 30)

    assert reader._tile_url(2, 1, 0) == "https://example.com/2/1/3.png"


def test_xyz_reader_tile_url_subdomains():
    reader = tasks._XYZReader(
        [
            "https://a.example.com/{z}/{x}/{y}.png",
            "https://b.example.com/{z}/{x}/{y}.png",
        ],
        30,
    )

    assert reader._tile_url(1, 0, 0) == "https://a.example.com/1/0/0.png"
    assert reader._tile_url(1, 1, 0) == "https://b.example.com/1/1/0.png"


def test_xyz_reader_tile_url_bbox():
    reader = tasks._XYZReader(["https://example.com/wms?BBOX={bbox}"], 30)

    result = reader._tile_url(0, 0, 0)

    assert result == (
        f"https://example.com/wms?BBOX={-HALF_WORLD},{-HALF_WORLD},{HALF_WORLD},{HALF_WORLD}"
    )


def test_xyz_reader_call():
    reader = tasks._XYZReader(["https://example.com/{z}/{x}/{y}.png"], 30)
    mock_session = mock.MagicMock()
    mock_session.get.return_value = mock.MagicMock(status_code=200, content=PNG)
    reader._session = mock.MagicMock(return_value=mock_session)

    result = reader(2, 1, 3)

    mock_session.get.assert_called_once_with(
        "https://example.com/2/1/3.png", timeout=30, allow_redirects=False
    )
    assert result == PNG


def test_xyz_reader_call_empty_content():
    reader = tasks._XYZReader(["https://example.com/{z}/{x}/{y}.png"], 30)
    mock_session = mock.MagicMock()
    mock_session.get.return_value = mock.MagicMock(status_code=200, content=b"")
    reader._session = mock.MagicMock(return_value=mock_session)

    assert reader(0, 0, 0) is None


def test_xyz_reader_call_no_tile():
    reader = tasks._XYZReader(["https://example.com/{z}/{x}/{y}.png"], 30)
    mock_session = mock.MagicMock()
    mock_session.get.return_value = mock.MagicMock(status_code=404)
    reader._session = mock.MagicMock(return_value=mock_session)

    assert reader(0, 0, 0) is None


def test_xyz_reader_call_refused():
    reader = tasks._XYZReader(["https://example.com/{z}/{x}/{y}.png"], 30)
    mock_session = mock.MagicMock()
    mock_session.get.return_value = mock.MagicMock(status_code=401, headers={}, text="")
    reader._session = mock.MagicMock(return_value=mock_session)

    with pytest.raises(tasks.TileFetchError, match="HTTP 401"):
        reader(0, 0, 0)


def test_xyz_reader_call_retries_busy_server():
    reader = tasks._XYZReader(["https://example.com/{z}/{x}/{y}.png"], 30)
    mock_session = mock.MagicMock()
    busy = mock.MagicMock(status_code=503)
    mock_session.get.side_effect = [busy, mock.MagicMock(status_code=200, content=PNG)]
    reader._session = mock.MagicMock(return_value=mock_session)
    reader._pause_all = mock.MagicMock()

    result = reader(0, 0, 0)

    reader._pause_all.assert_called_once_with(busy, 0)
    assert result == PNG


def test_xyz_reader_call_busy_on_last_attempt():
    reader = tasks._XYZReader(
        ["https://example.com/{z}/{x}/{y}.png"], 30, max_attempts=1
    )
    mock_session = mock.MagicMock()
    mock_session.get.return_value = mock.MagicMock(status_code=503, headers={}, text="")
    reader._session = mock.MagicMock(return_value=mock_session)

    with pytest.raises(tasks.TileFetchError, match="HTTP 503"):
        reader(0, 0, 0)


def test_xyz_reader_call_retries_connection_error():
    reader = tasks._XYZReader(["https://example.com/{z}/{x}/{y}.png"], 30)
    mock_session = mock.MagicMock()
    mock_session.get.side_effect = [
        requests.ConnectionError(),
        mock.MagicMock(status_code=200, content=PNG),
    ]
    reader._session = mock.MagicMock(return_value=mock_session)
    reader._sleep = mock.MagicMock()

    result = reader(0, 0, 0)

    reader._sleep.assert_called_once_with(1)
    assert result == PNG


def test_xyz_reader_call_connection_error_on_last_attempt():
    reader = tasks._XYZReader(
        ["https://example.com/{z}/{x}/{y}.png?key=secret"], 30, max_attempts=1
    )
    mock_session = mock.MagicMock()
    mock_session.get.side_effect = requests.ConnectTimeout()
    reader._session = mock.MagicMock(return_value=mock_session)

    with pytest.raises(RuntimeError) as error:
        reader(0, 0, 0)

    assert str(error.value) == (
        "Could not download https://example.com/0/0/0.png: ConnectTimeout"
    )


def test_xyz_reader_session():
    reader = tasks._XYZReader(
        ["https://example.com/{z}/{x}/{y}.png"],
        30,
        headers={"Authorization": "Bearer token"},
    )

    session = reader._session()

    assert session.headers["User-Agent"] == "Tethys Platform basemap capture"
    assert session.headers["Authorization"] == "Bearer token"
    assert reader._session() is session
    assert reader._sessions == [session]


def test_xyz_reader_close():
    reader = tasks._XYZReader(["https://example.com/{z}/{x}/{y}.png"], 30)
    mock_session = mock.MagicMock()
    reader._sessions = [mock_session]

    reader.close()

    mock_session.close.assert_called_once()


def test_xyz_reader_cancel():
    reader = tasks._XYZReader(["https://example.com/{z}/{x}/{y}.png"], 30)

    reader.cancel()

    assert reader._cancelled.is_set()


def test_xyz_reader_wait_turn_cancelled():
    reader = tasks._XYZReader(["https://example.com/{z}/{x}/{y}.png"], 30)
    reader.cancel()

    with pytest.raises(tasks.BasemapTaskCancelled):
        reader._wait_turn()


@mock.patch("tethys_basemaps.tasks.time.monotonic", return_value=10.0)
def test_xyz_reader_wait_turn_no_wait(mock_monotonic):
    reader = tasks._XYZReader(
        ["https://example.com/{z}/{x}/{y}.png"], 30, max_requests_per_second=2
    )
    reader._sleep = mock.MagicMock()

    reader._wait_turn()

    reader._sleep.assert_not_called()
    assert reader._next_slot == 10.5


@mock.patch("tethys_basemaps.tasks.time.monotonic", return_value=10.0)
def test_xyz_reader_wait_turn_paused(mock_monotonic):
    reader = tasks._XYZReader(["https://example.com/{z}/{x}/{y}.png"], 30)
    reader._pause_until = 12.0
    reader._sleep = mock.MagicMock()

    reader._wait_turn()

    reader._sleep.assert_called_once_with(2.0)


@mock.patch("tethys_basemaps.tasks.time.monotonic", return_value=10.0)
def test_xyz_reader_pause_all_retry_after(mock_monotonic):
    reader = tasks._XYZReader(["https://example.com/{z}/{x}/{y}.png"], 30)
    response = mock.MagicMock(headers={"Retry-After": "5"})

    reader._pause_all(response, 0)

    assert reader._pause_until == 15.0


@mock.patch("tethys_basemaps.tasks.time.monotonic", return_value=10.0)
def test_xyz_reader_pause_all_backoff(mock_monotonic):
    reader = tasks._XYZReader(["https://example.com/{z}/{x}/{y}.png"], 30)
    response = mock.MagicMock(headers={})

    reader._pause_all(response, 2)

    assert reader._pause_until == 14.0


@mock.patch("tethys_basemaps.tasks.time.monotonic", return_value=10.0)
def test_xyz_reader_pause_all_retry_after_date(mock_monotonic):
    reader = tasks._XYZReader(["https://example.com/{z}/{x}/{y}.png"], 30)
    response = mock.MagicMock(headers={"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"})

    reader._pause_all(response, 1)

    assert reader._pause_until == 12.0


@mock.patch("tethys_basemaps.tasks.time.monotonic", return_value=10.0)
def test_xyz_reader_pause_all_max_wait(mock_monotonic):
    reader = tasks._XYZReader(["https://example.com/{z}/{x}/{y}.png"], 30, max_wait=60)
    response = mock.MagicMock(headers={"Retry-After": "3600"})

    reader._pause_all(response, 0)

    assert reader._pause_until == 70.0


def test_xyz_reader_sleep():
    reader = tasks._XYZReader(["https://example.com/{z}/{x}/{y}.png"], 30)

    reader._sleep(0)


def test_xyz_reader_sleep_cancelled():
    reader = tasks._XYZReader(["https://example.com/{z}/{x}/{y}.png"], 30)
    reader.cancel()

    with pytest.raises(tasks.BasemapTaskCancelled):
        reader._sleep(10)


def test_mbtiles_reader(tmp_path):
    path = str(tmp_path / "test.mbtiles")
    conn = mbtiles.create_mbtiles(path)
    mbtiles.insert_tile(conn, 1, 0, 1, PNG)
    conn.commit()
    conn.close()
    reader = tasks._MBTilesReader(path)

    assert reader(1, 0, 1) == PNG
    assert reader(1, 1, 1) is None
    assert len(reader._conns) == 1

    reader.cancel()
    reader.close()


@mock.patch("large_image_source_rasterio.open")
def test_cog_reader(mock_rio_open):
    mock_rio_open.return_value.getTile.return_value = PNG
    reader = tasks._COGReader("/data/test.tif", style={"bands": []})

    assert reader(2, 1, 3) == PNG
    assert reader(2, 1, 3) == PNG

    mock_rio_open.assert_called_once_with(
        "/data/test.tif",
        projection="EPSG:3857",
        encoding="PNG",
        style=json.dumps({"bands": []}),
    )
    mock_rio_open.return_value.getTile.assert_called_with(1, 3, 2)


@mock.patch("large_image_source_rasterio.open")
def test_cog_reader_outside_image(mock_rio_open):
    mock_rio_open.return_value.getTile.side_effect = TileSourceXYZRangeError()
    reader = tasks._COGReader("/data/test.tif")

    assert reader(0, 0, 0) is None
    mock_rio_open.assert_called_once_with(
        "/data/test.tif", projection="EPSG:3857", encoding="PNG"
    )

    reader.cancel()
    reader.close()


def test_build_cog(tmp_path):
    source_path = tmp_path / "source.tif"
    with rasterio.open(
        source_path,
        "w",
        driver="GTiff",
        width=4,
        height=4,
        count=1,
        dtype="uint8",
        crs="EPSG:4326",
        transform=from_bounds(-1, -1, 1, 1, 4, 4),
    ) as dst:
        dst.write(numpy.full((1, 4, 4), 100, dtype="uint8"))
    output_path = tmp_path / "output" / "test.tif"
    result_path = tmp_path / "test.result.json"

    result = tasks.build_cog(
        1, str(source_path), str(output_path), result_path=str(result_path)
    )

    assert result["ok"] is True
    assert result["image_id"] == 1
    assert result["srs"] == "3857"
    assert result["source_epsg"] == 4326
    assert output_path.exists()
    assert json.loads(result_path.read_text()) == result


def test_build_cog_georeference_bounds(tmp_path):
    source_path = tmp_path / "source.tif"
    with rasterio.open(
        source_path, "w", driver="GTiff", width=4, height=4, count=1, dtype="uint8"
    ) as dst:
        dst.write(numpy.full((1, 4, 4), 100, dtype="uint8"))
    output_path = tmp_path / "test.tif"

    result = tasks.build_cog(
        1,
        str(source_path),
        str(output_path),
        georeference_bounds=[-1, -1, 1, 1],
        georeference_epsg=4326,
    )

    assert result["ok"] is True
    assert result["source_epsg"] is None
    assert output_path.exists()


def test_build_cog_no_georeference(tmp_path):
    source_path = tmp_path / "source.tif"
    with rasterio.open(
        source_path, "w", driver="GTiff", width=4, height=4, count=1, dtype="uint8"
    ) as dst:
        dst.write(numpy.full((1, 4, 4), 100, dtype="uint8"))
    output_path = tmp_path / "test.tif"

    result = tasks.build_cog(1, str(source_path), str(output_path))

    assert result["ok"] is False
    assert result["error"].startswith("The image has no georeferencing.")
    assert not output_path.exists()


def test_build_cog_cancelled(tmp_path):
    cancel_path = tmp_path / "test.cancel"
    cancel_path.touch()

    result = tasks.build_cog(
        1, "/data/source.tif", str(tmp_path / "test.tif"), cancel_path=str(cancel_path)
    )

    assert result == {"image_id": 1, "ok": False, "cancelled": True}
    assert not cancel_path.exists()


def test_build_mbtiles(tmp_path):
    packed_path = tmp_path / "test.tiles"
    packed_path.write_bytes(PNG + PNG + JPG)
    entries = [[0, 0, 0, len(PNG)], [1, 0, 0, len(PNG)], [1, 1, 0, len(JPG)]]
    output_path = tmp_path / "output" / "test.mbtiles"
    result_path = tmp_path / "test.result.json"

    result = tasks.build_mbtiles(
        1,
        str(packed_path),
        entries,
        WORLD_BBOX,
        "Test Capture",
        "Test Source",
        str(output_path),
        result_path=str(result_path),
    )

    assert result == {
        "capture_id": 1,
        "ok": True,
        "output_path": str(output_path),
        "tile_format": "png",
        "tiles": 3,
    }
    assert json.loads(result_path.read_text()) == result
    assert not packed_path.exists()
    conn = mbtiles.open_read_only(str(output_path))
    assert mbtiles.read_tile(conn, 1, 1, 0) == JPG
    assert mbtiles.summary(conn) == (3, 0, 1)
    conn.close()


def test_build_mbtiles_bad_tile(tmp_path):
    packed_path = tmp_path / "test.tiles"
    packed_path.write_bytes(b"<ServiceException/>")
    output_path = tmp_path / "test.mbtiles"

    result = tasks.build_mbtiles(
        1,
        str(packed_path),
        [[0, 0, 0, 19]],
        WORLD_BBOX,
        "Test Capture",
        "Test Source",
        str(output_path),
    )

    assert result["ok"] is False
    assert result["error"].startswith("Tile 0/0/0 is not a PNG, JPEG or WebP image.")
    assert not output_path.exists()
    assert not (tmp_path / "test.mbtiles.partial").exists()
    assert not packed_path.exists()


def test_build_mbtiles_cancelled(tmp_path):
    packed_path = tmp_path / "test.tiles"
    packed_path.write_bytes(PNG)
    cancel_path = tmp_path / "test.cancel"
    cancel_path.touch()
    output_path = tmp_path / "test.mbtiles"

    result = tasks.build_mbtiles(
        1,
        str(packed_path),
        [[0, 0, 0, len(PNG)]],
        WORLD_BBOX,
        "Test Capture",
        "Test Source",
        str(output_path),
        cancel_path=str(cancel_path),
    )

    assert result == {"capture_id": 1, "ok": False, "cancelled": True}
    assert not output_path.exists()
    assert not (tmp_path / "test.mbtiles.partial").exists()
    assert not cancel_path.exists()
    assert not packed_path.exists()


@mock.patch("tethys_basemaps.tasks.mbtiles.insert_tile", side_effect=KeyboardInterrupt)
@mock.patch("tethys_basemaps.tasks.mbtiles.create_mbtiles")
def test_build_mbtiles_interrupted(mock_create_mbtiles, mock_insert_tile, tmp_path):
    packed_path = tmp_path / "test.tiles"
    packed_path.write_bytes(PNG)

    with pytest.raises(KeyboardInterrupt):
        tasks.build_mbtiles(
            1,
            str(packed_path),
            [[0, 0, 0, len(PNG)]],
            WORLD_BBOX,
            "Test Capture",
            "Test Source",
            str(tmp_path / "test.mbtiles"),
        )

    mock_create_mbtiles.return_value.close.assert_called_once()
    assert not packed_path.exists()


@mock.patch("tethys_basemaps.tasks.PROGRESS_EVERY", 2)
@mock.patch("tethys_basemaps.tasks._make_reader")
def test_fetch_and_build_mbtiles(mock_make_reader, tmp_path):
    mock_reader = mock.MagicMock(return_value=PNG)
    mock_make_reader.return_value = mock_reader
    output_path = tmp_path / "test.mbtiles"
    progress_path = tmp_path / "test.progress.json"
    result_path = tmp_path / "test.result.json"

    result = tasks.fetch_and_build_mbtiles(
        1,
        [{"basemap_type": "xyz"}],
        WORLD_BBOX,
        0,
        1,
        256,
        "Test Capture",
        "Test Source",
        str(output_path),
        progress_path=str(progress_path),
        result_path=str(result_path),
        concurrency=2,
    )

    assert result == {
        "capture_id": 1,
        "ok": True,
        "output_path": str(output_path),
        "tile_format": "png",
        "tiles": 5,
    }
    assert json.loads(progress_path.read_text()) == {"done": 5, "total": 5}
    assert json.loads(result_path.read_text()) == result
    assert mock_reader.call_count == 5
    mock_reader.close.assert_called_once()


@mock.patch("tethys_basemaps.tasks._make_reader")
def test_fetch_and_build_mbtiles_download_error(mock_make_reader, tmp_path):
    mock_reader = mock.MagicMock(side_effect=RuntimeError("Test error"))
    mock_make_reader.return_value = mock_reader
    output_path = tmp_path / "test.mbtiles"

    result = tasks.fetch_and_build_mbtiles(
        1,
        [{"basemap_type": "xyz"}],
        WORLD_BBOX,
        0,
        1,
        256,
        "Test Capture",
        "Test Source",
        str(output_path),
        concurrency=1,
    )

    assert result["ok"] is False
    assert result["resumable"] is False
    assert result["error"].startswith("Stopped after 0 of 5 tiles. Test error")
    assert not (tmp_path / "test.mbtiles.partial").exists()
    mock_reader.cancel.assert_called_once()
    mock_reader.close.assert_called_once()


def test_fetch_and_build_mbtiles_unknown_layer(tmp_path):
    result = tasks.fetch_and_build_mbtiles(
        1,
        [{"basemap_type": "wms"}],
        WORLD_BBOX,
        0,
        1,
        256,
        "Test Capture",
        "Test Source",
        str(tmp_path / "test.mbtiles"),
    )

    assert result["ok"] is False
    assert result["resumable"] is False
    assert "Unknown layer basemap_type: wms" in result["error"]


@mock.patch("tethys_basemaps.tasks.mbtiles.summary", side_effect=sqlite3.Error)
@mock.patch("tethys_basemaps.tasks._make_reader")
def test_fetch_and_build_mbtiles_partial_unreadable(
    mock_make_reader, mock_summary, tmp_path
):
    mock_make_reader.return_value = mock.MagicMock(
        side_effect=RuntimeError("Test error")
    )

    result = tasks.fetch_and_build_mbtiles(
        1,
        [{"basemap_type": "xyz"}],
        WORLD_BBOX,
        0,
        1,
        256,
        "Test Capture",
        "Test Source",
        str(tmp_path / "test.mbtiles"),
        concurrency=1,
    )

    assert result["resumable"] is False
    assert not (tmp_path / "test.mbtiles.partial").exists()


@mock.patch("tethys_basemaps.tasks._make_reader")
def test_fetch_and_build_mbtiles_bad_tile(mock_make_reader, tmp_path):
    mock_make_reader.return_value = mock.MagicMock(return_value=b"<ServiceException/>")

    result = tasks.fetch_and_build_mbtiles(
        1,
        [{"basemap_type": "xyz"}],
        WORLD_BBOX,
        0,
        0,
        256,
        "Test Capture",
        "Test Source",
        str(tmp_path / "test.mbtiles"),
        concurrency=1,
    )

    assert result["ok"] is False
    assert "Tile 0/0/0 is not a PNG, JPEG or WebP image." in result["error"]


@mock.patch("tethys_basemaps.tasks._make_reader")
def test_fetch_and_build_mbtiles_no_tiles(mock_make_reader, tmp_path):
    mock_make_reader.return_value = mock.MagicMock(return_value=None)

    result = tasks.fetch_and_build_mbtiles(
        1,
        [{"basemap_type": "xyz"}],
        WORLD_BBOX,
        0,
        1,
        256,
        "Test Capture",
        "Test Source",
        str(tmp_path / "test.mbtiles"),
        concurrency=2,
    )

    assert result["ok"] is False
    assert "The basemap has no tiles in the selected area." in result["error"]


@mock.patch("tethys_basemaps.tasks._make_reader")
def test_fetch_and_build_mbtiles_resume(mock_make_reader, tmp_path):
    output_path = tmp_path / "test.mbtiles"

    def fail_on_last_tile(z, x, y):
        if (z, x, y) == (1, 1, 1):
            raise RuntimeError("Test error")
        return PNG

    mock_make_reader.return_value = mock.MagicMock(side_effect=fail_on_last_tile)
    first = tasks.fetch_and_build_mbtiles(
        1,
        [{"basemap_type": "xyz"}],
        WORLD_BBOX,
        0,
        1,
        256,
        "Test Capture",
        "Test Source",
        str(output_path),
        concurrency=1,
    )

    assert first["resumable"] is True
    assert (tmp_path / "test.mbtiles.partial").exists()

    mock_reader = mock.MagicMock(return_value=PNG)
    mock_make_reader.return_value = mock_reader
    second = tasks.fetch_and_build_mbtiles(
        1,
        [{"basemap_type": "xyz"}],
        WORLD_BBOX,
        0,
        1,
        256,
        "Test Capture",
        "Test Source",
        str(output_path),
        concurrency=1,
        resume=True,
    )

    assert second["ok"] is True
    assert second["tiles"] == 5
    mock_reader.assert_called_once_with(1, 1, 1)


@mock.patch("tethys_basemaps.tasks._make_reader")
def test_fetch_and_build_mbtiles_resume_nothing_left(mock_make_reader, tmp_path):
    partial_path = str(tmp_path / "test.mbtiles.partial")
    conn = mbtiles.create_mbtiles(partial_path)
    mbtiles.insert_tile(conn, 0, 0, 0, JPG)
    conn.commit()
    conn.close()
    mock_reader = mock.MagicMock()
    mock_make_reader.return_value = mock_reader

    result = tasks.fetch_and_build_mbtiles(
        1,
        [{"basemap_type": "xyz"}],
        WORLD_BBOX,
        0,
        0,
        256,
        "Test Capture",
        "Test Source",
        str(tmp_path / "test.mbtiles"),
        resume=True,
    )

    assert result["ok"] is True
    assert result["tile_format"] == "jpg"
    mock_reader.assert_not_called()


@mock.patch("tethys_basemaps.tasks._make_reader")
def test_fetch_and_build_mbtiles_cancelled(mock_make_reader, tmp_path):
    cancel_path = tmp_path / "test.cancel"
    cancel_path.touch()
    progress_path = tmp_path / "test.progress.json"
    mock_reader = mock.MagicMock()
    mock_make_reader.return_value = mock_reader

    result = tasks.fetch_and_build_mbtiles(
        1,
        [{"basemap_type": "xyz"}],
        WORLD_BBOX,
        0,
        1,
        256,
        "Test Capture",
        "Test Source",
        str(tmp_path / "test.mbtiles"),
        progress_path=str(progress_path),
        cancel_path=str(cancel_path),
    )

    assert result == {
        "capture_id": 1,
        "ok": False,
        "cancelled": True,
        "done": 0,
        "total": 5,
    }
    assert not cancel_path.exists()
    assert not progress_path.exists()
    assert not (tmp_path / "test.mbtiles.partial").exists()
    mock_reader.assert_not_called()


@mock.patch("tethys_basemaps.tasks.CANCEL_CHECK_SECONDS", 0)
@mock.patch("tethys_basemaps.tasks._make_reader")
def test_fetch_and_build_mbtiles_cancelled_while_running(mock_make_reader, tmp_path):
    cancel_path = tmp_path / "test.cancel"

    def cancel_during_download(z, x, y):
        cancel_path.touch()
        return PNG

    mock_reader = mock.MagicMock(side_effect=cancel_during_download)
    mock_make_reader.return_value = mock_reader

    result = tasks.fetch_and_build_mbtiles(
        1,
        [{"basemap_type": "xyz"}],
        WORLD_BBOX,
        0,
        1,
        256,
        "Test Capture",
        "Test Source",
        str(tmp_path / "test.mbtiles"),
        concurrency=1,
        cancel_path=str(cancel_path),
    )

    assert result["cancelled"] is True
    assert not (tmp_path / "test.mbtiles.partial").exists()
    mock_reader.cancel.assert_called_once()


@mock.patch("tethys_basemaps.tasks.mbtiles.insert_tile", side_effect=KeyboardInterrupt)
@mock.patch("tethys_basemaps.tasks.mbtiles.open_mbtiles_for_writing")
@mock.patch("tethys_basemaps.tasks._make_reader")
def test_fetch_and_build_mbtiles_interrupted(
    mock_make_reader, mock_open_mbtiles, mock_insert_tile, tmp_path
):
    mock_reader = mock.MagicMock(return_value=PNG)
    mock_make_reader.return_value = mock_reader

    with pytest.raises(KeyboardInterrupt):
        tasks.fetch_and_build_mbtiles(
            1,
            [{"basemap_type": "xyz"}],
            WORLD_BBOX,
            0,
            1,
            256,
            "Test Capture",
            "Test Source",
            str(tmp_path / "test.mbtiles"),
            concurrency=1,
        )

    mock_open_mbtiles.return_value.close.assert_called_once()
    mock_reader.cancel.assert_called_once()
    mock_reader.close.assert_called_once()


def test_dask_task_state_released():
    mock_scheduler = mock.MagicMock(tasks={})

    assert tasks.dask_task_state(mock_scheduler, "test-key") == (None, None)


def test_dask_task_state_running():
    mock_task = mock.MagicMock(state="processing")
    mock_scheduler = mock.MagicMock(tasks={"test-key": mock_task})

    assert tasks.dask_task_state(mock_scheduler, "test-key") == ("processing", None)


def test_dask_task_state_erred():
    mock_task = mock.MagicMock(state="erred", exception_text="Test error")
    mock_scheduler = mock.MagicMock(tasks={"test-key": mock_task})

    assert tasks.dask_task_state(mock_scheduler, "test-key") == ("erred", "Test error")


def test_dask_task_state_erred_no_text():
    mock_task = mock.MagicMock(state="erred", exception_text="")
    mock_scheduler = mock.MagicMock(tasks={"test-key": mock_task})

    assert tasks.dask_task_state(mock_scheduler, "test-key") == ("erred", None)
