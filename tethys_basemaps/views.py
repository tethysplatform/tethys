"""
********************************************************************************
* Name: views.py
* Author: Jacob Johnson
* Created On: 2026
* Copyright: (c) Aquaveo 2026
********************************************************************************
"""

import contextlib
from functools import lru_cache
import json
import logging
import math
import mimetypes
import os
import uuid

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.http import HttpResponse, HttpResponseBadRequest, FileResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.debug import sensitive_variables
from django.views.decorators.http import require_POST

from tethys_basemaps.jobs import run_basemap_task
from tethys_basemaps.models import (
    PortalBasemap,
    PortalBasemapSource,
    BasemapCapture,
    BasemapImage,
)
from tethys_basemaps.capture_sources import BrowserOnlySource, source_tile_templates
from tethys_basemaps.tasks import build_mbtiles, count_tiles, fetch_and_build_mbtiles
from tethys_compute.models import DaskScheduler
from tethys_services.models import SecureMapService

log = logging.getLogger(f"tethys.{__name__}")

MBTILES_MAX_ZOOM = 24
SECURE_CAPTURE_FETCH = {
    "max_requests_per_second": 50,
    "retry_statuses": [403, 429, 500, 502, 503, 504],
    "max_attempts": 8,
    "max_wait": 300,
}
SECURE_MAX_RATE = settings.BASEMAP_CAPTURE_SECURE_MAX_RATE
TILE_SECONDS = 0.1


@lru_cache(maxsize=32)
def _open_tile_source(path, mtime):
    from large_image_source_rasterio import open as rio_open

    style = _tile_style(path)
    if style:
        return rio_open(
            path, projection="EPSG:3857", encoding="PNG", style=json.dumps(style)
        )
    return rio_open(path, projection="EPSG:3857", encoding="PNG")


def _get_tile_source(path):
    # mtime in the cache key: a regenerated COG at the same path gets a fresh source
    return _open_tile_source(path, os.path.getmtime(path))


def _tile_style(path):
    """
    Build a style dictionary based on the image's color interpretation.
    """
    import rasterio
    from rasterio.enums import ColorInterp

    palettes = {
        ColorInterp.red: "#f00",
        ColorInterp.green: "#0f0",
        ColorInterp.blue: "#00f",
    }

    with rasterio.open(path) as ds:
        interp = ds.colorinterp

    bands = []
    for index, ci in enumerate(interp, start=1):
        if ci in palettes:
            bands.append({"band": index, "palette": palettes[ci], "min": 0, "max": 255})
        elif ci == ColorInterp.alpha:
            bands.append(
                {
                    "band": index,
                    "palette": ["#ffffff00", "#ffffffff"],
                    "min": 0,
                    "max": 255,
                    "composite": "multiply",
                }
            )

    return {"bands": bands} if bands else None


def _capture_layer(source, templates, headers, rate):
    """Build a layer dict used for downloading tiles."""
    layer = {"basemap_type": "xyz", "urls": templates, "opacity": 1}
    if headers:
        layer["headers"] = dict(headers)
    if isinstance(source, SecureMapService):
        layer["fetch"] = dict(
            getattr(settings, "BASEMAP_SECURE_CAPTURE_FETCH", SECURE_CAPTURE_FETCH)
        )
    if rate:
        layer.setdefault("fetch", {})["max_requests_per_second"] = rate
    return layer


def _concurrency_for(rate):
    """Determine the number of threads needed to reach `rate` or the default if there's no limit."""
    if not rate:
        return int(getattr(settings, "BASEMAP_CAPTURE_CONCURRENCY", 16))
    return max(2, min(16, math.ceil(rate * TILE_SECONDS)))


