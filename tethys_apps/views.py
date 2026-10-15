"""
********************************************************************************
* Name: views.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

import contextlib
from functools import lru_cache
import ipaddress
import json
import logging
import os
import re
import socket
import uuid
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse, FileResponse, HttpResponseBadRequest
from django.core.mail import send_mail
from django.urls import Resolver404, resolve
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

@login_required()
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

MBTILES_MAX_ZOOM = 24

@login_required()
@require_POST
def basemap_capture(request):
    """
    Save basemap tiles fetched by the map view as a BasemapCapture (an MBTiles file),
    which can then be assigned to basemap services.

    The tiles arrive as one packed file (the tile images concatenated) plus an
    "index" of [z, x, y, length] entries in XYZ order. The MBTiles file is built in a
    background job; the response returns right away with the capture's status, and
    the client polls basemap_capture_status until it's ready.
    """
    from django.core.files.storage import default_storage
    from django.utils.text import slugify
    from tethys_services.basemap_jobs import run_basemap_task
    from tethys_services.basemap_tasks import build_mbtiles
    from tethys_services.models import BasemapCapture, basemap_capture_upload_path

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
    for z, x, y, length in entries:
        if not (0 <= z <= MBTILES_MAX_ZOOM and 0 <= x < 2**z and 0 <= y < 2**z and length > 0):
            return HttpResponseBadRequest("Invalid tile index.")
    if sum(entry[3] for entry in entries) != tiles.size:
        return HttpResponseBadRequest("The tile index does not match the uploaded tiles.")

    name = request.POST.get("name", "").strip()[:100]
    if not name:
        return HttpResponseBadRequest("Enter a name for the basemap.")
    source_name = request.POST.get("source", "").strip()

    use_dask = request.POST.get("use_dask") == "true"
    if use_dask and not _dask_available():
        return HttpResponseBadRequest("Dask is not available for basemap captures.")

    # Stage the packed tiles where workers can read them; the task deletes this file
    staging_name = default_storage.save(
        f"basemaps/captures/staging/{uuid.uuid4().hex}.tiles", tiles
    )

    # Pick the output name up front (get_available_name keeps same-name captures from
    # overwriting each other) and record it, so refresh_status() knows where the result goes
    output_name = default_storage.get_available_name(
        basemap_capture_upload_path(None, f"{slugify(name) or 'basemap'}.mbtiles")
    )

    zooms = [entry[0] for entry in entries]
    capture = BasemapCapture.objects.create(
        name=name,
        owner=request.user,
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
            source_name,
            default_storage.path(output_name),
            name=f"Build basemap capture {capture.pk}",
            user=request.user,
            result_path=capture.result_path,
            apply_inline=capture.apply_build_result,
            use_dask=use_dask
        )
    except Exception as e:
        logger.exception("Could not start basemap capture job")
        BasemapCapture.objects.filter(pk=capture.pk).update(
            status=BasemapCapture.StatusChoices.FAILED, error_message=str(e)
        )
        return JsonResponse({"error": "Could not start the capture job."}, status=500)

    if job:
        BasemapCapture.objects.filter(pk=capture.pk).update(job=job)
    capture.refresh_from_db()

    return JsonResponse(
        {
            "id": capture.pk,
            "name": capture.name,
            "tiles": len(entries),
            "min_zoom": capture.min_zoom,
            "max_zoom": capture.max_zoom,
            "status": capture.status,
            "error": capture.error_message,
        },
        status=202 if capture.status == BasemapCapture.StatusChoices.PROCESSING else 200,
    )

@login_required()
def basemap_capture_status(request, capture_id):
    from tethys_services.models import BasemapCapture

    try:
        capture = BasemapCapture.objects.get(pk=capture_id, owner=request.user)
    except BasemapCapture.DoesNotExist:
        return HttpResponse(status=404)

    status = capture.refresh_status()
    data = {"id": capture.pk, "status": status, "error": capture.error_message}

    # Server-downloaded captures report {"done", "total"} while they run
    if status == BasemapCapture.StatusChoices.PROCESSING and capture.progress_path:
        with contextlib.suppress(OSError, ValueError):
            with open(capture.progress_path) as fh:
                data.update(json.load(fh))

    return JsonResponse(data)


# OpenStreetMap's tile usage policy prohibits bulk downloading from its servers
BLOCKED_CAPTURE_HOSTS = ("tile.openstreetmap.org",)


def _host_matches(host, patterns):
    return any(host == p or host.endswith("." + p) for p in patterns)


def _is_public_host(host):
    """True if every address the host resolves to is public (keeps captures from probing internal hosts)."""
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            return False
    return True

class _BrowserOnlyLayer(ValueError):
    """The server can't download this layer, but the browser can."""

