"""
********************************************************************************
* Name: mbtiles_utilities.py
* Author: Jacob Johnson
* Created On: 2026
* Copyright: (c) Aquaveo 2026
********************************************************************************

This module is used in Dask tasks, so do not import anything from django.
"""

import math
import os
from pathlib import Path
import sqlite3

SCHEMA = """
    CREATE TABLE metadata (name TEXT, value TEXT);
    CREATE TABLE tiles (
        zoom_level INTEGER, tile_column INTEGER, tile_row INTEGER, tile_data BLOB
    );
    CREATE UNIQUE INDEX tile_index ON tiles (zoom_level, tile_column, tile_row);
"""

WEB_MERCATOR_HALF_WORLD = 20037508.342789244


def tms_row(z, y):
    """MBTiles counts rows from the bottom (TMS); web maps count from the top (XYZ)."""
    return (2**z - 1) - y


def create_mbtiles(path):
    """Start a new, empty MBTiles file, replacing any existing one at that path."""
    if os.path.exists(path):
        os.remove(path)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    return conn


def open_mbtiles_for_writing(path, resume=False):
    """Reopen a partial file to resume it, or start a new one."""
    if resume and os.path.exists(path):
        return sqlite3.connect(path)
    return create_mbtiles(path)


def open_read_only(path, check_same_thread=True):
    uri = Path(path).resolve().as_uri() + "?mode=ro"
    return sqlite3.connect(uri, uri=True, check_same_thread=check_same_thread)


def insert_tile(conn, z, x, y, data):
    conn.execute(
        "INSERT OR REPLACE INTO tiles VALUES (?, ?, ?, ?)",
        (z, x, tms_row(z, y), sqlite3.Binary(data)),
    )


def read_tile(conn, z, x, y):
    """The tile's bytes, or None if the file doesn't have it."""
    row = conn.execute(
        "SELECT tile_data FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?",
        (z, x, tms_row(z, y)),
    ).fetchone()
    return row[0] if row else None


def has_tile(conn, z, x, y):
    """True if the file has the tile at z/x/y."""
    return (
        conn.execute(
            "SELECT 1 FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?",
            (z, x, tms_row(z, y)),
        ).fetchone()
        is not None
    )


def mercator_to_lonlat(x, y):
    lon = x / WEB_MERCATOR_HALF_WORLD * 180
    lat = math.degrees(
        2 * math.atan(math.exp(y / WEB_MERCATOR_HALF_WORLD * math.pi)) - math.pi / 2
    )
    return lon, lat


def write_metadata(conn, name, source_name, fmt, bbox, min_zoom, max_zoom):
    """
    Replace the file's metadata. bbox is in EPSG:3857; MBTiles stores it in degrees.
    Doesn't commit: the caller decides when its work is done.
    """
    west, south = mercator_to_lonlat(bbox[0], bbox[1])
    east, north = mercator_to_lonlat(bbox[2], bbox[3])
    metadata = {
        "name": name,
        "type": "baselayer",
        "version": "1.0",
        "description": (
            f"Captured from the {source_name} basemap" if source_name else name
        ),
        "format": fmt,
        "bounds": f"{west},{south},{east},{north}",
        "center": f"{(west + east) / 2},{(south + north) / 2},{min_zoom}",
        "minzoom": str(min_zoom),
        "maxzoom": str(max_zoom),
    }
    conn.execute("DELETE FROM metadata")
    conn.executemany("INSERT INTO metadata VALUES (?, ?)", metadata.items())


def summary(conn):
    """Returns the tile count, lowest zoom, and highest zoom in the file"""
    return conn.execute(
        "SELECT COUNT(*), MIN(zoom_level), MAX(zoom_level) FROM tiles"
    ).fetchone()


def get_any_tile(conn):
    """Return the data of any tile in the file, or None if empty."""
    row = conn.execute("SELECT tile_data FROM tiles LIMIT 1").fetchone()
    return row[0] if row else None
