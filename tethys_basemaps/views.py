"""
********************************************************************************
* Name: views.py
* Author: Jacob Johnson
* Created On: 2026
* Copyright: (c) Aquaveo 2026
********************************************************************************
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, FileResponse, JsonResponse
from django.views.decorators.http import require_POST

import contextlib
from functools import lru_cache
import json
import mimetypes
import os

from tethys_basemaps.models import BasemapImage, PortalBasemap


@lru_cache(maxsize=32)
def _open_tile_source(path, mtime):
    from large_original_image_rasterio import open as rio_open

    style = _tile_style(path)
    if style:
        return rio_open(path, projection="EPSG:3857", encoding="PNG", style=json.dumps(style))
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

    palettes = {ColorInterp.red: "#f00", ColorInterp.green: "#0f0", ColorInterp.blue: "#00f"}

    with rasterio.open(path) as ds:
        interp = ds.colorinterp

    bands = []
    for index, ci in enumerate(interp, start=1):
        if ci in palettes:
            bands.append({"band": index, "palette": palettes[ci], "min": 0, "max": 255})
        elif ci == ColorInterp.alpha:
            bands.append({
                "band": index,
                "palette": ["#ffffff00", "#ffffffff"],
                "min": 0,
                "max": 255,
                "composite": "multiply",
            })

    return {"bands": bands} if bands else None

@login_required
def image_tile(request, image_id, z, x, y):
    """Serve one XYZ tile rendered from an image's COG."""
    try:
        image = BasemapImage.objects.get(pk=image_id, status=BasemapImage.StatusChoices.READY)
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
        basemap = PortalBasemap.objects.select_related("basemapcapture", "basemapimage").get(
            pk=basemap_id
        )
    except PortalBasemap.DoesNotExist:
        return HttpResponse(status=404)

    record = getattr(basemap, "basemapcapture", None) or getattr(basemap, "basemapimage", None)
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
    # TODO implement this cancel endpoint+
    pass