def _resolve_capture_layer(layer, request):
    """
    Turn a layer from the browser's capture plan into something the capture task can read.

    Basemaps served by this portal are read straight from their files (the tile view
    needs a login the task doesn't have). Other basemaps are downloaded from their
    {z}/{x}/{y} URL templates, after checking the host.

    Raises:
        ValueError: with a message to show the user.
    """
    from tethys_services.models import BasemapImage

    if not isinstance(layer, dict):
        raise ValueError("Invalid basemap layer.")
    urls = layer.get("urls")
    if not isinstance(urls, list) or not urls or not all(isinstance(u, str) for u in urls):
        raise ValueError("Invalid basemap layer URLs.")
    try:
        opacity = min(1.0, max(0.0, float(layer.get("opacity", 1))))
    except (TypeError, ValueError):
        raise ValueError("Invalid basemap layer opacity.")

    # Browsers may percent-encode the braces in {z}/{x}/{y}
    templates = [re.sub("%7d", "}", re.sub("%7b", "{", u, flags=re.I), flags=re.I) for u in urls]

    # A basemap served by this portal: read its file directly
    parsed = urlparse(templates[0])
    if parsed.netloc in ("", request.get_host()):
        concrete = re.sub(r"\{-?[xyz]\}", "0", parsed.path)
        try:
            match = resolve(concrete)
        except Resolver404:
            match = None
        if match and match.url_name == "basemap_tile":
            try:
                image = BasemapImage.objects.get(
                    pk=match.kwargs["image_id"], status=BasemapImage.StatusChoices.READY
                )
            except BasemapImage.DoesNotExist:
                raise ValueError("That uploaded basemap isn't ready.")
            if image.capture_id:
                return {"kind": "mbtiles", "path": image.capture.mbtiles_file.path, "opacity": opacity}
            path = image.generated_file.path
            return {"kind": "cog", "path": path, "style": _tile_style(path), "opacity": opacity}

    # Anything else: download it, if the host is allowed
    allowed_hosts = getattr(settings, "BASEMAP_CAPTURE_ALLOWED_HOSTS", None) or []
    for template in templates:
        p = urlparse(template)
        if p.scheme not in ("http", "https") or not p.hostname:
            raise ValueError(f"Unsupported tile URL: {template}")
        if "{z}" not in template or "{x}" not in template or not ("{y}" in template or "{-y}" in template):
            raise ValueError(f"Not a {{z}}/{{x}}/{{y}} tile URL: {template}")

        host = p.hostname.lower()
        if _host_matches(host, BLOCKED_CAPTURE_HOSTS):
            raise _BrowserOnlyLayer(f'Tiles from "{host}" aren\'t downloaded on the server.')
        if allowed_hosts:
            if not _host_matches(host, [h.lower() for h in allowed_hosts]):
                raise _BrowserOnlyLayer(f'Tiles from "{host}" aren\'t downloaded on the server.')
        elif not _is_public_host(host):
            raise _BrowserOnlyLayer(f'Tiles from "{host}" aren\'t downloaded on the server.')

    return {"kind": "xyz", "urls": templates, "opacity": opacity}


def _dask_available():
    """True when BASEMAP_DASK_SCHEDULER names an existing Dask scheduler."""
    from tethys_services.basemap_jobs import get_basemap_scheduler

    return get_basemap_scheduler() is not None


