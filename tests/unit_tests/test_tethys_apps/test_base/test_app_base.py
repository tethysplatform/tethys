import unittest
import tethys_apps.base.app_base as tethys_app_base
from unittest import mock

import uuid
from django.db.utils import ProgrammingError
from django.test import RequestFactory
from ... import UserFactory
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from tethys_apps.exceptions import TethysAppSettingDoesNotExist, TethysAppSettingNotAssigned
from types import FunctionType
from tethys_apps.base.permissions import Permission, PermissionGroup


class TethysAppChild(tethys_app_base.TethysAppBase):
    """
    Tethys app class for Test App.
    """

    name = 'Test App'
    index = 'test_app:home'
    icon = 'test_app/images/icon.gif'
    package = 'test_app'
    root_url = 'test-app'
    color = '#2c3e50'
    description = 'Place a brief description of your app here.'


class TestTethysBase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_url_maps(self):
        result = tethys_app_base.TethysBase().url_maps()
        self.assertEqual([], result)

    @mock.patch('tethys_apps.base.app_base.url')
    @mock.patch('tethys_apps.base.app_base.TethysBaseMixin')
    def test_url_patterns(self, mock_tbm, mock_url):
        app = tethys_app_base.TethysBase()
        app._namespace = 'foo'
        url_map = mock.MagicMock(controller='test_app.controllers.home', url='test-url', protocol='http')
        url_map.name = 'home'
        url_map_ws = mock.MagicMock(controller='test_app.controllers.TestWS', url='test-url-ws', protocol='websocket')
        url_map_ws.name = 'ws'
        app.url_maps = mock.MagicMock(return_value=[url_map, url_map_ws])
        mock_tbm.return_value = mock.MagicMock(url_maps='test-app')

        # Execute
        result = app.url_patterns
        # Check url call at django_url = url...
        rts_call_args = mock_url.call_args_list
        self.assertEqual('test-url', rts_call_args[0][0][0])
        self.assertEqual('test-url-ws', rts_call_args[1][0][0])
        self.assertIn('name', rts_call_args[0][1])
        self.assertIn('name', rts_call_args[1][1])
        self.assertEqual('home', rts_call_args[0][1]['name'])
        self.assertEqual('ws', rts_call_args[1][1]['name'])
        self.assertIn('foo', result['http'])
        self.assertIn('foo', result['websocket'])
        self.assertIsInstance(rts_call_args[0][0][1], FunctionType)
        self.assertIsInstance(rts_call_args[1][0][1], type)

    @mock.patch('tethys_apps.base.app_base.url')
    @mock.patch('tethys_apps.base.app_base.TethysBaseMixin')
    def test_url_patterns_no_str(self, mock_tbm, mock_url):
        app = tethys_app_base.TethysBase()
        # controller_mock = mock.MagicMock()

        def test_func():
            return ''

        url_map = mock.MagicMock(controller=test_func, url='test-app', protocol='http')
        url_map.name = 'home'
        app.url_maps = mock.MagicMock(return_value=[url_map])
        mock_tbm.return_value = mock.MagicMock(url_maps='test-app')

        # Execute
        app.url_patterns

        # Check url call at django_url = url...
        rts_call_args = mock_url.call_args_list
        self.assertEqual('test-app', rts_call_args[0][0][0])
        self.assertIn('name', rts_call_args[0][1])
        self.assertEqual('home', rts_call_args[0][1]['name'])
        self.assertIs(rts_call_args[0][0][1], test_func)

    @mock.patch('tethys_apps.base.app_base.tethys_log')
    @mock.patch('tethys_apps.base.app_base.TethysBaseMixin')
    def test_url_patterns_import_error(self, mock_tbm, mock_log):
        mock_error = mock_log.error
        app = tethys_app_base.TethysBase()
        url_map = mock.MagicMock(controller='1module.1function', url='test-app', protocol='http')
        url_map.name = 'home'
        app.url_maps = mock.MagicMock(return_value=[url_map])
        mock_tbm.return_value = mock.MagicMock(url_maps='test-app')

        # assertRaises needs a callable, not a property
        def test_url_patterns():
            return app.url_patterns

        # Check Error Message
        self.assertRaises(ImportError, test_url_patterns)
        rts_call_args = mock_error.call_args_list
        error_message = 'The following error occurred while trying to import' \
                        ' the controller function "1module.1function"'
        self.assertIn(error_message, rts_call_args[0][0][0])

    @mock.patch('tethys_apps.base.app_base.tethys_log')
    @mock.patch('tethys_apps.base.app_base.TethysBaseMixin')
    def test_url_patterns_attribute_error(self, mock_tbm, mock_log):
        mock_error = mock_log.error
        app = tethys_app_base.TethysBase()
        url_map = mock.MagicMock(controller='test_app.controllers.home1', url='test-app', protocol='http')
        url_map.name = 'home'
        app.url_maps = mock.MagicMock(return_value=[url_map])
        mock_tbm.return_value = mock.MagicMock(url_maps='test-app')

        # assertRaises needs a callable, not a property
        def test_url_patterns():
            return app.url_patterns

        # Check Error Message
        self.assertRaises(AttributeError, test_url_patterns)
        rts_call_args = mock_error.call_args_list
        error_message = 'The following error occurred while trying to access' \
                        ' the controller function "test_app.controllers.home1"'
        self.assertIn(error_message, rts_call_args[0][0][0])

    @mock.patch('tethys_apps.base.app_base.url')
    @mock.patch('tethys_apps.base.app_base.TethysBaseMixin')
    def test_handler_patterns(self, mock_tbm, mock_url):
        # import pdb; pdb.set_trace()
        app = tethys_app_base.TethysBase()
        app._namespace = 'foo'
        app.root_url = 'test-url'
        url_map = mock.MagicMock(controller='test_app.controllers.home',
                                 handler='test_app.controllers.home_handler', handler_type='bokeh', url='')
        url_map.name = 'home'

        app.url_maps = mock.MagicMock(return_value=[url_map, ])
        mock_tbm.return_value = mock.MagicMock(url_maps=['test-app', ])

        # Execute
        result = app.handler_patterns
        # Check url call at django_url = url...
        rts_call_args = mock_url.call_args_list
        self.assertEqual(r'^apps/test-url/autoload.js$', rts_call_args[0][0][0])
        self.assertEqual(r'^apps/test-url/ws$', rts_call_args[1][0][0])
        self.assertIn('name', rts_call_args[0][1])
        self.assertIn('name', rts_call_args[1][1])
        self.assertEqual('home_bokeh_autoload', rts_call_args[0][1]['name'])
        self.assertEqual('home_bokeh_ws', rts_call_args[1][1]['name'])
        self.assertIn('foo', result['http'])
        self.assertIn('foo', result['websocket'])
        self.assertIsInstance(rts_call_args[0][0][1], type)
        self.assertIsInstance(rts_call_args[1][0][1], type)

    @mock.patch('tethys_apps.base.app_base.url')
    @mock.patch('tethys_apps.base.app_base.TethysBaseMixin')
    def test_handler_patterns_from_function(self, mock_tbm, mock_url):
        app = tethys_app_base.TethysBase()
        app._namespace = 'foo'
        app.root_url = 'test-url'

        def test_func(mock_doc):
            return ''

        url_map = mock.MagicMock(controller='test_app.controllers.home',
                                 handler=test_func, handler_type='bokeh', url='')
        url_map.name = 'home'
        app.url_maps = mock.MagicMock(return_value=[url_map, ])
        mock_tbm.return_value = mock.MagicMock(url_maps=['test-app', ])

        app.handler_patterns

        rts_call_args = mock_url.call_args_list
        self.assertEqual(r'^apps/test-url/autoload.js$', rts_call_args[0][0][0])
        self.assertIn('name', rts_call_args[0][1])
        self.assertIn('name', rts_call_args[1][1])
        self.assertEqual('home_bokeh_autoload', rts_call_args[0][1]['name'])
        self.assertEqual('home_bokeh_ws', rts_call_args[1][1]['name'])
        self.assertIs(rts_call_args[0][1]['kwargs']['app_context']._application._handlers[0]._func, test_func)

    @mock.patch('tethys_apps.base.app_base.url')
    @mock.patch('tethys_apps.base.app_base.TethysBaseMixin')
    def test_handler_patterns_url_basename(self, mock_tbm, mock_url):
        app = tethys_app_base.TethysBase()
        app._namespace = 'foo'
        app.root_url = 'test-url'

        def test_func(mock_doc):
            return ''

        url_map = mock.MagicMock(controller='test_app.controllers.home',
                                 handler=test_func, handler_type='bokeh')
        url_map.name = 'basename'
        url_map.url = 'basename/'
        app.url_maps = mock.MagicMock(return_value=[url_map, ])
        mock_tbm.return_value = mock.MagicMock(url_maps=['basename/', ])

        app.handler_patterns

        rts_call_args = mock_url.call_args_list
        self.assertEqual(r'^apps/test-url/basename/autoload.js$', rts_call_args[0][0][0])
        self.assertIn('name', rts_call_args[0][1])
        self.assertIn('name', rts_call_args[1][1])
        self.assertEqual('basename_bokeh_autoload', rts_call_args[0][1]['name'])
        self.assertEqual('basename_bokeh_ws', rts_call_args[1][1]['name'])
        self.assertIs(rts_call_args[0][1]['kwargs']['app_context']._application._handlers[0]._func, test_func)

    @mock.patch('tethys_apps.base.app_base.tethys_log')
    @mock.patch('tethys_apps.base.app_base.TethysBaseMixin')
    def test_handler_patterns_import_error(self, mock_tbm, mock_log):
        mock_error = mock_log.error
        app = tethys_app_base.TethysBase()
        url_map = mock.MagicMock(controller='test_app.controllers.home',
                                 handler='1module.1function', handler_type='bokeh', url='')
        url_map.name = 'home'
        app.url_maps = mock.MagicMock(return_value=[url_map])
        mock_tbm.return_value = mock.MagicMock(url_maps=['test-app', ])

        # assertRaises needs a callable, not a property
        def test_handler_patterns():
            return app.handler_patterns

        # Check Error Message
        self.assertRaises(ImportError, test_handler_patterns)
        rts_call_args = mock_error.call_args_list
        error_message = 'The following error occurred while trying to import' \
                        ' the handler function "1module.1function"'
        self.assertIn(error_message, rts_call_args[0][0][0])

    @mock.patch('tethys_apps.base.app_base.tethys_log')
    @mock.patch('tethys_apps.base.app_base.TethysBaseMixin')
    def test_handler_patterns_attribute_error(self, mock_tbm, mock_log):
        mock_error = mock_log.error
        app = tethys_app_base.TethysBase()
        url_map = mock.MagicMock(controller='test_app.controllers.home',
                                 handler='test_app.controllers.home_handler1', handler_type='bokeh', url='')
        url_map.name = 'home'
        app.url_maps = mock.MagicMock(return_value=[url_map])
        mock_tbm.return_value = mock.MagicMock(url_maps='test-app')

        # assertRaises needs a callable, not a property
        def test_handler_patterns():
            return app.handler_patterns

        # Check Error Message
        self.assertRaises(AttributeError, test_handler_patterns)
        rts_call_args = mock_error.call_args_list
        error_message = 'The following error occurred while trying to access' \
                        ' the handler function "test_app.controllers.home_handler1"'
        self.assertIn(error_message, rts_call_args[0][0][0])

    def test_sync_with_tethys_db(self):
        self.assertRaises(NotImplementedError, tethys_app_base.TethysBase().sync_with_tethys_db)

    def test_remove_from_db(self):
        self.assertRaises(NotImplementedError, tethys_app_base.TethysBase().remove_from_db)


