import os
import io
from subprocess import call, STDOUT
from django.test import TestCase
from unittest import mock
from conda.cli.python_api import Commands
from tethys_apps.cli import install_commands

FNULL = open(os.devnull, 'w')


class TestServiceInstallHelpers(TestCase):

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


# class TestInstallServicesCommands(TestCase):
#     def setUp(self):
#         self.src_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
#         self.root_app_path = os.path.join(self.src_dir, 'apps', 'tethysapp-test_app')
#
#         from tethys_services.models import (PersistentStoreService, WebProcessingService)
#         # Create test service
#         test_service_name = "test_service_for_install"
#         try:
#             PersistentStoreService.objects.get(name=test_service_name)
#         except Exception:
#             new_service = PersistentStoreService(name=test_service_name, host='localhost',
#                                                  port='1000', username='user', password='pass')
#             new_service.save()
#
#         test_service_name = "test_wps_for_install"
#
#         try:
#             WebProcessingService.objects.get(name=test_service_name)
#         except Exception:
#             new_service = WebProcessingService(
#                 name=test_service_name, endpoint='localhost', username='user', password='pass')
#             new_service.save()
#
#     def tearDown(self):
#
#         from tethys_services.models import (PersistentStoreService, WebProcessingService)
#         # Create test service
#         test_service_name = "test_service_for_install"
#         try:
#             service = PersistentStoreService.objects.get(name=test_service_name)
#             service.delete()
#         except Exception:
#             pass
#
#         test_service_name = "test_wps_for_install"
#         try:
#             service = WebProcessingService.objects.get(name=test_service_name)
#             service.delete()
#         except Exception:
#             pass
#
    # @mock.patch('tethys_apps.harvester.tethys_log')
    # @mock.patch('sys.stdout', new_callable=io.StringIO)
    # @mock.patch('tethys_apps.cli.install_commands.exit')
    # @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    # @mock.patch('tethys_apps.cli.install_commands.get_interactive_input', return_value='test_service_for_install')
    # @mock.patch('tethys_apps.cli.install_commands.get_service_name_input', return_value='primary')
    # @mock.patch('tethys_apps.cli.install_commands.link_service_to_app_setting')
    # def test_interactive_run(self, mock_link, mock_input, mock_input_2, mock_pretty_output, mock_exit, _, __):
    #     file_path = os.path.join(self.root_app_path, 'install-skip-setup.yml')
    #     services_path = os.path.join(self.root_app_path, 'services-basic.yml')
    #
    #     args = mock.MagicMock(file=file_path, services_file=services_path, verbose=False)
    #     mock_exit.side_effect = SystemExit
    #
    #     self.assertRaises(SystemExit, install_commands.install_command, args)
    #     po_call_args = mock_pretty_output().__enter__().write.call_args_list
    #     self.assertIn("Running Interactive Service Mode.", po_call_args[2][0][0])
    #     self.assertIn("Please enter the name of the service from your app.py", po_call_args[6][0][0])
    #     self.assertIn("Services Configuration Completed.", po_call_args[7][0][0])
    #     mock_link.assert_called_with('persistent', 'test_service_for_install', 'test_app', 'ps_database', 'primary')
    #
    #     mock_exit.assert_called_with(0)
    #
    # @mock.patch('tethys_apps.harvester.tethys_log')
    # @mock.patch('sys.stdout', new_callable=io.StringIO)
    # @mock.patch('tethys_apps.cli.install_commands.get_service_from_id', return_value=None)
    # @mock.patch('tethys_apps.cli.install_commands.exit')
    # @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    # @mock.patch('tethys_apps.cli.install_commands.get_interactive_input', return_value='1, 2')
    # def test_interactive_run_id(self, mock_input, mock_pretty_output, mock_exit, _, __, ___):
    #     file_path = os.path.join(self.root_app_path, 'install-skip-setup.yml')
    #     services_path = os.path.join(self.root_app_path, 'services-basic.yml')
    #
    #     args = mock.MagicMock(file=file_path, services_file=services_path, verbose=False)
    #     mock_exit.side_effect = SystemExit
    #
    #     self.assertRaises(SystemExit, install_commands.install_command, args)
    #     po_call_args = mock_pretty_output().__enter__().write.call_args_list
    #     self.assertIn("Running Interactive Service Mode.", po_call_args[2][0][0])
    #     self.assertIn("Services Configuration Completed.", po_call_args[6][0][0])
    #
    #     mock_exit.assert_called_with(0)
    #
    # @mock.patch('tethys_apps.harvester.tethys_log')
    # @mock.patch('sys.stdout', new_callable=io.StringIO)
    # @mock.patch('tethys_apps.cli.install_commands.exit')
    # @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    # @mock.patch('tethys_apps.cli.install_commands.get_interactive_input', return_value='')
    # def test_interactive_run_response_fail(self, mock_input, mock_pretty_output, mock_exit, _, __):
    #     file_path = os.path.join(self.root_app_path, 'install-skip-setup.yml')
    #     services_path = os.path.join(self.root_app_path, 'services-basic.yml')
    #
    #     args = mock.MagicMock(file=file_path, services_file=services_path, verbose=False)
    #     mock_exit.side_effect = SystemExit
    #
    #     self.assertRaises(SystemExit, install_commands.install_command, args)
    #
    #     po_call_args = mock_pretty_output().__enter__().write.call_args_list
    #     self.assertIn("Running Interactive Service Mode.", po_call_args[2][0][0])
    #     self.assertIn("Please run 'tethys services create -h' to create services via the command line.",
    #                   po_call_args[6][0][0])
    #     self.assertIn("Services Configuration Completed.", po_call_args[7][0][0])
    #
    #     mock_exit.assert_called_with(0)
    #
    # @mock.patch('tethys_apps.harvester.tethys_log')
    # @mock.patch('sys.stdout', new_callable=io.StringIO)
    # @mock.patch('tethys_apps.cli.install_commands.exit')
    # @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    # @mock.patch('tethys_apps.cli.install_commands.get_interactive_input', side_effect=KeyboardInterrupt)
    # def test_interactive_run_interrupt(self, mock_input, mock_pretty_output, mock_exit, _, __):
    #     file_path = os.path.join(self.root_app_path, 'install-skip-setup.yml')
    #     services_path = os.path.join(self.root_app_path, 'services-basic.yml')
    #
    #     args = mock.MagicMock(file=file_path, services_file=services_path, verbose=False)
    #     mock_exit.side_effect = SystemExit
    #
    #     self.assertRaises(SystemExit, install_commands.install_command, args)
    #
    #     po_call_args = mock_pretty_output().__enter__().write.call_args_list
    #     self.assertIn("Running Interactive Service Mode.", po_call_args[2][0][0])
    #     self.assertIn("Install Command cancelled.", po_call_args[6][0][0])
    #
    #     mock_exit.assert_called_with(0)
    #
    # @mock.patch('tethys_apps.harvester.tethys_log')
    # @mock.patch('sys.stdout', new_callable=io.StringIO)
    # @mock.patch('tethys_apps.cli.install_commands.exit')
    # @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    # @mock.patch('tethys_apps.cli.install_commands.link_service_to_app_setting')
    # def test_portal_run(self, mock_link, mock_pretty_output, mock_exit, _, __):
    #     file_path = os.path.join(self.root_app_path, 'install-skip-setup.yml')
    #     portal_config_file = os.path.join(self.root_app_path, '../../portal_config/portal_test.yml')
    #
    #     args = mock.MagicMock(file=file_path, portal_file=portal_config_file, services_file="", force_services=False,
    #                           verbose=False)
    #     mock_exit.side_effect = SystemExit
    #
    #     self.assertRaises(SystemExit, install_commands.install_command, args)
    #
    #     po_call_args = mock_pretty_output().__enter__().write.call_args_list
    #
    #     self.assertIn("Portal install file found...Processing...", po_call_args[2][0][0])
    #     mock_link.assert_called_with('persistent', 'test_service_for_install', 'test_app', 'ps_database', 'primary')
    #     mock_exit.assert_called_with(0)
    #
    # @mock.patch('tethys_apps.harvester.tethys_log')
    # @mock.patch('sys.stdout', new_callable=io.StringIO)
    # @mock.patch('tethys_apps.cli.install_commands.exit')
    # @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    # @mock.patch('tethys_apps.cli.install_commands.link_service_to_app_setting')
    # def test_portal_run_no_services(self, mock_link, mock_pretty_output, mock_exit, _, __):
    #     file_path = os.path.join(self.root_app_path, 'install-skip-setup.yml')
    #     portal_config_file = os.path.join(self.root_app_path, '../../portal_config/portal_test_no_services.yml')
    #
    #     args = mock.MagicMock(file=file_path, portal_file=portal_config_file, services_file="", force_services=False,
    #                           verbose=False)
    #     mock_exit.side_effect = SystemExit
    #
    #     self.assertRaises(SystemExit, install_commands.install_command, args)
    #
    #     po_call_args = mock_pretty_output().__enter__().write.call_args_list
    #     self.assertIn("Portal install file found...Processing...", po_call_args[2][0][0])
    #     self.assertIn("No app configuration found for app:", po_call_args[3][0][0])
    #     mock_exit.assert_called_with(0)
    #
    # @mock.patch('tethys_apps.harvester.tethys_log')
    # @mock.patch('sys.stdout', new_callable=io.StringIO)
    # @mock.patch('tethys_apps.cli.install_commands.exit')
    # @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    # def test_portal_run_no_apps(self, mock_pretty_output, mock_exit, _, __):
    #     file_path = os.path.join(self.root_app_path, 'install-skip-setup.yml')
    #     portal_config_file = os.path.join(self.root_app_path, '../../portal_config/portal_test_no_apps.yml')
    #
    #     args = mock.MagicMock(file=file_path, portal_file=portal_config_file, services_file="", force_services=False,
    #                           verbose=False)
    #     mock_exit.side_effect = SystemExit
    #
    #     self.assertRaises(SystemExit, install_commands.install_command, args)
    #
    #     po_call_args = mock_pretty_output().__enter__().write.call_args_list
    #
    #     self.assertIn("Portal install file found...Processing...", po_call_args[2][0][0])
    #     self.assertIn("No apps configuration found in portal config file.", po_call_args[3][0][0])
    #     mock_exit.assert_called_with(0)
    #
    # @mock.patch('tethys_apps.harvester.tethys_log')
    # @mock.patch('sys.stdout', new_callable=io.StringIO)
    # @mock.patch('tethys_apps.cli.install_commands.exit')
    # @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    # def test_portal_run_no_service_link(self, mock_pretty_output, mock_exit, _, __):
    #     file_path = os.path.join(self.root_app_path, 'install-skip-setup.yml')
    #     portal_config_file = os.path.join(self.root_app_path, '../../portal_config/portal_test_no_service.yml')
    #
    #     args = mock.MagicMock(file=file_path, portal_file=portal_config_file, services_file="", force_services=False,
    #                           verbose=False)
    #     mock_exit.side_effect = SystemExit
    #
    #     self.assertRaises(SystemExit, install_commands.install_command, args)
    #
    #     po_call_args = mock_pretty_output().__enter__().write.call_args_list
    #
    #     self.assertIn("Portal install file found...Processing...", po_call_args[2][0][0])
    #     self.assertIn("Warning: Could not find service of type:", po_call_args[3][0][0])
    #     mock_exit.assert_called_with(0)
    #
    # @mock.patch('tethys_apps.harvester.tethys_log')
    # @mock.patch('sys.stdout', new_callable=io.StringIO)
    # @mock.patch('tethys_apps.cli.install_commands.exit')
    # @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    # def test_portal_run_no_portal_file(self, mock_pretty_output, mock_exit, _, __):
    #     file_path = os.path.join(self.root_app_path, 'install-skip-setup.yml')
    #     args = mock.MagicMock(file=file_path, portal_file=None, services_file="", force_services=False, verbose=False)
    #     mock_exit.side_effect = SystemExit
    #
    #     self.assertRaises(SystemExit, install_commands.install_command, args)
    #
    #     po_call_args = mock_pretty_output().__enter__().write.call_args_list
    #     self.assertIn("No Portal Services file found.", po_call_args[2][0][0])
    #     mock_exit.assert_called_with(0)
    #
    # @mock.patch('tethys_apps.harvester.tethys_log')
    # @mock.patch('sys.stdout', new_callable=io.StringIO)
    # @mock.patch('builtins.open', side_effect=IOError())
    # @mock.patch('tethys_apps.cli.install_commands.exit')
    # @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    # def test_portal_run_portal_file_exception(self, mock_pretty_output, mock_exit, mock_open, _, __):
    #     file_path = os.path.join(self.root_app_path, 'install-skip-setup.yml')
    #     portal_config_file = os.path.join(self.root_app_path, '../../portal_config/portal_test_no_service.yml')
    #
    #     args = mock.MagicMock(file=file_path, portal_file=portal_config_file, services_file="", force_services=False,
    #                           verbose=False)
    #     mock_open.raiseError.side_effect = mock.MagicMock(side_effect=Exception('test'))
    #     mock_exit.side_effect = SystemExit
    #
    #     self.assertRaises(SystemExit, install_commands.install_command, args)
    #     po_call_args = mock_pretty_output().__enter__().write.call_args_list
    #     self.assertIn("An unexpected error occurred reading the file.", po_call_args[1][0][0])
    #     mock_exit.assert_called_with(1)
    #
    # @mock.patch('tethys_apps.cli.install_commands.call')
    # @mock.patch('tethys_apps.harvester.tethys_log')
    # @mock.patch('sys.stdout', new_callable=io.StringIO)
    # @mock.patch('tethys_apps.cli.install_commands.exit')
    # @mock.patch('tethys_apps.cli.install_commands.link_service_to_app_setting')
    # def test_basic_service(self, mock_link, mock_exit, _, __, ___):
    #     file_path = os.path.join(self.root_app_path, 'install-skip-setup.yml')
    #     services_path = os.path.join(self.root_app_path, 'services-basic.yml')
    #     args = mock.MagicMock(file=file_path, services_file="", verbose=False)
    #
    #     try:
    #         import tethysapp.test_app  # noqa: F401
    #         # Do a sync to ensure that the application's custom setting has been added
    #         call(['tethys', 'manage', 'syncdb'], stdout=FNULL, stderr=STDOUT)
    #     except ImportError:
    #         install_commands.install_command(args)
    #
    #     from tethys_services.models import PersistentStoreService
    #     # Create test service
    #     test_service_name = "test_persistent_install"
    #     try:
    #         PersistentStoreService.objects.get(name=test_service_name)
    #     except Exception:
    #         new_service = PersistentStoreService(name=test_service_name, host='localhost',
    #                                              port='1000', username='user', password='pass')
    #         new_service.save()
    #
    #     mock_exit.side_effect = SystemExit
    #
    #     args = mock.MagicMock(file=file_path, services_file=services_path, verbose=False)
    #
    #     self.assertRaises(SystemExit, install_commands.install_command, args)
    #
    #     mock_link.assert_called_with('persistent', test_service_name, 'test_app', 'ps_database', 'temp_db')
    #
    #     mock_exit.assert_called_with(0)
    #
    # @mock.patch('tethys_apps.cli.install_commands.call')
    # @mock.patch('tethys_apps.harvester.tethys_log')
    # @mock.patch('sys.stdout', new_callable=io.StringIO)
    # @mock.patch('tethys_apps.cli.install_commands.exit')
    # @mock.patch('tethys_apps.cli.install_commands.link_service_to_app_setting')
    # @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    # def test_service_skip(self, mock_pretty_output, mock_link, mock_exit):
    #     file_path = os.path.join(self.root_app_path, 'install-skip-setup.yml')
    #     services_path = os.path.join(self.root_app_path, 'services-skip.yml')
    #
    #     mock_exit.side_effect = SystemExit
    #
    #     args = mock.MagicMock(file=file_path, services_file=services_path, verbose=False)
    #
    #     self.assertRaises(SystemExit, install_commands.install_command, args)
    #
    #     po_call_args = mock_pretty_output().__enter__().write.call_args_list
    #     self.assertIn("Skipping services configuration, Skip option found.", po_call_args[2][0][0])
    #
    #     mock_exit.assert_called_with(0)


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

    @mock.patch('tethys_apps.cli.install_commands.call')
    @mock.patch('tethys_apps.cli.install_commands.exit')
    @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    def test_no_conda_input_file(self, mock_pretty_output, mock_exit, _):
        file_path = os.path.join(self.root_app_path, 'install-no-dep.yml')
        args = mock.MagicMock(file=file_path, verbose=False, services_file=None)
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, install_commands.install_command, args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn("Running application install....", po_call_args[0][0][0])
        self.assertIn("No Services file found.", po_call_args[1][0][0])
        self.assertIn("Quiet mode: No additional service setting validation will be performed.", po_call_args[2][0][0])
        self.assertIn("Services Configuration Completed.", po_call_args[3][0][0])
        self.assertIn("Skipping syncstores.", po_call_args[4][0][0])
        mock_exit.assert_called_with(0)

    # @mock.patch('tethys_apps.cli.install_commands.call')
    # @mock.patch('tethys_apps.cli.install_commands.exit')
    # @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    # def test_skip_dep_input_file(self, mock_pretty_output, mock_exit, _):
    #     file_path = os.path.join(self.root_app_path, 'install-skip-setup.yml')
    #     args = mock.MagicMock(file=file_path, services_file=None, verbose=False)
    #     mock_exit.side_effect = SystemExit
    #
    #     self.assertRaises(SystemExit, install_commands.install_command, args)
    #
    #     po_call_args = mock_pretty_output().__enter__().write.call_args_list
    #     self.assertIn("Skipping package installation, Skip option found.", po_call_args[0][0][0])
    #     self.assertIn("Running application install....", po_call_args[1][0][0])
    #     self.assertIn("No Services file found.", po_call_args[2][0][0])
    #
    #     mock_exit.assert_called_with(0)
    #
    # @mock.patch('tethys_apps.cli.install_commands.exit')
    # @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    # def test_post_command(self, mock_pretty_output, mock_exit):
    #     file_path = os.path.join(self.root_app_path, 'install-with-post.yml')
    #     args = mock.MagicMock(file=file_path, services_file="", verbose=False)
    #     mock_exit.side_effect = SystemExit
    #
    #     self.assertRaises(SystemExit, install_commands.install_command, args)
    #
    #     po_call_args = mock_pretty_output().__enter__().write.call_args_list
    #     self.assertIn("Running application install....", po_call_args[1][0][0])
    #     self.assertIn("No Services install file found. Skipping app service installation", po_call_args[2][0][0])
    #     self.assertIn("Running post installation tasks...", po_call_args[3][0][0])
    #     self.assertIn("Post Script Result: b'test\\n'", po_call_args[4][0][0])
    #
    #     mock_exit.assert_called_with(0)
    #
    # @mock.patch('tethys_apps.cli.install_commands.exit')
    # @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    # def test_install_clean(self, mock_pretty_output, mock_exit):
    #
    #     try:
    #         import tethysapp.test_app  # noqa: F401
    #         # If import succeeds, we have an instance of the app. Clean it out
    #         subprocess.call(['tethys', 'uninstall', 'test_app', '-f'], stdout=FNULL, stderr=subprocess.STDOUT)
    #     except ImportError:
    #         pass
    #
    #     file_path = os.path.join(self.root_app_path, 'install-skip-setup.yml')
    #     args = mock.MagicMock(file=file_path, services_file="", verbose=False)
    #     mock_exit.side_effect = SystemExit
    #
    #     self.assertRaises(SystemExit, install_commands.install_command, args)
    #
    #     po_call_args = mock_pretty_output().__enter__().write.call_args_list
    #     self.assertIn("Running application install....", po_call_args[1][0][0])
    #
    #     try:
    #         import tethysapp.test_app  # noqa: F401, F811
    #     except ImportError:
    #         self.fail("We should be able to import tethys application")
    #
    #     mock_exit.assert_called_with(0)
    #
    # @mock.patch('tethys_apps.cli.install_commands.run_services')
    # @mock.patch('tethys_apps.cli.install_commands.call')
    # @mock.patch('tethys_apps.cli.install_commands.conda_run', return_value=['', '', 1])
    # @mock.patch('tethys_apps.cli.install_commands.exit')
    # @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    # def test_dependencies_and_pip(self, mock_pretty_output, mock_exit, mock_conda_run, mock_call, _):
    #     file_path = os.path.join(self.root_app_path, 'install-dep.yml')
    #     args = mock.MagicMock(file=file_path, develop=True, verbose=False)
    #     mock_exit.side_effect = SystemExit
    #
    #     self.assertRaises(SystemExit, install_commands.install_command, args)
    #
    #     mock_conda_run.assert_called_with(Commands.INSTALL, '-c', 'tacaswell', 'geojson', use_exception_handler=False,
    #                                       stdout=None, stderr=None)
    #     mock_call.assert_called()
    #     po_call_args = mock_pretty_output().__enter__().write.call_args_list
    #     self.assertIn("Installing Dependencies.....", po_call_args[0][0][0])
    #     self.assertIn("Warning: Dependencies installation ran into an error.", po_call_args[1][0][0])
    #     self.assertIn("Running pip installation tasks...", po_call_args[2][0][0])
    #     mock_exit.assert_called_with(0)
    #

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

    @mock.patch('builtins.input', side_effect=[5])
    @mock.patch('tethys_apps.cli.install_commands.get_app_settings')
    @mock.patch('tethys_apps.cli.cli_colors.pretty_output')
    def test_interactive_custom_setting_set(self, mock_pretty_output, mock_get_settings, _):
        mock_cs = mock.MagicMock()
        mock_cs.name = 'mock_cs'
        mock_get_settings.return_value = {'unlinked_settings': [mock_cs]}

        install_commands.run_interactive_services('foo')

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn("Configuring mock_cs", po_call_args[2][0][0])
        self.assertIn("Type", po_call_args[3][0][0])
        self.assertIn("Enter the desired value", po_call_args[4][0][0])
        self.assertEqual(mock_cs.name + " successfully set with value: 5.", po_call_args[5][0][0])

    def test_interactive_custom_setting_skip(self):
        pass

    def test_interactive_custom_setting_interrupt(self):
        pass

