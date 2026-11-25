"""
********************************************************************************
* Name: tasks.py
* Author: Jacob Johnson
* Created On: 2026
* Copyright: (c) Aquaveo 2026
********************************************************************************
Basemap image and capture tasks. These run on Dask workers, so do not import anything from Django.
"""

from collections import Counter
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import io
import json
import math
import os
from pathlib import Path
import sqlite3
import tempfile
import threading
import time
import traceback
from urllib.parse import parse_qsl, urlsplit
import warnings

from tethys_basemaps import mbtiles_utilities as mbtiles

CANCEL_CHECK_SECONDS = 1.0  # how often a download looks for its cancel flag
CANCEL_CHECK_TILES = 500  # how often (in tiles) a build looks for its cancel flag
DEFAULT_RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})
PROGRESS_EVERY = 200  # tiles between progress-file updates and actual commits
REFUSED_STATUSES = frozenset({401, 403})

# Response headers to use in error messages
RESPONSE_DIAGNOSTIC_HEADERS = (
    "retry-after",
    "x-ratelimit-remaining",
    "x-ratelimit-reset",
    "server",
    "via",
    "x-cache",
    "x-amz-cf-id",
)

TEXT_CONTENT_TYPES = (
    "text/",
    "application/xml",
    "application/json",
    "application/vnd.ogc",
)


class TileFetchError(RuntimeError):
    """A tile request the service answered with an error."""

    def __init__(self, url, response, secrets=()):
        self.status = response.status_code
        headers = response.headers
        diagnostics = {
            k: headers[k] for k in RESPONSE_DIAGNOSTIC_HEADERS if k in headers
        }

        if self.status in REFUSED_STATUSES:
            reason = (
                "The service refused the request. The credentials may be invalid or expired, "
                "or the key may have hit a rate or usage limit."
            )
        else:
            reason = "The service returned an error."

        message = f"HTTP {self.status} from {_remove_url_params(url)}. {reason}"
        if diagnostics:
            message += f" {diagnostics}"

        # Short text bodies (e.g. a WMS ServiceException) are useful, but can echo the request
        if (
            headers.get("Content-Type", "").startswith(TEXT_CONTENT_TYPES)
            and response.text
        ):
            message += f" Response: {_scrub(response.text[:300], url, secrets)}"
        super().__init__(message)


class BasemapTaskCancelled(Exception):
    """The task's cancel flag is set: stop and leave no output behind."""


def _remove_url_params(url):
    """The URL without its query params, so API keys don't show up in errors or logs."""
    p = urlsplit(url)
    return f"{p.scheme}://{p.netloc}{p.path}"


def _scrub(text, url, secrets=()):
    """Remove the URL's query values and any sensitive values from text."""
    values = [v for _, v in parse_qsl(urlsplit(url).query)] + list(secrets)
    for value in values:
        if value and len(value) >= 8:
            text = text.replace(value, "***")
    return text


def _form_error_result(id_key, record_id, exc):
    """Forms a dictionary representing a failed task's result."""
    if isinstance(exc, TileFetchError):
        detail = str(exc)
    else:
        detail = f"{exc}\n{traceback.format_exc(limit=3)}"
    return {id_key: record_id, "ok": False, "error": detail}


def _write_json(path, data):
    """Writes JSON safely, making sure that any request for the
    contents of the file will always get a full file, never a half-written one.
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    partial = f"{path}.partial"
    with open(partial, "w") as fh:
        json.dump(data, fh)
    os.replace(partial, path)


def _write_result(result_path, result):
    """Write the result next to the output so Tethys can pick it up without Dask."""
    if result_path:
        _write_json(result_path, result)
    return result


def _form_cancelled_result(id_key, record_id, **extra):
    """Forms a dictionary representing a cancelled task's result."""
    return {id_key: record_id, "ok": False, "cancelled": True, **extra}


def _check_cancel(cancel_path):
    """Raise BasemapTaskCancelled if the cancel file exists."""
    if cancel_path and os.path.exists(cancel_path):
        raise BasemapTaskCancelled()


def _remove_files(*paths):
    """Delete files if they exist."""
    for path in paths:
        if path:
            try:
                os.remove(path)
            except FileNotFoundError:
                pass
            except OSError:
                traceback.print_exc()


