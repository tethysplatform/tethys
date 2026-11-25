from unittest import mock

import pytest
from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse

from tethys_apps.models import TethysApp
from tethys_basemaps.admin import BasemapCaptureAdmin, TethysAppBasemapsAdmin
from tethys_basemaps.models import BasemapCapture, BasemapImage, PortalBasemapSource
from tethys_compute.models import DaskJob, DaskScheduler


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_portal_basemap_source_list(admin_client):
    PortalBasemapSource.objects.create(name="Test Source", basemap_type="XYZ")
    response = admin_client.get("/admin/tethys_basemaps/portalbasemapsource/")
    assert response.status_code == 200
    assert b"Test Source" in response.content


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_portal_basemap_source_add(admin_client):
    response = admin_client.get("/admin/tethys_basemaps/portalbasemapsource/add/")
    assert response.status_code == 200


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_basemap_image_list(admin_client):
    BasemapImage.objects.create(name="Test Image")
    response = admin_client.get("/admin/tethys_basemaps/basemapimage/")
    assert response.status_code == 200
    assert b"Test Image" in response.content


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_basemap_image_add(admin_client):
    response = admin_client.get("/admin/tethys_basemaps/basemapimage/add/")
    assert response.status_code == 200
    assert response.context["image_overlay"] == {}


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_basemap_image_change_georeference(admin_client):
    image = BasemapImage.objects.create(
        name="Test Image", georeference_bounds=[0, 0, 1, 1]
    )
    response = admin_client.get(
        f"/admin/tethys_basemaps/basemapimage/{image.id}/change/"
    )
    assert response.status_code == 200
    assert response.context["image_overlay"] == {"bounds": [0, 0, 1, 1], "epsg": 3857}


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_basemap_image_change_generated_bounds(admin_client):
    image = BasemapImage.objects.create(
        name="Test Image", min_x=0, min_y=0, max_x=1, max_y=1
    )
    response = admin_client.get(
        f"/admin/tethys_basemaps/basemapimage/{image.id}/change/"
    )
    assert response.status_code == 200
    assert response.context["image_overlay"] == {"bounds": [0, 0, 1, 1], "epsg": 3857}


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_basemap_image_change_browser_image(admin_client):
    image = BasemapImage.objects.create(
        name="Test Image", source_file="basemaps/images/original/test/test.png"
    )
    response = admin_client.get(
        f"/admin/tethys_basemaps/basemapimage/{image.id}/change/"
    )
    assert response.status_code == 200
    assert response.context["image_overlay"]["image_url"] == reverse(
        "basemaps:original_image", args=[image.id]
    )


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_basemap_image_change_geotiff_ready(admin_client):
    image = BasemapImage.objects.create(
        name="Test Image",
        source_file="basemaps/images/original/test/test.tif",
        status=BasemapImage.StatusChoices.READY,
    )
    response = admin_client.get(
        f"/admin/tethys_basemaps/basemapimage/{image.id}/change/"
    )
    assert response.status_code == 200
    assert response.context["image_overlay"]["tile_url"].endswith("/{z}/{x}/{y}")


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_basemap_image_change_processing(admin_client, admin_user):
    job = DaskJob.objects.create(name="image job", user=admin_user)
    image = BasemapImage.objects.create(
        name="Test Image", status=BasemapImage.StatusChoices.PROCESSING, job=job
    )
    with mock.patch.object(
        BasemapImage,
        "refresh_status",
        return_value=BasemapImage.StatusChoices.PROCESSING,
    ):
        response = admin_client.get(
            f"/admin/tethys_basemaps/basemapimage/{image.id}/change/"
        )
    assert response.status_code == 200
    assert response.context["image_urls"] == {
        "status": reverse("basemaps:basemap_status", args=[image.id]),
        "cancel": reverse("basemaps:image_cancel", args=[image.id]),
    }


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_basemap_image_save_change_while_processing(admin_client):
    image = BasemapImage.objects.create(
        name="Test Image", status=BasemapImage.StatusChoices.PROCESSING
    )
    with mock.patch.object(BasemapImage, "start_generation"):
        response = admin_client.post(
            f"/admin/tethys_basemaps/basemapimage/{image.id}/change/",
            {
                "name": "Test Image",
                "attribution": "",
                "dask_scheduler": "",
                "georeference": "",
            },
        )
    assert response.status_code == 302
    assert response["Location"] == reverse(
        "admin:tethys_basemaps_basemapimage_change", args=[image.id]
    )


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_basemap_image_upload_starts_generation(admin_client, settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)

    def start_generation(image, user, dask_scheduler=None):
        image.status = BasemapImage.StatusChoices.PROCESSING

    with mock.patch.object(
        BasemapImage, "start_generation", autospec=True, side_effect=start_generation
    ) as mock_start:
        response = admin_client.post(
            "/admin/tethys_basemaps/basemapimage/add/",
            {
                "name": "Test Image",
                "source_file": SimpleUploadedFile("test.png", b"image bytes"),
                "dask_scheduler": "",
                "georeference": "",
            },
            follow=True,
        )
    assert response.status_code == 200
    mock_start.assert_called_once()
    assert b"It is being processed." in response.content


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_basemap_image_upload_generation_error(admin_client, settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    with mock.patch.object(
        BasemapImage, "start_generation", side_effect=Exception("Test error")
    ):
        response = admin_client.post(
            "/admin/tethys_basemaps/basemapimage/add/",
            {
                "name": "Test Image",
                "source_file": SimpleUploadedFile("test.png", b"image bytes"),
                "dask_scheduler": "",
                "georeference": "",
            },
            follow=True,
        )
    assert response.status_code == 200
    assert b"There was an error processing the uploaded image." in response.content


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_basemap_capture_list(admin_client):
    BasemapCapture.objects.create(name="Test Capture", min_zoom=0, max_zoom=5)
    response = admin_client.get("/admin/tethys_basemaps/basemapcapture/")
    assert response.status_code == 200
    assert b"Test Capture" in response.content


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_basemap_capture_add(admin_client):
    PortalBasemapSource.objects.create(
        name="Test Source",
        basemap_type="XYZ",
        options={"url": "https://tile.example.com/{z}/{x}/{y}.png"},
    )
    response = admin_client.get("/admin/tethys_basemaps/basemapcapture/add/")
    assert response.status_code == 200
    assert response.context["capture_map"]["basemap"] == [
        {
            "XYZ": {
                "url": "https://tile.example.com/{z}/{x}/{y}.png",
                "control_label": "Test Source",
            }
        }
    ]
    urls = response.context["capture_urls"]
    assert urls["upload"] == reverse("basemaps:capture_upload")
    assert urls["server"] == reverse("basemaps:capture_server")
    assert urls["status"] is None
    assert urls["cancel"] is None
    assert urls["restart"] is None


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_basemap_capture_change_processing(admin_client):
    capture = BasemapCapture.objects.create(
        name="Test Capture",
        min_zoom=0,
        max_zoom=5,
        status=BasemapCapture.StatusChoices.PROCESSING,
    )
    with mock.patch.object(
        BasemapCapture,
        "refresh_status",
        return_value=BasemapCapture.StatusChoices.PROCESSING,
    ):
        response = admin_client.get(
            f"/admin/tethys_basemaps/basemapcapture/{capture.id}/change/"
        )
    assert response.status_code == 200
    urls = response.context["capture_urls"]
    assert urls["status"] == reverse("basemaps:basemap_status", args=[capture.id])
    assert urls["cancel"] is None  # no Dask job
    assert urls["restart"] is None


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_basemap_capture_change_ready(admin_client):
    capture = BasemapCapture.objects.create(
        name="Test Capture",
        min_zoom=0,
        max_zoom=5,
        status=BasemapCapture.StatusChoices.READY,
    )
    response = admin_client.get(
        f"/admin/tethys_basemaps/basemapcapture/{capture.id}/change/"
    )
    assert response.status_code == 200
    urls = response.context["capture_urls"]
    assert urls["status"] is None
    assert urls["cancel"] is None
    assert urls["restart"] is None


def test_basemap_capture_admin_get_fields_add():
    capture_admin = BasemapCaptureAdmin(BasemapCapture, admin.site)

    assert capture_admin.get_fields(None) == [
        "name",
        "min_zoom",
        "max_zoom",
        "dask_scheduler",
        "max_requests_per_second",
    ]


def test_basemap_capture_admin_get_fields_change():
    capture_admin = BasemapCaptureAdmin(BasemapCapture, admin.site)
    capture = BasemapCapture(name="Test Capture", error_message="Test error")

    assert capture_admin.get_fields(None, capture) == [
        "name",
        "min_zoom",
        "max_zoom",
        "status",
        "error_message",
    ]


def test_basemap_capture_admin_get_fields_with_scheduler():
    capture_admin = BasemapCaptureAdmin(BasemapCapture, admin.site)
    capture = BasemapCapture(
        name="Test Capture", dask_scheduler=DaskScheduler(name="Test Scheduler")
    )

    assert capture_admin.get_fields(None, capture) == [
        "name",
        "min_zoom",
        "max_zoom",
        "status",
        "dask_scheduler",
        "rate_limit",
    ]


def test_basemap_capture_admin_get_readonly_fields():
    capture_admin = BasemapCaptureAdmin(BasemapCapture, admin.site)

    assert capture_admin.get_readonly_fields(None) == ()
    assert "status" in capture_admin.get_readonly_fields(None, BasemapCapture())


def test_basemap_capture_admin_rate_limit():
    capture_admin = BasemapCaptureAdmin(BasemapCapture, admin.site)

    assert capture_admin.rate_limit(BasemapCapture()) == "No limit"
    assert (
        capture_admin.rate_limit(BasemapCapture(max_requests_per_second=50))
        == "50 per second"
    )


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@pytest.mark.django_db
def test_admin_tethys_app_basemaps_field(admin_client, test_app):
    app = TethysApp.objects.get(package="test_app")
    response = admin_client.get(f"/admin/tethys_apps/tethysapp/{app.id}/change/")
    assert response.status_code == 200
    assert b"portal_basemaps" in response.content


@pytest.mark.django_db
def test_tethys_app_basemaps_admin_save_related():
    app = TethysApp.objects.create(name="Basemap Test App", package="basemap_test_app")
    source = PortalBasemapSource.objects.create(name="Test Source", basemap_type="XYZ")
    app_admin = TethysAppBasemapsAdmin(TethysApp, admin.site)
    form = mock.MagicMock(instance=app, cleaned_data={"portal_basemaps": [source]})

    app_admin.save_related(None, form, [], True)

    assert list(app.portal_basemaps.values_list("name", flat=True)) == ["Test Source"]


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@mock.patch("tethys_basemaps.admin.SecureMapService")
@pytest.mark.django_db
def test_admin_basemap_capture_add_secure_map_service(mock_sms, admin_client):
    service = mock.MagicMock()
    service.name = (
        "Secure Service"  # can't pass name= to MagicMock; that names the mock
    )
    service._generate_request.return_value = "https://secure.example.com/wms"

    mock_sms.objects.order_by.return_value = [service]
    response = admin_client.get("/admin/tethys_basemaps/basemapcapture/add/")

    assert response.status_code == 200
    assert response.context["capture_map"]["basemap"] == [
        {
            "WMS": {
                "control_label": "Secure Service",
                "url": "https://secure.example.com/wms",
            }
        }
    ]


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@mock.patch("tethys_basemaps.models.BasemapCapture.refresh_status")
@mock.patch("tethys_basemaps.admin.SecureMapService")
@pytest.mark.django_db
def test_admin_basemap_capture_edit_processing(
    mock_sms, mock_refresh_status, admin_client, admin_user
):
    job = DaskJob.objects.create(name="capture job", user=admin_user)
    capture = BasemapCapture.objects.create(
        name="Test Capture",
        status=BasemapCapture.StatusChoices.PROCESSING,
        min_zoom=5,
        max_zoom=9,
        job=job,
    )
    mock_refresh_status.return_value = BasemapCapture.StatusChoices.PROCESSING
    service = mock.MagicMock()
    service.name = (
        "Secure Service"  # can't pass name= to MagicMock; that names the mock
    )
    service._generate_request.return_value = "https://secure.example.com/wms"

    mock_sms.objects.order_by.return_value = [service]
    response = admin_client.get(
        f"/admin/tethys_basemaps/basemapcapture/{capture.id}/change/"
    )

    assert response.status_code == 200
    assert response.context["capture_map"]["basemap"] == [
        {
            "WMS": {
                "control_label": "Secure Service",
                "url": "https://secure.example.com/wms",
            }
        }
    ]
    urls = response.context["capture_urls"]
    assert urls["status"] == reverse("basemaps:basemap_status", args=[capture.id])
    assert urls["cancel"] == reverse("basemaps:capture_cancel", args=[capture.id])
    assert urls["restart"] is None


@override_settings(SHOW_PUBLIC_IF_NO_TENANT_FOUND=True)
@mock.patch("tethys_basemaps.models.BasemapCapture.restart_problem")
@mock.patch("tethys_basemaps.admin.SecureMapService")
@pytest.mark.django_db
def test_admin_basemap_capture_edit_restart(
    mock_sms, mock_restart_problem, admin_client
):
    capture = BasemapCapture.objects.create(name="Test Capture", min_zoom=4, max_zoom=7)
    mock_restart_problem.return_value = None
    service = mock.MagicMock()
    service.name = (
        "Secure Service"  # can't pass name= to MagicMock; that names the mock
    )
    service._generate_request.return_value = "https://secure.example.com/wms"

    mock_sms.objects.order_by.return_value = [service]
    response = admin_client.get(
        f"/admin/tethys_basemaps/basemapcapture/{capture.id}/change/"
    )

    assert response.status_code == 200
    assert response.context["capture_map"]["basemap"] == [
        {
            "WMS": {
                "control_label": "Secure Service",
                "url": "https://secure.example.com/wms",
            }
        }
    ]

    urls = response.context["capture_urls"]
    assert urls["status"] is None
    assert urls["cancel"] is None
    assert urls["restart"] == reverse("basemaps:capture_restart", args=[capture.id])
