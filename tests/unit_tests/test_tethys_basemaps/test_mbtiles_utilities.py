import pytest

from unittest import mock

import sqlite3
import tethys_basemaps.mbtiles_utilities as mbtiles_utilities

SELECT_TILE = "SELECT tile_data FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?"
HAS_TILE = (
    "SELECT 1 FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?"
)


def test_tms_row():
    assert mbtiles_utilities.tms_row(0, 0) == 0
    assert mbtiles_utilities.tms_row(1, 0) == 1
    assert mbtiles_utilities.tms_row(1, 1) == 0
    assert mbtiles_utilities.tms_row(2, 1) == 2
    assert mbtiles_utilities.tms_row(3, 0) == 7


@mock.patch("tethys_basemaps.mbtiles_utilities.sqlite3.connect")
@mock.patch("tethys_basemaps.mbtiles_utilities.os.remove")
@mock.patch("tethys_basemaps.mbtiles_utilities.os.path.exists", return_value=False)
def test_create_mbtiles_new_file(mock_exist, mock_remove, mock_connect):
    path = "example/path/file.mbtiles"
    mock_conn = mock.MagicMock()
    mock_connect.return_value = mock_conn

    result = mbtiles_utilities.create_mbtiles(path)

    mock_exist.assert_called_once_with(path)
    mock_remove.assert_not_called()
    assert result == mock_conn


@mock.patch("tethys_basemaps.mbtiles_utilities.sqlite3.connect")
@mock.patch("tethys_basemaps.mbtiles_utilities.os.remove")
@mock.patch("tethys_basemaps.mbtiles_utilities.os.path.exists", return_value=True)
def test_create_mbtiles_replace_file(mock_exist, mock_remove, mock_connect):
    path = "example/path/file.mbtiles"
    mock_conn = mock.MagicMock()
    mock_connect.return_value = mock_conn

    result = mbtiles_utilities.create_mbtiles(path)

    mock_exist.assert_called_once_with(path)
    mock_remove.assert_called_once_with(path)
    assert result == mock_conn


@mock.patch("tethys_basemaps.mbtiles_utilities.create_mbtiles")
@mock.patch("tethys_basemaps.mbtiles_utilities.sqlite3.connect")
@mock.patch("tethys_basemaps.mbtiles_utilities.os.path.exists", return_value=True)
def test_open_mbtiles_for_writing_resume(mock_exist, mock_connect, mock_create):
    path = "example/path/file.mbtiles.partial"

    result = mbtiles_utilities.open_mbtiles_for_writing(path, resume=True)

    mock_exist.assert_called_once_with(path)
    mock_connect.assert_called_once_with(path)
    mock_create.assert_not_called()
    assert result == mock_connect.return_value


@mock.patch("tethys_basemaps.mbtiles_utilities.create_mbtiles")
@mock.patch("tethys_basemaps.mbtiles_utilities.sqlite3.connect")
@mock.patch("tethys_basemaps.mbtiles_utilities.os.path.exists", return_value=False)
def test_open_mbtiles_for_writing_resume_no_file(mock_exist, mock_connect, mock_create):
    path = "example/path/file.mbtiles.partial"

    result = mbtiles_utilities.open_mbtiles_for_writing(path, resume=True)

    mock_exist.assert_called_once_with(path)
    mock_connect.assert_not_called()
    mock_create.assert_called_once_with(path)
    assert result == mock_create.return_value


@mock.patch("tethys_basemaps.mbtiles_utilities.create_mbtiles")
@mock.patch("tethys_basemaps.mbtiles_utilities.sqlite3.connect")
@mock.patch("tethys_basemaps.mbtiles_utilities.os.path.exists")
def test_open_mbtiles_for_writing_no_resume(mock_exist, mock_connect, mock_create):
    path = "example/path/file.mbtiles.partial"

    result = mbtiles_utilities.open_mbtiles_for_writing(path)

    mock_exist.assert_not_called()
    mock_connect.assert_not_called()
    mock_create.assert_called_once_with(path)
    assert result == mock_create.return_value


@mock.patch("tethys_basemaps.mbtiles_utilities.sqlite3.connect")
def test_open_read_only(mock_connect):
    result = mbtiles_utilities.open_read_only("/example/path/file.mbtiles")

    mock_connect.assert_called_once_with(
        "file:///example/path/file.mbtiles?mode=ro", uri=True, check_same_thread=True
    )
    assert result == mock_connect.return_value


