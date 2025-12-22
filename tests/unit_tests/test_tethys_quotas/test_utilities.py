from unittest import mock
from django.contrib.auth.models import User
from tethys_apps.models import TethysApp
from tethys_quotas.models import ResourceQuota, UserQuota, TethysAppQuota
from tethys_quotas import utilities
import pytest
from django.test import override_settings


@mock.patch("tethys_quotas.utilities.log")
@override_settings(RESOURCE_QUOTA_HANDLERS=["my"])
@pytest.mark.django_db
def test_bad_rq_handler(mock_log):
    utilities.sync_resource_quota_handlers()
    mock_log.warning.assert_called()


@mock.patch("tethys_quotas.utilities.log")
@override_settings(
    RESOURCE_QUOTA_HANDLERS=["tethys_quotas.handlers.workspace.WorkspaceQuotaHandler"]
)
@pytest.mark.django_db
def test_good_existing_rq(mock_log):
    utilities.sync_resource_quota_handlers()
    mock_log.warning.assert_not_called()


@mock.patch("tethys_quotas.utilities.log")
@override_settings(RESOURCE_QUOTA_HANDLERS=["incorrect.format.rq"])
@pytest.mark.django_db
def test_incorrect_format_rq(mock_log):
    utilities.sync_resource_quota_handlers()
    mock_log.warning.assert_called_with(
        "Unable to load ResourceQuotaHandler: incorrect.format.rq is not correctly formatted class or does not exist"
    )


@mock.patch("tethys_quotas.utilities.log")
@override_settings(RESOURCE_QUOTA_HANDLERS=["fake.module.NotAHandler"])
@pytest.mark.django_db
def test_not_subclass_rq_handler(mock_log, monkeypatch):
    import builtins

    real_import = builtins.__import__

    # Define a class that is NOT a subclass of ResourceQuotaHandler
    class NotAHandler:
        pass

    # Fake module returned by __import__
    fake_module = mock.MagicMock()
    fake_module.NotAHandler = NotAHandler

    def import_side_effect(name, *args, **kwargs):
        if name == "fake.module":
            return fake_module
        else:
            return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", import_side_effect)

    utilities.sync_resource_quota_handlers()

    mock_log.warning.assert_called_with(
        "Unable to load ResourceQuotaHandler: fake.module.NotAHandler is not a subclass of ResourceQuotaHandler"
    )


@mock.patch("tethys_quotas.models.ResourceQuota")
@override_settings(
    RESOURCE_QUOTA_HANDLERS=["tethys_quotas.handlers.workspace.WorkspaceQuotaHandler"]
)
def test_delete_quota_without_handler(mock_rq):
    rq = mock.MagicMock()
    rq.codename = "fake_codename"
    mock_rq.objects.all.return_value = [rq]
    utilities.sync_resource_quota_handlers()

    rq.delete.assert_called()


@mock.patch("tethys_quotas.models.ResourceQuota")
def test_passes_quota_passes(mock_rq):
    rq = mock.MagicMock()
    mock_rq.objects.get.return_value = rq
    rq.check_quota.return_value = True
    assert utilities.passes_quota(UserQuota, "codename")


@mock.patch("tethys_quotas.models.ResourceQuota")
def test_passes_quota_fails(mock_rq):
    from django.core.exceptions import PermissionDenied

    mock_rq.DoesNotExist = ResourceQuota.DoesNotExist
    rq = mock.MagicMock()
    mock_rq.objects.get.return_value = rq
    rq.check_quota.return_value = False
    rq.help = "Example quota exceeded message."

    # Test for permission denied being raised
    with pytest.raises(PermissionDenied) as excinfo:
        utilities.passes_quota(UserQuota, "codename")

    assert str(excinfo.value) == "Example quota exceeded message."

    # Test for False being returned when raise_on_false is False
    assert not utilities.passes_quota(UserQuota, "codename", raise_on_false=False)


@mock.patch("tethys_quotas.utilities.log")
@override_settings(SUPPRESS_QUOTA_WARNINGS=["codename"])
@pytest.mark.django_db
def test_passes_quota_no_rq(mock_log):
    assert utilities.passes_quota(UserQuota, "test_codename", raise_on_false=False)
    mock_log.info.assert_called_with(
        "ResourceQuota with codename test_codename does not exist."
    )

    assert utilities.passes_quota(UserQuota, "codename", raise_on_false=False)


@mock.patch("tethys_quotas.utilities.get_quota")
@mock.patch("tethys_quotas.models.ResourceQuota")
def test_get_resource_available_user(mock_rq, mock_get_quota):
    rq = mock.MagicMock()
    rq.units = "gb"
    mock_rq.objects.get.return_value = rq
    rqh = mock.MagicMock()
    rq.handler.return_value = rqh
    rqh.get_current_use.return_value = 1
    mock_get_quota.return_value = {"quota": 5}

    ret = utilities.get_resource_available(User(), "codename")

    assert 4 == ret["resource_available"]
    assert "gb" == ret["units"]


