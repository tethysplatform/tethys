"""
********************************************************************************
* Name: basemap_tasks.py
* Author: Jacob Johnson 
* Created On: 2026
* Copyright: (c) Aquaveo 2026
* License: 
********************************************************************************
"""

import io
import json
import math
import os
import shutil
import sqlite3
import tempfile
import threading
import time
import traceback
from collections import Counter
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

WEB_MERCATOR_HALF_WORLD = 20037508.342789244
PROGRESS_EVERY = 200  # tiles between progress-file updates and commits


def tile_format(data):
    if data.startswith(b"\x89PNG"):
        return "png"
    if data.startswith(b"\xff\xd8"):
        return "jpg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


def mercator_to_lonlat(x, y):
    lon = x / WEB_MERCATOR_HALF_WORLD * 180
    lat = math.degrees(2 * math.atan(math.exp(y / WEB_MERCATOR_HALF_WORLD * math.pi)) - math.pi / 2)
    return lon, lat


def _write_result(result_path, result):
    """Write the result next to the output (atomically) so Tethys can pick it up without Dask."""
    if result_path:
        Path(result_path).parent.mkdir(parents=True, exist_ok=True)
        partial = f"{result_path}.partial"
        with open(partial, "w") as fh:
            json.dump(result, fh)
        os.replace(partial, result_path)
    return result

def dask_task_state(dask_scheduler, key):
    """
    Run on the Dask scheduler via client.run_on_scheduler: (state, error) for a task.
    (None, None) means the scheduler no longer knows the task (it finished and was released).
    """
    ts = dask_scheduler.tasks.get(key)
    if ts is None:
        return None, None
    error = getattr(ts, "exception_text", None) if ts.state == "erred" else None
    return ts.state, error or None

def _error(id_key, record_id, exc):
    return {id_key: record_id, "ok": False, "error": f"{exc}\n{traceback.format_exc(limit=3)}"}


def build_cog(image_id, source_path, output_path, georeference_bounds=None,
                georeference_epsg=None, result_path=None):
    """Reproject an uploaded image to a web mercator COG at output_path."""
    try:
        import rasterio
        from rasterio.warp import calculate_default_transform, reproject, Resampling
        from rasterio.shutil import copy as rio_copy
        from rasterio.transform import from_bounds

        with rasterio.open(source_path) as src:
            source_epsg = src.crs.to_epsg() if src.crs else None

            if src.crs is None:
                if not georeference_bounds:
                    return _write_result(
                        result_path, {"image_id": image_id, "ok": True, "needs_georeference": True}
                    )
                src_crs = rasterio.crs.CRS.from_epsg(georeference_epsg)
                src_transform = from_bounds(*georeference_bounds, src.width, src.height)
                src_bounds = tuple(georeference_bounds)
            else:
                src_crs, src_transform, src_bounds = src.crs, src.transform, src.bounds

            dst_crs = "EPSG:3857"
            transform, width, height = calculate_default_transform(
                src_crs, dst_crs, src.width, src.height, *src_bounds
            )
            profile = {
                "driver": "GTiff", "dtype": src.dtypes[0], "count": src.count,
                "crs": dst_crs, "transform": transform, "width": width, "height": height,
                "tiled": True, "blockxsize": 512, "blockysize": 512, "compress": "DEFLATE",
            }

            with tempfile.TemporaryDirectory() as tmpdir:
                warped = Path(tmpdir) / "warped.tif"
                with rasterio.open(warped, "w", **profile) as dst:
                    for i in range(1, src.count + 1):
                        reproject(
                            source=src.read(i) if src.crs is None else rasterio.band(src, i),
                            destination=rasterio.band(dst, i),
                            src_transform=src_transform, src_crs=src_crs,
                            dst_transform=transform, dst_crs=dst_crs,
                            resampling=Resampling.bilinear, src_nodata=None, dst_nodata=0,
                        )

                cog = Path(tmpdir) / "cog.tif"
                rio_copy(warped, cog, driver="COG", compress="DEFLATE", overview_resampling="nearest")

                with rasterio.open(cog) as final:
                    bounds = list(final.bounds)
                    srs = str(final.crs.to_epsg() or "")
                    wkt = final.crs.to_wkt()

                # Copy next to the destination (streamed, not loaded into memory), then swap in atomically
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                partial = f"{output_path}.partial"
                shutil.copyfile(cog, partial)
                os.replace(partial, output_path)

        return _write_result(result_path, {
            "image_id": image_id, "ok": True, "output_path": output_path,
            "bounds": bounds, "srs": srs, "wkt": wkt, "source_epsg": source_epsg,
        })
    except Exception as e:
        return _write_result(result_path, _error("image_id", image_id, e))


