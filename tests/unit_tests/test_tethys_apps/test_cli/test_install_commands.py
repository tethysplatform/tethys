import os
from django.test import TestCase
from django.core.exceptions import ValidationError
from unittest import mock
from conda.cli.python_api import Commands
from tethys_apps.cli import install_commands

FNULL = open(os.devnull, 'w')


class TestServiceInstallHelpers(TestCase):

    @mock.patch('builtins.open', side_effect=IOError('test'))
    @mock.patch('tethys_apps.cli.install_commands.exit')
    @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    def test_open_file_error(self, mock_pretty_output, mock_exit, _):
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, install_commands.open_file, 'foo')
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual("test", po_call_args[0][0][0])
        self.assertIn("An unexpected error occurred reading the file.", po_call_args[1][0][0])

        mock_exit.assert_called_with(1)

    def test_get_service_from_id_fail(self):
        self.assertFalse(install_commands.get_service_from_id(9384))

    def test_get_service_from_name_fail(self):
        self.assertFalse(install_commands.get_service_from_name("sdfsdf"))

    @mock.patch('tethys_services.models.PersistentStoreService.objects.get', return_value=True)
    def test_get_service_from_id_persistent(self, mock_get):
        self.assertEqual(install_commands.get_service_from_id(1).get('service_type'), 'persistent')
        mock_get.assert_called_with(id=1)

    @mock.patch('tethys_services.models.SpatialDatasetService.objects.get', return_value=True)
    def test_get_service_from_id_spatial(self, mock_get):
        self.assertEqual(install_commands.get_service_from_id(1).get('service_type'), 'spatial')
        mock_get.assert_called_with(id=1)

    @mock.patch('tethys_services.models.DatasetService.objects.get', return_value=True)
    def test_get_service_from_id_dataset(self, mock_get):
        self.assertEqual(install_commands.get_service_from_id(1).get('service_type'), 'dataset')
        mock_get.assert_called_with(id=1)

    @mock.patch('tethys_services.models.WebProcessingService.objects.get', return_value=True)
    def test_get_service_from_id_wps(self, mock_get):
        self.assertEqual(install_commands.get_service_from_id(1).get('service_type'), 'wps')
        mock_get.assert_called_with(id=1)

    @mock.patch('tethys_services.models.PersistentStoreService.objects.get', return_value=True)
    def test_get_service_from_name_persistent(self, mock_get):
        self.assertEqual(install_commands.get_service_from_name("nonexisting").get('service_type'), 'persistent')
        mock_get.assert_called_with(name='nonexisting')

    @mock.patch('tethys_services.models.SpatialDatasetService.objects.get', return_value=True)
    def test_get_service_from_name_spatial(self, mock_get):
        self.assertEqual(install_commands.get_service_from_name("nonexisting").get('service_type'), 'spatial')
        mock_get.assert_called_with(name='nonexisting')

    @mock.patch('tethys_services.models.DatasetService.objects.get', return_value=True)
    def test_get_service_from_name_dataset(self, mock_get):
        self.assertEqual(install_commands.get_service_from_name("nonexisting").get('service_type'), 'dataset')
        mock_get.assert_called_with(name='nonexisting')

    @mock.patch('tethys_services.models.WebProcessingService.objects.get', return_value=True)
    def test_get_service_from_name_wps(self, mock_get):
        self.assertEqual(install_commands.get_service_from_name("nonexisting").get('service_type'), 'wps')
        mock_get.assert_called_with(name='nonexisting')

    @mock.patch('tethys_apps.cli.install_commands.input')
    def test_get_interactive_input(self, mock_input):
        install_commands.get_interactive_input()
        mock_input.assert_called_with("")

    @mock.patch('tethys_apps.cli.install_commands.input')
    def test_get_service_name_input(self, mock_input):
        install_commands.get_service_name_input()
        mock_input.assert_called_with("")

    @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
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

    @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    @mock.patch('tethys_apps.cli.install_commands.call')
    def test_run_sync_stores(self, mock_call, mock_pretty_output):
        from tethys_apps.models import PersistentStoreConnectionSetting

        app_name = 'foo'

        install_commands.run_sync_stores(app_name, [PersistentStoreConnectionSetting()])
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(f'Running syncstores for app {app_name}', po_call_args[0][0][0])
        mock_call.assert_called_with(['tethys', 'syncstores', app_name], )

    @mock.patch('tethys_apps.cli.install_commands.get_service_from_name', return_value={'service_type': 'service_type',
                                                                                        'linkParam': 'linkParam'})
    @mock.patch('tethys_apps.cli.install_commands.link_service_to_app_setting')
    def test_find_and_link(self, mock_link_service_to_app_setting, _):
        service_type = 'service_type'
        setting_name = 'setting_name'
        service_name = 'service_name'
        app_name = 'app_name'

        install_commands.find_and_link(service_type, setting_name, service_name, app_name)

        mock_link_service_to_app_setting.assert_called_with('service_type',
                                                            service_name,
                                                            app_name,
                                                            'linkParam',
                                                            setting_name)

    @mock.patch('tethys_apps.cli.install_commands.get_service_from_name', return_value=False)
    @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    def test_find_and_link_warning(self, mock_pretty_output, _):
        service_type = 'service_type'
        setting_name = 'setting_name'
        service_name = 'service_name'
        app_name = 'app_name'

        install_commands.find_and_link(service_type, setting_name, service_name, app_name)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(f'Warning: Could not find service of type: {service_type} with the name/id: {service_name}',
                         po_call_args[0][0][0])


