import pytest
from unittest.mock import MagicMock, patch
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from tethys_apps.models import TethysApp
from tethys_quotas import utilities
from tethys_quotas.models import ResourceQuota, TethysAppQuota, UserQuota
from tethys_quotas.handlers.base import ResourceQuotaHandler

# --- sync_resource_quota_handlers ---


class DummyHandler(ResourceQuotaHandler):
    codename = "dummy_quota"
    name = "Dummy Handler"
    description = "A dummy handler for testing."
    default = 6
    units = "dummies"
    help = "You have exceeded your dummy quota."
    applies_to = ["django.contrib.auth.models.User"]

    def get_current_use(self, *args, **kwargs):
        return 3


class BadHandler:
    pass


@pytest.mark.django_db
def test_sync_resource_quota_handlers(monkeypatch, settings):
    settings.RESOURCE_QUOTA_HANDLERS = [
        "unit_tests.test_tethys_quotas.test_utilities.DummyHandler"
    ]
    utilities.sync_resource_quota_handlers()
    assert ResourceQuota.objects.filter(codename="user_dummy_quota").exists()


@pytest.mark.django_db
def test_sync_resource_quota_handlers_delete_removed_quotas(monkeypatch, settings):
    # Create an existing ResourceQuota that should be deleted since it's not in the settings
    resource_quota = ResourceQuota(
        codename="user_dummy_quota",
        name="User Dummy Quota",
        description=DummyHandler.description,
        default=DummyHandler.default,
        units=DummyHandler.units,
        applies_to=DummyHandler.applies_to,
        impose_default=True,
        help=DummyHandler.help,
        _handler="unit_tests.test_tethys_quotas.test_utilities.DummyHandler",
    )
    resource_quota.save()
    settings.RESOURCE_QUOTA_HANDLERS = []
    assert ResourceQuota.objects.count() == 1
    utilities.sync_resource_quota_handlers()
    assert ResourceQuota.objects.count() == 0


@pytest.mark.django_db
def test_sync_resource_quota_handlers_bad_import(monkeypatch, settings):
    settings.RESOURCE_QUOTA_HANDLERS = ["not.a.real.module.Class"]
    with (patch("tethys_quotas.utilities.log") as mock_log,):
        utilities.sync_resource_quota_handlers()
        mock_log.warning.assert_called_with(
            "Unable to load ResourceQuotaHandler: not.a.real.module.Class is not correctly formatted class or does not exist"
        )


@pytest.mark.django_db
def test_sync_resource_quota_handlers_not_subclass(monkeypatch, settings):
    settings.RESOURCE_QUOTA_HANDLERS = [
        "unit_tests.test_tethys_quotas.test_utilities.BadHandler"
    ]
    with (patch("tethys_quotas.utilities.log") as mock_log,):
        utilities.sync_resource_quota_handlers()
        mock_log.warning.assert_called_with(
            "Unable to load ResourceQuotaHandler: unit_tests.test_tethys_quotas.test_utilities.BadHandler is not a subclass of ResourceQuotaHandler"
        )


# --- passes_quota ---


def test_passes_quota_permission_passed():
    rq = MagicMock()
    rq.check_quota.return_value = True
    rq.help = "Nope!"
    entity = MagicMock()
    with patch("tethys_quotas.models.ResourceQuota.objects.get", return_value=rq):
        ret = utilities.passes_quota(entity, "some_codename", raise_on_false=True)
        assert ret is True
        rq.check_quota.assert_called_once_with(entity)


def test_passes_quota_permission_denied_raise():
    rq = MagicMock()
    rq.check_quota.return_value = False
    rq.help = "Nope!"
    with patch("tethys_quotas.models.ResourceQuota.objects.get", return_value=rq):
        with pytest.raises(PermissionDenied) as exc:
            utilities.passes_quota(MagicMock(), "some_codename", raise_on_false=True)
        assert "Nope!" in str(exc.value)


def test_passes_quota_permission_denied_do_not_raise():
    rq = MagicMock()
    rq.check_quota.return_value = False
    rq.help = "Nope!"
    with patch("tethys_quotas.models.ResourceQuota.objects.get", return_value=rq):
        ret = utilities.passes_quota(MagicMock(), "some_codename", raise_on_false=False)
        assert ret is False


def test_passes_quota_does_not_exist(settings):
    settings.RESOURCE_QUOTA_HANDLERS = ["user_workspace_quota", "app_workspace_quota"]
    with (
        patch(
            "tethys_quotas.models.ResourceQuota.objects.get",
            side_effect=ResourceQuota.DoesNotExist,
        ),
        patch("tethys_quotas.utilities.log") as mock_log,
    ):
        ret = utilities.passes_quota(MagicMock(), "some_codename", raise_on_false=False)
        assert ret is True
        mock_log.info.assert_called_with(
            "ResourceQuota with codename some_codename does not exist."
        )