def build_mbtiles(capture_id, packed_path, entries, bbox, name, source_name, output_path,
                  result_path=None):
    """Write the packed capture tiles (XYZ [z, x, y, length] index) to an MBTiles file."""
    partial = f"{output_path}.partial"
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        if os.path.exists(partial):
            os.remove(partial)

        formats = Counter()
        conn = sqlite3.connect(partial)
        try:
            conn.executescript(
                """
                CREATE TABLE metadata (name TEXT, value TEXT);
                CREATE TABLE tiles (
                    zoom_level INTEGER, tile_column INTEGER, tile_row INTEGER, tile_data BLOB
                );
                CREATE UNIQUE INDEX tile_index ON tiles (zoom_level, tile_column, tile_row);
                """
            )
            with open(packed_path, "rb") as fh:
                for z, x, y, length in entries:
                    data = fh.read(length)
                    fmt = tile_format(data)
                    if fmt is None:
                        raise ValueError(f"Tile {z}/{x}/{y} is not a PNG, JPEG or WebP image.")
                    formats[fmt] += 1
                    # MBTiles rows use the TMS scheme: row 0 is the southernmost row
                    conn.execute(
                        "INSERT OR REPLACE INTO tiles VALUES (?, ?, ?, ?)",
                        (z, x, (2**z - 1) - y, sqlite3.Binary(data)),
                    )

            west, south = mercator_to_lonlat(bbox[0], bbox[1])
            east, north = mercator_to_lonlat(bbox[2], bbox[3])
            zooms = [e[0] for e in entries]
            fmt = formats.most_common(1)[0][0]
            metadata = {
                "name": name,
                "type": "baselayer",
                "version": "1.0",
                "description": f"Captured from the {source_name} basemap" if source_name else name,
                "format": fmt,
                "bounds": f"{west},{south},{east},{north}",
                "center": f"{(west + east) / 2},{(south + north) / 2},{min(zooms)}",
                "minzoom": str(min(zooms)),
                "maxzoom": str(max(zooms)),
            }
            conn.executemany("INSERT INTO metadata VALUES (?, ?)", metadata.items())
            conn.commit()
        finally:
            conn.close()

        os.replace(partial, output_path)
        return _write_result(result_path, {
            "capture_id": capture_id, "ok": True, "output_path": output_path,
            "tile_format": fmt, "tiles": len(entries),
        })
    except Exception as e:
        if os.path.exists(partial):
            os.remove(partial)
        return _write_result(result_path, _error("capture_id", capture_id, e))
    finally:
        if os.path.exists(packed_path):
            os.remove(packed_path)

def _write_json(path, data):
    """Write JSON atomically, so readers never see a half-written file."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    partial = f"{path}.partial"
    with open(partial, "w") as fh:
        json.dump(data, fh)
    os.replace(partial, path)


def _create_mbtiles(path):
    if os.path.exists(path):
        os.remove(path)
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE metadata (name TEXT, value TEXT);
        CREATE TABLE tiles (
            zoom_level INTEGER, tile_column INTEGER, tile_row INTEGER, tile_data BLOB
        );
        CREATE UNIQUE INDEX tile_index ON tiles (zoom_level, tile_column, tile_row);
        """
    )
    return conn


def _insert_tile(conn, z, x, y, data):
    # MBTiles rows use the TMS scheme: row 0 is the southernmost row
    conn.execute(
        "INSERT OR REPLACE INTO tiles VALUES (?, ?, ?, ?)",
        (z, x, (2**z - 1) - y, sqlite3.Binary(data)),
    )


def _write_metadata(conn, name, source_name, fmt, bbox, min_zoom, max_zoom):
    west, south = mercator_to_lonlat(bbox[0], bbox[1])
    east, north = mercator_to_lonlat(bbox[2], bbox[3])
    metadata = {
        "name": name,
        "type": "baselayer",
        "version": "1.0",
        "description": f"Captured from the {source_name} basemap" if source_name else name,
        "format": fmt,
        "bounds": f"{west},{south},{east},{north}",
        "center": f"{(west + east) / 2},{(south + north) / 2},{min_zoom}",
        "minzoom": str(min_zoom),
        "maxzoom": str(max_zoom),
    }
    conn.executemany("INSERT INTO metadata VALUES (?, ?)", metadata.items())