@login_required
def image_tile(request, image_id, z, x, y):
    """Serve one XYZ tile rendered from an image's COG."""
    try:
        image = BasemapImage.objects.get(
            pk=image_id, status=BasemapImage.StatusChoices.READY
        )
    except BasemapImage.DoesNotExist:
        return HttpResponse("Image not found or not ready.", status=404)

    try:
        tile = _get_tile_source(image.generated_file.path).getTile(x, y, z)
    except Exception as e:
        print(e)
        return HttpResponse(status=204)

    return HttpResponse(tile, content_type="image/png")


@login_required
def original_image(request, image_id):
    """The original uploaded file, for the georeference map's preview."""
    try:
        image = BasemapImage.objects.get(pk=image_id)
    except BasemapImage.DoesNotExist:
        return HttpResponse("Image not found.", status=404)
    if not image.source_file:
        return HttpResponse("Image has no source file.", status=404)

    content_type, _ = mimetypes.guess_type(image.source_file.name)
    return FileResponse(
        image.source_file.open("rb"),
        content_type=content_type or "application/octet-stream",
    )


@staff_member_required
def basemap_status(request, basemap_id):
    """Status of a capture or image while it's processing."""
    try:
        basemap = PortalBasemap.objects.select_related(
            "basemapcapture", "basemapimage"
        ).get(pk=basemap_id)
    except PortalBasemap.DoesNotExist:
        return HttpResponse(status=404)

    record = getattr(basemap, "basemapcapture", None) or getattr(
        basemap, "basemapimage", None
    )
    if record is None:
        return HttpResponse("Sources don't have a processing status.", status=404)

    status = record.refresh_status()
    data = {"id": record.pk, "status": status, "error": record.error_message}

    # Get specific progress info from the progress file if available
    progress_path = getattr(record, "progress_path", None)
    if status == "processing" and progress_path:
        with contextlib.suppress(OSError, ValueError):
            with open(progress_path) as fh:
                data.update(json.load(fh))

    return JsonResponse(data)


@staff_member_required
@require_POST
def image_cancel(request, image_id):
    """Stop an image generation that is processing on Dask."""
    try:
        image = BasemapImage.objects.get(pk=image_id)
    except BasemapImage.DoesNotExist:
        return HttpResponse("Image not found.", status=404)

    if not image.job_id:
        return HttpResponseBadRequest(
            "Only images processing on Dask can be cancelled."
        )
    if not image.cancel(request.user):
        return JsonResponse(
            {
                "error": f"The image has already finished ({image.get_status_display()}).",
                "status": image.status,
            },
            status=409,
        )
    return JsonResponse({"id": image.pk, "status": image.status})


def _capture_response(capture, tiles):
    """Build a JSON response for a BasemapCapture."""
    return JsonResponse(
        {
            "id": capture.pk,
            "name": capture.name,
            "tiles": tiles,
            "status": capture.status,
            "error": capture.error_message,
            "status_url": reverse("basemaps:basemap_status", args=[capture.pk]),
            "change_url": reverse(
                "admin:tethys_basemaps_basemapcapture_change", args=[capture.pk]
            ),
            "basemap_capture_list_url": reverse(
                "admin:tethys_basemaps_basemapcapture_changelist"
            ),
        },
        status=(
            202 if capture.status == BasemapCapture.StatusChoices.PROCESSING else 200
        ),
    )