def test_passes_quota_does_not_exist_warning_suppressed(settings):
    settings.RESOURCE_QUOTA_HANDLERS = [
        "user_workspace_quota",
        "app_workspace_quota",
        "some_codename",
    ]
    with (
        patch(
            "tethys_quotas.models.ResourceQuota.objects.get",
            side_effect=ResourceQuota.DoesNotExist,
        ),
        patch("tethys_quotas.utilities.log") as mock_log,
    ):
        ret = utilities.passes_quota(MagicMock(), "some_codename", raise_on_false=False)
        assert ret is True
        mock_log.warning.assert_not_called()


# --- get_resource_available ---


def test_get_resource_available_positive():
    quota = 5
    rq = MagicMock()
    rq.handler.return_value.get_current_use.return_value = (
        1  # current use less than quota
    )
    rq.units = "GB"

    with (
        patch("tethys_quotas.models.ResourceQuota.objects.get", return_value=rq),
        patch("tethys_quotas.utilities.get_quota", return_value={"quota": quota}),
    ):
        ret = utilities.get_resource_available(MagicMock(), "some_codename")
        assert ret["resource_available"] == 4
        assert ret["units"] == "GB"


def test_get_resource_available_zero():
    quota = 5
    rq = MagicMock()
    rq.handler.return_value.get_current_use.return_value = (
        5  # current use equal to quota
    )
    rq.units = "GB"

    with (
        patch("tethys_quotas.models.ResourceQuota.objects.get", return_value=rq),
        patch("tethys_quotas.utilities.get_quota", return_value={"quota": quota}),
    ):
        ret = utilities.get_resource_available(MagicMock(), "some_codename")
        assert ret["resource_available"] == 0
        assert ret["units"] == "GB"


def test_get_resource_available_negative():
    quota = 5
    rq = MagicMock()
    rq.handler.return_value.get_current_use.return_value = (
        7  # current use greater than quota
    )
    rq.units = "GB"

    with (
        patch("tethys_quotas.models.ResourceQuota.objects.get", return_value=rq),
        patch("tethys_quotas.utilities.get_quota", return_value={"quota": quota}),
    ):
        ret = utilities.get_resource_available(MagicMock(), "some_codename")
        assert ret["resource_available"] == 0
        assert ret["units"] == "GB"


def test_get_resource_avaialable_does_not_exist():
    with (
        patch(
            "tethys_quotas.models.ResourceQuota.objects.get",
            side_effect=ResourceQuota.DoesNotExist,
        ),
        patch("tethys_quotas.utilities.log") as mock_log,
    ):
        ret = utilities.get_resource_available(MagicMock(), "some_codename")
        assert ret is None
        mock_log.warning.assert_called_with(
            "Invalid Codename: ResourceQuota with codename some_codename does not exist."
        )


def test_get_resource_available_no_quota():
    quota = None
    rq = MagicMock()
    rq.handler.return_value.get_current_use.return_value = 1
    with (
        patch("tethys_quotas.models.ResourceQuota.objects.get", return_value=rq),
        patch("tethys_quotas.utilities.get_quota", return_value={"quota": quota}),
    ):
        ret = utilities.get_resource_available(MagicMock(), "some_codename")
        assert ret is None


# --- get_quota ---


def test_get_quota_user_entity():
    # User Entity
    entity = MagicMock(spec=User)
    entity.is_staff = False
    # Resource Quota
    rq = MagicMock()
    rq.active = True
    rq.units = "GB"
    rq.default = 11
    rq.impose_default = False
    # Entity Quota
    eq = MagicMock()
    eq.value = 6

    with (
        patch("tethys_quotas.models.ResourceQuota.objects.get", return_value=rq),
        patch("tethys_quotas.models.user_quota.UserQuota.objects.get", return_value=eq),
    ):
        ret = utilities.get_quota(entity, "some_codename")
        assert ret["units"] == "GB"
        assert ret["quota"] == 6


def test_get_quota_user_entity_staff_user():
    # User Entity
    entity = MagicMock(spec=User)
    entity.is_staff = True  # Staff user
    # Resource Quota
    rq = MagicMock()
    rq.active = True
    rq.units = "GB"
    rq.default = 11
    rq.impose_default = True
    # Entity Quota
    eq = MagicMock()
    eq.value = 6

    with (
        patch("tethys_quotas.models.ResourceQuota.objects.get", return_value=rq),
        patch("tethys_quotas.models.user_quota.UserQuota.objects.get", return_value=eq),
    ):
        ret = utilities.get_quota(entity, "some_codename")
        assert ret["units"] == "GB"
        assert ret["quota"] is None  # Staff users have no quota


