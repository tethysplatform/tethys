"""
********************************************************************************
* Name: capture_sources.py
* Author: Jacob Johnson
* Created On: 2026
* Copyright: (c) Aquaveo 2026
********************************************************************************

This module provides functions and classes for handling map capture sources on Dask workers,

Many functions build the tile URL templates (and request headers) a Dask worker uses to download a
capture on the server: WMS, XYZ, Esri, CartoDB and Azure portal basemaps, and WMS Secure Map Services.
"""

import re
from urllib.parse import urlencode, urlparse

# OpenStreetMap prohibits bulk downloading of tiles from its servers
BLOCKED_CAPTURE_HOSTS = ("tile.openstreetmap.org",)

WMS_DEFAULTS = {
    "SERVICE": "WMS",
    "REQUEST": "GetMap",
    "VERSION": "1.1.1",
    "SRS": "EPSG:3857",
    "WIDTH": 256,
    "HEIGHT": 256,
    "FORMAT": "image/png",
    "TRANSPARENT": "true",
    "STYLES": "",
}


class BrowserOnlySource(ValueError):
    """Use for sources that can only be captured in the browser."""


def _get_all_subdomains(template):
    """Get all subdomains for a single map service, if applicable.
    ex: a.tile.example.com, b.tile.example.com, c.tile.example.com
    (comes in form: {a-c} or {1-4} inside the url)
    """
    match = re.search(r"\{([a-z0-9])-([a-z0-9])\}", template)
    if not match:
        return [template]
    start, end = ord(match.group(1)), ord(match.group(2))
    return [
        template[: match.start()] + chr(c) + template[match.end() :]
        for c in range(start, end + 1)
    ]


def _wms_template(name, base, params):
    params = params or {}
    upper = {k.upper(): v for k, v in params.items()}
    if not base or not upper.get("LAYERS"):
        raise ValueError(f'The "{name}" WMS source needs a "url" and params.LAYERS.')
    query = {k: v for k, v in WMS_DEFAULTS.items() if k not in upper}
    # WMS 1.1.1 names the projection parameter SRS;
    # 1.3.0 renamed it CRS.
    # The defaults use SRS, so swap it for CRS when the source asks for
    # 1.3.0 and doesn't set CRS itself.
    if str(upper.get("VERSION", "")).startswith("1.3") and "CRS" not in upper:
        query.pop("SRS", None)
        query["CRS"] = "EPSG:3857"
    query.update(params)
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}{urlencode(query, safe=',:/')}&BBOX={{bbox}}"


def _secure_template(source, user):
    endpoint, params, headers = source._server_request(user)
    if source.service_type == "ImageWMS":
        return (_wms_template(source.name, endpoint, params), headers)
    raise BrowserOnlySource(
        f"\"{source.name}\" isn't a WMS service, so it can't be downloaded on the server."
    )


def _template_for(source, user):
    from tethys_services.models import SecureMapService

    if isinstance(source, SecureMapService):
        return _secure_template(source, user)

    options = source.options or {}
    basemap_type = (source.basemap_type or "").lower()

    if basemap_type == "wms":
        return _wms_template(source.name, options.get("url"), options.get("params")), {}
    if basemap_type == "xyz":
        url = options.get("url")
        if not url:
            raise ValueError(f'The "{source.name}" source has no "url" option.')
        return url, {}
    if basemap_type == "esri":
        layer = options.get("layer", "World_Street_Map")
        return (
            f"https://server.arcgisonline.com/ArcGIS/rest/services/{layer}/MapServer/tile/{{z}}/{{y}}/{{x}}",
            {},
        )
    if basemap_type == "cartodb":
        style = options.get("style", "light")
        labels = "_nolabels" if options.get("labels") is False else "_all"
        return (
            f"https://{{1-4}}.basemaps.cartocdn.com/{style}{labels}/{{z}}/{{x}}/{{y}}.png",
            {},
        )
    if basemap_type == "azure":
        return (
            "https://atlas.microsoft.com/map/tile?api-version=2.0"
            f"&tilesetId={options.get('tilesetId', '')}&zoom={{z}}&x={{x}}&y={{y}}"
            f"&subscription-key={options.get('subscriptionKey', '')}"
        ), {}
    if basemap_type == "openstreetmap":
        raise ValueError(
            "OpenStreetMap's tile usage policy doesn't allow bulk downloads."
        )
    raise BrowserOnlySource(
        f"\"{source.name}\" isn't a {{z}}/{{x}}/{{y}} tile source, so it can't be downloaded on the server."
    )


def source_tile_templates(source, user=None):
    """
    Get the {z}/{x}/{y} URL templates the capture task should download for a source.

    Returns:
        tuple: (list of URL templates, dict of request headers)

    Raises:
        BrowserOnlySource: the server can't download this source, but the browser can.
        ValueError: the source can't be captured at all;
    """
    template, headers = _template_for(source, user)
    templates = _get_all_subdomains(template)

    for url in templates:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            raise ValueError(
                f'The "{source.name}" source doesn\'t have a full http(s) tile URL.'
            )
        host = parsed.hostname.lower()
        if any(host == p or host.endswith("." + p) for p in BLOCKED_CAPTURE_HOSTS):
            raise ValueError(f'Tiles from "{host}" can\'t be bulk downloaded.')
    return templates, headers