def tile_ranges(bbox, min_zoom, max_zoom):
    """Yield (z, min_x, max_x, min_y, max_y) of the XYZ tiles covering bbox (EPSG:3857)."""
    h = WEB_MERCATOR_HALF_WORLD
    for z in range(min_zoom, max_zoom + 1):
        n = 2**z
        span = 2 * h / n
        min_x = max(0, math.floor((bbox[0] + h) / span))
        max_x = min(n - 1, math.ceil((bbox[2] + h) / span) - 1)
        min_y = max(0, math.floor((h - bbox[3]) / span))
        max_y = min(n - 1, math.ceil((h - bbox[1]) / span) - 1)
        if min_x <= max_x and min_y <= max_y:
            yield z, min_x, max_x, min_y, max_y


def count_tiles(bbox, min_zoom, max_zoom):
    return sum(
        (max_x - min_x + 1) * (max_y - min_y + 1)
        for _, min_x, max_x, min_y, max_y in tile_ranges(bbox, min_zoom, max_zoom)
    )


def _iter_coords(bbox, min_zoom, max_zoom):
    for z, min_x, max_x, min_y, max_y in tile_ranges(bbox, min_zoom, max_zoom):
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                yield z, x, y


class _XYZReader:
    """Fetches tiles from {z}/{x}/{y} URL templates. One HTTP session per thread."""

    def __init__(self, urls, timeout):
        self.urls = urls
        self.timeout = timeout
        self._local = threading.local()
        self._sessions = []
        self._lock = threading.Lock()

    def _session(self):
        import requests

        session = getattr(self._local, "session", None)
        if session is None:
            session = requests.Session()
            session.headers["User-Agent"] = "Tethys Platform basemap capture"
            self._local.session = session
            with self._lock:
                self._sessions.append(session)
        return session

    def __call__(self, z, x, y):
        import requests

        template = self.urls[(x + y) % len(self.urls)]
        url = (
            template.replace("{z}", str(z))
            .replace("{x}", str(x))
            .replace("{-y}", str(2**z - 1 - y))
            .replace("{y}", str(y))
        )
        for attempt in range(3):
            try:
                response = self._session().get(url, timeout=self.timeout, allow_redirects=False)
            except requests.RequestException as e:
                if attempt == 2:
                    raise RuntimeError(f"Could not download {url}: {e}")
                time.sleep(0.5 * (attempt + 1))
                continue

            if response.status_code in (204, 404):
                return None
            if response.status_code == 200:
                return response.content or None
            if (response.status_code == 429 or response.status_code >= 500) and attempt < 2:
                time.sleep(0.5 * (attempt + 1))
                continue
            raise RuntimeError(f"{url} returned HTTP {response.status_code}")

    def close(self):
        for session in self._sessions:
            session.close()


class _MBTilesReader:
    """Reads tiles straight from one of this portal's captures."""

    def __init__(self, path):
        self.uri = Path(path).as_uri() + "?mode=ro"
        self._local = threading.local()
        self._conns = []
        self._lock = threading.Lock()

    def __call__(self, z, x, y):
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(self.uri, uri=True, check_same_thread=False)
            self._local.conn = conn
            with self._lock:
                self._conns.append(conn)
        row = conn.execute(
            "SELECT tile_data FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?",
            (z, x, (2**z - 1) - y),
        ).fetchone()
        return row[0] if row else None

    def close(self):
        for conn in self._conns:
            conn.close()


class _COGReader:
    """Renders tiles straight from one of this portal's uploaded COGs."""

    def __init__(self, path, style=None):
        self.path = path
        self.style = style
        self._local = threading.local()

    def __call__(self, z, x, y):
        source = getattr(self._local, "source", None)
        if source is None:
            from large_image_source_rasterio import open as rio_open

            kwargs = {"projection": "EPSG:3857", "encoding": "PNG"}
            if self.style:
                kwargs["style"] = json.dumps(self.style)
            source = rio_open(self.path, **kwargs)
            self._local.source = source
        try:
            return source.getTile(x, y, z)
        except Exception:
            return None  # outside the image

    def close(self):
        pass


