from unittest import mock
from django.test import TestCase
from tethys_quotas.admin import ResourceQuotaAdmin, UserQuotasSettingInline
from tethys_quotas.models import UserQuota


class TethysQuotasAdminTest(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_ResourceQuotaAdmin(self):
        expected_fields = ('name', 'description', 'default', 'units', 'codename', 'applies_to', 'help', 'active',
                           'impose_default')
        expected_readonly_fields = ('codename', 'name', 'description', 'units', 'applies_to')
        ret = ResourceQuotaAdmin(mock.MagicMock(), mock.MagicMock())

        self.assertEquals(expected_fields, ret.fields)
        self.assertEquals(expected_readonly_fields, ret.readonly_fields)

    def test_has_delete_permission(self):
        mock_request = mock.MagicMock()
        ret = ResourceQuotaAdmin(mock.MagicMock(), mock.MagicMock())
        self.assertFalse(ret.has_delete_permission(mock_request))

    def test_has_add_permission(self):
        mock_request = mock.MagicMock()
        ret = ResourceQuotaAdmin(mock.MagicMock(), mock.MagicMock())
        self.assertFalse(ret.has_add_permission(mock_request))

    def test_UserQuotasSettingInline(self):
        expected_readonly_fields = ('name', 'description', 'default', 'units')
        expected_fields = ('name', 'description', 'value', 'default', 'units')
        expected_model = UserQuota

        ret = UserQuotasSettingInline(mock.MagicMock(), mock.MagicMock())

        self.assertEquals(expected_readonly_fields, ret.readonly_fields)
        self.assertEquals(expected_fields, ret.fields)
        self.assertEquals(expected_model, ret.model)

    # Need to check
    # def test_UserQuotasSettingInline_get_queryset(self):
    #     obj = UserQuotasSettingInline(mock.MagicMock(), mock.MagicMock())
    #     mock_request = mock.MagicMock()
    #     obj.get_queryset(mock_request)