class TestInstallServicesCommands(TestCase):
    @mock.patch('tethys_apps.cli.install_commands.find_and_link')
    @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    @mock.patch('tethys_apps.models.CustomSetting')
    def test_configure_services(self, mock_customsettings, mock_pretty_output, mock_find_and_link):
        app_name = 'foo'
        custom_service_name = 'custom_service_name'
        custom_setting_name = 'custom_setting_name'
        persistent_service_name = 'persistent_service_name'
        persistent_setting_name = 'persistent_setting_name'
        services = {'version': 1, 'custom_setting': {custom_setting_name: custom_service_name},
                    'persistent': {persistent_setting_name: persistent_service_name}}

        mock_customsetting = mock.MagicMock(value=1)
        mock_customsetting.save.side_effect = ValidationError('error')
        mock_customsettings.objects.get.return_value = mock_customsetting

        install_commands.configure_services(services, app_name)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn(f'Incorrect value type given for custom setting \'{custom_setting_name}\'', po_call_args[0][0][0])

        mock_find_and_link.assert_called_with('persistent', persistent_setting_name,
                                              persistent_service_name, app_name)

    @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    @mock.patch('tethys_apps.cli.install_commands.os')
    def test_run_portal_install_path_none(self, mock_os, _):

        mock_os.path.exists.return_value = False

        self.assertFalse(install_commands.run_portal_install(None, 'foo'))

    @mock.patch('tethys_apps.cli.install_commands.configure_services')
    @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    @mock.patch('tethys_apps.cli.install_commands.open_file')
    @mock.patch('tethys_apps.cli.install_commands.os')
    def test_run_portal_install(self, mock_os, mock_open_file, mock_pretty_output, mock_configure_services):
        app_name = 'foo'
        services = {'persistent': {'test_setting': 'test_service'}}
        portal_options_services = {'apps': {app_name: {'services': services}}}
        portal_options_empty_services = {'apps': {app_name: {'services': ''}}}
        portal_options_no_services = {'apps': {app_name: ''}}

        mock_open_file.side_effect = [portal_options_services, portal_options_empty_services,
                                      portal_options_no_services]
        mock_os.path.exists.return_value = True

        self.assertTrue(install_commands.run_portal_install(None, app_name))
        mock_configure_services.assert_called_with(services, app_name)
        self.assertFalse(install_commands.run_portal_install(None, app_name))
        self.assertFalse(install_commands.run_portal_install(None, app_name))

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn(f'No app configuration found for app: {app_name}', po_call_args[2][0][0])
        self.assertIn('No apps configuration found in portal config file.', po_call_args[4][0][0])

    @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    @mock.patch('tethys_apps.cli.install_commands.os')
    def test_run_services_path_none(self, mock_os, mock_pretty_output):
        args = mock.MagicMock(services_file=None)

        mock_os.path.exists.return_value = False

        install_commands.run_services('foo', args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual('No Services file found.', po_call_args[0][0][0])

    @mock.patch('tethys_apps.cli.install_commands.configure_services')
    @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    @mock.patch('tethys_apps.cli.install_commands.open_file')
    @mock.patch('tethys_apps.cli.install_commands.os')
    def test_run_services(self, mock_os, mock_open_file, mock_pretty_output, _):
        args = mock.MagicMock(services_file='services_file')

        mock_os.path.exists.return_value = True
        mock_open_file.side_effect = ['service_file', '']
        install_commands.run_services('foo', args)
        install_commands.run_services('foo', args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual('No Services listed in Services file.', po_call_args[0][0][0])


class TestInstallCommands(TestCase):
    def setUp(self):
        from tethys_apps.models import TethysApp
        self.src_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.root_app_path = os.path.join(self.src_dir, 'apps', 'tethysapp-test_app')
        self.app_model = TethysApp(
            name='test_app',
            package='test_app'
        )
        self.app_model.save()
        pass

    def tearDown(self):
        self.app_model.delete()
        pass

    @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    @mock.patch('builtins.input', side_effect=['x', 'n'])
    @mock.patch('tethys_apps.cli.install_commands.exit')
    @mock.patch('tethys_apps.cli.install_commands.call')
    def test_install_file_not_generate(self, mock_call, mock_exit, _, __):
        args = mock.MagicMock(file=None, quiet=False)

        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, install_commands.install_command, args)
        self.assertEqual(3, len(mock_call.call_args_list))

        mock_exit.assert_called_with(0)

    @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    @mock.patch('builtins.input', side_effect=['y'])
    @mock.patch('tethys_apps.cli.install_commands.call')
    @mock.patch('tethys_apps.cli.install_commands.exit')
    def test_install_file_generate(self, mock_exit, mock_call, _, __):
        args = mock.MagicMock(file=None, quiet=False)
        check_call = ['tethys', 'gen', 'install']

        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, install_commands.install_command, args)
        mock_call.assert_called_with(check_call)
        mock_exit.assert_called_with(0)

    @mock.patch('tethys_apps.cli.install_commands.run_services')
    @mock.patch('tethys_apps.cli.install_commands.call')
    @mock.patch('tethys_apps.cli.install_commands.exit')
    @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    def test_no_conda_input_file(self, mock_pretty_output, mock_exit, _, __):
        file_path = os.path.join(self.root_app_path, 'install-no-dep.yml')
        args = mock.MagicMock(file=file_path, verbose=False)
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, install_commands.install_command, args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn("Running application install....", po_call_args[0][0][0])
        self.assertIn("Quiet mode: No additional service setting validation will be performed.", po_call_args[1][0][0])
        self.assertIn("Services Configuration Completed.", po_call_args[2][0][0])
        self.assertIn("Skipping syncstores.", po_call_args[3][0][0])
        mock_exit.assert_called_with(0)

    @mock.patch('tethys_apps.cli.install_commands.run_services')
    @mock.patch('tethys_apps.cli.install_commands.call')
    @mock.patch('tethys_apps.cli.install_commands.exit')
    @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    def test_input_file_with_post(self, mock_pretty_output, mock_exit, _, __):
        file_path = os.path.join(self.root_app_path, 'install-with-post.yml')
        args = mock.MagicMock(file=file_path, verbose=False)
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, install_commands.install_command, args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn("Running application install....", po_call_args[1][0][0])
        self.assertIn("Quiet mode: No additional service setting validation will be performed.", po_call_args[2][0][0])
        self.assertIn("Services Configuration Completed.", po_call_args[3][0][0])
        self.assertIn("Skipping syncstores.", po_call_args[4][0][0])
        self.assertIn("Running post installation tasks...", po_call_args[5][0][0])
        self.assertIn("Post Script Result: b'test\\n'", po_call_args[6][0][0])
        mock_exit.assert_called_with(0)

    @mock.patch('tethys_apps.cli.install_commands.run_services')
    @mock.patch('tethys_apps.cli.install_commands.run_sync_stores')
    @mock.patch('tethys_apps.cli.install_commands.run_interactive_services')
    @mock.patch('tethys_apps.cli.install_commands.call')
    @mock.patch('tethys_apps.cli.install_commands.run_portal_install', return_value=False)
    @mock.patch('tethys_apps.cli.install_commands.run_services')
    @mock.patch('tethys_apps.cli.install_commands.exit')
    @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    def test_skip_input_file(self, mock_pretty_output, mock_exit, _, __, ___, ____, _____, ______):
        file_path = os.path.join(self.root_app_path, 'install-skip-setup.yml')
        mock_exit.side_effect = SystemExit

        args = mock.MagicMock(file=file_path, verbose=False)
        self.assertRaises(SystemExit, install_commands.install_command, args)

        args = mock.MagicMock(file=file_path, develop=False)
        self.assertRaises(SystemExit, install_commands.install_command, args)

        args = mock.MagicMock(file=file_path, verbose=False, develop=False, force_services=False, quiet=False,
                              no_sync=False)
        self.assertRaises(SystemExit, install_commands.install_command, args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual("Skipping package installation, Skip option found.", po_call_args[0][0][0])
        mock_exit.assert_called_with(0)

    @mock.patch('tethys_apps.cli.install_commands.run_services')
    @mock.patch('tethys_apps.cli.install_commands.call')
    @mock.patch('tethys_apps.cli.install_commands.conda_run', return_value=['', '', 1])
    @mock.patch('tethys_apps.cli.install_commands.exit')
    @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    def test_conda_and_pip_package_install(self, mock_pretty_output, mock_exit, mock_conda_run, mock_call, _):
        file_path = os.path.join(self.root_app_path, 'install-dep.yml')
        args = mock.MagicMock(file=file_path, develop=False, verbose=False, services_file=None)
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, install_commands.install_command, args)

        mock_conda_run.assert_called_with(Commands.INSTALL, '-c', 'tacaswell', 'geojson', use_exception_handler=False,
                                          stdout=None, stderr=None)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual("Running conda installation tasks...", po_call_args[0][0][0])
        self.assertIn("Warning: Packages installation ran into an error.", po_call_args[1][0][0])
        self.assertEqual("Running pip installation tasks...", po_call_args[2][0][0])
        self.assertEqual("Running application install....", po_call_args[3][0][0])
        self.assertEqual("Quiet mode: No additional service setting validation will be performed.",
                         po_call_args[4][0][0])
        self.assertEqual("Services Configuration Completed.", po_call_args[5][0][0])

        self.assertEqual(['pip', 'install', 'see'], mock_call.mock_calls[0][1][0])
        self.assertEqual(['python', 'setup.py', 'clean', '--all'], mock_call.mock_calls[1][1][0])
        self.assertEqual(['python', 'setup.py', 'install'], mock_call.mock_calls[2][1][0])
        self.assertEqual(['tethys', 'manage', 'sync'], mock_call.mock_calls[3][1][0])

        mock_exit.assert_called_with(0)

    @mock.patch('builtins.input', side_effect=['x', 5])
    @mock.patch('tethys_apps.cli.install_commands.get_app_settings')
    @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    def test_interactive_custom_setting_set(self, mock_pretty_output, mock_get_settings, _):
        mock_cs = mock.MagicMock()
        mock_cs.name = 'mock_cs'
        mock_cs.save.side_effect = [ValidationError('error'), mock.DEFAULT]
        mock_get_settings.return_value = {'unlinked_settings': [mock_cs]}

        install_commands.run_interactive_services('foo')

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn("Configuring mock_cs", po_call_args[2][0][0])
        self.assertIn("Type", po_call_args[3][0][0])
        self.assertIn("Enter the desired value", po_call_args[4][0][0])
        self.assertIn("Incorrect value type", po_call_args[5][0][0])
        self.assertIn("Enter the desired value", po_call_args[6][0][0])
        self.assertEqual(mock_cs.name + " successfully set with value: 5.", po_call_args[7][0][0])

    @mock.patch('builtins.input', side_effect=[''])
    @mock.patch('tethys_apps.cli.install_commands.get_app_settings')
    @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    def test_interactive_custom_setting_skip(self, mock_pretty_output, mock_get_settings, _):
        mock_cs = mock.MagicMock()
        mock_cs.name = 'mock_cs'
        mock_get_settings.return_value = {'unlinked_settings': [mock_cs]}

        install_commands.run_interactive_services('foo')

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn("Configuring mock_cs", po_call_args[2][0][0])
        self.assertIn("Type", po_call_args[3][0][0])
        self.assertIn("Enter the desired value", po_call_args[4][0][0])
        self.assertEqual(f"Skipping setup of {mock_cs.name}", po_call_args[5][0][0])

    @mock.patch('builtins.input', side_effect=KeyboardInterrupt)
    @mock.patch('tethys_apps.cli.install_commands.exit')
    @mock.patch('tethys_apps.cli.install_commands.get_app_settings')
    @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    def test_interactive_custom_setting_interrupt(self, mock_pretty_output, mock_get_settings, mock_exit, _):
        mock_cs = mock.MagicMock()
        mock_cs.name = 'mock_cs'
        mock_get_settings.return_value = {'unlinked_settings': [mock_cs]}

        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, install_commands.run_interactive_services, 'foo')

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn("Configuring mock_cs", po_call_args[2][0][0])
        self.assertIn("Type", po_call_args[3][0][0])
        self.assertIn("Enter the desired value", po_call_args[4][0][0])
        self.assertEqual("\nInstall Command cancelled.", po_call_args[5][0][0])

        mock_exit.assert_called_with(0)

    @mock.patch('builtins.input', side_effect=['1', '1', '', KeyboardInterrupt])
    @mock.patch('tethys_apps.cli.install_commands.get_setting_type', return_value='persistent')
    @mock.patch('tethys_apps.cli.install_commands.get_service_from_id', side_effect=ValueError)
    @mock.patch('tethys_apps.cli.install_commands.get_service_from_name', side_effect=[False, {'service_type': 'st',
                                                                                               'linkParam': 'lp'}])
    @mock.patch('tethys_apps.cli.install_commands.exit')
    @mock.patch('tethys_apps.cli.install_commands.services_list_command')
    @mock.patch('tethys_apps.cli.install_commands.get_app_settings')
    @mock.patch('tethys_apps.cli.install_commands.link_service_to_app_setting')
    @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    def test_interactive_service_setting_all(self, mock_pretty_output, mock_lstas, mock_get_settings, mock_slc,
                                             mock_exit, ____, ___, __, _):
        mock_ss = mock.MagicMock()
        del mock_ss.value
        mock_ss.name = 'mock_ss'
        mock_ss.save.side_effect = [ValidationError('error'), mock.DEFAULT]
        mock_get_settings.return_value = {'unlinked_settings': [mock_ss, mock_ss, mock_ss, mock_ss]}

        mock_s = mock.MagicMock()
        mock_slc.side_effect = [[[]], [[mock_s]], [[mock_s]], [[mock_s]]]

        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, install_commands.run_interactive_services, 'foo')

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn("Configuring mock_ss", po_call_args[2][0][0])
        self.assertIn("Type", po_call_args[3][0][0])
        self.assertIn("No compatible services found.", po_call_args[4][0][0])
        self.assertIn("Enter the service ID/Name", po_call_args[7][0][0])
        self.assertIn("Incorrect service ID/Name.", po_call_args[8][0][0])
        self.assertIn("Enter the service ID/Name", po_call_args[9][0][0])
        self.assertIn(f"Skipping setup of {mock_ss.name}", po_call_args[13][0][0])
        self.assertEqual("\nInstall Command cancelled.", po_call_args[17][0][0])

        mock_lstas.assert_called_with('st', '1', 'foo', 'lp', 'mock_ss')
        mock_exit.assert_called_with(0)

    def test_get_setting_type(self):
        from tethys_apps.models import PersistentStoreDatabaseSetting

        self.assertEqual('persistent', install_commands.get_setting_type(PersistentStoreDatabaseSetting()))