@mock.patch("tethys_quotas.utilities.get_quota")
@mock.patch("tethys_quotas.models.ResourceQuota")
def test_get_resource_available_app(mock_rq, mock_get_quota):
    rq = mock.MagicMock()
    rq.units = "gb"
    mock_rq.objects.get.return_value = rq
    rqh = mock.MagicMock()
    rq.handler.return_value = rqh
    rqh.get_current_use.return_value = 1
    mock_get_quota.return_value = {"quota": 5}

    ret = utilities.get_resource_available(TethysApp(), "codename")

    assert 4 == ret["resource_available"]
    assert "gb" == ret["units"]


@mock.patch("tethys_quotas.utilities.get_quota")
@mock.patch("tethys_quotas.models.ResourceQuota")
def test_get_resource_not_available(mock_rq, mock_get_quota):
    rq = mock.MagicMock()
    mock_rq.objects.get.return_value = rq
    rqh = mock.MagicMock()
    rq.handler.return_value = rqh
    rqh.get_current_use.return_value = 6
    mock_get_quota.return_value = {"quota": 3}

    ret = utilities.get_resource_available(TethysApp(), "codename")

    assert 0 == ret["resource_available"]


@mock.patch("tethys_quotas.utilities.log")
@mock.patch("tethys_quotas.models.ResourceQuota")
def test_get_resource_available_rq_dne(mock_rq, mock_log):
    mock_rq.objects.get.side_effect = ResourceQuota.DoesNotExist
    mock_rq.DoesNotExist = ResourceQuota.DoesNotExist
    ret = utilities.get_resource_available(mock.MagicMock(), "codename")

    mock_log.warning.assert_called_with(
        "Invalid Codename: ResourceQuota with codename codename does not exist."
    )
    assert ret is None


@mock.patch("tethys_quotas.utilities.log")
@mock.patch("tethys_quotas.models.ResourceQuota")
@mock.patch("tethys_quotas.utilities.get_quota")
@pytest.mark.django_db
def test_get_resource_available_no_quota(mock_gq, mock_rq, mock_log):
    rq = mock.MagicMock()
    mock_rq.objects.get.return_value = rq
    rqh = mock.MagicMock()
    rq.handler.return_value = rqh
    rqh.get_current_use.return_value = 6
    mock_gq.return_value = {"quota": None}
    ret = utilities.get_resource_available(mock.MagicMock(), "codename")
    assert ret is None

    # make sure no warning was logged for not finding the Resource Quota, which also returns none
    assert (
        mock.call(
            "Invalid Codename: ResourceQuota with codename codename does not exist."
        )
        not in mock_log.method_calls
    )


@mock.patch("tethys_quotas.models.ResourceQuota")
@pytest.mark.django_db
def test_get_quota_rq_inactive(
    mock_rq,
    load_quotas,
    admin_user,
):
    rq = mock.MagicMock()
    rq.active = False
    mock_rq.objects.get.return_value = rq

    ret = utilities.get_quota(mock.MagicMock(), "codename")
    assert ret["quota"] is None


@mock.patch("tethys_quotas.models.ResourceQuota")
def test_get_quota_bad_entity(mock_rq):
    rq = mock.MagicMock()
    rq.active = True
    mock_rq.objects.get.return_value = rq

    with pytest.raises(ValueError) as context:
        utilities.get_quota(mock.MagicMock(), "codename")

        assert "Entity needs to be User or TethysApp" in str(context.exception)


@mock.patch("tethys_quotas.models.TethysAppQuota")
@mock.patch("tethys_quotas.models.ResourceQuota")
def test_get_quota_aq(mock_rq, mock_aq):
    rq = mock.MagicMock()
    rq.active = True
    mock_rq.objects.get.return_value = rq

    aq = mock.MagicMock()
    aq.value = 100
    mock_aq.objects.get.return_value = aq

    ret = utilities.get_quota(TethysApp(), "codename")
    assert 100 == ret["quota"]


@mock.patch("tethys_quotas.models.TethysAppQuota")
@mock.patch("tethys_quotas.models.ResourceQuota")
def test_get_quota_aq_dne(mock_rq, mock_aq):
    rq = mock.MagicMock()
    rq.active = True
    rq.impose_default = False
    mock_rq.objects.get.return_value = rq

    mock_aq.objects.get.side_effect = TethysAppQuota.DoesNotExist
    mock_aq.DoesNotExist = TethysAppQuota.DoesNotExist

    ret = utilities.get_quota(TethysApp(), "codename")
    assert ret["quota"] is None


