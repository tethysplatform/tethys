import unittest
from unittest import mock

from tethys_config.models import SettingsCategory, Setting
from tethys_config.admin import SettingInline, SettingCategoryAdmin


class TethysConfigAdminTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_SettingInline(self):
        expected_fields = ('name', 'content', 'date_modified')
        expected_readonly_fields = ('name', 'date_modified')
        ret = SettingInline(mock.MagicMock(), mock.MagicMock())

        self.assertEqual(expected_fields, ret.fields)
        self.assertEqual(expected_readonly_fields, ret.readonly_fields)
        self.assertEqual(Setting, ret.model)
        self.assertEqual(0, ret.extra)
        self.assertIsNotNone(ret.formfield_overrides)

    def test_SettingCategoryAdmin(self):
        expected_fields = ('name',)
        expected_readonly_fields = ('name',)
        expected_inlines = [SettingInline]
        ret = SettingCategoryAdmin(mock.MagicMock(), mock.MagicMock())

        self.assertEqual(expected_fields, ret.fields)
        self.assertEqual(expected_readonly_fields, ret.readonly_fields)
        self.assertEqual(expected_inlines, ret.inlines)

    def test_has_delete_permission(self):
        mock_request = mock.MagicMock()
        ret = SettingCategoryAdmin(mock.MagicMock(), mock.MagicMock())
        self.assertFalse(ret.has_delete_permission(mock_request))

    def test_has_add_permission(self):
        mock_request = mock.MagicMock()
        ret = SettingCategoryAdmin(mock.MagicMock(), mock.MagicMock())
        self.assertFalse(ret.has_add_permission(mock_request))

    def test_admin_site_register(self):
        from django.contrib import admin
        registry = admin.site._registry
        self.assertIn(SettingsCategory, registry)
        self.assertIsInstance(registry[SettingsCategory], SettingCategoryAdmin)
