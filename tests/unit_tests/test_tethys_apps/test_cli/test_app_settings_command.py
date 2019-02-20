import unittest
from unittest import mock
from django.core.exceptions import ObjectDoesNotExist
import tethys_apps.cli.app_settings_commands as cli_app_settings_command


class TestCliAppSettingsCommand(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_apps.models.TethysApp')
    @mock.patch('tethys_apps.models.PersistentStoreConnectionSetting')
    @mock.patch('tethys_apps.models.PersistentStoreDatabaseSetting')
    @mock.patch('tethys_apps.models.SpatialDatasetServiceSetting')
    @mock.patch('tethys_apps.cli.app_settings_commands.pretty_output')
    def test_app_settings_list_command(self, mock_pretty_output, MockSdss, MockPsds, MockPscs, MockTethysApp):
        # mock the args
        mock_arg = mock.MagicMock(app='foo')

        # mock the PersistentStoreConnectionSetting filter return value
        MockPscs.objects.filter.return_value = [mock.MagicMock()]
        # mock the PersistentStoreDatabaseSetting filter return value
        MockPsds.objects.filter.return_value = [mock.MagicMock()]
        # mock the SpatialDatasetServiceSetting filter return value
        MockSdss.objects.filter.return_value = [mock.MagicMock()]

        cli_app_settings_command.app_settings_list_command(mock_arg)

        MockTethysApp.objects.get(package='foo').return_value = mock_arg.app

        # check TethysApp.object.get method is called with app
        MockTethysApp.objects.get.assert_called_with(package='foo')

        # get the app name from mock_ta
        app = MockTethysApp.objects.get()

        # check PersistentStoreConnectionSetting.objects.filter method is called with 'app'
        MockPscs.objects.filter.assert_called_with(tethys_app=app)
        # check PersistentStoreDatabaseSetting.objects.filter method is called with 'app'
        MockPsds.objects.filter.assert_called_with(tethys_app=app)
        # check SpatialDatasetServiceSetting.objects.filter is called with 'app'
        MockSdss.objects.filter.assert_called_with(tethys_app=app)

        # get the called arguments from the mock print
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn('Unlinked Settings:', po_call_args[0][0][0])
        self.assertIn('None', po_call_args[1][0][0])
        self.assertIn('Linked Settings:', po_call_args[2][0][0])
        self.assertIn('Name', po_call_args[3][0][0])

    @mock.patch('tethys_apps.models.TethysApp')
    @mock.patch('tethys_apps.models.PersistentStoreConnectionSetting')
    @mock.patch('tethys_apps.models.PersistentStoreDatabaseSetting')
    @mock.patch('tethys_apps.models.SpatialDatasetServiceSetting')
    @mock.patch('tethys_apps.cli.app_settings_commands.pretty_output')
    @mock.patch('tethys_apps.cli.app_settings_commands.type')
    def test_app_settings_list_command_unlink_settings(self, mock_type, mock_pretty_output, MockSdss, MockPsds,
                                                       MockPscs, MockTethysApp):
        # mock the args
        mock_arg = mock.MagicMock(app='foo')

        # mock the PersistentStoreConnectionSetting filter return value
        pscs = MockPscs()
        pscs.name = 'n001'
        pscs.pk = 'p001'
        pscs.persistent_store_service = ''
        del pscs.spatial_dataset_service
        MockPscs.objects.filter.return_value = [pscs]

        # mock the PersistentStoreDatabaseSetting filter return value
        psds = MockPsds()
        psds.name = 'n002'
        psds.pk = 'p002'
        psds.persistent_store_service = ''
        del psds.spatial_dataset_service
        MockPsds.objects.filter.return_value = [psds]

        # mock the Spatial Dataset ServiceSetting filter return value
        sdss = MockSdss()
        sdss.name = 'n003'
        sdss.pk = 'p003'
        sdss.spatial_dataset_service = ''
        del sdss.persistent_store_service
        MockSdss.objects.filter.return_value = [sdss]

        MockTethysApp.objects.get(package='foo').return_value = mock_arg.app

        def mock_type_func(obj):
            if obj is pscs:
                return MockPscs
            elif obj is psds:
                return MockPsds
            elif obj is sdss:
                return MockSdss

        mock_type.side_effect = mock_type_func

        cli_app_settings_command.app_settings_list_command(mock_arg)

        # check TethysApp.object.get method is called with app
        MockTethysApp.objects.get.assert_called_with(package='foo')

        # get the app name from mock_ta
        app = MockTethysApp.objects.get()

        # check PersistentStoreConnectionSetting.objects.filter method is called with 'app'
        MockPscs.objects.filter.assert_called_with(tethys_app=app)
        # check PersistentStoreDatabaseSetting.objects.filter method is called with 'app'
        MockPsds.objects.filter.assert_called_with(tethys_app=app)
        # check SpatialDatasetServiceSetting.objects.filter is called with 'app'
        MockSdss.objects.filter.assert_called_with(tethys_app=app)

        # get the called arguments from the mock print
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn('Unlinked Settings:', po_call_args[0][0][0])
        self.assertIn('ID', po_call_args[1][0][0])
        self.assertIn('n001', po_call_args[2][0][0])
        self.assertIn('n002', po_call_args[3][0][0])
        self.assertIn('n003', po_call_args[4][0][0])
        self.assertIn('n003', po_call_args[4][0][0])
        self.assertIn('Linked Settings:', po_call_args[5][0][0])
        self.assertIn('None', po_call_args[6][0][0])

    @mock.patch('tethys_apps.models.TethysApp')
    @mock.patch('tethys_apps.cli.app_settings_commands.pretty_output')
    def test_app_settings_list_command_object_does_not_exist(self, mock_pretty_output, MockTethysApp):
        # mock the args
        mock_arg = mock.MagicMock(app='foo')
        MockTethysApp.objects.get.side_effect = ObjectDoesNotExist

        # raise ObjectDoesNotExist error
        cli_app_settings_command.app_settings_list_command(mock_arg)

        # get the called arguments from the mock print
        po_call_args = mock_pretty_output().__enter__().write.call_args_list

        self.assertIn('The app you specified ("foo") does not exist. Command aborted.', po_call_args[0][0][0])

    @mock.patch('tethys_apps.models.TethysApp')
    @mock.patch('tethys_apps.cli.app_settings_commands.pretty_output')
    def test_app_settings_list_command_object_exception(self, mock_pretty_output, MockTethysApp):
        # mock the args
        mock_arg = mock.MagicMock(app='foo')

        MockTethysApp.objects.get.side_effect = Exception

        # raise ObjectDoesNotExist error
        cli_app_settings_command.app_settings_list_command(mock_arg)

        # get the called arguments from the mock print
        po_call_args = mock_pretty_output().__enter__().write.call_args_list

        self.assertIn('Something went wrong. Please try again', po_call_args[1][0][0])

    # @mock.patch('tethys_apps.cli.app_settings_commands.create_ps_database_setting')
    @mock.patch('tethys_apps.cli.app_settings_commands.exit')
    @mock.patch('tethys_apps.utilities.create_ps_database_setting')
    def test_app_settings_create_ps_database_command(self, mock_database_settings, mock_exit):
        # mock the args
        mock_arg = mock.MagicMock(app='foo')
        mock_arg.name = 'arg_name'
        mock_arg.description = 'mock_description'
        mock_arg.required = True
        mock_arg.initializer = ''
        mock_arg.initialized = 'initialized'
        mock_arg.spatial = 'spatial'
        mock_arg.dynamic = 'dynamic'

        # mock the system exit
        mock_exit.side_effect = SystemExit

        # raise the system exit call when database is created
        self.assertRaises(SystemExit, cli_app_settings_command.app_settings_create_ps_database_command, mock_arg)

        # check the call arguments from mock_database
        mock_database_settings.assert_called_with('foo', 'arg_name', 'mock_description', True, '',
                                                  'initialized', 'spatial', 'dynamic')
        # check the mock exit value
        mock_exit.assert_called_with(0)

    @mock.patch('tethys_apps.cli.app_settings_commands.exit')
    @mock.patch('tethys_apps.utilities.create_ps_database_setting')
    def test_app_settings_create_ps_database_command_with_no_success(self, mock_database_settings, mock_exit):

        # mock the args
        mock_arg = mock.MagicMock(app='foo')
        mock_arg.name = None
        mock_arg.description = 'mock_description'
        mock_arg.required = True
        mock_arg.initializer = ''
        mock_arg.initialized = 'initialized'
        mock_arg.spatial = 'spatial'
        mock_arg.dynamic = 'dynamic'

        # mock the system exit
        mock_exit.side_effect = SystemExit

        mock_database_settings.return_value = False

        # raise the system exit call when database is created
        self.assertRaises(SystemExit, cli_app_settings_command.app_settings_create_ps_database_command, mock_arg)

        # check the mock exit value
        mock_exit.assert_called_with(1)

    @mock.patch('tethys_apps.cli.app_settings_commands.exit')
    @mock.patch('tethys_apps.utilities.remove_ps_database_setting')
    def test_app_settings_remove_command(self, mock_database_settings, mock_exit):
        # mock the args
        mock_arg = mock.MagicMock(app='foo')
        mock_arg.name = 'arg_name'
        mock_arg.force = 'force'

        # mock the system exit
        mock_exit.side_effect = SystemExit

        # raise the system exit call when database is created
        self.assertRaises(SystemExit, cli_app_settings_command.app_settings_remove_command, mock_arg)

        # check the call arguments from mock_database
        mock_database_settings.assert_called_with('foo', 'arg_name', 'force')

        # check the mock exit value
        mock_exit.assert_called_with(0)

    @mock.patch('tethys_apps.cli.app_settings_commands.exit')
    @mock.patch('tethys_apps.utilities.remove_ps_database_setting')
    def test_app_settings_remove_command_with_no_success(self, mock_database_settings, mock_exit):
        # mock the args
        mock_arg = mock.MagicMock(app='foo')
        mock_arg.name = 'arg_name'
        mock_arg.force = 'force'

        # mock the system exit
        mock_exit.side_effect = SystemExit

        mock_database_settings.return_value = False

        # raise the system exit call when database is created
        self.assertRaises(SystemExit, cli_app_settings_command.app_settings_remove_command, mock_arg)

        # check the mock exit value
        mock_exit.assert_called_with(1)