def test_get_quota_user_entity_impose_default_entity_quota_set():
    # User Entity
    entity = MagicMock(spec=User)
    entity.is_staff = False
    # Resource Quota
    rq = MagicMock()
    rq.active = True
    rq.units = "GB"
    rq.default = 11
    rq.impose_default = True
    # Entity Quota
    eq = MagicMock()
    eq.value = 6  # Entity quota defined

    with (
        patch("tethys_quotas.models.ResourceQuota.objects.get", return_value=rq),
        patch("tethys_quotas.models.user_quota.UserQuota.objects.get", return_value=eq),
    ):
        ret = utilities.get_quota(entity, "some_codename")
        assert ret["units"] == "GB"
        assert ret["quota"] == 6  # Entity quota takes precedence over default


def test_get_quota_user_entity_impose_default_entity_quota_unset():
    # User Entity
    entity = MagicMock(spec=User)
    entity.is_staff = False
    # Resource Quota
    rq = MagicMock()
    rq.active = True
    rq.units = "GB"
    rq.default = 11
    rq.impose_default = True
    # Entity Quota
    eq = MagicMock()
    eq.value = None  # Entity quota not set

    with (
        patch("tethys_quotas.models.ResourceQuota.objects.get", return_value=rq),
        patch("tethys_quotas.models.user_quota.UserQuota.objects.get", return_value=eq),
    ):
        ret = utilities.get_quota(entity, "some_codename")
        assert ret["units"] == "GB"
        assert ret["quota"] == 11  # Default imposed since entity quota not set


def test_get_quota_user_entity_do_not_impose_default_entity_quota_unset():
    # User Entity
    entity = MagicMock(spec=User)
    entity.is_staff = False
    # Resource Quota
    rq = MagicMock()
    rq.active = True
    rq.units = "GB"
    rq.default = 11
    rq.impose_default = False
    # Entity Quota
    eq = MagicMock()
    eq.value = None  # Entity quota not set

    with (
        patch("tethys_quotas.models.ResourceQuota.objects.get", return_value=rq),
        patch("tethys_quotas.models.user_quota.UserQuota.objects.get", return_value=eq),
    ):
        ret = utilities.get_quota(entity, "some_codename")
        assert ret["units"] == "GB"
        assert (
            ret["quota"] is None
        )  # No quota since entity quota not set and default not imposed


def test_get_quota_user_entity_quota_dne():
    # User Entity
    entity = MagicMock(spec=User)
    entity.is_staff = False
    # Resource Quota
    rq = MagicMock()
    rq.active = True
    rq.units = "GB"
    rq.default = 11
    rq.impose_default = False
    # Entity Quota
    eq = MagicMock()
    eq.value = 6

    with (
        patch("tethys_quotas.models.ResourceQuota.objects.get", return_value=rq),
        patch(
            "tethys_quotas.models.user_quota.UserQuota.objects.get",
            side_effect=UserQuota.DoesNotExist,
        ),
    ):
        ret = utilities.get_quota(entity, "some_codename")
        assert ret["units"] == "GB"
        assert ret["quota"] is None  # No quota since entity quota does not exist


def test_get_quota_app_entity():
    # TethysApp Entity
    entity = MagicMock(spec=TethysApp)
    # Resource Quota
    rq = MagicMock()
    rq.active = True
    rq.units = "GB"
    rq.default = 10
    rq.impose_default = False
    # Entity Quota
    eq = MagicMock()
    eq.value = 5

    with (
        patch("tethys_quotas.models.ResourceQuota.objects.get", return_value=rq),
        patch(
            "tethys_quotas.models.tethys_app_quota.TethysAppQuota.objects.get",
            return_value=eq,
        ),
    ):
        ret = utilities.get_quota(entity, "some_codename")
        assert ret["units"] == "GB"
        assert ret["quota"] == 5


def test_get_quota_app_entity_impose_default_entity_quota_set():
    # TethysApp Entity
    entity = MagicMock(spec=TethysApp)
    # Resource Quota
    rq = MagicMock()
    rq.active = True
    rq.units = "GB"
    rq.default = 10
    rq.impose_default = True
    # Entity Quota
    eq = MagicMock()
    eq.value = 5  # Entity quota defined

    with (
        patch("tethys_quotas.models.ResourceQuota.objects.get", return_value=rq),
        patch(
            "tethys_quotas.models.tethys_app_quota.TethysAppQuota.objects.get",
            return_value=eq,
        ),
    ):
        ret = utilities.get_quota(entity, "some_codename")
        assert ret["units"] == "GB"
        assert ret["quota"] == 5  # Entity quota takes precedence over default