@mock.patch("tethys_quotas.models.TethysAppQuota")
@mock.patch("tethys_quotas.models.ResourceQuota")
def test_get_quota_impose_default(mock_rq, mock_aq):
    rq = mock.MagicMock()
    rq.active = True
    rq.default = 100
    mock_rq.objects.get.return_value = rq

    mock_aq.objects.get.side_effect = TethysAppQuota.DoesNotExist
    mock_aq.DoesNotExist = TethysAppQuota.DoesNotExist

    ret = utilities.get_quota(TethysApp(), "codename")
    assert 100 == ret["quota"]


@mock.patch("tethys_quotas.models.ResourceQuota")
def test_get_quota_staff(mock_rq):
    rq = mock.MagicMock()
    rq.active = True
    mock_rq.objects.get.return_value = rq

    user = User()
    user.is_staff = True

    ret = utilities.get_quota(user, "codename")
    assert ret["quota"] is None


@mock.patch("tethys_quotas.models.UserQuota")
@mock.patch("tethys_quotas.models.ResourceQuota")
@pytest.mark.django_db
def test_get_quota_not_staff(mock_rq, mock_uq, load_quotas):
    rq = mock.MagicMock()
    rq.active = True
    rq.units = "GB"
    mock_rq.objects.get.return_value = rq

    mock_uq.objects.get.return_value = UserQuota(value=50)

    user = User()
    user.is_staff = False
    user.save()

    ret = utilities.get_quota(user, "codename")
    assert 50 == ret["quota"]
    assert "GB" == ret["units"]


def test_can_add_file_invalid_codename():
    with pytest.raises(ValueError) as context:
        utilities.can_add_file_to_path(TethysApp(), "invalid_codename", 100)

        assert str(context.exception) == "Invalid codename: invalid_codename"


def test_can_add_file_invalid_not_app():
    with pytest.raises(ValueError) as context:
        utilities.can_add_file_to_path(
            "not an app or user", "tethysapp_workspace_quota", 100
        )

        assert (
            str(context.exception)
            == "Invalid entity type for codename tethysapp_workspace_quota, expected TethysApp, got str"
        )


def test_can_add_file_invalid_not_user():
    with pytest.raises(ValueError) as context:
        utilities.can_add_file_to_path(
            "not an app or user", "user_workspace_quota", 100
        )

        assert (
            str(context.exception)
            == "Invalid entity type for codename user_workspace_quota, expected User, got str"
        )


@mock.patch("tethys_quotas.utilities.get_resource_available")
def test_can_add_file_quota_met(mock_get_resource_available):
    mock_get_resource_available.return_value = {
        "resource_available": 0,
        "units": "GB",
    }
    result = utilities.can_add_file_to_path(
        TethysApp(), "tethysapp_workspace_quota", "file.txt"
    )
    assert not result


@mock.patch("tethys_quotas.utilities.get_resource_available")
def test_can_add_file_exceeds_quota(mock_get_resource_available):
    mock_get_resource_available.return_value = {
        "resource_available": 1,
        "units": "GB",
    }
    mock_file = mock.MagicMock()
    mock_file.stat.return_value.st_size = 2147483648  # 2 GB
    result = utilities.can_add_file_to_path(
        TethysApp(), "tethysapp_workspace_quota", mock_file
    )
    assert not result


@mock.patch("tethys_quotas.utilities.get_resource_available")
def test_can_add_file_within_quota(mock_get_resource_available):
    mock_get_resource_available.return_value = {
        "resource_available": 2,
        "units": "GB",
    }
    mock_file = mock.MagicMock()
    mock_file.stat.return_value.st_size = 1073741824  # 1 GB
    result = utilities.can_add_file_to_path(
        TethysApp(), "tethysapp_workspace_quota", mock_file
    )
    assert result


def test__convert_to_bytes():
    assert 1073741824 == utilities._convert_to_bytes("gb", 1)
    assert 1048576 == utilities._convert_to_bytes("mb", 1)
    assert 1024 == utilities._convert_to_bytes("kb", 1)
    assert utilities._convert_to_bytes("tb", 1) is None


def test__convert_storage_units():
    assert "1 PB" == utilities._convert_storage_units("pb", 1)
    assert "1 PB" == utilities._convert_storage_units("tb", 1024)
    assert "1 TB" == utilities._convert_storage_units("gb", 1024)
    assert "1 GB" == utilities._convert_storage_units("mb", 1024)
    assert "1 MB" == utilities._convert_storage_units("kb", 1024)
    assert "1 KB" == utilities._convert_storage_units("byte", 1024)
    assert "1 byte" == utilities._convert_storage_units("byte", 1)
    assert "2 bytes" == utilities._convert_storage_units("byte", 2)
    assert "2 bytes" == utilities._convert_storage_units("bytes", 2)
    assert "1 KB" == utilities._convert_storage_units("bytes", 1024)
    assert "2 MB" == utilities._convert_storage_units("bytes", 2 * 1024 * 1024)
    assert "512 bytes" == utilities._convert_storage_units("KB", 0.5)


def test__convert_storage_units_invalid_units():
    assert utilities._convert_storage_units("unknown", 1024) is None
