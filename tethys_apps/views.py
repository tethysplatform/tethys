"""
********************************************************************************
* Name: views.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

from functools import lru_cache
import json
import logging
import os
import requests
import tempfile

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse, FileResponse, HttpResponseBadRequest
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from large_image_source_rasterio import open as rio_open


from tethys_config.models import get_custom_template
from .base.app_base import TethysAppBase
from .models import TethysApp
from .utilities import get_active_app, user_can_access_app
from .models import ProxyApp
from .decorators import login_required

logger = logging.getLogger("tethys." + __name__)

# Forwarded so the browser's cached-copy check reaches the service and it can
# reply 304 instead of resending the whole body.
PROXY_FORWARDED_REQUEST_HEADERS = ("If-None-Match", "If-Modified-Since")

# Forwarded so the browser can cache proxied responses instead of making a new request
# on every pan and zoom.
PROXY_FORWARDED_RESPONSE_HEADERS = (
    "Cache-Control",
    "ETag",
    "Expires",
    "Last-Modified",
    "Vary",
    "Age",
)

MBTILES_MAX_TILES = 10_000    # Keep in sync with MBTILES_MAX_TILES in tethys_map_view.js
MBTILES_MAX_ZOOM = 24
WEB_MERCATOR_HALF_WORLD = 20037508.342789244


@login_required()
def library(request):
    """
    Handle the library view
    """
    # Retrieve the app harvester
    apps = TethysApp.objects.all()

    configured_apps = list()
    unconfigured_apps = list()

    for app in apps:
        if request.user.is_staff:
            if app.configured:
                configured_apps.append(app)
            else:
                unconfigured_apps.append(app)
        elif user_can_access_app(request.user, app):
            if app.configured and app.show_in_apps_library:
                configured_apps.append(app)

    # Fetch any proxied apps (these are always assumed to be configured)
    proxy_apps = ProxyApp.objects.all()

    for proxy_app in proxy_apps:
        if request.user.is_staff or (
            proxy_app.enabled
            and proxy_app.show_in_apps_library
            and user_can_access_app(request.user, proxy_app)
        ):
            configured_apps.append(proxy_app)

    # sort apps alphabetically
    configured_apps.sort(key=lambda a: a.name)

    # sort apps by order
    configured_apps.sort(key=lambda a: a.order)

    # Define the context object
    context = {
        "apps": {"configured": configured_apps, "unconfigured": unconfigured_apps}
    }

    template = get_custom_template(
        "Apps Library Template", "tethys_apps/app_library.html"
    )

    return render(request, template, context)


@login_required()
def handoff_capabilities(request, app_name):
    """
    Show handoff capabilities of the app name provided.
    """
    app_name = app_name.replace("-", "_")

    manager = TethysAppBase.get_handoff_manager()
    handlers = manager.get_capabilities(app_name, external_only=True, jsonify=True)

    return HttpResponse(handlers, content_type="application/javascript")


@login_required()
def handoff(request, app_name, handler_name):
    """
    Handle handoff requests.
    """
    app_name = app_name.replace("-", "_")

    manager = TethysAppBase.get_handoff_manager()

    return manager.handoff(request, handler_name, app_name, **request.GET.dict())


@login_required()
def send_beta_feedback_email(request):
    """
    Processes and send the beta form data submitted by beta testers
    """
    # Form parameters
    post = request.POST

    # Get url and parts
    url = post.get("betaFormUrl")

    # Get app
    app = get_active_app(url=url)

    if app is None or not hasattr(app, "feedback_emails"):
        json = {
            "success": False,
            "error": "App not found or feedback_emails not defined in app.py",
        }
        return JsonResponse(json)

    # Formulate email
    subject = "User Feedback for {0}".format(app.name.encode("utf-8"))

    message = (
        "User: {0}\n"
        "User Local Time: {1}\n"
        "UTC Offset in Hours: {2}\n"
        "App URL: {3}\n"
        "User Agent: {4}\n"
        "Vendor: {5}\n"
        "Comments:\n"
        "{6}".format(
            post.get("betaUser"),
            post.get("betaSubmitLocalTime"),
            post.get("betaSubmitUTCOffset"),
            post.get("betaFormUrl"),
            post.get("betaFormUserAgent"),
            post.get("betaFormVendor"),
            post.get("betaUserComments"),
        )
    )

    try:
        send_mail(subject, message, from_email=None, recipient_list=app.feedback_emails)
    except Exception as e:
        json = {"success": False, "error": "Failed to send email: " + str(e)}
        return JsonResponse(json)

    json = {"success": True, "result": "Emails sent to specified developers"}
    return JsonResponse(json)


@login_required()
def secure_map_proxy(request, setting_id):
    """
    Proxy view for securely accessing map services with credentials stored in Tethys Services or OAuth.
    """
    from tethys_services.models import SecureMapService

    try:
        service = SecureMapService.objects.get(id=setting_id)
    except SecureMapService.DoesNotExist:
        return HttpResponse("Service setting not found.", status=404)

    browser_params = {key: value for key, value in request.GET.items()}
    service_params = service.get_resolved_params()
    params = {**service_params, **browser_params}

    headers = {}
    if service.authentication_method == "oauth":
        access_token = service.get_oauth_token(request.user)
        if not access_token:
            return HttpResponse("Failed to retrieve OAuth token.", status=500)
        headers["Authorization"] = f"Bearer {access_token}"

    if request.content_type:
        headers["Content-Type"] = request.content_type

    for header in PROXY_FORWARDED_REQUEST_HEADERS:
        value = request.headers.get(header)
        if value:
            headers[header] = value

    resp = requests.request(
        method=request.method,
        url=service.endpoint,
        params=params,
        headers=headers,
        data=request.body if request.body else None,
        stream=True,
    )

    # A 304 has no body, so return it directly rather than returning an empty response
    if resp.status_code == 304:
        proxy_response = HttpResponse(status=304)
    else:
        proxy_response = StreamingHttpResponse(
            resp.iter_content(chunk_size=8192),
            status=resp.status_code,
            content_type=resp.headers.get("Content-Type", "application/octet-stream"),
        )

    for header in PROXY_FORWARDED_RESPONSE_HEADERS:
        value = resp.headers.get(header)
        if value:
            proxy_response[header] = value

    return proxy_response

def _tile_style(path):
    """
    Explicit large_image style: RGB at the full 8-bit range (no per-band min/max stretch)
    and an alpha band applied as transparency. The default stretch turns a constant
    alpha band (e.g. fully opaque) into fully transparent tiles.
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