def test_get_quota_app_entity_impose_default_entity_quota_unset():
    # TethysApp Entity
    entity = MagicMock(spec=TethysApp)
    # Resource Quota
    rq = MagicMock()
    rq.active = True
    rq.units = "GB"
    rq.default = 10
    rq.impose_default = True
    # Entity Quota
    eq = MagicMock()
    eq.value = None  # Entity quota not set

    with (
        patch("tethys_quotas.models.ResourceQuota.objects.get", return_value=rq),
        patch(
            "tethys_quotas.models.tethys_app_quota.TethysAppQuota.objects.get",
            return_value=eq,
        ),
    ):
        ret = utilities.get_quota(entity, "some_codename")
        assert ret["units"] == "GB"
        assert ret["quota"] == 10  # Default imposed since entity quota not set


def test_get_quota_app_entity_do_not_impose_default_entity_quota_unset():
    # TethysApp Entity
    entity = MagicMock(spec=TethysApp)
    # Resource Quota
    rq = MagicMock()
    rq.active = True
    rq.units = "GB"
    rq.default = 10
    rq.impose_default = False
    # Entity Quota
    eq = MagicMock()
    eq.value = None  # Entity quota not set

    with (
        patch("tethys_quotas.models.ResourceQuota.objects.get", return_value=rq),
        patch(
            "tethys_quotas.models.tethys_app_quota.TethysAppQuota.objects.get",
            return_value=eq,
        ),
    ):
        ret = utilities.get_quota(entity, "some_codename")
        assert ret["units"] == "GB"
        assert (
            ret["quota"] is None
        )  # No quota since entity quota not set and default not imposed


def test_get_quota_app_entity_quota_dne():
    # TethysApp Entity
    entity = MagicMock(spec=TethysApp)
    # Resource Quota
    rq = MagicMock()
    rq.active = True
    rq.units = "GB"
    rq.default = 10
    rq.impose_default = False

    with (
        patch("tethys_quotas.models.ResourceQuota.objects.get", return_value=rq),
        patch(
            "tethys_quotas.models.tethys_app_quota.TethysAppQuota.objects.get",
            side_effect=TethysAppQuota.DoesNotExist,
        ),
    ):
        ret = utilities.get_quota(entity, "some_codename")
        assert ret["units"] == "GB"
        assert ret["quota"] is None  # No quota since entity quota does not exist


def test_get_quota_rq_not_active():
    # User Entity
    entity = MagicMock(spec=User)
    entity.is_staff = False
    # Resource Quota
    rq = MagicMock()
    rq.active = False  # Not active
    rq.units = "GB"
    rq.default = 11
    rq.impose_default = True
    # Entity Quota
    eq = MagicMock()
    eq.value = 6

    with (
        patch("tethys_quotas.models.ResourceQuota.objects.get", return_value=rq),
        patch("tethys_quotas.models.user_quota.UserQuota.objects.get", return_value=eq),
    ):
        ret = utilities.get_quota(entity, "some_codename")
        assert ret["units"] == "GB"
        assert ret["quota"] is None  # No quota since ResourceQuota not active


def test_get_quota_rq_does_not_exist():
    with (
        patch(
            "tethys_quotas.models.ResourceQuota.objects.get",
            side_effect=ResourceQuota.DoesNotExist,
        ),
        patch("tethys_quotas.utilities.log") as mock_log,
    ):
        ret = utilities.get_quota(MagicMock(), "some_codename")
        assert ret["units"] is None
        assert ret["quota"] is None
        mock_log.warning.assert_called_with(
            "Invalid Codename: ResourceQuota with codename some_codename does not exist."
        )


def test_get_quota_entity_not_user_or_app():
    entity = MagicMock()
    # Resource Quota
    rq = MagicMock()
    rq.active = True
    # Entity Quota
    eq = MagicMock()
    with (
        patch("tethys_quotas.models.ResourceQuota.objects.get", return_value=rq),
        patch("tethys_quotas.models.user_quota.UserQuota.objects.get", return_value=eq),
    ):
        with pytest.raises(ValueError) as exc:
            utilities.get_quota(entity, "some_codename")
        assert "Entity needs to be User or TethysApp" in str(exc.value)


# --- _convert_storage_units ---


def test_convert_storage_units_bytes():
    bytes = 100
    ret = utilities._convert_storage_units(" bytes", bytes)
    assert ret == "100 bytes"