def _make_reader(layer, timeout):
    kind = layer.get("kind")
    if kind == "xyz":
        return _XYZReader(layer["urls"], timeout)
    if kind == "mbtiles":
        return _MBTilesReader(layer["path"])
    if kind == "cog":
        return _COGReader(layer["path"], layer.get("style"))
    raise ValueError(f"Unknown layer kind: {kind}")


def _composite(blobs, opacities, tile_size):
    """
    Combine one tile from each layer, bottom to top, like the browser does.
    A single-layer basemap keeps its original tile bytes (e.g. JPEG imagery).
    """
    if len(blobs) == 1:
        return blobs[0]
    if not any(blobs):
        return None

    from PIL import Image

    canvas = Image.new("RGBA", (tile_size, tile_size), (0, 0, 0, 0))
    for data, opacity in zip(blobs, opacities):
        if not data:
            continue
        image = Image.open(io.BytesIO(data)).convert("RGBA")
        if image.size != canvas.size:
            image = image.resize(canvas.size)
        if opacity < 1:
            image.putalpha(image.getchannel("A").point(lambda a: int(a * opacity)))
        canvas.alpha_composite(image)

    out = io.BytesIO()
    canvas.save(out, "PNG")
    return out.getvalue()


def fetch_and_build_mbtiles(capture_id, layers, bbox, min_zoom, max_zoom, tile_size, name,
                            source_name, output_path, progress_path=None, result_path=None,
                            concurrency=16, timeout=30):
    """
    Download a basemap's tiles over a zoom range and write them to an MBTiles file.

    Tiles are fetched with at most ``concurrency`` requests in flight and written to
    SQLite as they arrive, so memory stays flat no matter how big the capture is.
    Progress ({"done", "total"}) is written to ``progress_path`` as the download runs.
    """
    partial = f"{output_path}.partial"
    readers = []
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        readers = [_make_reader(layer, timeout) for layer in layers]
        opacities = [float(layer.get("opacity", 1)) for layer in layers]

        total = count_tiles(bbox, min_zoom, max_zoom)
        done = written = 0
        formats = Counter()
        zooms_written = set()

        def report():
            if progress_path:
                _write_json(progress_path, {"done": done, "total": total})

        def fetch_one(coord):
            z, x, y = coord
            return _composite([read(z, x, y) for read in readers], opacities, tile_size)

        report()
        conn = _create_mbtiles(partial)
        try:
            coords = _iter_coords(bbox, min_zoom, max_zoom)
            in_flight = {}

            with ThreadPoolExecutor(max_workers=concurrency) as pool:
                def submit_next():
                    coord = next(coords, None)
                    if coord is not None:
                        in_flight[pool.submit(fetch_one, coord)] = coord

                for _ in range(concurrency):
                    submit_next()

                # Only this loop writes to SQLite; the threads only fetch
                while in_flight:
                    finished, _ = wait(in_flight, return_when=FIRST_COMPLETED)
                    for future in finished:
                        z, x, y = in_flight.pop(future)
                        data = future.result()  # raises if a tile couldn't be downloaded
                        if data:
                            fmt = tile_format(data)
                            if fmt is None:
                                raise ValueError(f"Tile {z}/{x}/{y} is not a PNG, JPEG or WebP image.")
                            formats[fmt] += 1
                            zooms_written.add(z)
                            _insert_tile(conn, z, x, y, data)
                            written += 1
                        done += 1
                        if done % PROGRESS_EVERY == 0:
                            conn.commit()
                            report()
                        submit_next()

            if not written:
                raise ValueError("The basemap has no tiles in the selected area.")

            fmt = formats.most_common(1)[0][0]
            _write_metadata(conn, name, source_name, fmt, bbox, min(zooms_written), max(zooms_written))
            conn.commit()
        finally:
            conn.close()

        report()
        os.replace(partial, output_path)
        return _write_result(result_path, {
            "capture_id": capture_id, "ok": True, "output_path": output_path,
            "tile_format": fmt, "tiles": written,
        })
    except Exception as e:
        if os.path.exists(partial):
            os.remove(partial)
        return _write_result(result_path, _error("capture_id", capture_id, e))
    finally:
        for reader in readers:
            reader.close()