@mock.patch("tethys_basemaps.mbtiles_utilities.sqlite3.connect")
def test_open_read_only_other_threads(mock_connect):
    mbtiles_utilities.open_read_only(
        "/example/path/file.mbtiles", check_same_thread=False
    )

    mock_connect.assert_called_once_with(
        "file:///example/path/file.mbtiles?mode=ro", uri=True, check_same_thread=False
    )


def test_insert_tile():
    mock_conn = mock.MagicMock()

    mbtiles_utilities.insert_tile(mock_conn, 2, 1, 0, b"tile bytes")

    mock_conn.execute.assert_called_once_with(
        "INSERT OR REPLACE INTO tiles VALUES (?, ?, ?, ?)",
        (2, 1, 3, sqlite3.Binary(b"tile bytes")),
    )


def test_read_tile():
    mock_conn = mock.MagicMock()
    mock_conn.execute.return_value.fetchone.return_value = (b"tile bytes",)

    result = mbtiles_utilities.read_tile(mock_conn, 2, 1, 0)

    mock_conn.execute.assert_called_once_with(SELECT_TILE, (2, 1, 3))
    assert result == b"tile bytes"


def test_read_tile_missing():
    mock_conn = mock.MagicMock()
    mock_conn.execute.return_value.fetchone.return_value = None

    assert mbtiles_utilities.read_tile(mock_conn, 2, 1, 0) is None


def test_has_tile():
    mock_conn = mock.MagicMock()
    mock_conn.execute.return_value.fetchone.return_value = (1,)

    result = mbtiles_utilities.has_tile(mock_conn, 2, 1, 0)

    mock_conn.execute.assert_called_once_with(HAS_TILE, (2, 1, 3))
    assert result is True


def test_has_tile_missing():
    mock_conn = mock.MagicMock()
    mock_conn.execute.return_value.fetchone.return_value = None

    assert mbtiles_utilities.has_tile(mock_conn, 2, 1, 0) is False


def test_mercator_to_lonlat():
    half = mbtiles_utilities.WEB_MERCATOR_HALF_WORLD

    assert mbtiles_utilities.mercator_to_lonlat(0, 0) == (0, 0)
    assert mbtiles_utilities.mercator_to_lonlat(half, half) == pytest.approx(
        (180, 85.0511287798)
    )
    assert mbtiles_utilities.mercator_to_lonlat(-half, -half) == pytest.approx(
        (-180, -85.0511287798)
    )


def test_write_metadata():
    mock_conn = mock.MagicMock()

    mbtiles_utilities.write_metadata(
        mock_conn, "My Capture", "Test Source", "png", [0, 0, 0, 0], 3, 10
    )

    mock_conn.execute.assert_called_once_with("DELETE FROM metadata")
    sql, items = mock_conn.executemany.call_args.args
    assert sql == "INSERT INTO metadata VALUES (?, ?)"
    assert dict(items) == {
        "name": "Test Capture",
        "type": "baselayer",
        "version": "1.0",
        "description": "Captured from the Test Source basemap",
        "format": "png",
        "bounds": "0.0,0.0,0.0,0.0",
        "center": "0.0,0.0,3",
        "minzoom": "3",
        "maxzoom": "10",
    }


def test_write_metadata_no_source_name():
    mock_conn = mock.MagicMock()

    mbtiles_utilities.write_metadata(
        mock_conn, "Test Capture", "", "jpg", [0, 0, 0, 0], 3, 10
    )

    _, items = mock_conn.executemany.call_args.args
    assert dict(items)["description"] == "Test Capture"


def test_summary():
    mock_conn = mock.MagicMock()
    mock_conn.execute.return_value.fetchone.return_value = (12, 3, 10)

    result = mbtiles_utilities.summary(mock_conn)

    mock_conn.execute.assert_called_once_with(
        "SELECT COUNT(*), MIN(zoom_level), MAX(zoom_level) FROM tiles"
    )
    assert result == (12, 3, 10)


def test_get_any_tile():
    mock_conn = mock.MagicMock()
    mock_conn.execute.return_value.fetchone.return_value = (b"tile bytes",)

    result = mbtiles_utilities.get_any_tile(mock_conn)

    mock_conn.execute.assert_called_once_with("SELECT tile_data FROM tiles LIMIT 1")
    assert result == b"tile bytes"


def test_get_any_tile_empty():
    mock_conn = mock.MagicMock()
    mock_conn.execute.return_value.fetchone.return_value = None

    assert mbtiles_utilities.get_any_tile(mock_conn) is None
