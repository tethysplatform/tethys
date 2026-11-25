from unittest import mock

import pytest

import tethys_basemaps.capture_sources as capture_sources
from tethys_basemaps.models import PortalBasemapSource
from tethys_services.models import SecureMapService

WMS_URL = "https://example.com/wms"
WMS_QUERY = (
    "SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1&SRS=EPSG:3857&WIDTH=256&HEIGHT=256"
    "&FORMAT=image/png&TRANSPARENT=true&STYLES=&LAYERS=topp:states&BBOX={bbox}"
)


def test_get_all_subdomains_none():
    template = "https://tile.example.com/{z}/{x}/{y}.png"

    assert capture_sources._get_all_subdomains(template) == [template]


def test_get_all_subdomains_letters():
    template = "https://{a-c}.tile.example.com/{z}/{x}/{y}.png"

    assert capture_sources._get_all_subdomains(template) == [
        "https://a.tile.example.com/{z}/{x}/{y}.png",
        "https://b.tile.example.com/{z}/{x}/{y}.png",
        "https://c.tile.example.com/{z}/{x}/{y}.png",
    ]


def test_get_all_subdomains_numbers():
    template = "https://{1-4}.tile.example.com/{z}/{x}/{y}.png"

    assert capture_sources._get_all_subdomains(template) == [
        "https://1.tile.example.com/{z}/{x}/{y}.png",
        "https://2.tile.example.com/{z}/{x}/{y}.png",
        "https://3.tile.example.com/{z}/{x}/{y}.png",
        "https://4.tile.example.com/{z}/{x}/{y}.png",
    ]


def test_wms_template():
    result = capture_sources._wms_template(
        "Test WMS", WMS_URL, {"LAYERS": "topp:states"}
    )

    assert result == f"{WMS_URL}?{WMS_QUERY}"


def test_wms_template_url_with_query():
    result = capture_sources._wms_template(
        "Test WMS", f"{WMS_URL}?map=test", {"LAYERS": "topp:states"}
    )

    assert result == f"{WMS_URL}?map=test&{WMS_QUERY}"


def test_wms_template_params_override_defaults():
    result = capture_sources._wms_template(
        "Test WMS", WMS_URL, {"LAYERS": "topp:states", "FORMAT": "image/jpeg"}
    )

    assert "FORMAT=image/jpeg" in result
    assert "FORMAT=image/png" not in result


def test_wms_template_version_1_3():
    result = capture_sources._wms_template(
        "Test WMS", WMS_URL, {"LAYERS": "topp:states", "VERSION": "1.3.0"}
    )

    assert "CRS=EPSG:3857" in result
    assert "SRS=" not in result
    assert "VERSION=1.3.0" in result


def test_wms_template_no_url():
    with pytest.raises(ValueError, match='needs a "url" and params.LAYERS'):
        capture_sources._wms_template("Test WMS", None, {"LAYERS": "topp:states"})


def test_wms_template_no_layers():
    with pytest.raises(ValueError, match='needs a "url" and params.LAYERS'):
        capture_sources._wms_template("Test WMS", WMS_URL, None)


def test_secure_template_wms():
    source = SecureMapService(name="Test Secure", service_type="ImageWMS")
    source._server_request = mock.MagicMock(
        return_value=(WMS_URL, {"LAYERS": "topp:states"}, {"Authorization": "Bearer t"})
    )
    user = mock.MagicMock()

    template, headers = capture_sources._secure_template(source, user)

    source._server_request.assert_called_once_with(user)
    assert template == f"{WMS_URL}?{WMS_QUERY}"
    assert headers == {"Authorization": "Bearer t"}


def test_secure_template_not_wms():
    source = SecureMapService(name="Test Secure", service_type="GML")
    source._server_request = mock.MagicMock(return_value=(WMS_URL, {}, {}))

    with pytest.raises(capture_sources.BrowserOnlySource, match="isn't a WMS service"):
        capture_sources._secure_template(source, mock.MagicMock())


@mock.patch("tethys_basemaps.capture_sources._secure_template")
def test_template_for_secure_map_service(mock_secure_template):
    source = SecureMapService(name="Test Secure", service_type="ImageWMS")
    user = mock.MagicMock()

    result = capture_sources._template_for(source, user)

    mock_secure_template.assert_called_once_with(source, user)
    assert result == mock_secure_template.return_value


def test_template_for_wms():
    source = PortalBasemapSource(
        name="Test WMS",
        basemap_type="WMS",
        options={"url": WMS_URL, "params": {"LAYERS": "topp:states"}},
    )

    assert capture_sources._template_for(source, None) == (f"{WMS_URL}?{WMS_QUERY}", {})