def test_convert_storage_units_KB():
    bytes = 100 * 1024
    ret = utilities._convert_storage_units(" bytes", bytes)
    assert ret == "100 KB"


def test_convert_storage_units_MB():
    bytes = 100 * 1024**2
    ret = utilities._convert_storage_units(" bytes", bytes)
    assert ret == "100 MB"


def test_convert_storage_units_GB():
    bytes = 100 * 1024**3
    ret = utilities._convert_storage_units(" bytes", bytes)
    assert ret == "100 GB"


def test_convert_storage_units_TB():
    bytes = 100 * 1024**4
    ret = utilities._convert_storage_units(" bytes", bytes)
    assert ret == "100 TB"


def test_convert_storage_units_PB():
    bytes = 100 * 1024**5
    ret = utilities._convert_storage_units(" bytes", bytes)
    assert ret == "100 PB"


def test_convert_storage_units_bytes_to_mb():
    bytes = 1024 * 1024
    ret = utilities._convert_storage_units(" bytes", bytes)
    assert ret == "1 MB"


def test_convert_storage_units_kb_to_gb():
    kbs = 1024 * 1024
    ret = utilities._convert_storage_units(" kb", kbs)
    assert ret == "1 GB"


def test_convert_storage_units_mb_to_tb():
    mbs = 1024 * 1024
    ret = utilities._convert_storage_units(" mb", mbs)
    assert ret == "1 TB"


def test_convert_storage_units_tb_to_pb():
    tbs = 1024 * 1024
    ret = utilities._convert_storage_units(" tb", tbs)
    assert ret == "1024 PB"


def test_convert_storage_units_kb_to_single_byte():
    kbs = 1 / 1024
    ret = utilities._convert_storage_units(" KB", kbs)
    assert ret == "1 byte"


def test_convert_storage_units_invalid():
    ret = utilities._convert_storage_units(" ZZ", 100)
    assert ret is None

def test_can_add_file_invalid_codename(self):
    with self.assertRaises(ValueError) as context:
        utilities.can_add_file_to_path(TethysApp(), "invalid_codename", 100)

    self.assertEqual(str(context.exception), "Invalid codename: invalid_codename")

def test_can_add_file_invalid_not_app(self):
    with self.assertRaises(ValueError) as context:
        utilities.can_add_file_to_path(
            "not an app or user", "tethysapp_workspace_quota", 100
        )

    self.assertEqual(
        str(context.exception),
        "Invalid entity type for codename tethysapp_workspace_quota, expected TethysApp, got str",
    )

def test_can_add_file_invalid_not_user(self):
    with self.assertRaises(ValueError) as context:
        utilities.can_add_file_to_path(
            "not an app or user", "user_workspace_quota", 100
        )

    self.assertEqual(
        str(context.exception),
        "Invalid entity type for codename user_workspace_quota, expected User, got str",
    )

@mock.patch("tethys_quotas.utilities.get_resource_available")
def test_can_add_file_quota_met(self, mock_get_resource_available):
    mock_get_resource_available.return_value = {
        "resource_available": 0,
        "units": "GB",
    }
    result = utilities.can_add_file_to_path(
        TethysApp(), "tethysapp_workspace_quota", "file.txt"
    )
    self.assertFalse(result)

@mock.patch("tethys_quotas.utilities.get_resource_available")
def test_can_add_file_exceeds_quota(self, mock_get_resource_available):
    mock_get_resource_available.return_value = {
        "resource_available": 1,
        "units": "GB",
    }
    mock_file = mock.MagicMock()
    mock_file.stat.return_value.st_size = 2147483648  # 2 GB
    result = utilities.can_add_file_to_path(
        TethysApp(), "tethysapp_workspace_quota", mock_file
    )
    self.assertFalse(result)

@mock.patch("tethys_quotas.utilities.get_resource_available")
def test_can_add_file_within_quota(self, mock_get_resource_available):
    mock_get_resource_available.return_value = {
        "resource_available": 2,
        "units": "GB",
    }
    mock_file = mock.MagicMock()
    mock_file.stat.return_value.st_size = 1073741824  # 1 GB
    result = utilities.can_add_file_to_path(
        TethysApp(), "tethysapp_workspace_quota", mock_file
    )
    self.assertTrue(result)

def test__convert_to_bytes(self):
    self.assertEqual(1073741824, utilities._convert_to_bytes("gb", 1))
    self.assertEqual(1048576, utilities._convert_to_bytes("mb", 1))
    self.assertEqual(1024, utilities._convert_to_bytes("kb", 1))
    self.assertIsNone(utilities._convert_to_bytes("tb", 1))
