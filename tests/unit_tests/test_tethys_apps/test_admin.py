import os
import unittest
from unittest import mock
from django.db.utils import ProgrammingError
from django.utils.html import format_html
from django.shortcuts import reverse
from django.contrib.auth.models import User
from tethys_apps.admin import TethysAppSettingInline, CustomSettingInline, DatasetServiceSettingInline, \
    SpatialDatasetServiceSettingInline, WebProcessingServiceSettingInline, PersistentStoreConnectionSettingInline, \
    PersistentStoreDatabaseSettingInline, TethysAppAdmin, TethysExtensionAdmin, CustomUser, make_gop_app_access_form, \
    register_custom_group, register_user_keys_admin
from tethys_quotas.admin import TethysAppQuotasSettingInline, UserQuotasSettingInline

from tethys_quotas.models import TethysAppQuota

from tethys_apps.models import (TethysApp,
                                TethysExtension,
                                CustomSetting,
                                DatasetServiceSetting,
                                SpatialDatasetServiceSetting,
                                WebProcessingServiceSetting,
                                PersistentStoreConnectionSetting,
                                PersistentStoreDatabaseSetting,
                                ProxyApp)


class TestTethysAppAdmin(unittest.TestCase):

    def setUp(self):
        from tethys_apps.models import TethysApp
        self.src_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.root_app_path = os.path.join(self.src_dir, 'apps', 'tethysapp-test_app')
        self.app_model = TethysApp(
            name='test_app',
            package='test_app'
        )
        self.app_model.save()

        from django.contrib.auth.models import ContentType, Group, Permission

        app_content_type_id = ContentType.objects.get(app_label='tethys_apps', model='tethysapp').pk
        self.perm_model = Permission(
            name='Test Perm | Test',
            content_type_id=app_content_type_id,
            codename='test_perm:test'
        )
        self.perm_model.save()

        self.group_model = Group(
            name='test_group'
        )
        self.group_model.save()

    def tearDown(self):
        self.app_model.delete()
        self.perm_model.delete()
        self.group_model.delete()

    def test_TethysAppSettingInline(self):
        expected_template = 'tethys_portal/admin/edit_inline/tabular.html'
        TethysAppSettingInline.model = mock.MagicMock()
        ret = TethysAppSettingInline(mock.MagicMock(), mock.MagicMock())
        self.assertEqual(expected_template, ret.template)

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

        self.assertEqual(expected_readonly_fields, ret.readonly_fields)
        self.assertEqual(expected_fields, ret.fields)
        self.assertEqual(expected_model, ret.model)

    def test_DatasetServiceSettingInline(self):
        expected_readonly_fields = ('name', 'description', 'required', 'engine')
        expected_fields = ('name', 'description', 'dataset_service', 'engine', 'required')
        expected_model = DatasetServiceSetting

        ret = DatasetServiceSettingInline(mock.MagicMock(), mock.MagicMock())

        self.assertEqual(expected_readonly_fields, ret.readonly_fields)
        self.assertEqual(expected_fields, ret.fields)
        self.assertEqual(expected_model, ret.model)

    def test_SpatialDatasetServiceSettingInline(self):
        expected_readonly_fields = ('name', 'description', 'required', 'engine')
        expected_fields = ('name', 'description', 'spatial_dataset_service', 'engine', 'required')
        expected_model = SpatialDatasetServiceSetting

        ret = SpatialDatasetServiceSettingInline(mock.MagicMock(), mock.MagicMock())

        self.assertEqual(expected_readonly_fields, ret.readonly_fields)
        self.assertEqual(expected_fields, ret.fields)
        self.assertEqual(expected_model, ret.model)

    def test_WebProcessingServiceSettingInline(self):
        expected_readonly_fields = ('name', 'description', 'required')
        expected_fields = ('name', 'description', 'web_processing_service', 'required')
        expected_model = WebProcessingServiceSetting

        ret = WebProcessingServiceSettingInline(mock.MagicMock(), mock.MagicMock())

        self.assertEqual(expected_readonly_fields, ret.readonly_fields)
        self.assertEqual(expected_fields, ret.fields)
        self.assertEqual(expected_model, ret.model)

    def test_PersistentStoreConnectionSettingInline(self):
        expected_readonly_fields = ('name', 'description', 'required')
        expected_fields = ('name', 'description', 'persistent_store_service', 'required')
        expected_model = PersistentStoreConnectionSetting

        ret = PersistentStoreConnectionSettingInline(mock.MagicMock(), mock.MagicMock())

        self.assertEqual(expected_readonly_fields, ret.readonly_fields)
        self.assertEqual(expected_fields, ret.fields)
        self.assertEqual(expected_model, ret.model)

    def test_PersistentStoreDatabaseSettingInline(self):
        expected_readonly_fields = ('name', 'description', 'required', 'spatial', 'initialized')
        expected_fields = ('name', 'description', 'spatial', 'initialized', 'persistent_store_service', 'required')
        expected_model = PersistentStoreDatabaseSetting

        ret = PersistentStoreDatabaseSettingInline(mock.MagicMock(), mock.MagicMock())

        self.assertEqual(expected_readonly_fields, ret.readonly_fields)
        self.assertEqual(expected_fields, ret.fields)
        self.assertEqual(expected_model, ret.model)

    # Need to check
    def test_PersistentStoreDatabaseSettingInline_get_queryset(self):
        obj = PersistentStoreDatabaseSettingInline(mock.MagicMock(), mock.MagicMock())
        mock_request = mock.MagicMock()
        obj.get_queryset(mock_request)

    def test_TethysAppQuotasSettingInline(self):
        expected_readonly_fields = ('name', 'description', 'default', 'units')
        expected_fields = ('name', 'description', 'value', 'default', 'units')
        expected_model = TethysAppQuota

        ret = TethysAppQuotasSettingInline(mock.MagicMock(), mock.MagicMock())

        self.assertEquals(expected_readonly_fields, ret.readonly_fields)
        self.assertEquals(expected_fields, ret.fields)
        self.assertEquals(expected_model, ret.model)

    # Need to check
    # def test_TethysAppQuotasSettingInline_get_queryset(self):
    #     obj = TethysAppQuotasSettingInline(mock.MagicMock(), mock.MagicMock())
    #     mock_request = mock.MagicMock()
    #     obj.get_queryset(mock_request)

    def test_TethysAppAdmin(self):
        expected_readonly_fields = ('package', 'manage_app_storage',)
        expected_fields = ('package', 'name', 'description', 'icon', 'color', 'tags', 'enabled',
                           'show_in_apps_library', 'enable_feedback', 'manage_app_storage')
        expected_inlines = [CustomSettingInline,
                            PersistentStoreConnectionSettingInline,
                            PersistentStoreDatabaseSettingInline,
                            DatasetServiceSettingInline,
                            SpatialDatasetServiceSettingInline,
                            WebProcessingServiceSettingInline,
                            TethysAppQuotasSettingInline]

        ret = TethysAppAdmin(mock.MagicMock(), mock.MagicMock())

        self.assertEqual(expected_readonly_fields, ret.readonly_fields)
        self.assertEqual(expected_fields, ret.fields)
        self.assertEqual(expected_inlines, ret.inlines)

    def test_TethysAppAdmin_has_delete_permission(self):
        ret = TethysAppAdmin(mock.MagicMock(), mock.MagicMock())
        self.assertFalse(ret.has_delete_permission(mock.MagicMock()))

    def test_TethysAppAdmin_has_add_permission(self):
        ret = TethysAppAdmin(mock.MagicMock(), mock.MagicMock())
        self.assertFalse(ret.has_add_permission(mock.MagicMock()))

    @mock.patch('tethys_apps.admin.get_quota')
    @mock.patch('tethys_apps.admin._convert_storage_units')
    def test_TethysAppAdmin_manage_app_storage(self, mock_convert, mock_get_quota):
        ret = TethysAppAdmin(mock.MagicMock(), mock.MagicMock())
        app = mock.MagicMock()
        app.id = 1
        mock_convert.return_value = '0 bytes'
        mock_get_quota.return_value = {'quota': None}
        url = reverse('admin:clear_workspace', kwargs={'app_id': app.id})

        expected_html = format_html("""
                <span>{} of {}</span>
                <a id="clear-workspace" class="btn btn-danger btn-sm"
                href="{url}">
                Clear Workspace</a>
                """.format('0 bytes', "&#8734;", url=url))
        actual_html = ret.manage_app_storage(app)

        self.assertEquals(expected_html.replace(" ", ""), actual_html.replace(" ", ""))

        mock_convert.return_value = '0 bytes'
        mock_get_quota.return_value = {'quota': 5, 'units': 'gb'}
        url = reverse('admin:clear_workspace', kwargs={'app_id': app.id})

        expected_html = format_html("""
                        <span>{} of {}</span>
                        <a id="clear-workspace" class="btn btn-danger btn-sm"
                        href="{url}">
                        Clear Workspace</a>
                        """.format('0 bytes', "0 bytes", url=url))
        actual_html = ret.manage_app_storage(app)

        self.assertEquals(expected_html.replace(" ", ""), actual_html.replace(" ", ""))

    def test_TethysExtensionAdmin(self):
        expected_readonly_fields = ('package', 'name', 'description')
        expected_fields = ('package', 'name', 'description', 'enabled')

        ret = TethysExtensionAdmin(mock.MagicMock(), mock.MagicMock())

        self.assertEqual(expected_readonly_fields, ret.readonly_fields)
        self.assertEqual(expected_fields, ret.fields)

    def test_TethysExtensionAdmin_has_delete_permission(self):
        ret = TethysExtensionAdmin(mock.MagicMock(), mock.MagicMock())
        self.assertFalse(ret.has_delete_permission(mock.MagicMock()))

    def test_TethysExtensionAdmin_has_add_permission(self):
        ret = TethysExtensionAdmin(mock.MagicMock(), mock.MagicMock())
        self.assertFalse(ret.has_add_permission(mock.MagicMock()))

    @mock.patch('django.contrib.auth.admin.UserAdmin.change_view')
    @mock.patch('django.contrib.auth.admin.UserAdmin.add_view')
    def test_admin_site_register_custom_user(self, mock_ua_add_view, mock_ua_change_view):
        from django.contrib import admin
        ret = CustomUser(mock.MagicMock(), mock.MagicMock())

        # Add custom inline when change_view is called
        ret.change_view(mock.MagicMock())
        mock_ua_change_view.assert_called()
        self.assertIn(UserQuotasSettingInline, ret.inlines)

        # Remove custom inline when change_view is called
        ret.add_view(mock.MagicMock())
        mock_ua_add_view.assert_called()
        self.assertNotIn(UserQuotasSettingInline, ret.inlines)

        # Repeat to complete full cycle (change -> add -> change -> add)
        # Add custom inline when change_view is called
        ret.change_view(mock.MagicMock())
        mock_ua_change_view.assert_called()
        self.assertIn(UserQuotasSettingInline, ret.inlines)

        # Remove custom inline when change_view is called
        ret.add_view(mock.MagicMock())
        mock_ua_add_view.assert_called()
        self.assertNotIn(UserQuotasSettingInline, ret.inlines)

        # Check registration
        registry = admin.site._registry
        self.assertIn(User, registry)
        self.assertIsInstance(registry[User], CustomUser)

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

    def test_admin_site_register_proxy_app(self):
        from django.contrib import admin
        registry = admin.site._registry
        self.assertIn(ProxyApp, registry)

    @mock.patch('tethys_apps.admin.GroupObjectPermission.objects')
    @mock.patch('tethys_apps.admin.TethysApp.objects.all')
    def test_make_gop_app_access_form(self, mock_all_apps, mock_gop):
        mock_all_apps.return_value = [self.app_model]
        mock_gop.filter().values().distinct.return_value = [{'group_id': 9999}]

        ret = make_gop_app_access_form()

        self.assertIn('test_app_permissions', ret.base_fields)
        self.assertIn('test_app_groups', ret.base_fields)

    @mock.patch('tethys_apps.admin.Group.objects')
    @mock.patch('tethys_apps.admin.Permission.objects')
    @mock.patch('tethys_apps.admin.GroupObjectPermission.objects')
    @mock.patch('tethys_apps.admin.TethysApp.objects.all')
    def test_gop_form_init(self, mock_all_apps, mock_gop, mock_perms, mock_groups):
        mock_all_apps.return_value = [self.app_model]
        mock_obj = mock.MagicMock(pk=True)
        mock_gop.values().distinct().filter.return_value = [{'object_pk': self.app_model.pk}]
        mock_gop.values_list().filter().distinct.side_effect = [
            [9999],
            [9999],
            mock.MagicMock(exclude=mock.MagicMock(return_value=[self.app_model.pk, 9999])),
            [self.app_model.pk]
        ]

        mock_perms.filter().exclude.side_effect = [mock_perms.none(), '_permissions_test']
        mock_groups.filter().exclude.return_value = '_groups_test'

        gop_app_access_form_dynamic = make_gop_app_access_form()
        ret = gop_app_access_form_dynamic(instance=mock_obj)

        self.assertIn(self.app_model, ret.fields['apps'].initial)
        self.assertEqual(ret.fields['test_app_permissions'].initial, '_permissions_test')
        self.assertEqual(ret.fields['test_app_groups'].initial, '_groups_test')

    @mock.patch('tethys_apps.admin.TethysApp.objects.all')
    def test_gop_form_clean(self, mock_all_apps):
        mock_all_apps.return_value = [self.app_model]
        mock_obj = mock.MagicMock(pk=True)
        mock_data = mock.MagicMock(getlist=mock.MagicMock(return_value=[9999]))

        gop_app_access_form_dynamic = make_gop_app_access_form()
        ret = gop_app_access_form_dynamic(instance=mock_obj)

        ret.data = mock_data
        ret.cleaned_data = {}
        ret.clean()

        self.assertIn('test_app_permissions', ret.cleaned_data)
        self.assertIn('test_app_groups', ret.cleaned_data)

    @mock.patch('tethys_apps.admin.remove_perm')
    @mock.patch('tethys_apps.admin.assign_perm')
    @mock.patch('tethys_apps.admin.TethysApp.objects.all')
    def test_gop_form_save_new(self, mock_all_apps, _, __):
        mock_all_apps.return_value = [self.app_model]
        mock_obj = mock.MagicMock(pk=False)
        mock_data = mock.MagicMock(getlist=mock.MagicMock(return_value=[9999]))

        gop_app_access_form_dynamic = make_gop_app_access_form()
        ret = gop_app_access_form_dynamic(instance=mock_obj)

        ret.data = mock_data
        ret.cleaned_data = {'apps': [self.app_model]}
        ret.fields = {'apps': ret.fields['apps']}

        ret.save()

        self.assertEqual(mock_obj.save.call_count, 1)

    @mock.patch('tethys_apps.admin.assign_perm')
    @mock.patch('tethys_apps.admin.remove_perm')
    @mock.patch('tethys_apps.admin.TethysApp.objects')
    def test_gop_form_save_edit_apps(self, mock_apps, mock_remove_perm, mock_assign_perm):
        mock_apps.all.return_value = [self.app_model]
        mock_diff = mock.MagicMock(return_value=[self.app_model])
        mock_apps.filter.return_value = mock.MagicMock(difference=mock_diff, return_value=True)
        mock_obj = mock.MagicMock(pk=True)
        mock_data = mock.MagicMock(getlist=mock.MagicMock(return_value=[9999]))

        gop_app_access_form_dynamic = make_gop_app_access_form()
        ret = gop_app_access_form_dynamic(instance=mock_obj)

        ret.data = mock_data
        ret.cleaned_data = {'apps': [self.app_model]}
        ret.fields = {'apps': ret.fields['apps']}

        ret.save()

        mock_remove_perm.assert_called_with('test_app:access_app', mock_obj, self.app_model)
        mock_assign_perm.assert_called_with('test_app:access_app', mock_obj, self.app_model)

    @mock.patch('tethys_apps.admin.assign_perm')
    @mock.patch('tethys_apps.admin.remove_perm')
    @mock.patch('tethys_apps.admin.TethysApp.objects')
    def test_gop_form_save_edit_permissions(self, mock_apps, mock_remove_perm, mock_assign_perm):
        mock_apps.all.return_value = [self.app_model]
        mock_diff = mock.MagicMock(side_effect=[[self.app_model], [self.perm_model]])
        mock_apps.filter.return_value = mock.MagicMock(difference=mock_diff, return_value=True)
        mock_obj = mock.MagicMock(pk=True)
        mock_data = mock.MagicMock(getlist=mock.MagicMock(return_value=[9999]))

        gop_app_access_form_dynamic = make_gop_app_access_form()
        ret = gop_app_access_form_dynamic(instance=mock_obj)

        ret.data = mock_data
        ret.cleaned_data = {'apps': [self.app_model], 'test_app_permissions': [self.perm_model]}
        ret.fields = {'apps': ret.fields['apps'], 'test_app_permissions': ret.fields['apps']}

        ret.save()

        mock_remove_perm.assert_called_with('test_perm:test', mock_obj, mock_apps.filter())
        mock_assign_perm.assert_called_with('test_perm:test', mock_obj, mock_apps.filter())

    @mock.patch('tethys_apps.admin.assign_perm')
    @mock.patch('tethys_apps.admin.remove_perm')
    @mock.patch('tethys_apps.admin.GroupObjectPermission.objects')
    @mock.patch('tethys_apps.admin.TethysApp.objects')
    def test_gop_form_save_edit_groups(self, mock_apps, mock_gop, mock_remove_perm, mock_assign_perm):
        mock_apps.all.return_value = [self.app_model]
        mock_diff = mock.MagicMock(side_effect=[
            [self.app_model],
            mock.MagicMock(values_list=mock.MagicMock(distinct=[self.group_model.pk]))
        ])
        mock_apps.filter.return_value = mock.MagicMock(difference=mock_diff, return_value=True)
        mock_obj = mock.MagicMock(pk=True)
        mock_data = mock.MagicMock(getlist=mock.MagicMock(return_value=[9999]))
        mock_gop.filter().values_list().distinct.return_value = [self.perm_model.pk]

        gop_app_access_form_dynamic = make_gop_app_access_form()
        ret = gop_app_access_form_dynamic(instance=mock_obj)

        ret.data = mock_data
        ret.cleaned_data = {'apps': [self.app_model], 'test_app_groups': mock.MagicMock()}
        ret.cleaned_data['test_app_groups'].values_list().distinct.return_value = [self.group_model.pk]
        ret.fields = {'apps': ret.fields['apps'], 'test_app_groups': ret.fields['apps']}

        ret.save()

        mock_remove_perm.assert_called_with('test_perm:test', mock_obj, mock_apps.filter())
        mock_assign_perm.assert_called_with('test_perm:test', mock_obj, mock_apps.filter())

    @mock.patch('tethys_apps.admin.tethys_log.warning')
    @mock.patch('tethys_apps.admin.make_gop_app_access_form')
    def test_admin_programming_error(self, mock_gop_form, mock_logwarning):
        mock_gop_form.side_effect = ProgrammingError

        register_custom_group()

        mock_gop_form.assert_called()
        mock_logwarning.assert_called_with('Unable to register CustomGroup.')

    @mock.patch('tethys_apps.admin.tethys_log.warning')
    @mock.patch('tethys_apps.admin.admin.site.register')
    def test_admin_user_keys_programming_error(self, mock_register, mock_logwarning):
        mock_register.side_effect = ProgrammingError

        register_user_keys_admin()

        mock_register.assert_called()
        mock_logwarning.assert_called_with('Unable to register UserKeys.')