@login_required()
def basemap_capture_config(request):
    """Tell the map view whether it can offer the Dask options for captures."""
    return JsonResponse({"dask_available": _dask_available()})


@login_required()
@require_POST
def basemap_capture_server(request):
    """
    Start a capture that a Dask worker downloads itself (USE_BASEMAP_UPLOAD_DASK on).

    The browser sends only the plan as JSON: name, source label, bbox (EPSG:3857),
    zoom range, tile size and each layer's {z}/{x}/{y} URL templates and opacity.
    A background job downloads the tiles into an MBTiles file; the client polls
    basemap_capture_status for progress and completion.
    """
    from django.core.files.storage import default_storage
    from django.utils.text import slugify
    from tethys_services.basemap_jobs import run_basemap_task
    from tethys_services.basemap_tasks import count_tiles, fetch_and_build_mbtiles
    from tethys_services.models import BasemapCapture, basemap_capture_upload_path

    if not _dask_available():
        return HttpResponseBadRequest("Downloading basemaps on the server is not available.")

    try:
        plan = json.loads(request.body)
    except ValueError:
        return HttpResponseBadRequest("Invalid capture plan.")
    if not isinstance(plan, dict):
        return HttpResponseBadRequest("Invalid capture plan.")

    name = str(plan.get("name", "")).strip()[:100]
    if not name:
        return HttpResponseBadRequest("Enter a name for the basemap.")
    source_name = str(plan.get("source", "")).strip()

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

    layers = plan.get("layers")
    if not isinstance(layers, list) or not layers:
        return HttpResponseBadRequest("The basemap has no layers to download.")
    try:
        resolved_layers = [_resolve_capture_layer(layer, request) for layer in layers]
    except _BrowserOnlyLayer as e:
        return JsonResponse({"error": str(e), "browser_only": True}, status=400)
    except ValueError as e:
        return HttpResponseBadRequest(str(e))
    total = count_tiles(bbox, min_zoom, max_zoom)
    if not total:
        return HttpResponseBadRequest("The selected area is outside the map.")

    output_name = default_storage.get_available_name(
        basemap_capture_upload_path(None, f"{slugify(name) or 'basemap'}.mbtiles")
    )
    capture = BasemapCapture.objects.create(
        name=name,
        owner=request.user,
        status=BasemapCapture.StatusChoices.PROCESSING,
        mbtiles_file=output_name,
        min_zoom=min_zoom,
        max_zoom=max_zoom,
        min_x=bbox[0],
        min_y=bbox[1],
        max_x=bbox[2],
        max_y=bbox[3],
    )

    try:
        job = run_basemap_task(
            fetch_and_build_mbtiles,
            capture.pk,
            resolved_layers,
            bbox,
            min_zoom,
            max_zoom,
            tile_size,
            name,
            source_name,
            default_storage.path(output_name),
            name=f"Download basemap capture {capture.pk}",
            user=request.user,
            result_path=capture.result_path,
            apply_inline=capture.apply_build_result,
            use_dask=True,
            progress_path=capture.progress_path,
            concurrency=int(getattr(settings, "BASEMAP_CAPTURE_CONCURRENCY", 16)),
        )
    except Exception as e:
        logger.exception("Could not start basemap capture job")
        BasemapCapture.objects.filter(pk=capture.pk).update(
            status=BasemapCapture.StatusChoices.FAILED, error_message=str(e)
        )
        return JsonResponse({"error": "Could not start the capture job."}, status=500)

    if job:
        BasemapCapture.objects.filter(pk=capture.pk).update(job=job)
    capture.refresh_from_db()

    return JsonResponse(
        {
            "id": capture.pk,
            "name": capture.name,
            "tiles": total,
            "min_zoom": capture.min_zoom,
            "max_zoom": capture.max_zoom,
            "status": capture.status,
            "error": capture.error_message,
        },
        status=202 if capture.status == BasemapCapture.StatusChoices.PROCESSING else 200,
    )