@lru_cache(maxsize=32)
def _open_source(path, mtime):
    style = _tile_style(path)
    if style:
        return rio_open(path, projection="EPSG:3857", encoding="PNG", style=json.dumps(style))
    return rio_open(path, projection="EPSG:3857", encoding="PNG")

def _get_source(path):
    return _open_source(path, os.path.getmtime(path))

# @login_required()
def basemap_tile(request, image_id, z, x, y):
    from tethys_services.models import BasemapImage
    z, x, y = int(z), int(x), int(y)

    try:
        image = BasemapImage.objects.get(
            pk=image_id, status=BasemapImage.StatusChoices.READY
        )

    except BasemapImage.DoesNotExist:
        return HttpResponse("Basemap image not found or not ready.", status=404)

    if image.capture_id:
        tile = image.capture.get_tile(z, x, y)
        if tile is None:
            return HttpResponse(status=204)
        return HttpResponse(tile, content_type=image.capture.tile_content_type)

    ts = _get_source(image.generated_file.path)

    try:
        tile = ts.getTile(x, y, z)
    except Exception:
        # Outside the image extent — OpenLayers requests a full grid,
        # so most tiles at low zoom fall here. Not an error.
        return HttpResponse(status=204)

    return HttpResponse(tile, content_type="image/png")

@login_required()
def basemap_source_file(request, image_id):
    import mimetypes
    from tethys_services.models import BasemapImage

    try:
        image = BasemapImage.objects.get(pk=image_id)
    except BasemapImage.DoesNotExist:
        return HttpResponse("Basemap image not found.", status=404)

    content_type, _ = mimetypes.guess_type(image.source_file.path)

    return FileResponse(
        image.source_file.open("rb"),
        content_type=content_type or "application/octet-stream"
    )

