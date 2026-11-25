from unittest import mock

import pytest

from tethys_apps.models import TethysApp
from tethys_basemaps.models import BasemapCapture, BasemapImage, PortalBasemapSource
from tethys_basemaps.utilities import get_app_basemaps


@pytest.fixture
def basemap_app(db):
    return TethysApp.objects.create(name="Basemap Test App", package="basemap_test_app")


def test_get_app_basemaps_no_app():
    assert get_app_basemaps(None) == []


def test_get_app_basemaps_no_assigned_basemaps(basemap_app):
    assert get_app_basemaps(basemap_app) == []


def test_get_app_basemaps_with_app(basemap_app):
    basemap_source = PortalBasemapSource.objects.create(
        name="Test Basemap Source",
        basemap_type=PortalBasemapSource.BasemapSourceType.XYZ,
        options={"url": "https://test_basemap_source.com/{z}/{x}/{y}.png"},
    )

    basemap_capture = BasemapCapture.objects.create(
        name="Test Basemap Capture",
        min_zoom=0,
        max_zoom=5,
        status=BasemapCapture.StatusChoices.READY,
    )
    basemap_image = BasemapImage.objects.create(
        name="Test Basemap Image", status=BasemapImage.StatusChoices.READY
    )
    basemap_capture_processing = BasemapCapture.objects.create(
        name="Test Basemap Capture (processing)",
        min_zoom=0,
        max_zoom=5,
        status=BasemapCapture.StatusChoices.PROCESSING,
    )
    for basemap in (
        basemap_source,
        basemap_capture,
        basemap_image,
        basemap_capture_processing,
    ):
        basemap.apps.add(basemap_app)

    result = get_app_basemaps(basemap_app)

    # Sorted by name since get_app_basemaps sorts this way
    associated_ready_basemaps = [
        basemap_capture,
        basemap_image,
        basemap_source,
    ]

    assert associated_ready_basemaps[0].as_basemap() == result[0]
    assert associated_ready_basemaps[1].as_basemap() == result[1]
    assert associated_ready_basemaps[2].format_options() == result[2]


def test_get_app_basemaps_app_class_uses_db_object(basemap_app):
    basemap_source = PortalBasemapSource.objects.create(
        name="Test Basemap Source",
        basemap_type=PortalBasemapSource.BasemapSourceType.XYZ,
    )
    basemap_source.apps.add(basemap_app)
    app_class = mock.MagicMock(db_object=basemap_app)

    result = get_app_basemaps(app_class)

    assert result == [basemap_source.format_options()]