@staff_member_required
@require_POST
def capture_upload(request):
    """
    Save tiles fetched in the browser as a BasemapCapture (an MBTiles file).

    The request should include:
        tiles: one packed file, the tile images joined end to end
        index: list of [z, x, y, length] for each tile
        bbox: the bounding box of the capture in EPSG:3857
        name: the capture's name
        source (optional): the name of the portal source or SecureMapService
    """
    tiles = request.FILES.get("tiles")
    if tiles is None:
        return HttpResponseBadRequest("No tiles were provided.")

    try:
        index = json.loads(request.POST.get("index", ""))
        bbox = [float(v) for v in request.POST.get("bbox", "").split(",")]
    except ValueError:
        return HttpResponseBadRequest("Invalid tile index or bbox.")
    if len(bbox) != 4 or bbox[0] >= bbox[2] or bbox[1] >= bbox[3]:
        return HttpResponseBadRequest("Invalid bbox.")
    if not isinstance(index, list) or not index:
        return HttpResponseBadRequest("No tiles were provided.")

    try:
        entries = [tuple(int(v) for v in entry) for entry in index]
    except (TypeError, ValueError):
        return HttpResponseBadRequest("Invalid tile index.")
    for entry in entries:
        if len(entry) != 4:
            return HttpResponseBadRequest("Invalid tile index.")
        z, x, y, length = entry
        if not (
            0 <= z <= MBTILES_MAX_ZOOM
            and 0 <= x < 2**z
            and 0 <= y < 2**z
            and length > 0
        ):
            return HttpResponseBadRequest("Invalid tile index.")
    if sum(entry[3] for entry in entries) != tiles.size:
        return HttpResponseBadRequest(
            "The tile index does not match the uploaded tiles."
        )

    name = request.POST.get("name", "").strip()[:255]
    if not name:
        return HttpResponseBadRequest("Enter a name for the capture.")

    # Find the basemap source based on the source label
    source_label = request.POST.get("source", "").strip()
    source = secure_source = None
    if source_label:
        source = PortalBasemapSource.objects.filter(name=source_label).first()
        if source is None:
            secure_source = SecureMapService.objects.filter(name=source_label).first()

    if PortalBasemap.objects.filter(name=name).exists():
        return HttpResponseBadRequest("A basemap with this name already exists.")

    # Stage the packed tiles to use when building the mbtiles file
    staging_name = default_storage.save(
        f"basemaps/captures/staging/{uuid.uuid4().hex}.tiles", tiles
    )

    # Keeps captures with the same names from overwriting each other by generating a unique output name
    output_name = BasemapCapture.unique_output_name(name)

    zooms = [entry[0] for entry in entries]
    capture = BasemapCapture.objects.create(
        name=name,
        source=source,
        secure_source=secure_source,
        status=BasemapCapture.StatusChoices.PROCESSING,
        mbtiles_file=output_name,
        min_zoom=min(zooms),
        max_zoom=max(zooms),
        min_x=bbox[0],
        min_y=bbox[1],
        max_x=bbox[2],
        max_y=bbox[3],
    )

    try:
        job = run_basemap_task(
            build_mbtiles,
            capture.pk,
            default_storage.path(staging_name),
            [list(entry) for entry in entries],
            bbox,
            name,
            source_label,
            default_storage.path(output_name),
            name=f"Build basemap capture {capture.pk}",
            user=request.user,
            result_path=capture.result_path,
            non_dask_result_handler=capture.apply_build_result,
            cancel_path=capture.cancel_path,
        )
    except Exception as e:
        log.exception("Basemap capture %s failed to build", capture.pk)
        BasemapCapture.objects.filter(pk=capture.pk).update(
            status=BasemapCapture.StatusChoices.FAILED, error_message=str(e)
        )
        job = None

    if job:
        BasemapCapture.objects.filter(pk=capture.pk).update(job=job)
    capture.refresh_from_db()
    return _capture_response(capture, len(entries))


