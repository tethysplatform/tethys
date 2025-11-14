from unittest import mock
from django.test import TestCase
from django.contrib.auth.models import User
from tethys_apps.models import TethysApp
from tethys_quotas.models import ResourceQuota, UserQuota, TethysAppQuota
from tethys_quotas import utilities


class TethysQuotasUtilitiesTest(TestCase):
    def setUp(self):
        ResourceQuota.objects.all().delete()

    def tearDown(self):
        pass

    @mock.patch("tethys_quotas.utilities.settings", RESOURCE_QUOTA_HANDLERS=["my"])
    @mock.patch("tethys_quotas.utilities.log")
    def test_bad_rq_handler(self, mock_log, _):
        utilities.sync_resource_quota_handlers()
        mock_log.warning.assert_called()

    @mock.patch(
        "tethys_quotas.utilities.settings",
        RESOURCE_QUOTA_HANDLERS=[
            "tethys_quotas.handlers.workspace.WorkspaceQuotaHandler"
        ],
    )
    @mock.patch("tethys_quotas.utilities.log")
    def test_good_existing_rq(self, mock_log, _):
        utilities.sync_resource_quota_handlers()
        mock_log.warning.assert_not_called()

    @mock.patch(
        "tethys_quotas.utilities.settings",
        RESOURCE_QUOTA_HANDLERS=["not.subclass.of.rq"],
    )
    @mock.patch("tethys_quotas.utilities.log")
    def test_not_subclass_of_rq(self, mock_log, _):
        utilities.sync_resource_quota_handlers()
        mock_log.warning.assert_called()

    @mock.patch("tethys_quotas.models.ResourceQuota")
    def test_passes_quota_passes(self, mock_rq):
        rq = mock.MagicMock()
        mock_rq.objects.get.return_value = rq
        rq.check_quota.return_value = True
        self.assertTrue(utilities.passes_quota(UserQuota, "codename"))

    @mock.patch("tethys_quotas.models.ResourceQuota")
    def test_passes_quota_fails(self, mock_rq):
        mock_rq.DoesNotExist = ResourceQuota.DoesNotExist
        rq = mock.MagicMock()
        mock_rq.objects.get.return_value = rq
        rq.check_quota.return_value = False
        self.assertFalse(
            utilities.passes_quota(UserQuota, "codename", raise_on_false=False)
        )

    @mock.patch("tethys_quotas.utilities.get_quota")
    @mock.patch("tethys_quotas.models.ResourceQuota")
    def test_get_resource_available_user(self, mock_rq, mock_get_quota):
        rq = mock.MagicMock()
        rq.units = "gb"
        mock_rq.objects.get.return_value = rq
        rqh = mock.MagicMock()
        rq.handler.return_value = rqh
        rqh.get_current_use.return_value = 1
        mock_get_quota.return_value = {"quota": 5}

        ret = utilities.get_resource_available(User(), "codename")

        self.assertEqual(4, ret["resource_available"])
        self.assertEqual("gb", ret["units"])

    @mock.patch("tethys_quotas.utilities.get_quota")
    @mock.patch("tethys_quotas.models.ResourceQuota")
    def test_get_resource_available_app(self, mock_rq, mock_get_quota):
        rq = mock.MagicMock()
        rq.units = "gb"
        mock_rq.objects.get.return_value = rq
        rqh = mock.MagicMock()
        rq.handler.return_value = rqh
        rqh.get_current_use.return_value = 1
        mock_get_quota.return_value = {"quota": 5}

        ret = utilities.get_resource_available(TethysApp(), "codename")

        self.assertEqual(4, ret["resource_available"])
        self.assertEqual("gb", ret["units"])

    @mock.patch("tethys_quotas.utilities.get_quota")
    @mock.patch("tethys_quotas.models.ResourceQuota")
    def test_get_resource_not_available(self, mock_rq, mock_get_quota):
        rq = mock.MagicMock()
        mock_rq.objects.get.return_value = rq
        rqh = mock.MagicMock()
        rq.handler.return_value = rqh
        rqh.get_current_use.return_value = 6
        mock_get_quota.return_value = {"quota": 3}

        ret = utilities.get_resource_available(TethysApp(), "codename")

        self.assertEqual(0, ret["resource_available"])

    @mock.patch("tethys_quotas.utilities.log")
    @mock.patch("tethys_quotas.models.ResourceQuota")
    def test_get_resource_available_rq_dne(self, mock_rq, mock_log):
        mock_rq.objects.get.side_effect = ResourceQuota.DoesNotExist
        mock_rq.DoesNotExist = ResourceQuota.DoesNotExist
        ret = utilities.get_resource_available(mock.MagicMock(), "codename")

        mock_log.warning.assert_called_with(
            "Invalid Codename: ResourceQuota with codename codename does not exist."
        )
        self.assertEqual(None, ret)

    @mock.patch("tethys_quotas.models.ResourceQuota")
    def test_get_quota_rq_inactive(self, mock_rq):
        rq = mock.MagicMock()
        rq.active = False
        mock_rq.objects.get.return_value = rq

        ret = utilities.get_quota(mock.MagicMock(), "codename")
        self.assertEqual(None, ret["quota"])

    @mock.patch("tethys_quotas.models.ResourceQuota")
    def test_get_quota_bad_entity(self, mock_rq):
        rq = mock.MagicMock()
        rq.active = True
        mock_rq.objects.get.return_value = rq

        with self.assertRaises(ValueError) as context:
            utilities.get_quota(mock.MagicMock(), "codename")
        self.assertTrue(
            "Entity needs to be User or TethysApp" in str(context.exception)
        )

    @mock.patch("tethys_quotas.models.TethysAppQuota")
    @mock.patch("tethys_quotas.models.ResourceQuota")
    def test_get_quota_aq(self, mock_rq, mock_aq):
        rq = mock.MagicMock()
        rq.active = True
        mock_rq.objects.get.return_value = rq

        aq = mock.MagicMock()
        aq.value = 100
        mock_aq.objects.get.return_value = aq

        ret = utilities.get_quota(TethysApp(), "codename")
        self.assertEqual(100, ret["quota"])

    @mock.patch("tethys_quotas.models.TethysAppQuota")
    @mock.patch("tethys_quotas.models.ResourceQuota")
    def test_get_quota_aq_dne(self, mock_rq, mock_aq):
        rq = mock.MagicMock()
        rq.active = True
        rq.impose_default = False
        mock_rq.objects.get.return_value = rq

        mock_aq.objects.get.side_effect = TethysAppQuota.DoesNotExist
        mock_aq.DoesNotExist = TethysAppQuota.DoesNotExist

        ret = utilities.get_quota(TethysApp(), "codename")
        self.assertEqual(None, ret["quota"])

    @mock.patch("tethys_quotas.models.TethysAppQuota")
    @mock.patch("tethys_quotas.models.ResourceQuota")
    def test_get_quota_impose_default(self, mock_rq, mock_aq):
        rq = mock.MagicMock()
        rq.active = True
        rq.default = 100
        mock_rq.objects.get.return_value = rq

        mock_aq.objects.get.side_effect = TethysAppQuota.DoesNotExist
        mock_aq.DoesNotExist = TethysAppQuota.DoesNotExist

        ret = utilities.get_quota(TethysApp(), "codename")
        self.assertEqual(100, ret["quota"])

    @mock.patch("tethys_quotas.models.ResourceQuota")
    def test_get_quota_staff(self, mock_rq):
        rq = mock.MagicMock()
        rq.active = True
        mock_rq.objects.get.return_value = rq

        user = User()
        user.is_staff = True

        ret = utilities.get_quota(user, "codename")
        self.assertEqual(None, ret["quota"])

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