def tile_format(data):
    """Determine the image file format from the tile's first bytes."""
    if data.startswith(b"\x89PNG"):
        return "png"
    if data.startswith(b"\xff\xd8"):
        return "jpg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


def tile_ranges(bbox, min_zoom, max_zoom):
    """Get the range (z, min_x, max_x, min_y, max_y) of the XYZ tiles covering a bounding box"""
    h = mbtiles.WEB_MERCATOR_HALF_WORLD
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
    """How many tiles cover a bounding box over the zoom range."""
    return sum(
        (max_x - min_x + 1) * (max_y - min_y + 1)
        for _, min_x, max_x, min_y, max_y in tile_ranges(bbox, min_zoom, max_zoom)
    )


def _iter_coords(bbox, min_zoom, max_zoom):
    """Get every set of coordinates (z, x, y) that cover a bounding box, one at a time."""
    for z, min_x, max_x, min_y, max_y in tile_ranges(bbox, min_zoom, max_zoom):
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                yield z, x, y


def _composite(blobs, opacities, tile_size):
    """
    Combine one tile from each layer, like the browser does.
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


def _make_reader(layer, timeout):
    """Build the reader for a layer dict by its basemap_type."""
    basemap_type = layer.get("basemap_type")
    if basemap_type == "xyz":
        fetch = layer.get("fetch") or {}
        return _XYZReader(
            layer["urls"],
            timeout,
            headers=layer.get("headers"),
            retry_statuses=fetch.get("retry_statuses"),
            max_requests_per_second=fetch.get("max_requests_per_second"),
            max_attempts=fetch.get("max_attempts", 6),
            max_wait=fetch.get("max_wait", 120),
        )
    if basemap_type == "mbtiles":
        return _MBTilesReader(layer["path"])
    if basemap_type == "cog":
        return _COGReader(layer["path"], layer.get("style"))
    raise ValueError(f"Unknown layer basemap_type: {basemap_type}")


class _XYZReader:
    """Fetches tiles from {z}/{x}/{y} URL templates."""

    def __init__(
        self,
        urls,
        timeout,
        headers=None,
        retry_statuses=None,
        max_requests_per_second=None,
        max_attempts=6,
        max_wait=120,
    ):
        self.urls = urls
        self.timeout = timeout
        self._local = threading.local()
        self._sessions = []
        self._lock = threading.Lock()
        self.headers = headers or {}
        self.secrets = [
            part
            for value in self.headers.values()
            for part in (value, value.split(" ", 1)[-1])
        ]
        self.retry_statuses = (
            DEFAULT_RETRY_STATUSES if retry_statuses is None else retry_statuses
        )
        self.max_attempts = max_attempts
        self.max_wait = max_wait
        # Minimum time(per second) between two requests per second
        self._min_interval = (
            1 / max_requests_per_second if max_requests_per_second else 0
        )
        # The next available time slot for making a request
        self._next_slot = 0.0
        # Wait time for next request slot in case of rate limiting
        self._pause_until = 0.0
        self._cancelled = threading.Event()

    def __call__(self, z, x, y):
        import requests

        url = self._tile_url(z, x, y)
        last = self.max_attempts - 1
        for attempt in range(self.max_attempts):
            # Make sure not to exceed the rate limit for requests
            self._wait_turn()
            try:
                response = self._session().get(
                    url, timeout=self.timeout, allow_redirects=False
                )
            except requests.RequestException as e:
                if attempt == last:
                    raise RuntimeError(
                        f"Could not download {_remove_url_params(url)}: {type(e).__name__}"
                    )
                self._sleep(min(2**attempt, self.max_wait))
                continue

            status = response.status_code
            if status in (204, 404):
                return None
            if status == 200:
                return response.content or None
            if status in self.retry_statuses and attempt < last:
                self._pause_all(response, attempt)
                continue
            raise TileFetchError(url, response, secrets=self.secrets)

    def cancel(self):
        """Stop waiting and retrying. Called once the capture has already failed."""
        self._cancelled.set()

    def close(self):
        for session in self._sessions:
            session.close()

    def _session(self):
        import requests

        session = getattr(self._local, "session", None)
        if session is None:
            session = requests.Session()
            session.headers["User-Agent"] = "Tethys Platform basemap capture"
            session.headers.update(self.headers)
            self._local.session = session
            with self._lock:
                self._sessions.append(session)
        return session

    def _tile_url(self, z, x, y):
        template = self.urls[(x + y) % len(self.urls)]
        url = (
            template.replace("{z}", str(z))
            .replace("{x}", str(x))
            .replace("{-y}", str(2**z - 1 - y))
            .replace("{y}", str(y))
        )
        if "{bbox}" in url:
            # Get the corners of the tile in EPSG:3857 coordinates
            span = 2 * mbtiles.WEB_MERCATOR_HALF_WORLD / 2**z
            min_x = -mbtiles.WEB_MERCATOR_HALF_WORLD + x * span
            max_y = mbtiles.WEB_MERCATOR_HALF_WORLD - y * span
            url = url.replace(
                "{bbox}", f"{min_x},{max_y - span},{min_x + span},{max_y}"
            )
        return url

    def _wait_turn(self):
        """Make sure to not exceed the rate limit, then take the next slot under the rate cap."""
        if self._cancelled.is_set():
            raise BasemapTaskCancelled()
        with self._lock:
            now = time.monotonic()
            start = max(now, self._pause_until, self._next_slot)
            self._next_slot = start + self._min_interval
        if start > now:
            self._sleep(start - now)

    def _pause_all(self, response, attempt):
        """Pause every thread if the server indicates a retry is needed."""
        value = response.headers.get("Retry-After")
        try:
            wait = float(value) if value else 2**attempt
        except ValueError:  # Retry-After can also be an HTTP date
            wait = 2**attempt
        with self._lock:
            self._pause_until = max(
                self._pause_until, time.monotonic() + min(wait, self.max_wait)
            )

    def _sleep(self, seconds):
        if self._cancelled.wait(seconds):
            raise BasemapTaskCancelled()


class _MBTilesReader:
    """Reads tiles straight from a Basemap capture."""

    def __init__(self, path):
        self.path = path
        self._local = threading.local()
        self._conns = []
        self._lock = threading.Lock()

    def __call__(self, z, x, y):
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = mbtiles.open_read_only(self.path, check_same_thread=False)
            self._local.conn = conn
            with self._lock:
                self._conns.append(conn)
        return mbtiles.read_tile(conn, z, x, y)

    def cancel(self):
        pass

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
        from large_image.exceptions import TileSourceXYZRangeError

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
        except TileSourceXYZRangeError:
            return None  # outside the image

    def cancel(self):
        pass

    def close(self):
        pass


MOSAIC_FILL = 255  # gaps between a mosaic's images are filled with white


def _rgb_bands(src):
    """
    Which source bands give red, green and blue, and the colormap of a paletted
    image. Grayscale images use their one color band for all three.
    """
    from rasterio.enums import ColorInterp

    interp = list(src.colorinterp)
    if src.count == 1 and interp[0] == ColorInterp.palette:
        return [1, 1, 1], src.colormap(1)
    color = [i for i, ci in enumerate(interp, start=1) if ci != ColorInterp.alpha] or [
        1
    ]
    return (color[:3] if len(color) >= 3 else [color[0]] * 3), None


def _to_byte(data):
    """Clip a band to 0-255 so every image in a mosaic shares one data type."""
    import numpy as np

    if data.dtype == np.uint8:
        return data
    return np.clip(data, 0, 255).astype(np.uint8)


def _warp_source(source, out_path, cancel_path):
    """
    Reproject one source image to a web mercator RGB GeoTIFF at out_path, with
    a mask marking where the image is. Transparent parts are blended onto white.

    Returns:
        dict: the source's own EPSG code (or None) and the output's resolution.
    """
    import numpy as np
    import rasterio
    from rasterio.errors import NotGeoreferencedWarning
    from rasterio.transform import from_bounds
    from rasterio.warp import Resampling, calculate_default_transform, reproject

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", NotGeoreferencedWarning)
        src = rasterio.open(source["path"])

    with src:
        source_epsg = src.crs.to_epsg() if src.crs else None
        name = Path(source["path"]).name

        if src.crs is None:
            if not source.get("bounds"):
                raise ValueError(
                    f'"{name}" has no georeferencing. Please place it on the map.'
                )
            src_crs = rasterio.crs.CRS.from_epsg(source.get("epsg") or 3857)
            src_transform = from_bounds(*source["bounds"], src.width, src.height)
            src_bounds = tuple(source["bounds"])
        else:
            src_crs, src_transform, src_bounds = src.crs, src.transform, src.bounds

        dst_crs = "EPSG:3857"
        transform, width, height = calculate_default_transform(
            src_crs, dst_crs, src.width, src.height, *src_bounds
        )

        def warp(data, resampling):
            out = np.zeros((height, width), dtype=data.dtype)
            reproject(
                source=data,
                destination=out,
                src_transform=src_transform,
                src_crs=src_crs,
                dst_transform=transform,
                dst_crs=dst_crs,
                resampling=resampling,
                # No nodata: GDAL would nudge real 0 pixels to 1 to avoid it.
                # The warped mask below marks where the image is instead.
                init_dest_nodata=False,
            )
            return out

        # 255 where the image is, 0 where it's transparent or nodata.
        # Outside the image after the warp is 0 too.
        _check_cancel(cancel_path)
        alpha = warp(src.dataset_mask(), Resampling.nearest).astype(np.float32)

        band_indexes, colormap = _rgb_bands(src)
        if colormap:
            _check_cancel(cancel_path)
            lut = np.zeros((256, 4), dtype=np.uint8)
            for value, rgba in colormap.items():
                if 0 <= value < 256:
                    lut[value] = rgba
            rgba = lut[warp(_to_byte(src.read(1)), Resampling.nearest)]
            bands = [rgba[..., i] for i in range(3)]
            alpha *= rgba[..., 3] / 255.0
        else:
            bands, warped = [], {}
            for index in band_indexes:
                if index not in warped:
                    _check_cancel(cancel_path)
                    warped[index] = warp(_to_byte(src.read(index)), Resampling.bilinear)
                bands.append(warped[index])

    # Blend partly transparent pixels onto white, so overlaps match the gap fill
    alpha /= 255.0
    profile = {
        "driver": "GTiff",
        "dtype": "uint8",
        "count": 3,
        "crs": dst_crs,
        "transform": transform,
        "width": width,
        "height": height,
        "tiled": True,
        "blockxsize": 512,
        "blockysize": 512,
        "compress": "DEFLATE",
        "photometric": "RGB",
    }
    with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=True):
        with rasterio.open(out_path, "w", **profile) as dst:
            for i, band in enumerate(bands, start=1):
                blended = band * alpha + MOSAIC_FILL * (1.0 - alpha)
                dst.write(np.rint(blended).astype(np.uint8), i)
            dst.write_mask(alpha > 0)

    return {"epsg": source_epsg, "res": (abs(transform.a), abs(transform.e))}


def build_cog(
    image_id,
    sources,
    output_path,
    result_path=None,
    cancel_path=None,
):
    """
    Reproject each uploaded image to web mercator and mosaic them into one COG
    at output_path. Later sources are drawn on top of earlier ones, and the space
    between images is filled with white.
    """
    partial = f"{output_path}.partial"
    try:
        # Make sure the job wasn't cancelled while it waited in the queue
        _check_cancel(cancel_path)
        if not sources:
            raise ValueError("The basemap has no images to build from.")

        import rasterio
        from rasterio.merge import merge
        from rasterio.shutil import copy as rio_copy

        with tempfile.TemporaryDirectory() as tmpdir:
            warped_paths, source_epsgs, resolutions = [], {}, []
            for n, source in enumerate(sources):
                warped = str(Path(tmpdir) / f"warped_{n}.tif")
                info = _warp_source(source, warped, cancel_path)
                warped_paths.append(warped)
                source_epsgs[str(source["id"])] = info["epsg"]
                resolutions.append(info["res"])

            # Keep all detail of any image
            res = (
                min(r[0] for r in resolutions),
                min(r[1] for r in resolutions),
            )

            _check_cancel(cancel_path)
            mosaic = str(Path(tmpdir) / "mosaic.tif")
            merge(
                warped_paths,
                res=res,
                nodata=MOSAIC_FILL,
                method="last",
                dst_path=mosaic,
                dst_kwds={
                    "tiled": True,
                    "blockxsize": 512,
                    "blockysize": 512,
                    "photometric": "RGB",
                },
            )
            # The white fill is part of the picture, not missing data
            with rasterio.open(mosaic, "r+") as ds:
                ds.nodata = None

            _check_cancel(cancel_path)
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            rio_copy(
                mosaic,
                partial,
                driver="COG",
                compress="DEFLATE",
                overview_resampling="nearest",
            )

        with rasterio.open(partial) as final:
            bounds = list(final.bounds)
            srs = str(final.crs.to_epsg() or "")
            wkt = final.crs.to_wkt()

        os.replace(partial, output_path)

        return _write_result(
            result_path,
            {
                "image_id": image_id,
                "ok": True,
                "output_path": output_path,
                "bounds": bounds,
                "srs": srs,
                "wkt": wkt,
                "source_epsgs": source_epsgs,
            },
        )
    except BasemapTaskCancelled:
        _remove_files(partial, cancel_path)
        return _form_cancelled_result("image_id", image_id)
    except Exception as e:
        _remove_files(partial)
        return _write_result(result_path, _form_error_result("image_id", image_id, e))


def build_mbtiles(
    capture_id,
    packed_path,
    entries,
    bbox,
    name,
    source_name,
    output_path,
    result_path=None,
    cancel_path=None,
):
    """
    Write the capture tiles (XYZ [z, x, y, length] index) to an MBTiles file.
    """
    partial = f"{output_path}.partial"
    conn = None
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        conn = mbtiles.create_mbtiles(partial)

        formats = Counter()
        with open(packed_path, "rb") as fh:
            for i, (z, x, y, length) in enumerate(entries):
                if i % CANCEL_CHECK_TILES == 0:
                    _check_cancel(cancel_path)
                data = fh.read(length)
                fmt = tile_format(data)
                if fmt is None:
                    raise ValueError(
                        f"Tile {z}/{x}/{y} is not a PNG, JPEG or WebP image."
                    )
                formats[fmt] += 1
                mbtiles.insert_tile(conn, z, x, y, data)

        zooms = [e[0] for e in entries]
        fmt = formats.most_common(1)[0][0]
        mbtiles.write_metadata(
            conn, name, source_name, fmt, bbox, min(zooms), max(zooms)
        )
        conn.commit()
        conn.close()
        conn = None

        _check_cancel(cancel_path)
        os.replace(partial, output_path)
        return _write_result(
            result_path,
            {
                "capture_id": capture_id,
                "ok": True,
                "output_path": output_path,
                "tile_format": fmt,
                "tiles": len(entries),
            },
        )
    except BasemapTaskCancelled:
        if conn is not None:
            conn.close()
            conn = None
        _remove_files(partial, cancel_path)
        return _form_cancelled_result("capture_id", capture_id)
    except Exception as e:
        if conn is not None:
            conn.close()
            conn = None
        _remove_files(partial)
        return _write_result(
            result_path, _form_error_result("capture_id", capture_id, e)
        )
    finally:
        if conn is not None:
            conn.close()
        _remove_files(packed_path)


def fetch_and_build_mbtiles(
    capture_id,
    layers,
    bbox,
    min_zoom,
    max_zoom,
    tile_size,
    name,
    source_name,
    output_path,
    progress_path=None,
    result_path=None,
    concurrency=16,
    timeout=30,
    resume=False,
    cancel_path=None,
):
    """
    Download a basemap's tiles over a zoom range and write them to an MBTiles file.

    If the download fails, the tiles fetched so far are kept in a partial file to allow
    for resuming later.
    """
    partial = f"{output_path}.partial"
    readers = []
    conn = None
    total = count_tiles(bbox, min_zoom, max_zoom)
    done = 0

    def report():
        if progress_path:
            _write_json(progress_path, {"done": done, "total": total})

    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        readers = [_make_reader(layer, timeout) for layer in layers]
        opacities = [float(layer.get("opacity", 1)) for layer in layers]
        formats = Counter()

        def fetch_one(coord):
            z, x, y = coord
            return _composite([read(z, x, y) for read in readers], opacities, tile_size)

        conn = mbtiles.open_mbtiles_for_writing(partial, resume=resume)

        def pending():
            nonlocal done
            for z, x, y in _iter_coords(bbox, min_zoom, max_zoom):
                if resume and mbtiles.has_tile(conn, z, x, y):
                    done += 1
                    continue
                yield z, x, y

        _check_cancel(cancel_path)  # cancelled while it waited in the queue
        report()
        coords = pending()
        in_flight = {}
        last_cancel_check = time.monotonic()

        with ThreadPoolExecutor(max_workers=concurrency) as pool:

            def submit_next():
                coord = next(coords, None)
                if coord is not None:
                    in_flight[pool.submit(fetch_one, coord)] = coord

            try:
                for _ in range(concurrency):
                    submit_next()

                # Only this loop touches SQLite; the threads only fetch
                while in_flight:
                    # The timeout keeps the cancel check running while every request is
                    # slow or waiting out a throttle pause
                    finished, _ = wait(
                        in_flight,
                        timeout=CANCEL_CHECK_SECONDS,
                        return_when=FIRST_COMPLETED,
                    )
                    if time.monotonic() - last_cancel_check >= CANCEL_CHECK_SECONDS:
                        last_cancel_check = time.monotonic()
                        _check_cancel(cancel_path)
                    for future in finished:
                        z, x, y = in_flight.pop(future)
                        data = (
                            future.result()
                        )  # Raises an exception if a tile couldn't be downloaded.
                        if data:
                            fmt = tile_format(data)
                            if fmt is None:
                                raise ValueError(
                                    f"Tile {z}/{x}/{y} is not a PNG, JPEG or WebP image."
                                )
                            formats[fmt] += 1
                            mbtiles.insert_tile(conn, z, x, y, data)
                        done += 1
                        if done % PROGRESS_EVERY == 0:
                            conn.commit()
                            report()
                        submit_next()
            except BaseException:
                # Stop the other threads
                for reader in readers:
                    reader.cancel()
                pool.shutdown(wait=False, cancel_futures=True)
                raise

        # Get a summary of the stored tiles and their zoom levels
        stored, low, high = mbtiles.summary(conn)
        if not stored:
            raise ValueError("The basemap has no tiles in the selected area.")
        if formats:
            fmt = formats.most_common(1)[0][0]
        else:  # every tile came from an earlier run
            fmt = tile_format(mbtiles.get_any_tile(conn))

        mbtiles.write_metadata(conn, name, source_name, fmt, bbox, low, high)
        conn.commit()
        conn.close()
        conn = None

        _check_cancel(cancel_path)
        report()
        os.replace(partial, output_path)
        return _write_result(
            result_path,
            {
                "capture_id": capture_id,
                "ok": True,
                "output_path": output_path,
                "tile_format": fmt,
                "tiles": stored,
            },
        )
    except BasemapTaskCancelled:
        if conn is not None:
            conn.close()
            conn = None
        _remove_files(partial, progress_path, cancel_path)
        return _form_cancelled_result("capture_id", capture_id, done=done, total=total)
    except Exception as e:
        stored = 0
        if conn is not None:
            try:
                conn.commit()
                stored = mbtiles.summary(conn)[0]
            except sqlite3.Error:
                pass
            conn.close()
            conn = None
        if not stored:
            _remove_files(partial)
        report()

        result = _form_error_result("capture_id", capture_id, e)
        result["error"] = (
            f"Stopped after {done:,} of {total:,} tiles. {result['error']}"
        )
        result.update(resumable=bool(stored), done=done, total=total)
        return _write_result(result_path, result)
    finally:
        if conn is not None:
            conn.close()
        for reader in readers:
            reader.close()


def dask_task_state(dask_scheduler, key):
    """
    Run on the Dask scheduler via client.run_on_scheduler: (state, error) for a task.
    (None, None) means the scheduler no longer has the task (it finished and was released).
    """
    ts = dask_scheduler.tasks.get(key)
    if ts is None:
        return None, None
    error = getattr(ts, "exception_text", None) if ts.state == "erred" else None
    return ts.state, error or None