class TestTethysExtensionBase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__str__(self):
        result = tethys_app_base.TethysExtensionBase().__str__()
        self.assertEqual('<TethysApp: >', result)

    def test__repr__(self):
        result = tethys_app_base.TethysExtensionBase().__repr__()
        self.assertEqual('<TethysApp: >', result)

    def test_url_maps(self):
        result = tethys_app_base.TethysExtensionBase().url_maps()
        self.assertEqual([], result)

    @mock.patch('tethys_apps.models.TethysExtension')
    def test_sync_with_tethys_db(self, mock_te):
        mock_te.objects.filter().all.return_value = []

        tethys_app_base.TethysExtensionBase().sync_with_tethys_db()

        mock_te.assert_called_with(description='', name='', package='', root_url='')
        mock_te().save.assert_called()

    @mock.patch('django.conf.settings')
    @mock.patch('tethys_apps.models.TethysExtension')
    def test_sync_with_tethys_db_exists(self, mock_te, mock_ds):
        mock_ds.DEBUG = True
        ext = tethys_app_base.TethysExtensionBase()
        ext.root_url = 'test_url'
        mock_te2 = mock.MagicMock()
        mock_te.objects.filter().all.return_value = [mock_te2]
        ext.sync_with_tethys_db()

        # Check_result
        self.assertTrue(mock_te2.save.call_count == 2)

    @mock.patch('tethys_apps.base.app_base.tethys_log')
    @mock.patch('tethys_apps.models.TethysExtension')
    def test_sync_with_tethys_db_exists_log_error(self, mock_te, mock_log):
        mock_error = mock_log.error
        ext = tethys_app_base.TethysExtensionBase()
        ext.root_url = 'test_url'
        mock_te.objects.filter().all.side_effect = Exception('test_error')
        ext.sync_with_tethys_db()

        # Check_result
        rts_call_args = mock_error.call_args_list
        self.assertEqual('test_error', rts_call_args[0][0][0].args[0])

    @mock.patch('tethys_apps.base.app_base.tethys_log')
    @mock.patch('tethys_apps.models.TethysExtension')
    def test_sync_with_tethys_db_exists_progamming_error(self, mock_te, mock_log):
        mock_warning = mock_log.warning
        ext = tethys_app_base.TethysExtensionBase()
        ext.root_url = 'test_url'
        mock_te.objects.filter().all.side_effect = ProgrammingError('test_error')
        ext.sync_with_tethys_db()

        # Check_result
        mock_warning.assert_called_with("Unable to sync extension with database. "
                                        "tethys_apps_tethysextension table does not exist")


