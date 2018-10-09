import unittest
import mock

from tethys_apps.admin import TethysAppSettingInline, CustomSettingInline, DatasetServiceSettingInline, \
    SpatialDatasetServiceSettingInline, WebProcessingServiceSettingInline, PersistentStoreConnectionSettingInline, \
    PersistentStoreDatabaseSettingInline, TethysAppAdmin, TethysExtensionAdmin

from tethys_apps.models import (TethysApp,
                                TethysExtension,
                                CustomSetting,
                                DatasetServiceSetting,
                                SpatialDatasetServiceSetting,
                                WebProcessingServiceSetting,
                                PersistentStoreConnectionSetting,
                                PersistentStoreDatabaseSetting)


class TestTethysAppAdmin(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_TethysAppSettingInline(self):
        expected_template = 'tethys_portal/admin/edit_inline/tabular.html'
        TethysAppSettingInline.model = mock.MagicMock()
        ret = TethysAppSettingInline(mock.MagicMock(), mock.MagicMock())
        self.assertEquals(expected_template, ret.template)

    def test_has_delete_permission(self):
        TethysAppSettingInline.model = mock.MagicMock()
        ret = TethysAppSettingInline(mock.MagicMock(), mock.MagicMock())
        self.assertFalse(ret.has_delete_permission(mock.MagicMock()))

    def test_has_add_permission(self):
        TethysAppSettingInline.model = mock.MagicMock()
        ret = TethysAppSettingInline(mock.MagicMock(), mock.MagicMock())
        self.assertFalse(ret.has_add_permission(mock.MagicMock()))

    def test_CustomSettingInline(self):
        expected_readonly_fields = ('name', 'description', 'type', 'required')
        expected_fields = ('name', 'description', 'type', 'value', 'required')
        expected_model = CustomSetting

        ret = CustomSettingInline(mock.MagicMock(), mock.MagicMock())

        self.assertEquals(expected_readonly_fields, ret.readonly_fields)
        self.assertEquals(expected_fields, ret.fields)
        self.assertEquals(expected_model, ret.model)

    def test_DatasetServiceSettingInline(self):
        expected_readonly_fields = ('name', 'description', 'required', 'engine')
        expected_fields = ('name', 'description', 'dataset_service', 'engine', 'required')
        expected_model = DatasetServiceSetting

        ret = DatasetServiceSettingInline(mock.MagicMock(), mock.MagicMock())

        self.assertEquals(expected_readonly_fields, ret.readonly_fields)
        self.assertEquals(expected_fields, ret.fields)
        self.assertEquals(expected_model, ret.model)

    def test_SpatialDatasetServiceSettingInline(self):
        expected_readonly_fields = ('name', 'description', 'required', 'engine')
        expected_fields = ('name', 'description', 'spatial_dataset_service', 'engine', 'required')
        expected_model = SpatialDatasetServiceSetting

        ret = SpatialDatasetServiceSettingInline(mock.MagicMock(), mock.MagicMock())

        self.assertEquals(expected_readonly_fields, ret.readonly_fields)
        self.assertEquals(expected_fields, ret.fields)
        self.assertEquals(expected_model, ret.model)

    def test_WebProcessingServiceSettingInline(self):
        expected_readonly_fields = ('name', 'description', 'required')
        expected_fields = ('name', 'description', 'web_processing_service', 'required')
        expected_model = WebProcessingServiceSetting

        ret = WebProcessingServiceSettingInline(mock.MagicMock(), mock.MagicMock())

        self.assertEquals(expected_readonly_fields, ret.readonly_fields)
        self.assertEquals(expected_fields, ret.fields)
        self.assertEquals(expected_model, ret.model)

    def test_PersistentStoreConnectionSettingInline(self):
        expected_readonly_fields = ('name', 'description', 'required')
        expected_fields = ('name', 'description', 'persistent_store_service', 'required')
        expected_model = PersistentStoreConnectionSetting

        ret = PersistentStoreConnectionSettingInline(mock.MagicMock(), mock.MagicMock())

        self.assertEquals(expected_readonly_fields, ret.readonly_fields)
        self.assertEquals(expected_fields, ret.fields)
        self.assertEquals(expected_model, ret.model)

    def test_PersistentStoreDatabaseSettingInline(self):
        expected_readonly_fields = ('name', 'description', 'required', 'spatial', 'initialized')
        expected_fields = ('name', 'description', 'spatial', 'initialized', 'persistent_store_service', 'required')
        expected_model = PersistentStoreDatabaseSetting

        ret = PersistentStoreDatabaseSettingInline(mock.MagicMock(), mock.MagicMock())

        self.assertEquals(expected_readonly_fields, ret.readonly_fields)
        self.assertEquals(expected_fields, ret.fields)
        self.assertEquals(expected_model, ret.model)

    # Need to check
    def test_PersistentStoreDatabaseSettingInline_get_queryset(self):
        obj = PersistentStoreDatabaseSettingInline(mock.MagicMock(), mock.MagicMock())
        mock_request = mock.MagicMock()
        obj.get_queryset(mock_request)

    def test_TethysAppAdmin(self):
        expected_readonly_fields = ('package',)
        expected_fields = ('package', 'name', 'description', 'tags', 'enabled', 'show_in_apps_library',
                           'enable_feedback')
        expected_inlines = [CustomSettingInline,
                            PersistentStoreConnectionSettingInline,
                            PersistentStoreDatabaseSettingInline,
                            DatasetServiceSettingInline,
                            SpatialDatasetServiceSettingInline,
                            WebProcessingServiceSettingInline]

        ret = TethysAppAdmin(mock.MagicMock(), mock.MagicMock())

        self.assertEquals(expected_readonly_fields, ret.readonly_fields)
        self.assertEquals(expected_fields, ret.fields)
        self.assertEquals(expected_inlines, ret.inlines)

    def test_TethysAppAdmin_has_delete_permission(self):
        ret = TethysAppAdmin(mock.MagicMock(), mock.MagicMock())
        self.assertFalse(ret.has_delete_permission(mock.MagicMock()))

    def test_TethysAppAdmin_has_add_permission(self):
        ret = TethysAppAdmin(mock.MagicMock(), mock.MagicMock())
        self.assertFalse(ret.has_add_permission(mock.MagicMock()))

    def test_TethysExtensionAdmin(self):
        expected_readonly_fields = ('package', 'name', 'description')
        expected_fields = ('package', 'name', 'description', 'enabled')

        ret = TethysExtensionAdmin(mock.MagicMock(), mock.MagicMock())

        self.assertEquals(expected_readonly_fields, ret.readonly_fields)
        self.assertEquals(expected_fields, ret.fields)

    def test_TethysExtensionAdmin_has_delete_permission(self):
        ret = TethysExtensionAdmin(mock.MagicMock(), mock.MagicMock())
        self.assertFalse(ret.has_delete_permission(mock.MagicMock()))

    def test_TethysExtensionAdmin_has_add_permission(self):
        ret = TethysExtensionAdmin(mock.MagicMock(), mock.MagicMock())
        self.assertFalse(ret.has_add_permission(mock.MagicMock()))

    def test_admin_site_register_tethys_app_admin(self):
        from django.contrib import admin
        registry = admin.site._registry
        self.assertIn(TethysApp, registry)
        self.assertIsInstance(registry[TethysApp], TethysAppAdmin)

    def test_admin_site_register_tethys_app_extension(self):
        from django.contrib import admin
        registry = admin.site._registry
        self.assertIn(TethysExtension, registry)
        self.assertIsInstance(registry[TethysExtension], TethysExtensionAdmin)
