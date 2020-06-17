import os

from django.db import transaction
from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from unittest import mock
from conda.cli.python_api import Commands
from tethys_cli import install_commands

FNULL = open(os.devnull, 'w')


class TestServiceInstallHelpers(TestCase):

    def setUp(self):
        from tethys_apps.models import TethysApp

        self.app = TethysApp.objects.create(
            name='An App',
            package='an_app',
        )
        self.app.save()

    @mock.patch('tethys_cli.install_commands.exit')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    def test_open_file_error(self, mock_pretty_output, mock_exit):
        mock_exit.side_effect = SystemExit

        mock_file_path = mock.MagicMock()
        mock_file_path.open.side_effect = IOError('test')

        self.assertRaises(SystemExit, install_commands.open_file, mock_file_path)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual("test", po_call_args[0][0][0])
        self.assertIn("An unexpected error occurred reading the file.", po_call_args[1][0][0])

        mock_exit.assert_called_with(1)

    @mock.patch('tethys_cli.install_commands.input')
    def test_get_interactive_input(self, mock_input):
        install_commands.get_interactive_input()
        mock_input.assert_called_with("")

    @mock.patch('tethys_cli.install_commands.input')
    def test_get_service_name_input(self, mock_input):
        install_commands.get_service_name_input()
        mock_input.assert_called_with("")

    @mock.patch('tethys_cli.cli_colors.pretty_output')
    def test_print_unconfigured_settings(self, mock_pretty_output):
        class MockSetting:
            def __init__(self, name, required):
                self.name = name
                self.required = required

        app_name = 'foo'
        mock_setting = [MockSetting('test_name', True)]
        install_commands.print_unconfigured_settings(app_name, mock_setting)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(f'\nThe following settings were not configured for app: {app_name}:\n', po_call_args[0][0][0])
        self.assertIn('test_name', po_call_args[2][0][0])

    @mock.patch('tethys_cli.cli_colors.pretty_output')
    @mock.patch('tethys_cli.install_commands.call')
    def test_run_sync_stores(self, mock_call, mock_pretty_output):
        from tethys_apps.models import PersistentStoreConnectionSetting

        app_name = 'foo'

        install_commands.run_sync_stores(app_name, [PersistentStoreConnectionSetting()])
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(f'Running syncstores for app {app_name}', po_call_args[0][0][0])
        mock_call.assert_called_with(['tethys', 'syncstores', app_name], )

    @mock.patch('tethys_cli.install_commands.validate_service_id', return_value=True)
    @mock.patch('tethys_cli.install_commands.get_setting_type_from_setting', return_value='setting_type')
    @mock.patch('tethys_cli.install_commands.link_service_to_app_setting')
    def test_find_and_link(self, mock_link_service_to_app_setting, mock_gstfs, mock_vsi):
        service_type = 'service_type'
        setting_name = 'setting_name'
        service_id = 'service_name'
        app_name = 'app_name'
        mock_setting = mock.MagicMock()

        install_commands.find_and_link(service_type, setting_name, service_id, app_name, mock_setting)

        mock_vsi.assert_called_with(service_type, service_id)
        mock_gstfs.assert_called_with(mock_setting)
        mock_link_service_to_app_setting.assert_called_with(service_type, service_id, app_name, 'setting_type',
                                                            setting_name)

    @mock.patch('tethys_cli.install_commands.validate_service_id', return_value=False)
    @mock.patch('tethys_cli.install_commands.get_setting_type_from_setting', return_value='setting_type')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    def test_find_and_link_warning(self, mock_pretty_output, _, __):
        service_type = 'service_type'
        setting_name = 'setting_name'
        service_id = 'service_name'
        app_name = 'app_name'
        mock_setting = mock.MagicMock()

        install_commands.find_and_link(service_type, setting_name, service_id, app_name, mock_setting)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(f'Warning: Could not find service of type: "{service_type}" with the Name/ID: "{service_id}"',
                         po_call_args[0][0][0])

    def test_get_setting_type(self):
        from tethys_apps.models import PersistentStoreDatabaseSetting

        self.assertEqual('persistent', install_commands.get_setting_type(PersistentStoreDatabaseSetting()))

    def test_validate_service_id_valid_id_int(self):
        from tethys_services.models import SpatialDatasetService
        test_service = SpatialDatasetService.objects.create(
            name='foo',
            engine=SpatialDatasetService.GEOSERVER,
            endpoint='https://example.com:8181/geoserver/rest/',
            username='admin',
            password='geoserver'
        )
        test_service.save()
        int_id = int(test_service.id)
        ret = install_commands.validate_service_id('spatial', int_id)
        self.assertTrue(ret)

    def test_validate_service_id_valid_id_str(self):
        from tethys_services.models import PersistentStoreService
        test_service = PersistentStoreService.objects.create(
            name='foo',
            engine='postgresql',
            host='example.com',
            port='5432',
            username='fake_user',
            password='password',
        )
        test_service.save()
        string_id = str(test_service.id)
        ret = install_commands.validate_service_id('persistent', string_id)
        self.assertTrue(ret)

    def test_validate_service_id_valid_name(self):
        from tethys_services.models import DatasetService
        service_name = 'fake_service'
        test_service = DatasetService.objects.create(
            name=service_name,
            engine=DatasetService.CKAN,
            endpoint='https://example.com/api/3/action/',
            apikey='F8k@p1K3Y'
        )
        test_service.save()
        ret = install_commands.validate_service_id('dataset', service_name)
        self.assertTrue(ret)

    def test_validate_service_id_invalid(self):
        from tethys_services.models import WebProcessingService
        service_name = 'fake_service'
        test_service = WebProcessingService.objects.create(
            name=service_name,
            endpoint='https://example.com/wps/WebProcessingService/',
            username='fake_user',
            password='password'
        )
        test_service.save()
        ret = install_commands.validate_service_id('wps', 'does_not_exist')
        self.assertFalse(ret)

    def test_get_setting_type_from_setting_persistent_db(self):
        from tethys_apps.models import PersistentStoreDatabaseSetting

        with transaction.atomic():
            setting = PersistentStoreDatabaseSetting.objects.create(
                name='fake_db',
                description='The fake database.',
                initializer='fake.path.to.initializer',
                spatial=False,
                required=False,
                tethys_app=self.app
            )

            ret = install_commands.get_setting_type_from_setting(setting)

        self.assertEqual('ps_database', ret)

    def test_get_setting_type_from_setting_persistent_connection(self):
        from tethys_apps.models import PersistentStoreConnectionSetting

        with transaction.atomic():
            setting = PersistentStoreConnectionSetting.objects.create(
                name='fake_conn',
                description='The fake database connection.',
                required=False,
                tethys_app=self.app
            )

            ret = install_commands.get_setting_type_from_setting(setting)

        self.assertEqual('ps_connection', ret)

    def test_get_setting_type_from_setting_spatial_dataset(self):
        from tethys_apps.models import SpatialDatasetServiceSetting

        with transaction.atomic():
            setting = SpatialDatasetServiceSetting.objects.create(
                name='fake_sds',
                description='The fake GeoServer dataset service.',
                engine=SpatialDatasetServiceSetting.GEOSERVER,
                required=False,
                tethys_app=self.app
            )

            ret = install_commands.get_setting_type_from_setting(setting)

        self.assertEqual('ds_spatial', ret)

    def test_get_setting_type_from_setting_dataset(self):
        from tethys_apps.models import DatasetServiceSetting

        with transaction.atomic():
            setting = DatasetServiceSetting.objects.create(
                name='fake_ds',
                description='The fake CKAN dataset service.',
                engine=DatasetServiceSetting.CKAN,
                required=False,
                tethys_app=self.app
            )

            ret = install_commands.get_setting_type_from_setting(setting)

        self.assertEqual('ds_dataset', ret)

    def test_get_setting_type_from_setting_wps(self):
        from tethys_apps.models import WebProcessingServiceSetting

        with transaction.atomic():
            setting = WebProcessingServiceSetting.objects.create(
                name='fake_sds',
                description='The fake spatial dataset service.',
                required=False,
                tethys_app=self.app
            )

            ret = install_commands.get_setting_type_from_setting(setting)

            self.assertEqual('wps', ret)

    def test_get_setting_type_from_setting_invalid_setting(self):
        not_a_setting = mock.MagicMock()
        with self.assertRaises(RuntimeError) as cm:
            install_commands.get_setting_type_from_setting(not_a_setting)

            self.assertIn('Could not determine setting type for setting:', str(cm.exception))

    def test_get_service_type_from_setting_persistent_db(self):
        from tethys_apps.models import PersistentStoreDatabaseSetting

        with transaction.atomic():
            setting = PersistentStoreDatabaseSetting.objects.create(
                name='fake_db',
                description='The fake database.',
                initializer='fake.path.to.initializer',
                spatial=False,
                required=False,
                tethys_app=self.app
            )

            ret = install_commands.get_service_type_from_setting(setting)

        self.assertEqual('persistent', ret)

    def test_get_service_type_from_setting_persistent_connection(self):
        from tethys_apps.models import PersistentStoreConnectionSetting

        with transaction.atomic():
            setting = PersistentStoreConnectionSetting.objects.create(
                name='fake_conn',
                description='The fake database connection.',
                required=False,
                tethys_app=self.app
            )

            ret = install_commands.get_service_type_from_setting(setting)

        self.assertEqual('persistent', ret)

    def test_get_service_type_from_setting_spatial_dataset(self):
        from tethys_apps.models import SpatialDatasetServiceSetting

        with transaction.atomic():
            setting = SpatialDatasetServiceSetting.objects.create(
                name='fake_sds',
                description='The fake GeoServer dataset service.',
                engine=SpatialDatasetServiceSetting.GEOSERVER,
                required=False,
                tethys_app=self.app
            )

            ret = install_commands.get_service_type_from_setting(setting)

        self.assertEqual('spatial', ret)

    def test_get_service_type_from_setting_dataset(self):
        from tethys_apps.models import DatasetServiceSetting

        with transaction.atomic():
            setting = DatasetServiceSetting.objects.create(
                name='fake_ds',
                description='The fake CKAN dataset service.',
                engine=DatasetServiceSetting.CKAN,
                required=False,
                tethys_app=self.app
            )

            ret = install_commands.get_service_type_from_setting(setting)

        self.assertEqual('dataset', ret)

    def test_get_service_type_from_setting_wps(self):
        from tethys_apps.models import WebProcessingServiceSetting

        with transaction.atomic():
            setting = WebProcessingServiceSetting.objects.create(
                name='fake_sds',
                description='The fake spatial dataset service.',
                required=False,
                tethys_app=self.app
            )

            ret = install_commands.get_service_type_from_setting(setting)

            self.assertEqual('wps', ret)

    def test_get_service_type_from_setting_invalid_setting(self):
        not_a_setting = mock.MagicMock()
        with self.assertRaises(RuntimeError) as cm:
            install_commands.get_service_type_from_setting(not_a_setting)

            self.assertIn('Could not determine service type for setting:', str(cm.exception))