class TestTethysAppBase(unittest.TestCase):
    def setUp(self):
        self.app = tethys_app_base.TethysAppBase()
        self.user = UserFactory()
        self.request_factory = RequestFactory()
        self.fake_name = 'fake_name'

    def tearDown(self):
        pass

    def test__str__(self):
        result = tethys_app_base.TethysAppBase().__str__()
        self.assertEqual('<TethysApp: >', result)

    def test__repr__(self):
        result = tethys_app_base.TethysAppBase().__repr__()
        self.assertEqual('<TethysApp: >', result)

    def test_custom_settings(self):
        self.assertIsNone(tethys_app_base.TethysAppBase().custom_settings())

    def test_persistent_store_settings(self):
        self.assertIsNone(tethys_app_base.TethysAppBase().persistent_store_settings())

    def test_dataset_service_settings(self):
        self.assertIsNone(tethys_app_base.TethysAppBase().dataset_service_settings())

    def test_spatial_dataset_service_settings(self):
        self.assertIsNone(tethys_app_base.TethysAppBase().spatial_dataset_service_settings())

    def test_web_processing_service_settings(self):
        self.assertIsNone(tethys_app_base.TethysAppBase().web_processing_service_settings())

    def test_handoff_handlers(self):
        self.assertIsNone(tethys_app_base.TethysAppBase().handoff_handlers())

    def test_permissions(self):
        self.assertIsNone(tethys_app_base.TethysAppBase().permissions())

    @mock.patch('guardian.shortcuts.get_perms')
    @mock.patch('guardian.shortcuts.remove_perm')
    @mock.patch('guardian.shortcuts.assign_perm')
    @mock.patch('tethys_apps.models.TethysApp')
    @mock.patch('django.contrib.auth.models.Group')
    @mock.patch('django.contrib.auth.models.Permission')
    def test_register_app_permissions(self, mock_dp, mock_dg, mock_ta, mock_asg, mock_rem, mock_get):
        group_name = 'test_group'
        create_test_perm = Permission(name='create_test', description='test_create')
        delete_test_perm = Permission(name='delete_test', description='test_delete')
        group_perm = PermissionGroup(name=group_name, permissions=[create_test_perm, delete_test_perm])
        self.app.permissions = mock.MagicMock(return_value=[create_test_perm, group_perm])

        # Mock db_app_permissions
        db_app_permission = mock.MagicMock(codename='test_code')
        mock_perm_query = mock_dp.objects.filter().filter().all
        mock_perm_query.return_value = [db_app_permission]

        # Mock Group.objects.filter
        db_group = mock.MagicMock()
        db_group.name = 'test_app_name:group'

        mock_group = mock_dg.objects.filter().all
        mock_group.return_value = [db_group]

        # Mock TethysApp.objects.all()
        db_app = mock.MagicMock(package='test_app_name')

        mock_toa = mock_ta.objects.all
        mock_toa.return_value = [db_app]

        # Mock TethysApp.objects.get()
        mock_ta_get = mock_ta.objects.get
        mock_ta_get.return_value = 'test_get'

        # Mock Group.objects.get()
        mock_group_get = mock_dg.objects.get
        mock_group_get.return_value = group_name

        # Mock get permission get_perms(g, db_app)
        mock_get.return_value = ['create_test']

        # Execute
        self.app.register_app_permissions()

        # Check if db_app_permission.delete() is called
        db_app_permission.delete.assert_called_with()

        # Check if p.saved is called in perm
        mock_dp.objects.get().save.assert_called_with()

        # Check if db_group.delete() is called
        db_group.delete.assert_called_with()

        # Check if remove_perm(p, g, db_app) is called
        mock_rem.assert_called_with('create_test', group_name, 'test_get')

        # Check if assign_perm(p, g, db_app) is called
        mock_asg.assert_called_with(':delete_test', group_name, 'test_get')

    @mock.patch('guardian.shortcuts.get_perms')
    @mock.patch('guardian.shortcuts.remove_perm')
    @mock.patch('guardian.shortcuts.assign_perm')
    @mock.patch('tethys_apps.models.TethysApp')
    @mock.patch('django.contrib.auth.models.Group')
    @mock.patch('django.contrib.auth.models.Permission')
    def test_register_app_permissions_except_permission(self, mock_dp, mock_dg, mock_ta, mock_asg, mock_rem, mock_get):
        group_name = 'test_group'
        create_test_perm = Permission(name='create_test', description='test_create')
        delete_test_perm = Permission(name='delete_test', description='test_delete')
        group_perm = PermissionGroup(name=group_name, permissions=[create_test_perm, delete_test_perm])
        self.app.permissions = mock.MagicMock(return_value=[create_test_perm, group_perm])

        # Mock Permission.objects.filter
        db_app_permission = mock.MagicMock(codename='test_code')
        mock_perm_query = mock_dp.objects.filter().filter().all
        mock_perm_query.return_value = [db_app_permission]

        # Mock Permission.DoesNotExist
        mock_dp.DoesNotExist = Exception
        # Mock Permission.objects.get
        mock_perm_get = mock_dp.objects.get
        mock_perm_get.side_effect = Exception

        # Mock Group.objects.filter
        db_group = mock.MagicMock()
        db_group.name = 'test_app_name:group'

        mock_group = mock_dg.objects.filter().all
        mock_group.return_value = [db_group]

        # Mock TethysApp.objects.all()
        db_app = mock.MagicMock(package='test_app_name')

        mock_toa = mock_ta.objects.all
        mock_toa.return_value = [db_app]

        # Mock TethysApp.objects.get()
        mock_ta_get = mock_ta.objects.get
        mock_ta_get.return_value = 'test_get'

        # Mock Permission.DoesNotExist
        mock_dg.DoesNotExist = Exception

        # Mock Permission.objects.get
        mock_group_get = mock_dg.objects.get
        mock_group_get.side_effect = Exception

        # Execute
        self.app.register_app_permissions()

        # Check if Permission in Permission.DoesNotExist is called
        rts_call_args = mock_dp.call_args_list

        codename_check = []
        name_check = []
        for i in range(len(rts_call_args)):
            codename_check.append(rts_call_args[i][1]['codename'])
            name_check.append(rts_call_args[i][1]['name'])

        self.assertIn(':create_test', codename_check)
        self.assertIn(' | test_create', name_check)

        # Check if db_group.delete() is called
        db_group.delete.assert_called_with()

        # Check if Permission is called inside DoesNotExist
        # Get the TethysApp content type
        from django.contrib.contenttypes.models import ContentType
        tethys_content_type = ContentType.objects.get(
            app_label='tethys_apps',
            model='tethysapp'
        )
        mock_dp.assert_any_call(codename=':create_test', content_type=tethys_content_type,
                                name=' | test_create')

        # Check if p.save() is called inside DoesNotExist
        mock_dp().save.assert_called()

        # Check if Group in Group.DoesNotExist is called
        rts_call_args = mock_dg.call_args_list
        self.assertEqual(':test_group', rts_call_args[0][1]['name'])

        # Check if Group(name=group) is called
        mock_dg.assert_called_with(name=':test_group')

        # Check if g.save() is called
        mock_dg().save.assert_called()

        # Check if assign_perm(p, g, db_app) is called
        rts_call_args = mock_asg.call_args_list
        check_list = []
        for i in range(len(rts_call_args)):
            for j in [0, 2]:  # only get first and last element to check
                check_list.append(rts_call_args[i][0][j])

        self.assertIn(':create_test', check_list)
        self.assertIn('test_get', check_list)
        self.assertIn(':delete_test', check_list)
        self.assertIn('test_get', check_list)

    @mock.patch('tethys_apps.base.app_base.HandoffManager')
    def test_get_handoff_manager(self, mock_hom):
        mock_hom.return_value = 'test_handoff'
        self.assertEqual('test_handoff', self.app.get_handoff_manager())

    @mock.patch('tethys_compute.job_manager.JobManager')
    def test_get_job_manager(self, mock_jm):
        mock_jm.return_value = 'test_job_manager'
        self.assertEqual('test_job_manager', self.app.get_job_manager())

    @mock.patch('tethys_apps.base.app_base.TethysWorkspace')
    def test_get_user_workspace(self, mock_tws):
        user = self.user
        self.app.get_user_workspace(user)

        # Check result
        rts_call_args = mock_tws.call_args_list
        self.assertIn('workspaces', rts_call_args[0][0][0])
        self.assertIn('user_workspaces', rts_call_args[0][0][0])
        self.assertIn(user.username, rts_call_args[0][0][0])

    @mock.patch('tethys_apps.base.app_base.TethysWorkspace')
    def test_get_user_workspace_http(self, mock_tws):
        from django.http import HttpRequest
        request = HttpRequest()
        request.user = self.user

        self.app.get_user_workspace(request)

        # Check result
        rts_call_args = mock_tws.call_args_list
        self.assertIn('workspaces', rts_call_args[0][0][0])
        self.assertIn('user_workspaces', rts_call_args[0][0][0])
        self.assertIn(self.user.username, rts_call_args[0][0][0])

    @mock.patch('tethys_apps.base.app_base.TethysWorkspace')
    def test_get_user_workspace_none(self, mock_tws):
        self.app.get_user_workspace(None)

        # Check result
        rts_call_args = mock_tws.call_args_list
        self.assertIn('workspaces', rts_call_args[0][0][0])
        self.assertIn('user_workspaces', rts_call_args[0][0][0])
        self.assertIn('anonymous_user', rts_call_args[0][0][0])

    def test_get_user_workspace_error(self):
        self.assertRaises(ValueError, self.app.get_user_workspace, user=['test'])

    @mock.patch('tethys_apps.base.app_base.TethysWorkspace')
    def test_get_app_workspace(self, mock_tws):
        self.app.get_app_workspace()

        # Check result
        rts_call_args = mock_tws.call_args_list
        self.assertIn('workspaces', rts_call_args[0][0][0])
        self.assertIn('app_workspace', rts_call_args[0][0][0])
        self.assertNotIn('user_workspaces', rts_call_args[0][0][0])

    @mock.patch('tethys_apps.models.TethysApp')
    def test_get_custom_setting(self, mock_ta):
        setting_name = 'fake_setting'
        result = TethysAppChild.get_custom_setting(name=setting_name)
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)
        mock_ta.objects.get().custom_settings.get.assert_called_with(name=setting_name)
        mock_ta.objects.get().custom_settings.get().get_value.assert_called()
        self.assertEqual(mock_ta.objects.get().custom_settings.get().get_value(), result)

    @mock.patch('tethys_apps.base.app_base.TethysAppSettingDoesNotExist')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_get_custom_setting_object_not_exist(self, mock_ta, mock_tas_dne):
        mock_db_app = mock_ta.objects.get
        mock_db_app.return_value = mock.MagicMock()

        mock_custom_settings = mock_ta.objects.get().custom_settings.get
        mock_custom_settings.side_effect = ObjectDoesNotExist

        mock_tas_dne.return_value = TypeError
        self.assertRaises(TypeError, self.app.get_custom_setting, name='test')

        mock_tas_dne.assert_called_with('CustomTethysAppSetting', 'test', '')

    @mock.patch('tethys_apps.models.TethysApp')
    def test_set_custom_setting(self, mock_app):
        setting_name = 'fake_setting'
        mock_save = mock.MagicMock()
        mock_app.objects.get().custom_settings.get.side_effect = [
            mock.MagicMock(type='STRING', save=mock_save),
            mock.MagicMock(type='INTEGER', save=mock_save),
            mock.MagicMock(type='FLOAT', save=mock_save),
            mock.MagicMock(type='BOOLEAN', save=mock_save),
            mock.MagicMock(type='UUID', save=mock_save),
        ]

        TethysAppChild.set_custom_setting(name=setting_name, value='test')
        TethysAppChild.set_custom_setting(name=setting_name, value=1)
        TethysAppChild.set_custom_setting(name=setting_name, value=1.0)
        TethysAppChild.set_custom_setting(name=setting_name, value=True)
        TethysAppChild.set_custom_setting(name=setting_name, value=uuid.uuid4())

        self.assertEqual(5, mock_save.call_count)

    @mock.patch('tethys_apps.base.app_base.TethysAppSettingDoesNotExist')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_set_custom_setting_object_not_exist(self, mock_app, mock_tas_dne):
        setting_name = 'fake_setting'
        mock_db_app = mock_app.objects.get
        mock_db_app.return_value = mock.MagicMock()

        mock_app.objects.get().custom_settings.get.side_effect = [ObjectDoesNotExist]
        mock_tas_dne.return_value = TypeError

        self.assertRaises(TypeError, self.app.set_custom_setting, name=setting_name, value='test')
        mock_tas_dne.assert_called_with('CustomTethysAppSetting', setting_name, '')

    @mock.patch('tethys_apps.models.TethysApp')
    def test_set_custom_setting_type_not_match(self, mock_app):
        setting_name = 'fake_setting'
        mock_app.objects.get().custom_settings.get.return_value = mock.MagicMock(type='UUID')

        with self.assertRaises(ValidationError) as ret:
            self.app.set_custom_setting(name=setting_name, value=1)

        self.assertEqual('Value must be of type UUID.', ret.exception.message)

    @mock.patch('tethys_apps.models.TethysApp')
    def test_get_dataset_service(self, mock_ta):
        TethysAppChild.get_dataset_service(name=self.fake_name)
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)
        mock_ta.objects.get().dataset_services_settings.get.assert_called_with(name=self.fake_name)
        mock_ta.objects.get().dataset_services_settings.get().\
            get_value.assert_called_with(as_endpoint=False, as_engine=False, as_public_endpoint=False)

    @mock.patch('tethys_apps.base.app_base.TethysAppSettingDoesNotExist')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_get_dataset_service_object_not_exist(self, mock_ta, mock_tas_dne):
        mock_dss = mock_ta.objects.get().dataset_services_settings.get
        mock_dss.side_effect = ObjectDoesNotExist

        mock_tas_dne.return_value = TypeError
        self.assertRaises(TypeError, TethysAppChild.get_dataset_service, name=self.fake_name)

        mock_tas_dne.assert_called_with('DatasetServiceSetting', self.fake_name, TethysAppChild.name)

    @mock.patch('tethys_apps.models.TethysApp')
    def test_get_spatial_dataset_service(self, mock_ta):
        TethysAppChild.get_spatial_dataset_service(name=self.fake_name)
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)
        mock_ta.objects.get().spatial_dataset_service_settings.get.assert_called_with(name=self.fake_name)
        mock_ta.objects.get().spatial_dataset_service_settings.get().\
            get_value.assert_called_with(as_endpoint=False, as_engine=False, as_public_endpoint=False,
                                         as_wfs=False, as_wms=False)

    @mock.patch('tethys_apps.base.app_base.TethysAppSettingDoesNotExist')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_get_spatial_dataset_service_object_not_exist(self, mock_ta, mock_tas_dne):
        mock_sdss = mock_ta.objects.get().spatial_dataset_service_settings.get
        mock_sdss.side_effect = ObjectDoesNotExist

        mock_tas_dne.return_value = TypeError
        self.assertRaises(TypeError, TethysAppChild.get_spatial_dataset_service, name=self.fake_name)

        mock_tas_dne.assert_called_with('SpatialDatasetServiceSetting', self.fake_name, TethysAppChild.name)

    @mock.patch('tethys_apps.models.TethysApp')
    def test_get_web_processing_service(self, mock_ta):
        TethysAppChild.get_web_processing_service(name=self.fake_name)
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)
        mock_ta.objects.get().wps_services_settings.objects.get.assert_called_with(name=self.fake_name)
        mock_ta.objects.get().wps_services_settings.objects.get().get_value.\
            assert_called_with(as_public_endpoint=False, as_endpoint=False, as_engine=False)

    @mock.patch('tethys_apps.base.app_base.TethysAppSettingDoesNotExist')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_get_web_processing_service_object_not_exist(self, mock_ta, mock_tas_dne):
        mock_wss = mock_ta.objects.get().wps_services_settings.objects.get
        mock_wss.side_effect = ObjectDoesNotExist

        mock_tas_dne.return_value = TypeError
        self.assertRaises(TypeError, TethysAppChild.get_web_processing_service, name=self.fake_name)

        mock_tas_dne.assert_called_with('WebProcessingServiceSetting', self.fake_name, TethysAppChild.name)

    @mock.patch('tethys_apps.models.TethysApp')
    def test_get_persistent_store_connection(self, mock_ta):
        TethysAppChild.get_persistent_store_connection(name=self.fake_name)
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)
        mock_ta.objects.get().persistent_store_connection_settings.get.assert_called_with(name=self.fake_name)
        mock_ta.objects.get().persistent_store_connection_settings.get().get_value.\
            assert_called_with(as_engine=True, as_sessionmaker=False, as_url=False)

    @mock.patch('tethys_apps.base.app_base.TethysAppSettingDoesNotExist')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_get_persistent_store_connection_object_not_exist(self, mock_ta, mock_tas_dne):
        mock_sdss = mock_ta.objects.get().persistent_store_connection_settings.get
        mock_sdss.side_effect = ObjectDoesNotExist

        mock_tas_dne.return_value = TypeError
        self.assertRaises(TypeError, TethysAppChild.get_persistent_store_connection, name=self.fake_name)

        mock_tas_dne.assert_called_with('PersistentStoreConnectionSetting', self.fake_name, TethysAppChild.name)

    @mock.patch('tethys_apps.base.app_base.tethys_log')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_get_persistent_store_connection_not_assign(self, mock_ta, mock_log):
        mock_sdss = mock_ta.objects.get().persistent_store_connection_settings.get
        mock_sdss.side_effect = TethysAppSettingNotAssigned

        # Execute
        TethysAppChild.get_persistent_store_connection(name=self.fake_name)

        # Check log
        rts_call_args = mock_log.warning.call_args_list
        self.assertIn('Tethys app setting is not assigned.', rts_call_args[0][0][0])
        check_string = 'PersistentStoreConnectionSetting named "{}" has not been assigned'. format(self.fake_name)
        self.assertIn(check_string, rts_call_args[0][0][0])

    @mock.patch('tethys_apps.base.app_base.is_testing_environment')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_get_persistent_store_database(self, mock_ta, mock_ite):
        mock_ite.return_value = False
        TethysAppChild.get_persistent_store_database(name=self.fake_name)
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)

        # Check ps_database_settings.get(name=verified_name) is called
        mock_ta.objects.get().persistent_store_database_settings.get.assert_called_with(name=self.fake_name)
        mock_ta.objects.get().persistent_store_database_settings.get().get_value.\
            assert_called_with(as_engine=True, as_sessionmaker=False, as_url=False, with_db=True)

    @mock.patch('tethys_apps.base.app_base.is_testing_environment')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_get_persistent_store_database_object_does_not_exist(self, mock_ta, mock_ite):
        mock_ite.return_value = False
        mock_ta.objects.get().persistent_store_database_settings.get.side_effect = ObjectDoesNotExist

        # Check Raise
        self.assertRaises(TethysAppSettingDoesNotExist, TethysAppChild.get_persistent_store_database,
                          name=self.fake_name)

    @mock.patch('tethys_apps.base.app_base.tethys_log')
    @mock.patch('tethys_apps.base.app_base.is_testing_environment')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_get_persistent_store_database_not_assigned(self, mock_ta, mock_ite, mock_log):
        mock_ite.return_value = False
        mock_ta.objects.get().persistent_store_database_settings.get.side_effect = TethysAppSettingNotAssigned

        TethysAppChild.get_persistent_store_database(name=self.fake_name)

        # Check log
        rts_call_args = mock_log.warning.call_args_list
        self.assertIn('Tethys app setting is not assigned.', rts_call_args[0][0][0])
        check_string = 'PersistentStoreDatabaseSetting named "{}" has not been assigned'. format(self.fake_name)
        self.assertIn(check_string, rts_call_args[0][0][0])

    @mock.patch('tethys_apps.base.app_base.is_testing_environment')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_create_persistent_store(self, mock_ta, mock_ite):
        mock_ite.return_value = False
        result = TethysAppChild.create_persistent_store(db_name='example_db', connection_name='primary')

        # Check ps_connection_settings.get(name=connection_name) is called
        mock_ta.objects.get().persistent_store_connection_settings.get.assert_called_with(name='primary')

        # Check db_app.persistent_store_database_settings.get(name=verified_db_name) is called
        mock_ta.objects.get().persistent_store_database_settings.get.assert_called_with(name='example_db')

        # Check db_setting.save() is called
        mock_ta.objects.get().persistent_store_database_settings.get().save.assert_called()

        # Check Create the new database is called
        mock_ta.objects.get().persistent_store_database_settings.get().create_persistent_store_database.\
            assert_called_with(force_first_time=False, refresh=False)

        # Check result is true
        self.assertTrue(result)

    @mock.patch('tethys_apps.base.app_base.get_test_db_name')
    @mock.patch('tethys_apps.base.app_base.is_testing_environment')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_create_persistent_store_testing_env(self, mock_ta, mock_ite, mock_tdn):
        mock_ite.return_value = True
        mock_tdn.return_value = 'verified_db_name'
        TethysAppChild.create_persistent_store(db_name='example_db', connection_name=None)

        # Check get_test_db_name(db_name) is called
        mock_tdn.assert_called_with('example_db')

        rts_call_args = mock_ta.objects.get().persistent_store_database_settings.get.call_args_list
        # Check ps_connection_settings.get(name=connection_name) is called
        self.assertEqual({'name': 'example_db'}, rts_call_args[0][1])

        # Check db_app.persistent_store_database_settings.get(name=verified_db_name) is called
        self.assertEqual({'name': 'verified_db_name'}, rts_call_args[1][1])

        # Check db_setting.save() is called
        mock_ta.objects.get().persistent_store_database_settings.get().save.assert_called()

        # Check Create the new database is called
        mock_ta.objects.get().persistent_store_database_settings.get().create_persistent_store_database.\
            assert_called_with(force_first_time=False, refresh=False)

    @mock.patch('tethys_apps.base.app_base.is_testing_environment')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_create_persistent_store_no_connection_name(self, _, mock_ite):
        mock_ite.return_value = False
        self.assertRaises(ValueError, TethysAppChild.create_persistent_store, db_name='example_db',
                          connection_name=None)

    @mock.patch('tethys_apps.base.app_base.is_testing_environment')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_create_persistent_store_no_connection_object_not_exist_testing_env(self, mock_ta, mock_ite):
        # Need to test in testing env to test the connection_name is None case
        mock_ite.return_value = True
        mock_ta.objects.get().persistent_store_database_settings.get.side_effect = ObjectDoesNotExist

        self.assertRaises(TethysAppSettingDoesNotExist, TethysAppChild.create_persistent_store, db_name='example_db',
                          connection_name=None)

    @mock.patch('tethys_apps.base.app_base.is_testing_environment')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_create_persistent_store_connection_object_not_exist_testing_env(self, mock_ta, mock_ite):
        # Need to test in testing env to test the connection_name is None case
        mock_ite.return_value = True
        mock_ta.objects.get().persistent_store_connection_settings.get.side_effect = ObjectDoesNotExist

        self.assertRaises(TethysAppSettingDoesNotExist, TethysAppChild.create_persistent_store, db_name='example_db',
                          connection_name='test_con')

    @mock.patch('tethys_apps.models.PersistentStoreDatabaseSetting')
    @mock.patch('tethys_apps.base.app_base.is_testing_environment')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_create_persistent_store_object_not_exist(self, mock_ta, mock_ite, mock_psd):
        # Need to test in testing env to test the connection_name is None case
        mock_ite.return_value = False
        mock_ta.objects.get().persistent_store_database_settings.get.side_effect = ObjectDoesNotExist

        # Execute
        TethysAppChild.create_persistent_store(db_name='example_db', connection_name='test_con')

        # Check if PersistentStoreDatabaseSetting is called
        mock_psd.assert_called_with(description='', dynamic=True, initializer='', name='example_db',
                                    required=False, spatial=False)

        # Check if db_setting is called
        db_setting = mock_psd()
        mock_ta.objects.get().add_settings.assert_called_with((db_setting,))

        # Check if save is called
        mock_ta.objects.get().save.assert_called()

    @mock.patch('tethys_apps.base.app_base.is_testing_environment')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_drop_persistent_store(self, mock_ta, mock_ite):
        mock_ite.return_value = False
        result = TethysAppChild.drop_persistent_store(name='example_store')

        # Check if TethysApp.objects.get(package=cls.package) is called
        mock_ta.objects.get.assert_called_with(package='test_app')

        # Check if ps_database_settings.get(name=verified_name) is called
        mock_ta.objects.get().persistent_store_database_settings.get.assert_called_with(name='example_store')

        # Check if drop the persistent store is called
        mock_ta.objects.get().persistent_store_database_settings.get().drop_persistent_store_database.assert_called()

        # Check if remove the database setting is called
        mock_ta.objects.get().persistent_store_database_settings.get().delete.assert_called()

        # Check result return True
        self.assertTrue(result)

    @mock.patch('tethys_apps.base.app_base.is_testing_environment')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_drop_persistent_store_object_does_not_exist(self, mock_ta, mock_ite):
        mock_ite.return_value = False
        mock_ta.objects.get().persistent_store_database_settings.get.side_effect = ObjectDoesNotExist
        result = TethysAppChild.drop_persistent_store(name='example_store')

        # Check result return True
        self.assertTrue(result)

    @mock.patch('tethys_apps.models.TethysApp')
    def test_list_persistent_store_databases_dynamic(self, mock_ta):
        mock_settings = mock_ta.objects.get().persistent_store_database_settings.filter
        setting1 = mock.MagicMock()
        setting1.name = 'test1'
        setting2 = mock.MagicMock()
        setting2.name = 'test2'
        mock_settings.return_value = [setting1, setting2]

        result = TethysAppChild.list_persistent_store_databases(dynamic_only=True)

        # Check TethysApp.objects.get is called
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)

        # Check filter is called
        mock_ta.objects.get().persistent_store_database_settings.filter.\
            assert_called_with(persistentstoredatabasesetting__dynamic=True)

        # Check result
        self.assertEqual(['test1', 'test2'], result)

    @mock.patch('tethys_apps.models.TethysApp')
    def test_list_persistent_store_databases_static(self, mock_ta):
        mock_settings = mock_ta.objects.get().persistent_store_database_settings.filter
        setting1 = mock.MagicMock()
        setting1.name = 'test1'
        setting2 = mock.MagicMock()
        setting2.name = 'test2'
        mock_settings.return_value = [setting1, setting2]

        result = TethysAppChild.list_persistent_store_databases(static_only=True)

        # Check TethysApp.objects.get is called
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)

        # Check filter is called
        mock_ta.objects.get().persistent_store_database_settings.filter.\
            assert_called_with(persistentstoredatabasesetting__dynamic=False)

        # Check result
        self.assertEqual(['test1', 'test2'], result)

    @mock.patch('tethys_apps.models.TethysApp')
    def test_list_persistent_store_connections(self, mock_ta):
        setting1 = mock.MagicMock()
        setting1.name = 'test1'
        setting2 = mock.MagicMock()
        setting2.name = 'test2'
        mock_ta.objects.get().persistent_store_connection_settings = [setting1, setting2]

        result = TethysAppChild.list_persistent_store_connections()

        # Check TethysApp.objects.get is called
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)

        # Check result
        self.assertEqual(['test1', 'test2'], result)

    @mock.patch('tethys_apps.base.app_base.is_testing_environment')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_persistent_store_exists(self, mock_ta, mock_ite):
        mock_ite.return_value = False
        result = TethysAppChild.persistent_store_exists(name='test_store')

        # Check TethysApp.objects.get is called
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)

        # Check if ps_database_settings.get is called
        mock_ta.objects.get().persistent_store_database_settings.get.assert_called_with(name='test_store')

        # Check if database exists is called
        mock_ta.objects.get().persistent_store_database_settings.get().persistent_store_database_exists.assert_called()

        # Check if result True
        self.assertTrue(result)

    @mock.patch('tethys_apps.base.app_base.is_testing_environment')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_persistent_store_exists_object_does_not_exist(self, mock_ta, mock_ite):
        mock_ite.return_value = False
        mock_ta.objects.get().persistent_store_database_settings.get.side_effect = ObjectDoesNotExist
        result = TethysAppChild.persistent_store_exists(name='test_store')

        # Check TethysApp.objects.get is called
        mock_ta.objects.get.assert_called_with(package=TethysAppChild.package)

        # Check if ps_database_settings.get is called
        mock_ta.objects.get().persistent_store_database_settings.get.assert_called_with(name='test_store')

        # Check if result False
        self.assertFalse(result)

    @mock.patch('django.conf.settings')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_sync_with_tethys_db(self, mock_ta, _):
        mock_ta.objects.filter().all.return_value = []
        self.app.name = 'n'
        self.app.package = 'p'
        self.app.description = 'd'
        self.app.enable_feedback = 'e'
        self.app.feedback_emails = 'f'
        self.app.index = 'in'
        self.app.icon = 'ic'
        self.app.root_url = 'r'
        self.app.color = 'c'
        self.app.tags = 't'
        self.app.sync_with_tethys_db()

        # Check if TethysApp.objects.filter is called
        mock_ta.objects.filter().all.assert_called()

        # Check if TethysApp is called
        mock_ta.assert_called_with(color='c', description='d', enable_feedback='e', feedback_emails='f',
                                   icon='ic', index='in', name='n', package='p', root_url='r', tags='t')

        # Check if save is called 2 times
        self.assertTrue(mock_ta().save.call_count == 2)

        # Check if add_settings is called 5 times
        self.assertTrue(mock_ta().add_settings.call_count == 5)

    @mock.patch('django.conf.settings')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_sync_with_tethys_db_in_db(self, mock_ta, mock_ds):
        mock_ds.DEBUG = True
        mock_app = mock.MagicMock()
        mock_ta.objects.filter().all.return_value = [mock_app]
        self.app.sync_with_tethys_db()

        # Check if TethysApp.objects.filter is called
        mock_ta.objects.filter().all.assert_called()

        # Check if save is called 2 times
        self.assertTrue(mock_app.save.call_count == 2)

        # Check if add_settings is called 5 times
        self.assertTrue(mock_app.add_settings.call_count == 5)

    @mock.patch('django.conf.settings')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_sync_with_tethys_db_more_than_one(self, mock_ta, mock_ds):
        mock_ds.DEBUG = True
        mock_app = mock.MagicMock()
        mock_ta.objects.filter().all.return_value = [mock_app, mock_app]
        self.app.sync_with_tethys_db()

        # Check if TethysApp.objects.filter is called
        mock_ta.objects.filter().all.assert_called()

        # Check if is not called
        mock_app.save.assert_not_called()

        # Check if is not called
        mock_app.add_settings.assert_not_called()

    @mock.patch('tethys_apps.base.app_base.tethys_log')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_sync_with_tethys_db_exception(self, mock_ta, mock_log):
        mock_ta.objects.filter().all.side_effect = Exception
        self.app.sync_with_tethys_db()

        mock_log.error.assert_called()

    @mock.patch('tethys_apps.base.app_base.tethys_log')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_sync_with_tethys_db_programming_error(self, mock_ta, mock_log):
        mock_ta.objects.filter().all.side_effect = ProgrammingError
        self.app.sync_with_tethys_db()

        mock_log.warning.assert_called_with("Unable to sync app with database. "
                                            "tethys_apps_tethysapp table does not exist")

    @mock.patch('tethys_apps.models.TethysApp')
    def test_remove_from_db(self, mock_ta):
        self.app.remove_from_db()

        # Check if delete is called
        mock_ta.objects.filter().delete.assert_called()

    @mock.patch('tethys_apps.base.app_base.tethys_log')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_remove_from_db_2(self, mock_ta, mock_log):
        mock_ta.objects.filter().delete.side_effect = Exception
        self.app.remove_from_db()

        # Check tethys log error
        mock_log.error.assert_called()