def test_template_for_xyz():
    source = PortalBasemapSource(
        name="Test XYZ",
        basemap_type="XYZ",
        options={"url": "https://tile.example.com/{z}/{x}/{y}.png"},
    )

    assert capture_sources._template_for(source, None) == (
        "https://tile.example.com/{z}/{x}/{y}.png",
        {},
    )


def test_template_for_xyz_no_url():
    source = PortalBasemapSource(name="Test XYZ", basemap_type="XYZ", options=None)

    with pytest.raises(ValueError, match='has no "url" option'):
        capture_sources._template_for(source, None)


def test_template_for_esri_default_layer():
    source = PortalBasemapSource(name="Test ESRI", basemap_type="ESRI", options={})

    assert capture_sources._template_for(source, None) == (
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map"
        "/MapServer/tile/{z}/{y}/{x}",
        {},
    )


def test_template_for_esri_layer():
    source = PortalBasemapSource(
        name="Test ESRI", basemap_type="ESRI", options={"layer": "World_Imagery"}
    )

    template, _ = capture_sources._template_for(source, None)

    assert "/World_Imagery/MapServer/" in template


def test_template_for_cartodb_default():
    source = PortalBasemapSource(name="Test CartoDB", basemap_type="CartoDB")

    assert capture_sources._template_for(source, None) == (
        "https://{1-4}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
        {},
    )


def test_template_for_cartodb_no_labels():
    source = PortalBasemapSource(
        name="Test CartoDB",
        basemap_type="CartoDB",
        options={"style": "dark", "labels": False},
    )

    template, _ = capture_sources._template_for(source, None)

    assert (
        template == "https://{1-4}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}.png"
    )


def test_template_for_azure():
    source = PortalBasemapSource(
        name="Test Azure",
        basemap_type="Azure",
        options={"tilesetId": "microsoft.imagery", "subscriptionKey": "test-key"},
    )

    assert capture_sources._template_for(source, None) == (
        "https://atlas.microsoft.com/map/tile?api-version=2.0"
        "&tilesetId=microsoft.imagery&zoom={z}&x={x}&y={y}"
        "&subscription-key=test-key",
        {},
    )


def test_template_for_openstreetmap():
    source = PortalBasemapSource(name="Test OSM", basemap_type="OpenStreetMap")

    with pytest.raises(ValueError, match="doesn't allow bulk downloads"):
        capture_sources._template_for(source, None)


def test_template_for_unknown_type():
    source = PortalBasemapSource(name="Test Unknown", basemap_type="Unknown")

    with pytest.raises(capture_sources.BrowserOnlySource, match="tile source"):
        capture_sources._template_for(source, None)


def test_source_tile_templates():
    source = PortalBasemapSource(
        name="Test XYZ",
        basemap_type="XYZ",
        options={"url": "https://{a-b}.tile.example.com/{z}/{x}/{y}.png"},
    )

    templates, headers = capture_sources.source_tile_templates(source)

    assert templates == [
        "https://a.tile.example.com/{z}/{x}/{y}.png",
        "https://b.tile.example.com/{z}/{x}/{y}.png",
    ]
    assert headers == {}


@mock.patch("tethys_basemaps.capture_sources._template_for")
def test_source_tile_templates_headers(mock_template_for):
    mock_template_for.return_value = (
        "https://tile.example.com/{z}/{x}/{y}.png",
        {"Authorization": "Bearer t"},
    )
    source = mock.MagicMock()
    user = mock.MagicMock()

    templates, headers = capture_sources.source_tile_templates(source, user)

    mock_template_for.assert_called_once_with(source, user)
    assert templates == ["https://tile.example.com/{z}/{x}/{y}.png"]
    assert headers == {"Authorization": "Bearer t"}


def test_source_tile_templates_not_http():
    source = PortalBasemapSource(
        name="Test XYZ", basemap_type="XYZ", options={"url": "/tiles/{z}/{x}/{y}.png"}
    )

    with pytest.raises(ValueError, match="doesn't have a full http"):
        capture_sources.source_tile_templates(source)


def test_source_tile_templates_blocked_host():
    source = PortalBasemapSource(
        name="Test XYZ",
        basemap_type="XYZ",
        options={"url": "https://{a-c}.tile.openstreetmap.org/{z}/{x}/{y}.png"},
    )

    with pytest.raises(ValueError, match="can't be bulk downloaded"):
        capture_sources.source_tile_templates(source)
