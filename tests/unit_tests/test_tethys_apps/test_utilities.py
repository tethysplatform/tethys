import unittest
from unittest import mock

from guardian.shortcuts import assign_perm

from tethys_sdk.testing import TethysTestCase
from tethys_apps import utilities


class TethysAppsUtilitiesTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_directories_in_tethys_templates(self):
        # Get the templates directories for the test_app and test_extension
        result = utilities.get_directories_in_tethys(('templates',))
        self.assertGreaterEqual(len(result), 2)

        test_app = False
        test_ext = False

        for r in result:
            if '/tethysapp/test_app/templates' in r:
                test_app = True
            if '/tethysext-test_extension/tethysext/test_extension/templates' in r:
                test_ext = True

        self.assertTrue(test_app)
        self.assertTrue(test_ext)

    def test_get_directories_in_tethys_templates_with_app_name(self):
        # Get the templates directories for the test_app and test_extension
        # Use the with_app_name argument, so that the app and extension names appear in the result
        result = utilities.get_directories_in_tethys(('templates',), with_app_name=True)
        self.assertGreaterEqual(len(result), 2)
        self.assertEqual(2, len(result[0]))
        self.assertEqual(2, len(result[1]))

        test_app = False
        test_ext = False

        for r in result:
            if 'test_app' in r and '/tethysapp/test_app/templates' in r[1]:
                test_app = True
            if 'test_extension' in r and '/tethysext-test_extension/tethysext/test_extension/templates' in r[1]:
                test_ext = True

        self.assertTrue(test_app)
        self.assertTrue(test_ext)

    @mock.patch('tethys_apps.utilities.SingletonHarvester')
    def test_get_directories_in_tethys_templates_extension_import_error(self, mock_harvester):
        # Mock the extension_modules variable with bad data, to throw an ImportError
        mock_harvester().extension_modules = {'foo_invalid_foo': 'tethysext.foo_invalid_foo'}
        mock_harvester().app_modules = {'test_app': 'tethysapp.test_app'}

        result = utilities.get_directories_in_tethys(('templates',))
        self.assertGreaterEqual(len(result), 1)

        test_app = False
        test_ext = False

        for r in result:
            if '/tethysapp/test_app/templates' in r:
                test_app = True
            if '/tethysext-test_extension/tethysext/test_extension/templates' in r:
                test_ext = True

        self.assertTrue(test_app)
        self.assertFalse(test_ext)

    @mock.patch('tethys_apps.utilities.SingletonHarvester')
    def test_get_directories_in_tethys_templates_apps_import_error(self, mock_harvester):
        # Mock the extension_modules variable with bad data, to throw an ImportError
        mock_harvester().app_modules = {'foo_invalid_foo': 'tethys_app.foo_invalid_foo'}

        result = utilities.get_directories_in_tethys(('templates',))
        self.assertGreaterEqual(len(result), 0)

        test_app = False

        for r in result:
            if '/tethysapp/foo_invalid_foo/templates' in r:
                test_app = True

        self.assertFalse(test_app)

    def test_get_directories_in_tethys_foo(self):
        # Get the foo directories for the test_app and test_extension
        # foo doesn't exist
        result = utilities.get_directories_in_tethys(('foo',))
        self.assertEqual(0, len(result))

    def test_get_directories_in_tethys_foo_public(self):
        # Get the foo and public directories for the test_app and test_extension
        # foo doesn't exist, but public will
        result = utilities.get_directories_in_tethys(('foo', 'public'))
        self.assertGreaterEqual(len(result), 2)

        test_app = False
        test_ext = False

        for r in result:
            if '/tethysapp/test_app/public' in r:
                test_app = True
            if '/tethysext-test_extension/tethysext/test_extension/public' in r:
                test_ext = True

        self.assertTrue(test_app)
        self.assertTrue(test_ext)

    def test_get_active_app_none_none(self):
        # Get the active TethysApp object, with a request of None and url of None
        result = utilities.get_active_app(request=None, url=None)
        self.assertEqual(None, result)

        # Try again with the defaults, which are a request of None and url of None
        result = utilities.get_active_app()
        self.assertEqual(None, result)

    @mock.patch('tethys_apps.models.TethysApp')
    def test_get_active_app_request(self, mock_app):
        # Mock up for TethysApp, and request
        mock_app.objects.get.return_value = mock.MagicMock()
        mock_request = mock.MagicMock()
        mock_request.path = '/apps/foo/bar'

        # Result should be mock for mock_app.objects.get.return_value
        result = utilities.get_active_app(request=mock_request)
        self.assertEqual(mock_app.objects.get(), result)

    @mock.patch('tethys_apps.models.TethysApp')
    def test_get_active_app_url(self, mock_app):
        # Mock up for TethysApp
        mock_app.objects.get.return_value = mock.MagicMock()

        # Result should be mock for mock_app.objects.get.return_value
        result = utilities.get_active_app(url='/apps/foo/bar')
        self.assertEqual(mock_app.objects.get(), result)

    @mock.patch('tethys_apps.utilities.SingletonHarvester')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_get_active_app_class(self, mock_app, mock_harvester):
        # Mock up for TethysApp
        app = mock.MagicMock()
        mock_app.objects.get.return_value = app

        mock_harvester().apps = [app]

        # Result should be mock for mock_app.objects.get.return_value
        result = utilities.get_active_app(url='/apps/foo/bar', get_class=True)
        self.assertEqual(mock_app.objects.get(), result)

    @mock.patch('tethys_apps.models.TethysApp')
    def test_get_active_app_request_bad_path(self, mock_app):
        # Mock up for TethysApp
        mock_app.objects.get.return_value = mock.MagicMock()
        mock_request = mock.MagicMock()
        # Path does not contain apps
        mock_request.path = '/foo/bar'

        # Because 'app' not in request path, return None
        result = utilities.get_active_app(request=mock_request)
        self.assertEqual(None, result)

    @mock.patch('tethys_apps.utilities.tethys_log.warning')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_get_active_app_request_exception1(self, mock_app, mock_log_warning):
        from django.core.exceptions import ObjectDoesNotExist

        # Mock up for TethysApp to raise exception, and request
        mock_app.objects.get.side_effect = ObjectDoesNotExist
        mock_request = mock.MagicMock()
        mock_request.path = '/apps/foo/bar'

        # Result should be None due to the exception
        result = utilities.get_active_app(request=mock_request)
        self.assertEqual(None, result)
        mock_log_warning.assert_called_once_with('Could not locate app with root url "foo".')

    @mock.patch('tethys_apps.utilities.tethys_log.warning')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_get_active_app_request_exception2(self, mock_app, mock_log_warning):
        from django.core.exceptions import MultipleObjectsReturned

        # Mock up for TethysApp to raise exception, and request
        mock_app.objects.get.side_effect = MultipleObjectsReturned
        mock_request = mock.MagicMock()
        mock_request.path = '/apps/foo/bar'

        # Result should be None due to the exception
        result = utilities.get_active_app(request=mock_request)
        self.assertEqual(None, result)
        mock_log_warning.assert_called_once_with('Multiple apps found with root url "foo".')

    @mock.patch('tethys_cli.cli_colors.pretty_output')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_create_ps_database_setting_app_does_not_exist(self, mock_app, mock_pretty_output):
        from django.core.exceptions import ObjectDoesNotExist

        # Mock up for TethysApp to not exist
        mock_app.objects.get.side_effect = ObjectDoesNotExist
        mock_app_package = mock.MagicMock()
        mock_name = mock.MagicMock()

        # ObjectDoesNotExist should be thrown, and False returned
        result = utilities.create_ps_database_setting(app_package=mock_app_package, name=mock_name)

        self.assertEqual(False, result)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('A Tethys App with the name', po_call_args[0][0][0])
        self.assertIn('does not exist. Aborted.', po_call_args[0][0][0])

    @mock.patch('tethys_cli.cli_colors.pretty_output')
    @mock.patch('tethys_apps.models.PersistentStoreDatabaseSetting')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_create_ps_database_setting_ps_database_setting_exists(self, mock_app, mock_ps_db_setting,
                                                                   mock_pretty_output):
        # Mock up for TethysApp and PersistentStoreDatabaseSetting to exist
        mock_app.objects.get.return_value = mock.MagicMock()
        mock_ps_db_setting.objects.get.return_value = mock.MagicMock()
        mock_app_package = mock.MagicMock()
        mock_name = mock.MagicMock()

        # PersistentStoreDatabaseSetting should exist, and False returned
        result = utilities.create_ps_database_setting(app_package=mock_app_package, name=mock_name)

        self.assertEqual(False, result)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('A PersistentStoreDatabaseSetting with name', po_call_args[0][0][0])
        self.assertIn('already exists. Aborted.', po_call_args[0][0][0])

    @mock.patch('tethys_apps.utilities.print')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    @mock.patch('tethys_apps.models.PersistentStoreDatabaseSetting')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_create_ps_database_setting_ps_database_setting_exceptions(self, mock_app, mock_ps_db_setting,
                                                                       mock_pretty_output, mock_print):
        from django.core.exceptions import ObjectDoesNotExist

        # Mock up for TethysApp to exist and PersistentStoreDatabaseSetting to throw exceptions
        mock_app.objects.get.return_value = mock.MagicMock()
        mock_ps_db_setting.objects.get.side_effect = ObjectDoesNotExist
        mock_ps_db_setting().save.side_effect = Exception('foo exception')
        mock_app_package = mock.MagicMock()
        mock_name = mock.MagicMock()

        # PersistentStoreDatabaseSetting should exist, and False returned
        result = utilities.create_ps_database_setting(app_package=mock_app_package, name=mock_name)

        self.assertEqual(False, result)
        mock_ps_db_setting.assert_called()
        mock_ps_db_setting().save.assert_called()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('The above error was encountered. Aborted.', po_call_args[0][0][0])
        rts_call_args = mock_print.call_args_list
        self.assertIn('foo exception', rts_call_args[0][0][0].args[0])

    @mock.patch('tethys_cli.cli_colors.pretty_output')
    @mock.patch('tethys_apps.models.PersistentStoreDatabaseSetting')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_create_ps_database_setting_ps_database_savess(self, mock_app, mock_ps_db_setting, mock_pretty_output):
        # Mock up for TethysApp to exist and PersistentStoreDatabaseSetting to not
        mock_app.objects.get.return_value = mock.MagicMock()
        mock_ps_db_setting.objects.get.return_value = False
        mock_ps_db_setting().save.return_value = True
        mock_app_package = mock.MagicMock()
        mock_name = mock.MagicMock()

        # True should be returned
        result = utilities.create_ps_database_setting(app_package=mock_app_package, name=mock_name)

        self.assertEqual(True, result)
        mock_ps_db_setting.assert_called()
        mock_ps_db_setting().save.assert_called()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('PersistentStoreDatabaseSetting named', po_call_args[0][0][0])
        self.assertIn('created successfully!', po_call_args[0][0][0])

    @mock.patch('tethys_cli.cli_colors.pretty_output')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_remove_ps_database_setting_app_not_exist(self, mock_app, mock_pretty_output):
        from django.core.exceptions import ObjectDoesNotExist

        # Mock up for TethysApp to throw an exception
        mock_app.objects.get.side_effect = ObjectDoesNotExist
        mock_app_package = mock.MagicMock()
        mock_name = mock.MagicMock()

        # An exception will be thrown and false returned
        result = utilities.remove_ps_database_setting(app_package=mock_app_package, name=mock_name)

        self.assertEqual(False, result)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('A Tethys App with the name', po_call_args[0][0][0])
        self.assertIn('does not exist. Aborted.', po_call_args[0][0][0])

    @mock.patch('tethys_cli.cli_colors.pretty_output')
    @mock.patch('tethys_apps.models.PersistentStoreDatabaseSetting')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_remove_ps_database_setting_psdbs_not_exist(self, mock_app, mock_ps_db_setting, mock_pretty_output):
        from django.core.exceptions import ObjectDoesNotExist

        # Mock up for TethysApp and PersistentStoreDatabaseSetting to throw an exception
        mock_app.objects.get.return_value = mock.MagicMock()
        mock_ps_db_setting.objects.get.side_effect = ObjectDoesNotExist
        mock_app_package = mock.MagicMock()
        mock_name = mock.MagicMock()

        # An exception will be thrown and false returned
        result = utilities.remove_ps_database_setting(app_package=mock_app_package, name=mock_name)

        self.assertEqual(False, result)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('An PersistentStoreDatabaseSetting with the name', po_call_args[0][0][0])
        self.assertIn(' for app ', po_call_args[0][0][0])
        self.assertIn('does not exist. Aborted.', po_call_args[0][0][0])

    @mock.patch('tethys_cli.cli_colors.pretty_output')
    @mock.patch('tethys_apps.models.PersistentStoreDatabaseSetting')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_remove_ps_database_setting_force_delete(self, mock_app, mock_ps_db_setting, mock_pretty_output):
        # Mock up for TethysApp and PersistentStoreDatabaseSetting
        mock_app.objects.get.return_value = mock.MagicMock()
        mock_ps_db_setting.objects.get.return_value = mock.MagicMock()
        mock_ps_db_setting.objects.get().delete.return_value = True
        mock_app_package = mock.MagicMock()
        mock_name = mock.MagicMock()

        # Delete will be called and True returned
        result = utilities.remove_ps_database_setting(app_package=mock_app_package, name=mock_name, force=True)

        self.assertEqual(True, result)
        mock_ps_db_setting.objects.get().delete.assert_called_once()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('Successfully removed PersistentStoreDatabaseSetting with name', po_call_args[0][0][0])

    @mock.patch('tethys_apps.utilities.input')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    @mock.patch('tethys_apps.models.PersistentStoreDatabaseSetting')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_remove_ps_database_setting_proceed_delete(self, mock_app, mock_ps_db_setting, mock_pretty_output,
                                                       mock_input):
        # Mock up for TethysApp and PersistentStoreDatabaseSetting
        mock_app.objects.get.return_value = mock.MagicMock()
        mock_ps_db_setting.objects.get.return_value = mock.MagicMock()
        mock_ps_db_setting.objects.get().delete.return_value = True
        mock_input.side_effect = ['Y']
        mock_app_package = mock.MagicMock()
        mock_name = mock.MagicMock()

        # Based on the raw_input, delete not called and None returned
        result = utilities.remove_ps_database_setting(app_package=mock_app_package, name=mock_name)

        self.assertEqual(True, result)
        mock_ps_db_setting.objects.get().delete.assert_called()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('Successfully removed PersistentStoreDatabaseSetting with name', po_call_args[0][0][0])

    @mock.patch('tethys_apps.utilities.input')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    @mock.patch('tethys_apps.models.PersistentStoreDatabaseSetting')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_remove_ps_database_setting_do_not_proceed(self, mock_app, mock_ps_db_setting, mock_pretty_output,
                                                       mock_input):
        # Mock up for TethysApp and PersistentStoreDatabaseSetting
        mock_app.objects.get.return_value = mock.MagicMock()
        mock_ps_db_setting.objects.get.return_value = mock.MagicMock()
        mock_ps_db_setting.objects.get().delete.return_value = True
        mock_input.side_effect = ['foo', 'N']
        mock_app_package = mock.MagicMock()
        mock_name = mock.MagicMock()

        # Based on the raw_input, delete not called and None returned
        result = utilities.remove_ps_database_setting(app_package=mock_app_package, name=mock_name)

        self.assertEqual(None, result)
        mock_ps_db_setting.objects.get().delete.assert_not_called()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual('Aborted. PersistentStoreDatabaseSetting not removed.', po_call_args[0][0][0])

    @mock.patch('tethys_cli.cli_colors.pretty_output')
    @mock.patch('tethys_services.models.SpatialDatasetService')
    def test_link_service_to_app_setting_spatial_dss_does_not_exist(self, mock_service, mock_pretty_output):
        from django.core.exceptions import ObjectDoesNotExist

        # Mock up the SpatialDatasetService to throw ObjectDoesNotExist
        mock_service.objects.get.side_effect = ObjectDoesNotExist

        # Based on exception, False will be returned
        result = utilities.link_service_to_app_setting(service_type='spatial', service_uid='123',
                                                       app_package='foo_app', setting_type='ds_spatial',
                                                       setting_uid='456')

        self.assertEqual(False, result)
        mock_service.objects.get.assert_called_once_with(pk=123)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('with ID/Name', po_call_args[0][0][0])
        self.assertIn('does not exist.', po_call_args[0][0][0])

    @mock.patch('tethys_cli.cli_colors.pretty_output')
    @mock.patch('tethys_services.models.SpatialDatasetService')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_link_service_to_app_setting_spatial_dss_value_error(self, mock_app, mock_service, mock_pretty_output):
        from django.core.exceptions import ObjectDoesNotExist

        # Mock up TethysApp to throw ObjectDoesNotExist
        mock_app.objects.get.side_effect = ObjectDoesNotExist
        # Mock up the SpatialDatasetService to MagicMock
        mock_service.objects.get.return_value = mock.MagicMock()

        # Based on ValueError exception casting to int, then TethysApp ObjectDoesNotExist False will be returned
        result = utilities.link_service_to_app_setting(service_type='spatial', service_uid='foo_spatial_service',
                                                       app_package='foo_app', setting_type='ds_spatial',
                                                       setting_uid='456')

        self.assertEqual(False, result)
        mock_service.objects.get.assert_called_once_with(name='foo_spatial_service')
        mock_app.objects.get.assert_called_once_with(package='foo_app')
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('A Tethys App with the name', po_call_args[0][0][0])
        self.assertIn('does not exist. Aborted.', po_call_args[0][0][0])

    @mock.patch('tethys_cli.cli_colors.pretty_output')
    @mock.patch('tethys_services.models.SpatialDatasetService')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_link_service_to_app_setting_spatial_link_key_error(self, mock_app, mock_service, mock_pretty_output):
        # Mock up TethysApp to MagicMock
        mock_app.objects.get.return_value = mock.MagicMock()
        # Mock up the SpatialDatasetService to MagicMock
        mock_service.objects.get.return_value = mock.MagicMock()

        # Based on KeyError for invalid setting_type False will be returned
        result = utilities.link_service_to_app_setting(service_type='spatial', service_uid='foo_spatial_service',
                                                       app_package='foo_app', setting_type='foo_invalid',
                                                       setting_uid='456')

        self.assertEqual(False, result)
        mock_service.objects.get.assert_called_once_with(name='foo_spatial_service')
        mock_app.objects.get.assert_called_once_with(package='foo_app')
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('The setting_type you specified ("foo_invalid") does not exist.', po_call_args[0][0][0])
        self.assertIn('Choose from: "ps_database|ps_connection|ds_spatial"', po_call_args[0][0][0])

    @mock.patch('tethys_cli.cli_colors.pretty_output')
    @mock.patch('tethys_sdk.app_settings.SpatialDatasetServiceSetting')
    @mock.patch('tethys_services.models.SpatialDatasetService')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_link_service_to_app_setting_spatial_link_value_error_save(self, mock_app, mock_service, mock_setting,
                                                                       mock_pretty_output):
        # Mock up TethysApp to MagicMock
        mock_app.objects.get.return_value = mock.MagicMock()
        # Mock up the SpatialDatasetService to MagicMock
        mock_service.objects.get.return_value = mock.MagicMock()
        # Mock up the SpatialDatasetServiceSetting to MagicMock
        mock_setting.objects.get.return_value = mock.MagicMock()
        mock_setting.objects.get().save.return_value = True

        # True will be returned, mocked save will be called
        result = utilities.link_service_to_app_setting(service_type='spatial', service_uid='foo_spatial_service',
                                                       app_package='foo_app', setting_type='ds_spatial',
                                                       setting_uid='foo_456')

        self.assertEqual(True, result)
        mock_service.objects.get.assert_called_once_with(name='foo_spatial_service')
        mock_app.objects.get.assert_called_once_with(package='foo_app')
        mock_setting.objects.get.assert_called()
        mock_setting.objects.get().save.assert_called_once()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('was successfully linked to', po_call_args[0][0][0])

    @mock.patch('tethys_cli.cli_colors.pretty_output')
    @mock.patch('tethys_sdk.app_settings.SpatialDatasetServiceSetting', __name__='SpatialDatasetServiceSetting')
    @mock.patch('tethys_services.models.SpatialDatasetService')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_link_service_to_app_setting_spatial_link_does_not_exist(self, mock_app, mock_service, mock_setting,
                                                                     mock_pretty_output):
        from django.core.exceptions import ObjectDoesNotExist

        # Mock up TethysApp to MagicMock
        mock_app.objects.get.return_value = mock.MagicMock()
        # Mock up the SpatialDatasetService to MagicMock
        mock_service.objects.get.return_value = mock.MagicMock()
        # Mock up the SpatialDatasetServiceSetting to MagicMock
        mock_setting.objects.get.side_effect = ObjectDoesNotExist

        # Based on KeyError for invalid setting_type False will be returned
        result = utilities.link_service_to_app_setting(service_type='spatial', service_uid='foo_spatial_service',
                                                       app_package='foo_app', setting_type='ds_spatial',
                                                       setting_uid='456')

        self.assertEqual(False, result)
        mock_service.objects.get.assert_called_once_with(name='foo_spatial_service')
        mock_app.objects.get.assert_called_once_with(package='foo_app')
        mock_setting.objects.get.assert_called()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('A SpatialDatasetServiceSetting with ID/Name', po_call_args[0][0][0])
        self.assertIn('does not exist.', po_call_args[0][0][0])

    @mock.patch('tethys_apps.utilities.os')
    def test_get_tethys_home_dir__default_env_name__tethys_home_not_defined(self, mock_os):
        env_tethys_home = None
        conda_default_env = 'tethys'  # Default Tethys environment name
        default_tethys_home = '/home/tethys/.tethys'

        mock_os.environ.get.side_effect = [env_tethys_home, conda_default_env]  # [TETHYS_HOME, CONDA_DEFAULT_ENV]
        mock_os.path.expanduser.return_value = default_tethys_home

        ret = utilities.get_tethys_home_dir()

        mock_os.environ.get.assert_any_call('TETHYS_HOME')
        mock_os.environ.get.assert_any_call('CONDA_DEFAULT_ENV')
        mock_os.path.expanduser.assert_called_with('~/.tethys')

        # Returns default tethys home environment
        self.assertEqual(default_tethys_home, ret)

    @mock.patch('tethys_apps.utilities.os')
    def test_get_tethys_home_dir__non_default_env_name__tethys_home_not_defined(self, mock_os):
        env_tethys_home = None
        conda_default_env = 'foo'  # Non-default Tethys environment name
        default_tethys_home = '/home/tethys/.tethys'

        mock_os.environ.get.side_effect = [env_tethys_home, conda_default_env]  # [TETHYS_HOME, CONDA_DEFAULT_ENV]
        mock_os.path.expanduser.return_value = default_tethys_home

        ret = utilities.get_tethys_home_dir()

        mock_os.environ.get.assert_any_call('TETHYS_HOME')
        mock_os.environ.get.assert_any_call('CONDA_DEFAULT_ENV')
        mock_os.path.expanduser.assert_called_with('~/.tethys')
        mock_os.path.join.assert_called_with(default_tethys_home, conda_default_env)

        # Returns joined path of default tethys home path and environment name
        self.assertEqual(mock_os.path.join(), ret)

    @mock.patch('tethys_apps.utilities.os')
    def test_get_tethys_home_dir__tethys_home_defined(self, mock_os):
        env_tethys_home = '/foo/.bar'
        conda_default_env = 'foo'
        mock_os.environ.get.side_effect = [env_tethys_home, conda_default_env]  # [TETHYS_HOME, CONDA_DEFAULT_ENV]

        ret = utilities.get_tethys_home_dir()

        mock_os.environ.get.assert_called_once_with('TETHYS_HOME')
        mock_os.path.expanduser.assert_not_called()

        # Returns path defined by TETHYS_HOME environment variable
        self.assertEqual(env_tethys_home, ret)

    @mock.patch('tethys_apps.utilities.tethys_log')
    @mock.patch('tethys_apps.utilities.os')
    def test_get_tethys_home_dir__exception(self, mock_os, mock_tethys_log):
        env_tethys_home = None
        conda_default_env = 'foo'  # Non-default Tethys environment name
        default_tethys_home = '/home/tethys/.tethys'

        mock_os.environ.get.side_effect = [env_tethys_home, conda_default_env]  # [TETHYS_HOME, CONDA_DEFAULT_ENV]
        mock_os.path.expanduser.return_value = default_tethys_home

        mock_os.path.join.side_effect = Exception

        ret = utilities.get_tethys_home_dir()

        mock_os.environ.get.assert_any_call('TETHYS_HOME')
        mock_os.environ.get.assert_any_call('CONDA_DEFAULT_ENV')
        mock_os.path.expanduser.assert_called_with('~/.tethys')
        mock_os.path.join.assert_called_with(default_tethys_home, conda_default_env)
        mock_tethys_log.warning.assert_called()

        # Returns default tethys home environment path
        self.assertEqual(default_tethys_home, ret)

    @mock.patch('tethys_apps.utilities.SingletonHarvester')
    def test_get_app_class(self, mock_harvester):
        """"""
        from tethysapp.test_app.app import TestApp
        test_app = TestApp()
        mock_harvester().apps = [test_app]

        mock_db_app = mock.MagicMock()
        mock_db_app.name = TestApp.name  # This should match the name of TestApp
        mock_db_app.package = 'test_app'  # This should match the package of TestApp

        ret = utilities.get_app_class(mock_db_app)

        # Should work because package is used to find the class, not the name
        self.assertTrue(ret is test_app)

    @mock.patch('tethys_apps.utilities.SingletonHarvester')
    def test_get_app_class__different_name(self, mock_harvester):
        """Test case when user changes name of app in DB (from app settings)."""
        from tethysapp.test_app.app import TestApp
        test_app = TestApp()
        mock_harvester().apps = [test_app]

        mock_db_app = mock.MagicMock()
        mock_db_app.name = 'Different Name'  # This shouldn't match the name of TestApp
        mock_db_app.package = 'test_app'  # This should match the package of TestApp

        ret = utilities.get_app_class(mock_db_app)

        # Should work because package is used to find the class, not the name
        self.assertTrue(ret is test_app)

    @mock.patch('tethys_apps.utilities.SingletonHarvester')
    def test_get_app_class__no_matching_class(self, mock_harvester):
        """Test case when no app class can be found for the app."""
        from tethysapp.test_app.app import TestApp
        mock_harvester().apps = [TestApp()]

        mock_db_app = mock.MagicMock()
        mock_db_app.name = TestApp.name  # This should match the name of TestApp
        mock_db_app.package = 'does_not_exist'  # This shouldn't match the package of TestApp

        ret = utilities.get_app_class(mock_db_app)

        # Should not work because package is used to find the class
        self.assertIsNone(ret)


class TestTethysAppsUtilitiesTethysTestCase(TethysTestCase):
    def set_up(self):
        self.c = self.get_test_client()
        self.user = self.create_test_user(username="joe", password="secret", email="joe@some_site.com")

    def tear_down(self):
        self.user.delete()

    @mock.patch('django.conf.settings')
    def test_user_can_access_app(self, mock_settings):
        mock_settings.ENABLE_RESTRICTED_APP_ACCESS = False
        mock_settings.ENABLE_OPEN_PORTAL = False
        user = self.user
        app = utilities.get_active_app(url='/apps/test-app')

        result0 = utilities.user_can_access_app(user, app)
        self.assertTrue(result0)

        # test restricted access no permission
        mock_settings.ENABLE_RESTRICTED_APP_ACCESS = True
        result1 = utilities.user_can_access_app(user, app)
        self.assertFalse(result1)

        # test with permission
        assign_perm(f'{app.package}:access_app', user, app)

        result2 = utilities.user_can_access_app(user, app)
        self.assertTrue(result2)

        # test open portal mode case
        mock_settings.ENABLE_OPEN_PORTAL = True
        result3 = utilities.user_can_access_app(user, app)
        self.assertTrue(result3)
