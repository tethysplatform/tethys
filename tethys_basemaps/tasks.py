"""
********************************************************************************
* Name: tasks.py
* Author: Jacob Johnson
* Created On: 2026
* Copyright: (c) Aquaveo 2026
********************************************************************************
"""

import json
import os
from pathlib import Path
import shutil
import tempfile
import traceback
from urllib.parse import parse_qsl, urlsplit
import warnings

RESPONSE_DIAGNOSTIC_HEADERS = (
    "retry-after",
    "x-ratelimit-remaining",
    "x-ratelimit-reset",
    "server",
    "via",
    "x-cache",
    "x-amz-cf-id",
)
REFUSED_STATUSES = frozenset({401, 403})
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


def _write_result(result_path, result):
    """Write the result next to the output so Tethys can pick it up without Dask."""
    if result_path:
        Path(result_path).parent.mkdir(parents=True, exist_ok=True)
        partial = f"{result_path}.partial"
        with open(partial, "w") as fh:
            json.dump(result, fh)
        os.replace(partial, result_path)
    return result


def _remove_files(*paths):
    for path in paths:
        if path:
            try:
                os.remove(path)
            except FileNotFoundError:
                pass


def _check_cancel(cancel_path):
    if cancel_path and os.path.exists(cancel_path):
        raise BasemapTaskCancelled()


def _error(id_key, record_id, exc):
    if isinstance(exc, TileFetchError):
        detail = str(exc)
    else:
        detail = f"{exc}\n{traceback.format_exc(limit=3)}"
    return {id_key: record_id, "ok": False, "error": detail}


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


def build_cog(
    image_id,
    source_path,
    output_path,
    georeference_bounds=None,
    georeference_epsg=None,
    result_path=None,
    cancel_path=None,
):
    """
    Reproject an uploaded image to a web mercator COG at output_path.

    Stops without output if the ``cancel_path`` file appears. It is checked between
    steps (each band, the COG conversion, the final copy), not during one.
    """
    partial = f"{output_path}.partial"
    try:
        # Make sure the job wasn't cancelled while it waited in the queue
        _check_cancel(cancel_path)
        import rasterio
        from rasterio.errors import NotGeoreferencedWarning
        from rasterio.warp import calculate_default_transform, reproject, Resampling
        from rasterio.shutil import copy as rio_copy
        from rasterio.transform import from_bounds

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", NotGeoreferencedWarning)
            src = rasterio.open(source_path)

        with src:
            source_epsg = src.crs.to_epsg() if src.crs else None

            if src.crs is None:
                if not georeference_bounds:
                    raise ValueError(
                        "The image has no georeferencing. Please provide georeference bounds."
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
                "driver": "GTiff",
                "dtype": src.dtypes[0],
                "count": src.count,
                "crs": dst_crs,
                "transform": transform,
                "width": width,
                "height": height,
                "tiled": True,
                "blockxsize": 512,
                "blockysize": 512,
                "compress": "DEFLATE",
            }

            with tempfile.TemporaryDirectory() as tmpdir:
                warped = Path(tmpdir) / "warped.tif"
                with rasterio.open(warped, "w", **profile) as dst:
                    for i in range(1, src.count + 1):
                        _check_cancel(cancel_path)
                        reproject(
                            source=(
                                src.read(i)
                                if src.crs is None
                                else rasterio.band(src, i)
                            ),
                            destination=rasterio.band(dst, i),
                            src_transform=src_transform,
                            src_crs=src_crs,
                            dst_transform=transform,
                            dst_crs=dst_crs,
                            resampling=Resampling.bilinear,
                            src_nodata=None,
                            dst_nodata=0,
                        )

                _check_cancel(cancel_path)
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                rio_copy(
                    warped,
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
                "source_epsg": source_epsg,
            },
        )
    except BasemapTaskCancelled:
        # Not written to result_path: the record is already marked cancelled
        _remove_files(partial, cancel_path)
        return {"image_id": image_id, "ok": False, "cancelled": True}
    except Exception as e:
        _remove_files(partial)
        return _write_result(result_path, _error("image_id", image_id, e))