@staff_member_required
@require_POST
@sensitive_variables("templates", "headers", "layer")
def capture_server(request):
    """
    Create a capture to run on a dask worker

    `request` will include a plan, a JSON object containing the following details for the capture:
        name: the capture's name
        source: the name of the portal source or SecureMapService
        bbox: the bounding box of the capture area in EPSG:3857 coordinates
        min_zoom: the minimum zoom level of the capture
        max_zoom: the maximum zoom level of the capture
        tile_size: the size of the tiles (256 or 512)
        dask_scheduler: the ID of the Dask scheduler to use for the capture
        max_requests_per_second: the maximum number of requests per second the capture should make
    """
    try:
        plan = json.loads(request.body)
    except ValueError:
        return HttpResponseBadRequest("Invalid capture plan.")
    if not isinstance(plan, dict):
        return HttpResponseBadRequest("Invalid capture plan.")

    name = str(plan.get("name", "")).strip()[:255]
    if not name:
        return HttpResponseBadRequest("Enter a name for the capture.")

    try:
        bbox = [float(v) for v in plan.get("bbox") or []]
        min_zoom = int(plan.get("min_zoom"))
        max_zoom = int(plan.get("max_zoom"))
        tile_size = int(plan.get("tile_size", 256))
    except (TypeError, ValueError):
        return HttpResponseBadRequest("Invalid bbox, zoom range or tile size.")
    if len(bbox) != 4 or bbox[0] >= bbox[2] or bbox[1] >= bbox[3]:
        return HttpResponseBadRequest("Invalid bbox.")
    if not (0 <= min_zoom <= max_zoom <= MBTILES_MAX_ZOOM):
        return HttpResponseBadRequest("Invalid zoom range.")
    if tile_size not in (256, 512):
        return HttpResponseBadRequest("Invalid tile size.")

    scheduler_id = plan.get("dask_scheduler", "")

    try:
        dask_scheduler = DaskScheduler.objects.get(pk=scheduler_id)
    except (DaskScheduler.DoesNotExist, ValueError):
        return HttpResponseBadRequest("Invalid Dask scheduler.")

    source_name = str(plan.get("source", "")).strip()

    source = (
        PortalBasemapSource.objects.filter(name=source_name).first()
        or SecureMapService.objects.filter(name=source_name).first()
    )

    if source is None:
        return JsonResponse(
            {
                "error": "That basemap isn't a valid portal source, so it can't be downloaded on the server.",
                "browser_only": True,
            },
            status=400,
        )
    try:
        templates, headers = source_tile_templates(source, request.user)
    except BrowserOnlySource as e:
        return JsonResponse({"error": str(e), "browser_only": True}, status=400)
    except ValueError as e:
        return HttpResponseBadRequest(str(e))

    total = count_tiles(bbox, min_zoom, max_zoom)
    if not total:
        return HttpResponseBadRequest("The selected area is outside the map.")

    if PortalBasemap.objects.filter(name=name).exists():
        return HttpResponseBadRequest(f'A basemap named "{name}" already exists.')

    is_secure = isinstance(source, SecureMapService)
    rate = plan.get("max_requests_per_second")
    if rate in (None, ""):
        rate = SECURE_CAPTURE_FETCH["max_requests_per_second"] if is_secure else None
    else:
        try:
            rate = int(rate)
        except (TypeError, ValueError):
            return HttpResponseBadRequest("Invalid max requests per second.")
        if not 1 <= rate <= SECURE_MAX_RATE:
            return HttpResponseBadRequest(
                f"Requests per second must be between 1 and {SECURE_MAX_RATE}."
            )
    capture = BasemapCapture.objects.create(
        name=name,
        source=None if is_secure else source,
        secure_source=source if is_secure else None,
        status=BasemapCapture.StatusChoices.PROCESSING,
        mbtiles_file=BasemapCapture.unique_output_name(name),
        max_requests_per_second=rate,
        downloaded_on_server=True,
        dask_scheduler=dask_scheduler,
        tile_size=tile_size,
        min_zoom=min_zoom,
        max_zoom=max_zoom,
        min_x=bbox[0],
        min_y=bbox[1],
        max_x=bbox[2],
        max_y=bbox[3],
    )
    _submit_server_download(capture, source, templates, headers, request.user)
    return _capture_response(capture, total)