class TestInstallServicesCommands(TestCase):

    def setUp(self):
        self.mock_path = mock.MagicMock()
        path_patcher = mock.patch('tethys_cli.install_commands.Path', return_value=self.mock_path)
        path_patcher.start()
        self.addCleanup(path_patcher.stop)

    @mock.patch('tethys_cli.install_commands.get_app_settings')
    @mock.patch('tethys_cli.install_commands.find_and_link')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    @mock.patch('tethys_apps.models.CustomSetting')
    def test_configure_services_from_file(self, mock_CustomSetting, mock_pretty_output, mock_find_and_link, mock_gas):
        app_name = 'foo'
        invalid_custom_setting_name = 'custom_setting_name'
        invalid_custom_setting_value = 'hello world'
        valid_custom_setting_name = 'valid_setting'
        valid_custom_setting_value = False
        persistent_setting_name = 'persistent_setting_name'
        persistent_service_name = 'persistent_service_name'
        no_val_persistent_setting_name = 'no_val'
        setting_already_linked_name = 'already_linked'

        services_file_contents = {
            'version': 1,
            'custom_setting': {
                invalid_custom_setting_name: invalid_custom_setting_value,
                valid_custom_setting_name: valid_custom_setting_value,
                'custom_setting_dne': 1
            },
            'persistent': {
                persistent_setting_name: persistent_service_name,
                no_val_persistent_setting_name: None,
                setting_already_linked_name: persistent_service_name
            }
        }

        # Saving raises a validation error
        mock_invalid_custom_setting = mock.MagicMock(value=None)
        mock_invalid_custom_setting.save.side_effect = ValidationError('error')

        # Saving will pass on the valid custom setting (not mocked to raise ValidationError)
        mock_valid_custom_setting = mock.MagicMock(value=None)

        # Third custom setting listed does not exist
        mock_CustomSetting.objects.get.side_effect = [
            mock_invalid_custom_setting,  #: Save raises Validation error
            mock_valid_custom_setting,  #: Should pass without errors
            ObjectDoesNotExist  #: Setting not found
        ]

        # This persistent setting exists and is listed in the file
        mock_persistent_database_setting = mock.MagicMock()
        mock_persistent_database_setting.name = persistent_setting_name

        # This setting exists, but there is no value assigned in the file
        mock_no_val_persistent_setting = mock.MagicMock()
        mock_no_val_persistent_setting.name = no_val_persistent_setting_name

        # This persistent setting is not listed in the file, but exists in the db
        mock_setting_unlisted = mock.MagicMock()
        mock_setting_unlisted.name = 'this_setting_is_in_the_file_but_does_not_exist'

        mock_setting_already_linked = mock.MagicMock()
        mock_setting_already_linked.name = setting_already_linked_name

        mock_gas.return_value = {
            'unlinked_settings': [
                mock_setting_unlisted,  #: This persistent setting is not listed in the file, but exists in the db
                mock_persistent_database_setting,  #: This persistent setting exists and is listed with value
                mock_no_val_persistent_setting,  #: This setting exists and is listed in the file, but no value given
            ],
            'linked_settings': [
                mock_setting_already_linked,  #: This setting is already linked, and so it won't be configured again
            ]
        }

        install_commands.configure_services_from_file(services_file_contents, app_name)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn(f'Incorrect value type given for custom setting \'{invalid_custom_setting_name}\'',
                      po_call_args[0][0][0])
        self.assertEqual(f'CustomSetting: "{valid_custom_setting_name}" was assigned the value: '
                         f'"{valid_custom_setting_value}"', po_call_args[1][0][0])
        self.assertEqual('Custom setting named "custom_setting_dne" could not be found in app "foo". Skipping...',
                         po_call_args[2][0][0])
        self.assertEqual(f'No service given for setting "{no_val_persistent_setting_name}". Skipping...',
                         po_call_args[3][0][0])
        self.assertIn('already configured or does not exist in app', po_call_args[4][0][0])

        mock_find_and_link.assert_called_with('persistent', persistent_setting_name, persistent_service_name, app_name,
                                              mock_persistent_database_setting)

    @mock.patch('tethys_cli.install_commands.get_app_settings')
    @mock.patch('tethys_cli.install_commands.find_and_link')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    def test_configure_services_from_file_no_settings_for_app(self, mock_pretty_output, mock_find_and_link, mock_gas):
        app_name = 'foo'
        persistent_setting_name = 'persistent_setting_name'
        persistent_service_name = 'persistent_service_name'

        services_file_contents = {
            'version': 1,
            'persistent': {
                persistent_setting_name: persistent_service_name
            }
        }

        # No settings found for this app
        mock_gas.return_value = None

        install_commands.configure_services_from_file(services_file_contents, app_name)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(f'No settings found for app "{app_name}". Skipping automated configuration...',
                         po_call_args[0][0][0])
        mock_find_and_link.assert_not_called()

    @mock.patch('tethys_cli.cli_colors.pretty_output')
    def test_run_portal_install_path_none(self, _):

        self.mock_path.__truediv__().exists.return_value = False

        self.assertFalse(install_commands.run_portal_install('foo'))

    @mock.patch('tethys_cli.install_commands.configure_services_from_file')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    @mock.patch('tethys_cli.install_commands.open_file')
    def test_run_portal_install(self, mock_open_file, mock_pretty_output, mock_configure_services):
        app_name = 'foo'
        services = {'persistent': {'test_setting': 'test_service'}}
        portal_options_services = {'apps': {app_name: {'services': services}}}
        portal_options_empty_services = {'apps': {app_name: {'services': ''}}}
        portal_options_no_services = {'apps': {app_name: ''}}

        mock_open_file.side_effect = [portal_options_services, portal_options_empty_services,
                                      portal_options_no_services]
        self.mock_path.exists.return_value = True

        self.assertTrue(install_commands.run_portal_install(app_name))
        mock_configure_services.assert_called_with(services, app_name)
        self.assertFalse(install_commands.run_portal_install(app_name))
        self.assertFalse(install_commands.run_portal_install(app_name))

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn(f'No app configuration found for app: {app_name}', po_call_args[2][0][0])
        self.assertIn('No apps configuration found in portal config file.', po_call_args[4][0][0])

    @mock.patch('tethys_cli.cli_colors.pretty_output')
    def test_run_services_path_none(self, mock_pretty_output):
        args = mock.MagicMock(services_file=None, no_db_sync=False, only_dependencies=False, without_dependencies=False)

        self.mock_path.exists.return_value = False

        install_commands.run_services('foo', args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual('No Services file found.', po_call_args[0][0][0])

    @mock.patch('tethys_cli.install_commands.configure_services_from_file')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    @mock.patch('tethys_cli.install_commands.open_file')
    def test_run_services(self, mock_open_file, mock_pretty_output, _):
        args = mock.MagicMock(services_file='services_file', no_db_sync=False, only_dependencies=False,
                              without_dependencies=False)

        self.mock_path.exists.return_value = True
        mock_open_file.side_effect = ['service_file', '']
        install_commands.run_services('foo', args)
        install_commands.run_services('foo', args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual('No Services listed in Services file.', po_call_args[0][0][0])


class TestInstallCommands(TestCase):
    def setUp(self):
        from tethys_apps.models import TethysApp
        self.src_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.root_app_path = os.path.join(self.src_dir, 'apps', 'tethysapp-test_app')
        self.app_model = TethysApp(
            name='test_app',
            package='test_app'
        )
        self.app_model.save()

    def tearDown(self):
        self.app_model.delete()

    @mock.patch('tethys_cli.cli_colors.pretty_output')
    @mock.patch('builtins.input', side_effect=['x', 'n'])
    @mock.patch('tethys_cli.install_commands.exit')
    @mock.patch('tethys_cli.install_commands.call')
    def test_install_file_not_generate(self, mock_call, mock_exit, _, __):
        args = mock.MagicMock(file=None, quiet=False, no_db_sync=False, only_dependencies=False,
                              without_dependencies=False)

        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, install_commands.install_command, args)
        self.assertEqual(3, len(mock_call.call_args_list))

        mock_exit.assert_called_with(0)

    @mock.patch('tethys_cli.cli_colors.pretty_output')
    @mock.patch('builtins.input', side_effect=['y'])
    @mock.patch('tethys_cli.install_commands.call')
    @mock.patch('tethys_cli.install_commands.exit')
    def test_install_file_generate(self, mock_exit, mock_call, _, __):
        args = mock.MagicMock(file=None, quiet=False, no_db_sync=False, only_dependencies=False,
                              without_dependencies=False)
        check_call = ['tethys', 'gen', 'install']

        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, install_commands.install_command, args)
        mock_call.assert_called_with(check_call)
        mock_exit.assert_called_with(0)

    @mock.patch('tethys_cli.install_commands.run_services')
    @mock.patch('tethys_cli.install_commands.call')
    @mock.patch('tethys_cli.install_commands.exit')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    def test_no_conda_input_file(self, mock_pretty_output, mock_exit, _, __):
        file_path = os.path.join(self.root_app_path, 'install-no-dep.yml')
        args = mock.MagicMock(file=file_path, verbose=False, no_db_sync=False, only_dependencies=False,
                              without_dependencies=False)
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, install_commands.install_command, args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual("Installing dependencies...", po_call_args[0][0][0])
        self.assertIn("Running application install....", po_call_args[1][0][0])
        self.assertIn("Quiet mode: No additional service setting validation will be performed.", po_call_args[2][0][0])
        self.assertIn("Services Configuration Completed.", po_call_args[3][0][0])
        self.assertIn("Skipping syncstores.", po_call_args[4][0][0])
        mock_exit.assert_called_with(0)

    @mock.patch('tethys_cli.install_commands.run_services')
    @mock.patch('tethys_cli.install_commands.call')
    @mock.patch('tethys_cli.install_commands.exit')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    def test_input_file_with_post(self, mock_pretty_output, mock_exit, _, __):
        file_path = os.path.join(self.root_app_path, 'install-with-post.yml')
        args = mock.MagicMock(file=file_path, verbose=False, no_db_sync=False, only_dependencies=False,
                              without_dependencies=False)
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, install_commands.install_command, args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual("Installing dependencies...", po_call_args[0][0][0])
        self.assertEqual("Skipping package installation, Skip option found.", po_call_args[1][0][0])
        self.assertIn("Running application install....", po_call_args[2][0][0])
        self.assertIn("Quiet mode: No additional service setting validation will be performed.", po_call_args[3][0][0])
        self.assertIn("Services Configuration Completed.", po_call_args[4][0][0])
        self.assertIn("Skipping syncstores.", po_call_args[5][0][0])
        self.assertIn("Running post installation tasks...", po_call_args[6][0][0])
        self.assertIn("Post Script Result: b'test\\n'", po_call_args[7][0][0])
        mock_exit.assert_called_with(0)

    @mock.patch('tethys_cli.install_commands.run_services')
    @mock.patch('tethys_cli.install_commands.run_sync_stores')
    @mock.patch('tethys_cli.install_commands.run_interactive_services')
    @mock.patch('tethys_cli.install_commands.call')
    @mock.patch('tethys_cli.install_commands.run_portal_install', return_value=False)
    @mock.patch('tethys_cli.install_commands.run_services')
    @mock.patch('tethys_cli.install_commands.exit')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    def test_skip_input_file(self, mock_pretty_output, mock_exit, _, __, ___, ____, _____, ______):
        file_path = os.path.join(self.root_app_path, 'install-skip-setup.yml')
        mock_exit.side_effect = SystemExit

        args = mock.MagicMock(file=file_path, verbose=False, no_db_sync=False, only_dependencies=False,
                              without_dependencies=False)
        self.assertRaises(SystemExit, install_commands.install_command, args)

        args = mock.MagicMock(file=file_path, develop=False, no_db_sync=False, only_dependencies=False,
                              without_dependencies=False)
        self.assertRaises(SystemExit, install_commands.install_command, args)

        args = mock.MagicMock(file=file_path, verbose=False, develop=False, force_services=False, quiet=False,
                              no_sync_stores=False, no_db_sync=False, only_dependencies=False,
                              without_dependencies=False)
        self.assertRaises(SystemExit, install_commands.install_command, args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual("Skipping package installation, Skip option found.", po_call_args[1][0][0])
        mock_exit.assert_called_with(0)

    @mock.patch('tethys_cli.install_commands.run_services')
    @mock.patch('tethys_cli.install_commands.call')
    @mock.patch('tethys_cli.install_commands.conda_run', return_value=['', '', 1])
    @mock.patch('tethys_cli.install_commands.exit')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    def test_conda_and_pip_package_install(self, mock_pretty_output, mock_exit, mock_conda_run, mock_call, _):
        file_path = os.path.join(self.root_app_path, 'install-dep.yml')
        args = mock.MagicMock(file=file_path, develop=False, verbose=False, services_file=None, update_installed=False,
                              no_db_sync=False, only_dependencies=False, without_dependencies=False)
        mock_exit.side_effect = SystemExit
        self.assertRaises(SystemExit, install_commands.install_command, args)

        mock_conda_run.assert_called_with(Commands.INSTALL, '-c', 'tacaswell', '--freeze-installed', 'geojson',
                                          use_exception_handler=False, stdout=None, stderr=None)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual("Installing dependencies...", po_call_args[0][0][0])
        self.assertEqual("Running conda installation tasks...", po_call_args[1][0][0])
        self.assertIn("Warning: Packages installation ran into an error.", po_call_args[2][0][0])
        self.assertEqual("Running pip installation tasks...", po_call_args[3][0][0])
        self.assertEqual("Running application install....", po_call_args[4][0][0])
        self.assertEqual("Quiet mode: No additional service setting validation will be performed.",
                         po_call_args[5][0][0])
        self.assertEqual("Services Configuration Completed.", po_call_args[6][0][0])

        self.assertEqual(['pip', 'install', 'see'], mock_call.mock_calls[0][1][0])
        self.assertEqual(['python', 'setup.py', 'clean', '--all'], mock_call.mock_calls[1][1][0])
        self.assertEqual(['python', 'setup.py', 'install'], mock_call.mock_calls[2][1][0])
        self.assertEqual(['tethys', 'db', 'sync'], mock_call.mock_calls[3][1][0])

        mock_exit.assert_called_with(0)

    @mock.patch('tethys_cli.install_commands.run_services')
    @mock.patch('tethys_cli.install_commands.call')
    @mock.patch('tethys_cli.install_commands.conda_run', return_value=['', '', 1])
    @mock.patch('tethys_cli.install_commands.exit')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    def test_without_dependencies(self, mock_pretty_output, mock_exit, mock_conda_run, mock_call, _):
        file_path = os.path.join(self.root_app_path, 'install-dep.yml')
        args = mock.MagicMock(file=file_path, develop=False, verbose=False, services_file=None, update_installed=False,
                              no_db_sync=False, only_dependencies=False, without_dependencies=True)
        mock_exit.side_effect = SystemExit
        self.assertRaises(SystemExit, install_commands.install_command, args)

        # Ensure conda command wasn't called to install dependencies
        mock_conda_run.assert_not_called()

        # Make sure 'pip install' isn't in any of the calls
        self.assertFalse(any(['pip install' in ' '.join(mc[1][0]) for mc in mock_call.mock_calls]))

        # Validate output displayed to the user
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual("Skipping package installation.", po_call_args[1][0][0])
        self.assertEqual("Running application install....", po_call_args[2][0][0])
        self.assertEqual("Quiet mode: No additional service setting validation will be performed.",
                         po_call_args[3][0][0])
        self.assertEqual("Services Configuration Completed.", po_call_args[4][0][0])

        # Verify that the application install still happens
        self.assertEqual(['python', 'setup.py', 'clean', '--all'], mock_call.mock_calls[0][1][0])
        self.assertEqual(['python', 'setup.py', 'install'], mock_call.mock_calls[1][1][0])
        self.assertEqual(['tethys', 'db', 'sync'], mock_call.mock_calls[2][1][0])

        mock_exit.assert_called_with(0)

    @mock.patch('tethys_cli.install_commands.run_services')
    @mock.patch('tethys_cli.install_commands.call')
    @mock.patch('tethys_cli.install_commands.conda_run', return_value=['', '', 1])
    @mock.patch('tethys_cli.install_commands.exit')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    def test_conda_and_pip_package_install_only_dependencies(self, mock_pretty_output, mock_exit, mock_conda_run,
                                                             mock_call, _):
        file_path = os.path.join(self.root_app_path, 'install-dep.yml')
        args = mock.MagicMock(file=file_path, develop=False, verbose=False, services_file=None, update_installed=False,
                              no_db_sync=False, only_dependencies=True, without_dependencies=False)
        mock_exit.side_effect = SystemExit
        self.assertRaises(SystemExit, install_commands.install_command, args)

        mock_conda_run.assert_called_with(Commands.INSTALL, '-c', 'tacaswell', '--freeze-installed', 'geojson',
                                          use_exception_handler=False, stdout=None, stderr=None)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual("Installing dependencies...", po_call_args[0][0][0])
        self.assertEqual("Running conda installation tasks...", po_call_args[1][0][0])
        self.assertIn("Warning: Packages installation ran into an error.", po_call_args[2][0][0])
        self.assertEqual("Running pip installation tasks...", po_call_args[3][0][0])
        self.assertEqual("Successfully installed dependencies for test_app.", po_call_args[4][0][0])

        self.assertEqual(1, len(mock_call.mock_calls))
        self.assertEqual(['pip', 'install', 'see'], mock_call.mock_calls[0][1][0])

        mock_exit.assert_called_with(0)

    @mock.patch('tethys_cli.install_commands.run_services')
    @mock.patch('tethys_cli.install_commands.call')
    @mock.patch('tethys_cli.install_commands.conda_run', return_value=['', '', 1])
    @mock.patch('tethys_cli.install_commands.exit')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    def test_conda_and_pip_package_install_update_installed(self, mock_pretty_output, mock_exit, mock_conda_run,
                                                            mock_call, _):
        file_path = os.path.join(self.root_app_path, 'install-dep.yml')
        args = mock.MagicMock(file=file_path, develop=False, verbose=False, services_file=None, update_installed=True,
                              no_db_sync=True, only_dependencies=False, without_dependencies=False)
        mock_exit.side_effect = SystemExit
        self.assertRaises(SystemExit, install_commands.install_command, args)

        mock_conda_run.assert_called_with(Commands.INSTALL, '-c', 'tacaswell', 'geojson', use_exception_handler=False,
                                          stdout=None, stderr=None)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual("Installing dependencies...", po_call_args[0][0][0])
        self.assertEqual("Warning: Updating previously installed packages. This could break your Tethys environment.",
                         po_call_args[1][0][0])
        self.assertEqual("Running conda installation tasks...", po_call_args[2][0][0])
        self.assertIn("Warning: Packages installation ran into an error.", po_call_args[3][0][0])
        self.assertEqual("Running pip installation tasks...", po_call_args[4][0][0])
        self.assertEqual("Running application install....", po_call_args[5][0][0])
        self.assertEqual("Successfully installed test_app.", po_call_args[6][0][0])

        self.assertEqual(['pip', 'install', 'see'], mock_call.mock_calls[0][1][0])
        self.assertEqual(['python', 'setup.py', 'clean', '--all'], mock_call.mock_calls[1][1][0])
        self.assertEqual(['python', 'setup.py', 'install'], mock_call.mock_calls[2][1][0])

        mock_exit.assert_called_with(0)

    @mock.patch('builtins.input', side_effect=['x', 5])
    @mock.patch('tethys_cli.install_commands.get_app_settings')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    def test_interactive_custom_setting_set(self, mock_pretty_output, mock_gas, _):
        mock_cs = mock.MagicMock()
        mock_cs.name = 'mock_cs'
        mock_cs.save.side_effect = [ValidationError('error'), mock.DEFAULT]
        mock_gas.return_value = {'unlinked_settings': [mock_cs]}

        install_commands.run_interactive_services('foo')

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn("Configuring mock_cs", po_call_args[2][0][0])
        self.assertIn("Type", po_call_args[3][0][0])
        self.assertIn("Enter the desired value", po_call_args[4][0][0])
        self.assertIn("Incorrect value type", po_call_args[5][0][0])
        self.assertIn("Enter the desired value", po_call_args[6][0][0])
        self.assertEqual(mock_cs.name + " successfully set with value: 5.", po_call_args[7][0][0])

    @mock.patch('builtins.input', side_effect=[''])
    @mock.patch('tethys_cli.install_commands.get_app_settings')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    def test_interactive_custom_setting_skip(self, mock_pretty_output, mock_gas, _):
        mock_cs = mock.MagicMock()
        mock_cs.name = 'mock_cs'
        mock_gas.return_value = {'unlinked_settings': [mock_cs]}

        install_commands.run_interactive_services('foo')

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn("Configuring mock_cs", po_call_args[2][0][0])
        self.assertIn("Type", po_call_args[3][0][0])
        self.assertIn("Enter the desired value", po_call_args[4][0][0])
        self.assertEqual(f"Skipping setup of {mock_cs.name}", po_call_args[5][0][0])

    @mock.patch('builtins.input', side_effect=KeyboardInterrupt)
    @mock.patch('tethys_cli.install_commands.exit')
    @mock.patch('tethys_cli.install_commands.get_app_settings')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    def test_interactive_custom_setting_interrupt(self, mock_pretty_output, mock_gas, mock_exit, _):
        mock_cs = mock.MagicMock()
        mock_cs.name = 'mock_cs'
        mock_gas.return_value = {'unlinked_settings': [mock_cs]}

        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, install_commands.run_interactive_services, 'foo')

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn("Configuring mock_cs", po_call_args[2][0][0])
        self.assertIn("Type", po_call_args[3][0][0])
        self.assertIn("Enter the desired value", po_call_args[4][0][0])
        self.assertEqual("\nInstall Command cancelled.", po_call_args[5][0][0])

        mock_exit.assert_called_with(0)

    @mock.patch('builtins.input', side_effect=['1', '1', '', '1', '1', KeyboardInterrupt])
    @mock.patch('tethys_cli.install_commands.validate_service_id', side_effect=[False, True])
    @mock.patch('tethys_cli.install_commands.get_setting_type', return_value='persistent')
    @mock.patch('tethys_cli.install_commands.get_setting_type_from_setting',
                side_effect=['ps_database', 'ps_database', 'ps_database', RuntimeError('setting_type_not_found')])
    @mock.patch('tethys_cli.install_commands.get_service_type_from_setting',
                side_effect=['persistent', 'persistent', RuntimeError('service_type_not_found'), 'persistent'])
    @mock.patch('tethys_cli.install_commands.exit')
    @mock.patch('tethys_cli.install_commands.services_list_command')
    @mock.patch('tethys_cli.install_commands.get_app_settings')
    @mock.patch('tethys_cli.install_commands.link_service_to_app_setting')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    def test_interactive_service_setting_all(self, mock_pretty_output, mock_lstas, mock_gas, mock_slc,
                                             mock_exit, _, __, ___, ____, _____):
        mock_ss = mock.MagicMock()
        del mock_ss.value
        mock_ss.name = 'mock_ss'
        mock_ss.description = 'This is a fake setting for testing.'
        mock_ss.required = True
        mock_ss.save.side_effect = [ValidationError('error'), mock.DEFAULT]
        mock_gas.return_value = {'unlinked_settings': [mock_ss, mock_ss, mock_ss, mock_ss, mock_ss, mock_ss]}

        mock_s = mock.MagicMock()
        mock_slc.side_effect = [[[]], [[mock_s]], [[mock_s]], [[mock_s]], [[mock_s]], [[mock_s]]]

        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, install_commands.run_interactive_services, 'foo')

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual('Running Interactive Service Mode. Any configuration options in services.yml or '
                         'portal_config.yml will be ignored...', po_call_args[0][0][0])
        self.assertIn("Hit return at any time to skip a step.", po_call_args[1][0][0])
        self.assertIn("Configuring mock_ss", po_call_args[2][0][0])
        self.assertIn("Type: MagicMock", po_call_args[3][0][0])
        self.assertIn(f"Description: {mock_ss.description}", po_call_args[3][0][0])
        self.assertIn(f"Required: {mock_ss.required}", po_call_args[3][0][0])
        self.assertIn("No compatible services found.", po_call_args[4][0][0])
        self.assertIn("tethys services create persistent -h", po_call_args[4][0][0])
        self.assertIn("Enter the service ID/Name", po_call_args[7][0][0])
        self.assertIn("Incorrect service ID/Name. Please try again.", po_call_args[8][0][0])
        self.assertIn("Enter the service ID/Name", po_call_args[9][0][0])
        self.assertIn(f"Skipping setup of {mock_ss.name}", po_call_args[13][0][0])
        self.assertEqual("service_type_not_found Skipping...", po_call_args[17][0][0])
        self.assertEqual("setting_type_not_found Skipping...", po_call_args[21][0][0])
        self.assertEqual("\nInstall Command cancelled.", po_call_args[25][0][0])

        mock_lstas.assert_called_with('persistent', '1', 'foo', 'ps_database', 'mock_ss')
        mock_exit.assert_called_with(0)

    @mock.patch('builtins.input', side_effect=['x', 5])
    @mock.patch('tethys_cli.install_commands.get_app_settings')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    def test_interactive_no_settings(self, mock_pretty_output, mock_gas, _):
        mock_cs = mock.MagicMock()
        mock_cs.name = 'mock_cs'
        mock_cs.save.side_effect = [ValidationError('error'), mock.DEFAULT]
        mock_gas.return_value = None

        install_commands.run_interactive_services('foo')

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn('No settings found for app "foo". Skipping interactive configuration...', po_call_args[2][0][0])
