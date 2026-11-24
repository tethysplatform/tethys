import json

import pytest
from django import forms
from django.conf import settings

from tethys_apps.models import TethysApp
from tethys_basemaps.forms import (
    BasemapCaptureForm,
    BasemapImageForm,
    TethysAppBasemapsForm,
)
from tethys_basemaps.models import BasemapCapture, BasemapImage, PortalBasemapSource


def clean_georeference(raw):
    form = BasemapImageForm()
    form.cleaned_data = {"georeference": raw}
    return form.clean_georeference()


def test_tethys_app_basemaps_form_choices(db):
    PortalBasemapSource.objects.create(
        name="A Source", basemap_type=PortalBasemapSource.BasemapSourceType.XYZ
    )
    BasemapCapture.objects.create(
        name="B Capture",
        min_zoom=0,
        max_zoom=1,
        status=BasemapCapture.StatusChoices.READY,
    )
    BasemapImage.objects.create(name="C Image", status=BasemapImage.StatusChoices.READY)
    BasemapCapture.objects.create(
        name="D Capture Processing",
        min_zoom=0,
        max_zoom=1,
        status=BasemapCapture.StatusChoices.PROCESSING,
    )
    BasemapImage.objects.create(
        name="E Image Failed", status=BasemapImage.StatusChoices.FAILED
    )

    form = TethysAppBasemapsForm()

    choices = form.fields["portal_basemaps"].queryset
    assert list(choices.values_list("name", flat=True)) == [
        "A Source",
        "B Capture",
        "C Image",
    ]


def test_tethys_app_basemaps_form_initial_for_existing_app(db):
    app = TethysApp.objects.create(name="Basemap Test App", package="basemap_test_app")
    source = PortalBasemapSource.objects.create(
        name="A Source", basemap_type=PortalBasemapSource.BasemapSourceType.XYZ
    )
    app.portal_basemaps.add(source)

    form = TethysAppBasemapsForm(instance=app)

    initial = form.fields["portal_basemaps"].initial
    assert list(initial.values_list("name", flat=True)) == ["A Source"]


def test_tethys_app_basemaps_form_no_initial_for_new_app(db):
    form = TethysAppBasemapsForm()

    assert form.fields["portal_basemaps"].initial is None


def test_basemap_image_form_init_no_georeference():
    form = BasemapImageForm(instance=BasemapImage())

    assert "georeference" not in form.initial
    assert form._saved_georeference == (None, None)


def test_basemap_image_form_init_with_georeference():
    instance = BasemapImage(georeference_epsg=4326, georeference_bounds=[0, 0, 1, 1])

    form = BasemapImageForm(instance=instance)

    assert json.loads(form.initial["georeference"]) == {
        "epsg": 4326,
        "bounds": [0, 0, 1, 1],
    }
    assert form._saved_georeference == (4326, [0, 0, 1, 1])


def test_basemap_image_form_init_defaults_epsg():
    instance = BasemapImage(georeference_bounds=[0, 0, 1, 1])

    form = BasemapImageForm(instance=instance)

    assert json.loads(form.initial["georeference"])["epsg"] == 3857


def test_clean_georeference_empty():
    assert clean_georeference("") is None


def test_clean_georeference_valid():
    raw = json.dumps({"epsg": "4326", "bounds": ["0", "0", "1", "1"]})

    assert clean_georeference(raw) == {"epsg": 4326, "bounds": [0.0, 0.0, 1.0, 1.0]}


def test_clean_georeference_default_epsg():
    raw = json.dumps({"bounds": [0, 0, 1, 1]})

    assert clean_georeference(raw)["epsg"] == 3857


def test_clean_georeference_invalid_json():
    with pytest.raises(
        forms.ValidationError, match="Couldn't read the image placement"
    ):
        clean_georeference("not json")


def test_clean_georeference_missing_bounds():
    raw = json.dumps({"epsg": 4326})

    with pytest.raises(
        forms.ValidationError, match="Couldn't read the image placement"
    ):
        clean_georeference(raw)


def test_clean_georeference_invalid_number_of_bounds():
    raw = json.dumps({"bounds": [0, 0, 1]})

    with pytest.raises(forms.ValidationError, match="needs 4 values, but got 3"):
        clean_georeference(raw)


def test_clean_georeference_no_width():
    raw = json.dumps({"bounds": [0, 0, 0, 1]})

    with pytest.raises(forms.ValidationError, match="has no width or height"):
        clean_georeference(raw)


def test_clean_georeference_flipped():
    raw = json.dumps({"bounds": [1, 0, 0, 1]})

    with pytest.raises(forms.ValidationError, match="is flipped"):
        clean_georeference(raw)


def test_georeference_changed():
    instance = BasemapImage(georeference_epsg=4326, georeference_bounds=[0, 0, 1, 1])
    form = BasemapImageForm(instance=instance)
    form.cleaned_data = {"georeference": {"epsg": 4326, "bounds": [0, 0, 2, 2]}}

    assert form.georeference_changed is True


def test_georeference_not_changed():
    instance = BasemapImage(georeference_epsg=4326, georeference_bounds=[0, 0, 1, 1])
    form = BasemapImageForm(instance=instance)
    form.cleaned_data = {"georeference": {"epsg": 4326, "bounds": [0, 0, 1, 1]}}

    assert form.georeference_changed is False


def test_georeference_changed_no_georeference():
    form = BasemapImageForm(instance=BasemapImage())
    form.cleaned_data = {"georeference": None}

    assert form.georeference_changed is False


def test_basemap_image_form_save(db):
    data = {
        "name": "Test Image",
        "georeference": json.dumps({"epsg": 4326, "bounds": [0, 0, 1, 1]}),
    }
    form = BasemapImageForm(data=data)
    assert form.is_valid(), form.errors

    instance = form.save()

    saved = BasemapImage.objects.get(pk=instance.pk)
    assert saved.georeference_epsg == 4326
    assert saved.georeference_bounds == [0.0, 0.0, 1.0, 1.0]


def test_basemap_image_form_save_no_commit(db):
    data = {
        "name": "Test Image",
        "georeference": json.dumps({"epsg": 4326, "bounds": [0, 0, 1, 1]}),
    }
    form = BasemapImageForm(data=data)
    assert form.is_valid(), form.errors

    instance = form.save(commit=False)

    assert instance.pk is None
    assert instance.georeference_epsg == 4326


def test_basemap_image_form_save_without_georeference(db):
    form = BasemapImageForm(data={"name": "Test Image"})
    assert form.is_valid(), form.errors

    instance = form.save(commit=False)

    assert instance.georeference_epsg is None
    assert instance.georeference_bounds is None


def test_basemap_capture_form_fields():
    form = BasemapCaptureForm()

    rate = form.fields["max_requests_per_second"]
    assert not rate.required
    assert rate.min_value == 1
    assert rate.max_value == settings.BASEMAP_CAPTURE_SECURE_MAX_RATE


def test_basemap_capture_form_valid(db):
    data = {"name": "Test Capture", "min_zoom": 0, "max_zoom": 5}

    form = BasemapCaptureForm(data=data)

    assert form.is_valid(), form.errors


def test_basemap_capture_form_rate_too_low(db):
    data = {
        "name": "Test Capture",
        "min_zoom": 0,
        "max_zoom": 5,
        "max_requests_per_second": 0,
    }

    form = BasemapCaptureForm(data=data)

    assert not form.is_valid()
    assert "max_requests_per_second" in form.errors