@sensitive_variables("templates", "headers", "layer")  # the tile URLs can hold API keys
def _submit_server_download(capture, source, templates, headers, user):
    """
    Start the Dask job that downloads a capture's tiles, from the plan stored on it.
    """
    rate = capture.max_requests_per_second
    layer = _capture_layer(source, templates, headers, rate)
    concurrency = _concurrency_for(rate)

    try:
        job = run_basemap_task(
            fetch_and_build_mbtiles,
            capture.pk,
            [layer],
            [capture.min_x, capture.min_y, capture.max_x, capture.max_y],
            capture.min_zoom,
            capture.max_zoom,
            capture.tile_size,
            capture.name,
            source.name,
            capture.mbtiles_file.path,
            name=f"Download basemap capture {capture.pk}",
            user=user,
            result_path=capture.result_path,
            non_dask_result_handler=capture.apply_build_result,
            dask_scheduler=capture.dask_scheduler,
            progress_path=capture.progress_path,
            concurrency=concurrency,
            cancel_path=capture.cancel_path,
        )
    except Exception as e:
        log.exception("Could not start server download for capture %s", capture.pk)
        BasemapCapture.objects.filter(pk=capture.pk).update(
            status=BasemapCapture.StatusChoices.FAILED, error_message=str(e)
        )
        job = None

    if job:
        BasemapCapture.objects.filter(pk=capture.pk).update(job=job)
    capture.refresh_from_db()


@staff_member_required
@require_POST
def capture_cancel(request, capture_id):
    """Stop a capture that is processing on a dask worker."""
    try:
        capture = BasemapCapture.objects.get(pk=capture_id)
    except BasemapCapture.DoesNotExist:
        return HttpResponse("Capture not found.", status=404)

    if not capture.job_id:
        return HttpResponseBadRequest(
            "Only captures processing on Dask can be cancelled."
        )
    if not capture.cancel(request.user):
        return JsonResponse(
            {
                "error": f"The capture has already finished ({capture.get_status_display()}).",
                "status": capture.status,
            },
            status=409,
        )
    return JsonResponse({"id": capture.pk, "status": capture.status})


@login_required
def capture_tile(request, capture_id, z, x, y):
    """Retrieve a tile for a basemap capture."""
    try:
        capture = BasemapCapture.objects.get(
            pk=capture_id, status=BasemapCapture.StatusChoices.READY
        )
    except BasemapCapture.DoesNotExist:
        return HttpResponse("Capture not found or not ready.", status=404)

    tile = capture.get_tile(z, x, y)
    if tile is None:
        return HttpResponse(status=204)

    return HttpResponse(tile, content_type=capture.tile_content_type)


@staff_member_required
@require_POST
@sensitive_variables("templates")
def capture_restart(request, capture_id):
    """Download a cancelled server capture again, from the start, with its original plan."""
    try:
        capture = BasemapCapture.objects.select_related("source", "secure_source").get(
            pk=capture_id
        )
    except BasemapCapture.DoesNotExist:
        return HttpResponse("Capture not found.", status=404)

    problem = capture.restart_problem()
    if problem:
        return HttpResponseBadRequest(problem)

    source = capture.source or capture.secure_source
    try:
        templates, headers = source_tile_templates(source)
    except (BrowserOnlySource, ValueError) as e:
        return HttpResponseBadRequest(str(e))

    # Claim it with a conditional update so a double click can't start two downloads.
    # The new run gets its own files: the cancelled task may still be shutting down.
    claimed = BasemapCapture.objects.filter(
        pk=capture.pk, status=BasemapCapture.StatusChoices.CANCELLED
    ).update(
        status=BasemapCapture.StatusChoices.PROCESSING,
        error_message="",
        mbtiles_file=capture.unique_output_name(capture.name),
        job=None,
    )
    if not claimed:
        return JsonResponse(
            {"error": "The capture is no longer cancelled."}, status=409
        )

    capture.refresh_from_db()
    _submit_server_download(capture, source, templates, headers, request.user)
    # Earlier runs' leftovers (e.g. a flag from a run cancelled before it started)
    total = count_tiles(
        [capture.min_x, capture.min_y, capture.max_x, capture.max_y],
        capture.min_zoom,
        capture.max_zoom,
    )
    return _capture_response(capture, total)