def _mercator_to_lonlat(x, y):
    import math

    lon = x / WEB_MERCATOR_HALF_WORLD * 180
    lat = math.degrees(2 * math.atan(math.exp(y / WEB_MERCATOR_HALF_WORLD * math.pi)) - math.pi / 2)
    return lon, lat


def _tile_format(data):
    if data.startswith(b"\x89PNG"):
        return "png"
    if data.startswith(b"\xff\xd8"):
        return "jpg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


@login_required()
@require_POST
def basemap_capture(request):
    """
    Save basemap tiles fetched by the map view as a BasemapCapture (an MBTiles file),
    which can then be assigned to basemap services.

    The tiles arrive as one packed file (the tile images concatenated) plus an
    "index" of [z, x, y, length] entries in XYZ order, so the upload is a single
    file no matter how many tiles there are.
    """
    import sqlite3
    from collections import Counter
    from django.core.files import File
    from django.utils.text import slugify
    from tethys_services.models import BasemapCapture

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
    if len(index) > MBTILES_MAX_TILES:
        return HttpResponseBadRequest(f"Too many tiles (the limit is {MBTILES_MAX_TILES}).")

    try:
        entries = [tuple(int(v) for v in entry) for entry in index]
    except (TypeError, ValueError):
        return HttpResponseBadRequest("Invalid tile index.")
    for z, x, y, length in entries:
        if not (0 <= z <= MBTILES_MAX_ZOOM and 0 <= x < 2**z and 0 <= y < 2**z and length > 0):
            return HttpResponseBadRequest("Invalid tile index.")
    if sum(entry[3] for entry in entries) != tiles.size:
        return HttpResponseBadRequest("The tile index does not match the uploaded tiles.")

    name = request.POST.get("name", "").strip()[:100]
    if not name:
        return HttpResponseBadRequest("Enter a name for the basemap.")
    source_name = request.POST.get("source", "").strip()

    out = tempfile.NamedTemporaryFile(suffix=".mbtiles", delete=False)
    out.close()

    try:
        formats = Counter()
        conn = sqlite3.connect(out.name)
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

            with tiles.open("rb") as fh:
                for z, x, y, length in entries:
                    data = fh.read(length)
                    tile_format = _tile_format(data)
                    if tile_format is None:
                        return HttpResponseBadRequest("A tile is not a PNG, JPEG or WebP image.")
                    formats[tile_format] += 1
                    # MBTiles rows use the TMS scheme: row 0 is the southernmost row
                    conn.execute(
                        "INSERT OR REPLACE INTO tiles VALUES (?, ?, ?, ?)",
                        (z, x, (2**z - 1) - y, sqlite3.Binary(data)),
                    )

            west, south = _mercator_to_lonlat(bbox[0], bbox[1])
            east, north = _mercator_to_lonlat(bbox[2], bbox[3])
            zooms = [entry[0] for entry in entries]
            tile_format = formats.most_common(1)[0][0]
            metadata = {
                "name": name,
                "type": "baselayer",
                "version": "1.0",
                "description": f"Captured from the {source_name} basemap" if source_name else name,
                "format": tile_format,
                "bounds": f"{west},{south},{east},{north}",
                "center": f"{(west + east) / 2},{(south + north) / 2},{min(zooms)}",
                "minzoom": str(min(zooms)),
                "maxzoom": str(max(zooms)),
            }
            conn.executemany("INSERT INTO metadata VALUES (?, ?)", metadata.items())
            conn.commit()
        finally:
            conn.close()

        capture = BasemapCapture(
            name=name,
            owner=request.user,
            tile_format=tile_format,
            min_zoom=min(zooms),
            max_zoom=max(zooms),
            min_x=bbox[0],
            min_y=bbox[1],
            max_x=bbox[2],
            max_y=bbox[3],
        )
        with open(out.name, "rb") as fh:
            capture.mbtiles_file.save(
                f"{slugify(name) or 'basemap'}.mbtiles", File(fh), save=False
            )
        try:
            capture.save()
        except Exception:
            capture.mbtiles_file.delete(save=False)
            raise
    finally:
        os.unlink(out.name)

    return JsonResponse({
        "id": capture.pk,
        "name": capture.name,
        "tiles": len(entries),
        "min_zoom": capture.min_zoom,
        "max_zoom": capture.max_zoom,
    })
