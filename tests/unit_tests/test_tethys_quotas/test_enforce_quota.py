import pytest
from unittest import mock
from tethys_quotas.decorators import enforce_quota
from tethys_quotas.models import ResourceQuota
from django.http import HttpRequest
from tethys_apps.models import TethysApp


@enforce_quota(codename="foo")
def a_controller(request):
    return "Success"


@pytest.mark.django_db
def test_enforce_quota_applies_to_app(test_app):
    with (
        mock.patch("tethys_quotas.decorators.passes_quota") as mock_passes_quota,
        mock.patch("tethys_quotas.decorators.get_active_app") as mock_active_app,
        mock.patch("tethys_quotas.decorators.ResourceQuota") as mock_RQ,
    ):
        mock_RQ.objects.get.return_value = mock.MagicMock(
            codename="foo", applies_to="tethys_apps.models.TethysApp"
        )
        mock_request = mock.MagicMock(spec=HttpRequest)
        mock_active_app.return_value = mock.MagicMock(
            TethysApp.objects.get(name="Test App")
        )
        ret = a_controller(mock_request)
        mock_passes_quota.assert_called()
        assert "Success" == ret


def test_enforce_quota_applies_to_user():
    with (
        mock.patch("tethys_quotas.decorators.passes_quota") as mock_passes_quota,
        mock.patch("tethys_quotas.decorators.ResourceQuota") as mock_RQ,
    ):
        mock_RQ.objects.get.return_value = mock.MagicMock(
            codename="foo", applies_to="django.contrib.auth.models.User"
        )
        mock_request = mock.MagicMock(spec=HttpRequest, user=mock.MagicMock())
        ret = a_controller(mock_request)
        mock_passes_quota.assert_called()
        assert "Success" == ret


def test_enforce_quota_rq_does_not_exist():
    with (
        mock.patch("tethys_quotas.decorators.log") as mock_log,
        mock.patch("tethys_quotas.decorators.ResourceQuota") as mock_RQ,
    ):
        mock_RQ.objects.get.side_effect = ResourceQuota.DoesNotExist
        mock_RQ.DoesNotExist = ResourceQuota.DoesNotExist
        mock_request = mock.MagicMock(spec=HttpRequest)
        ret = a_controller(mock_request)
        mock_log.warning.assert_called_with(
            "ResourceQuota with codename foo does not exist."
        )
        assert "Success" == ret


def test_enforce_quota_no_HttpRequest():
    with mock.patch("tethys_quotas.decorators.log") as mock_log:
        mock_request = mock.MagicMock()
        ret = a_controller(mock_request)
        mock_log.warning.assert_called_with("Invalid request")
        assert "Success" == ret


def test_enforce_quota_bad_applies_to():
    with (
        mock.patch("tethys_quotas.decorators.log") as mock_log,
        mock.patch("tethys_quotas.decorators.ResourceQuota") as mock_RQ,
    ):
        mock_RQ.objects.get.return_value = mock.MagicMock(
            codename="foo", applies_to="not.valid.rq"
        )
        mock_request = mock.MagicMock(spec=HttpRequest)
        ret = a_controller(mock_request)
        mock_log.warning.assert_called_with(
            "ResourceQuota that applies_to not.valid.rq is not supported"
        )
        assert "Success" == ret


def test_enforce_quota_app_not_found():
    with (
        mock.patch("tethys_quotas.decorators.log") as mock_log,
        mock.patch("tethys_quotas.decorators.ResourceQuota") as mock_RQ,
        mock.patch("tethys_quotas.decorators.get_active_app", return_value=None),
    ):
        mock_RQ.objects.get.return_value = mock.MagicMock(
            codename="foo", applies_to="tethys_apps.models.TethysApp"
        )
        mock_request = mock.MagicMock(spec=HttpRequest)
        ret = a_controller(mock_request)
        mock_log.warning.assert_called_with("Request could not be used to find app")
        assert "Success" == ret
