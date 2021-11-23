import unittest
from unittest import mock
from django.core.exceptions import ObjectDoesNotExist
import tethys_cli.app_settings_commands as cli_app_settings_command
from tethys_sdk.testing import TethysTestCase


class TestCliAppSettingsCommand(unittest.TestCase):
    def setUp(self):
        load_apps_patcher = mock.patch('tethys_cli.app_settings_commands.load_apps')
        load_apps_patcher.start()
        self.addCleanup(load_apps_patcher.stop)

    def tearDown(self):
        pass

    @mock.patch('tethys_cli.app_settings_commands.get_setting_type', return_value='setting_type')
    @mock.patch('tethys_apps.models.TethysApp')
    @mock.patch('tethys_apps.models.PersistentStoreConnectionSetting')
    @mock.patch('tethys_apps.models.PersistentStoreDatabaseSetting')
    @mock.patch('tethys_apps.models.SpatialDatasetServiceSetting')
    @mock.patch('tethys_apps.models.DatasetServiceSetting')
    @mock.patch('tethys_apps.models.WebProcessingServiceSetting')
    @mock.patch('tethys_apps.models.CustomSetting')
    @mock.patch('tethys_cli.app_settings_commands.pretty_output')
    def test_app_settings_list_command_unlinked(self, mock_pretty_output, __, ___, ____, _____, ______,
                                                MockPscs, MockTethysApp, _):
        # mock the args
        mock_arg = mock.MagicMock(app='foo')

        mock_setting = mock.MagicMock(pk='pk')
        mock_setting.persistent_store_service.name = 'mock_ps'
        mock_setting.name = 'name'
        del mock_setting.persistent_store_service
        del mock_setting.spatial_dataset_service
        del mock_setting.dataset_service
        del mock_setting.web_processing_service
        del mock_setting.value

        # mock the PersistentStoreConnectionSetting filter return value
        MockPscs.objects.filter.return_value = [mock_setting]

        cli_app_settings_command.app_settings_list_command(mock_arg)

        MockTethysApp.objects.get(package='foo').return_value = mock_arg.app

        # check TethysApp.object.get method is called with app
        MockTethysApp.objects.get.assert_called_with(package='foo')

        # get the app name from mock_ta
        app = MockTethysApp.objects.get()

        # check PersistentStoreConnectionSetting.objects.filter method is called with 'app'
        MockPscs.objects.filter.assert_called_with(tethys_app=app)

        # get the called arguments from the mock print
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn('Unlinked Settings:', po_call_args[0][0][0])
        self.assertIn('Name', po_call_args[1][0][0])
        self.assertIn('pk', po_call_args[2][0][0])
        self.assertIn('Linked Settings:', po_call_args[3][0][0])
        self.assertIn('None', po_call_args[4][0][0])

    @mock.patch('tethys_cli.app_settings_commands.get_setting_type', return_value='setting_type')
    @mock.patch('tethys_apps.models.TethysApp')
    @mock.patch('tethys_apps.models.PersistentStoreConnectionSetting')
    @mock.patch('tethys_apps.models.PersistentStoreDatabaseSetting')
    @mock.patch('tethys_apps.models.SpatialDatasetServiceSetting')
    @mock.patch('tethys_apps.models.DatasetServiceSetting')
    @mock.patch('tethys_apps.models.WebProcessingServiceSetting')
    @mock.patch('tethys_apps.models.CustomSetting')
    @mock.patch('tethys_cli.app_settings_commands.pretty_output')
    @mock.patch('tethys_cli.app_settings_commands.type')
    def test_app_settings_list_command_linked(self, mock_type, mock_pretty_output, MockCs, MockWpss, MockDss,
                                              MockSdss, MockPsds, MockPscs, MockTethysApp, _):
        # mock the args
        mock_arg = mock.MagicMock(app='foo')

        # mock the PersistentStoreConnectionSetting filter return value
        pscs = MockPscs()
        pscs.name = 'n001'
        pscs.pk = 'p001'
        pscs.persistent_store_service.name = ''
        MockPscs.objects.filter.return_value = [pscs]

        # mock the PersistentStoreDatabaseSetting filter return value
        psds = MockPsds()
        psds.name = 'n002'
        psds.pk = 'p002'
        psds.persistent_store_service.name = ''
        # del psds.spatial_dataset_service
        MockPsds.objects.filter.return_value = [psds]

        # mock the Spatial Dataset ServiceSetting filter return value
        sdss = MockSdss()
        sdss.name = 'n003'
        sdss.pk = 'p003'
        sdss.spatial_dataset_service.name = ''
        del sdss.persistent_store_service
        MockSdss.objects.filter.return_value = [sdss]

        # mock the Dataset ServiceSetting filter return value
        dss = MockDss()
        dss.name = 'n004'
        dss.pk = 'p004'
        dss.dataset_service.name = ''
        del dss.persistent_store_service
        del dss.spatial_dataset_service
        MockDss.objects.filter.return_value = [dss]

        # mock the Web Processing ServiceSetting filter return value
        wpss = MockWpss()
        wpss.name = 'n005'
        wpss.pk = 'p005'
        wpss.web_processing_service.name = ''
        del wpss.persistent_store_service
        del wpss.spatial_dataset_service
        del wpss.dataset_service
        MockWpss.objects.filter.return_value = [wpss]

        # mock the Custom Setting filter return value
        cs = MockCs()
        cs.name = 'n006'
        cs.pk = 'p006'
        cs.value = '5'
        del cs.persistent_store_service
        del cs.spatial_dataset_service
        del cs.dataset_service
        del cs.web_processing_service
        MockCs.objects.filter.return_value = [cs]

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
        # check DatasetServiceSetting.objects.filter is called with 'app'
        MockDss.objects.filter.assert_called_with(tethys_app=app)
        # check WepProcessingServiceSetting.objects.filter is called with 'app'
        MockWpss.objects.filter.assert_called_with(tethys_app=app)
        # check CustomSetting.objects.filter is called with 'app'
        MockCs.objects.filter.assert_called_with(tethys_app=app)

        # get the called arguments from the mock print
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn('Unlinked Settings:', po_call_args[0][0][0])
        self.assertIn('None', po_call_args[1][0][0])
        self.assertIn('Linked Settings:', po_call_args[2][0][0])
        self.assertIn('Name', po_call_args[3][0][0])
        self.assertIn('n001', po_call_args[4][0][0])
        self.assertIn('n002', po_call_args[5][0][0])
        self.assertIn('n003', po_call_args[6][0][0])
        self.assertIn('n004', po_call_args[7][0][0])
        self.assertIn('n005', po_call_args[8][0][0])
        self.assertIn('n006', po_call_args[9][0][0])

    @mock.patch('tethys_apps.models.TethysApp')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    def test_app_settings_list_command_object_does_not_exist(self, mock_pretty_output, MockTethysApp):
        # mock the args
        mock_arg = mock.MagicMock(app='foo')
        MockTethysApp.objects.get.side_effect = ObjectDoesNotExist

        # raise ObjectDoesNotExist error
        cli_app_settings_command.app_settings_list_command(mock_arg)

        # get the called arguments from the mock print
        po_call_args = mock_pretty_output().__enter__().write.call_args_list

        self.assertIn('The app or extension you specified ("foo") does not exist. Command aborted.',
                      po_call_args[0][0][0])

    @mock.patch('tethys_apps.models.TethysApp')
    @mock.patch('tethys_cli.cli_colors.pretty_output')
    def test_app_settings_list_command_object_exception(self, mock_pretty_output, MockTethysApp):
        # mock the args
        mock_arg = mock.MagicMock(app='foo')

        MockTethysApp.objects.get.side_effect = Exception("error message")

        # raise ObjectDoesNotExist error
        cli_app_settings_command.app_settings_list_command(mock_arg)

        # get the called arguments from the mock print
        po_call_args = mock_pretty_output().__enter__().write.call_args_list

        self.assertIn('Something went wrong. Please try again', po_call_args[1][0][0])

    # @mock.patch('tethys_cli.app_settings_commands.create_ps_database_setting')
    @mock.patch('tethys_cli.app_settings_commands.exit')
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

    @mock.patch('tethys_cli.app_settings_commands.exit')
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

    @mock.patch('tethys_cli.app_settings_commands.exit')
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

    @mock.patch('tethys_cli.app_settings_commands.exit')
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

    def test_app_settings_get_setting_type(self):
        from tethys_apps.models import (PersistentStoreConnectionSetting, PersistentStoreDatabaseSetting,
                                        SpatialDatasetServiceSetting, DatasetServiceSetting,
                                        WebProcessingServiceSetting,
                                        CustomSetting)

        self.assertEqual('ps_connection', cli_app_settings_command.get_setting_type(PersistentStoreConnectionSetting()))
        self.assertEqual('ps_database', cli_app_settings_command.get_setting_type(PersistentStoreDatabaseSetting()))
        self.assertEqual('ds_spatial', cli_app_settings_command.get_setting_type(SpatialDatasetServiceSetting()))
        self.assertEqual('ds_dataset', cli_app_settings_command.get_setting_type(DatasetServiceSetting()))
        self.assertEqual('wps', cli_app_settings_command.get_setting_type(WebProcessingServiceSetting()))
        self.assertEqual('custom_setting', cli_app_settings_command.get_setting_type(CustomSetting()))


class TestCliAppSettingsCommandTethysTestCase(TethysTestCase):
    def set_up(self):
        pass

    def tear_down(self):
        pass

    @mock.patch('tethys_cli.app_settings_commands.write_success')
    @mock.patch('tethys_cli.app_settings_commands.write_error')
    @mock.patch('tethys_cli.app_settings_commands.exit', side_effect=SystemExit)
    def test_app_settings_set_str(self, mock_exit, mock_write_error, mock_write_success):
        """Test against the installed test app."""
        # String Custom Setting
        mock_args_str = mock.MagicMock(
            app='test_app',
            setting='default_name',
            value='foo'
        )

        self.assertRaises(SystemExit, cli_app_settings_command.app_settings_set_command, mock_args_str)
        mock_write_error.assert_not_called()
        mock_write_success.assert_called()
        mock_exit.called_with(0)

    @mock.patch('tethys_cli.app_settings_commands.write_success')
    @mock.patch('tethys_cli.app_settings_commands.write_error')
    @mock.patch('tethys_cli.app_settings_commands.exit', side_effect=SystemExit)
    def test_app_settings_set_int(self, mock_exit, mock_write_error, mock_write_success):
        """Test against the installed test app."""
        # Integer Custom Setting
        mock_args_int = mock.MagicMock(
            app='test_app',
            setting='max_count',
            value='1'
        )

        self.assertRaises(SystemExit, cli_app_settings_command.app_settings_set_command, mock_args_int)
        mock_write_error.assert_not_called()
        mock_write_success.assert_called()
        mock_exit.called_with(0)

    @mock.patch('tethys_cli.app_settings_commands.write_success')
    @mock.patch('tethys_cli.app_settings_commands.write_error')
    @mock.patch('tethys_cli.app_settings_commands.exit', side_effect=SystemExit)
    def test_app_settings_set_float(self, mock_exit, mock_write_error, mock_write_success):
        """Test against the installed test app."""
        # Float Custom Setting
        mock_args_float = mock.MagicMock(
            app='test_app',
            setting='change_factor',
            value='1.5'
        )

        self.assertRaises(SystemExit, cli_app_settings_command.app_settings_set_command, mock_args_float)
        mock_write_error.assert_not_called()
        mock_write_success.assert_called()
        mock_exit.called_with(0)

    @mock.patch('tethys_cli.app_settings_commands.write_success')
    @mock.patch('tethys_cli.app_settings_commands.write_error')
    @mock.patch('tethys_cli.app_settings_commands.exit', side_effect=SystemExit)
    def test_app_settings_set_bool(self, mock_exit, mock_write_error, mock_write_success):
        """Test against the installed test app."""
        # Boolean Custom Setting
        mock_args_bool = mock.MagicMock(
            app='test_app',
            setting='enable_feature',
            value='True'
        )

        self.assertRaises(SystemExit, cli_app_settings_command.app_settings_set_command, mock_args_bool)
        mock_write_error.assert_not_called()
        mock_write_success.assert_called()
        mock_exit.called_with(0)

    @mock.patch('tethys_cli.app_settings_commands.write_success')
    @mock.patch('tethys_cli.app_settings_commands.write_error')
    @mock.patch('tethys_cli.app_settings_commands.exit', side_effect=SystemExit)
    def test_app_settings_set_bad_value_int(self, mock_exit, mock_write_error, mock_write_success):
        """Test against the installed test app."""
        # Integer Custom Setting
        mock_args_int = mock.MagicMock(
            app='test_app',
            setting='max_count',
            value='1.5'  # Not int
        )

        self.assertRaises(SystemExit, cli_app_settings_command.app_settings_set_command, mock_args_int)
        mock_write_error.assert_called()
        mock_write_success.assert_not_called()
        mock_exit.assert_called_with(1)

    @mock.patch('tethys_cli.app_settings_commands.write_success')
    @mock.patch('tethys_cli.app_settings_commands.write_error')
    @mock.patch('tethys_cli.app_settings_commands.exit', side_effect=SystemExit)
    def test_app_settings_set_bad_value_float(self, mock_exit, mock_write_error, mock_write_success):
        """Test against the installed test app."""
        # Float Custom Setting
        mock_args_float = mock.MagicMock(
            app='test_app',
            setting='change_factor',
            value='foo'  # Not float
        )

        self.assertRaises(SystemExit, cli_app_settings_command.app_settings_set_command, mock_args_float)
        mock_write_error.assert_called()
        mock_write_success.assert_not_called()
        mock_exit.assert_called_with(1)

    @mock.patch('tethys_cli.app_settings_commands.write_success')
    @mock.patch('tethys_cli.app_settings_commands.write_error')
    @mock.patch('tethys_cli.app_settings_commands.exit', side_effect=SystemExit)
    def test_app_settings_set_bad_value_bool(self, mock_exit, mock_write_error, mock_write_success):
        """Test against the installed test app."""
        # Boolean Custom Setting
        mock_args_bool = mock.MagicMock(
            app='test_app',
            setting='enable_feature',
            value='foo'  # Not valid bool string
        )

        self.assertRaises(SystemExit, cli_app_settings_command.app_settings_set_command, mock_args_bool)
        mock_write_error.assert_called()
        mock_write_success.assert_not_called()
        mock_exit.assert_called_with(1)

    @mock.patch('tethys_cli.app_settings_commands.write_success')
    @mock.patch('tethys_cli.app_settings_commands.write_error')
    @mock.patch('tethys_cli.app_settings_commands.exit', side_effect=SystemExit)
    def test_app_settings_set_non_existant_setting(self, mock_exit, mock_write_error, mock_write_success):
        """Test against the installed test app."""
        # Boolean Custom Setting
        mock_args_bool = mock.MagicMock(
            app='test_app',
            setting='foo',  # Setting doesn't exist for test_app
            value='bar'
        )

        self.assertRaises(SystemExit, cli_app_settings_command.app_settings_set_command, mock_args_bool)
        mock_write_error.assert_called()
        mock_write_success.assert_not_called()
        mock_exit.assert_called_with(1)

    @mock.patch('tethys_cli.app_settings_commands.write_success')
    @mock.patch('tethys_cli.app_settings_commands.write_error')
    @mock.patch('tethys_cli.app_settings_commands.exit', side_effect=SystemExit)
    def test_app_settings_set_non_existant_app(self, mock_exit, mock_write_error, mock_write_success):
        """Test against the installed test app."""
        # Boolean Custom Setting
        mock_args_bool = mock.MagicMock(
            app='foo',  # App foo doesn't exist
            setting='enable_feature',
            value='bar'
        )

        self.assertRaises(SystemExit, cli_app_settings_command.app_settings_set_command, mock_args_bool)
        mock_write_error.assert_called()
        mock_write_success.assert_not_called()
        mock_exit.assert_called_with(1)

    @mock.patch('tethys_cli.app_settings_commands.write_success')
    @mock.patch('tethys_cli.app_settings_commands.write_error')
    @mock.patch('tethys_cli.app_settings_commands.exit', side_effect=SystemExit)
    def test_app_settings_reset_str(self, mock_exit, mock_write_error, mock_write_success):
        """Test against the installed test app."""
        # String Custom Setting
        mock_args_str = mock.MagicMock(
            app='test_app',
            setting='default_name',
        )

        self.assertRaises(SystemExit, cli_app_settings_command.app_settings_reset_command, mock_args_str)
        mock_write_error.assert_not_called()
        mock_write_success.assert_called()
        mock_exit.called_with(0)

    @mock.patch('tethys_cli.app_settings_commands.write_success')
    @mock.patch('tethys_cli.app_settings_commands.write_error')
    @mock.patch('tethys_cli.app_settings_commands.exit', side_effect=SystemExit)
    def test_app_settings_reset_int(self, mock_exit, mock_write_error, mock_write_success):
        """Test against the installed test app."""
        # Integer Custom Setting
        mock_args_int = mock.MagicMock(
            app='test_app',
            setting='max_count',
        )

        self.assertRaises(SystemExit, cli_app_settings_command.app_settings_reset_command, mock_args_int)
        mock_write_error.assert_not_called()
        mock_write_success.assert_called()
        mock_exit.called_with(0)

    @mock.patch('tethys_cli.app_settings_commands.write_success')
    @mock.patch('tethys_cli.app_settings_commands.write_error')
    @mock.patch('tethys_cli.app_settings_commands.exit', side_effect=SystemExit)
    def test_app_settings_reset_float(self, mock_exit, mock_write_error, mock_write_success):
        """Test against the installed test app."""
        # Float Custom Setting
        mock_args_float = mock.MagicMock(
            app='test_app',
            setting='change_factor',
        )

        self.assertRaises(SystemExit, cli_app_settings_command.app_settings_reset_command, mock_args_float)
        mock_write_error.assert_not_called()
        mock_write_success.assert_called()
        mock_exit.called_with(0)

    @mock.patch('tethys_cli.app_settings_commands.write_success')
    @mock.patch('tethys_cli.app_settings_commands.write_error')
    @mock.patch('tethys_cli.app_settings_commands.exit', side_effect=SystemExit)
    def test_app_settings_reset_bool(self, mock_exit, mock_write_error, mock_write_success):
        """Test against the installed test app."""
        # Boolean Custom Setting
        mock_args_bool = mock.MagicMock(
            app='test_app',
            setting='enable_feature',
        )

        self.assertRaises(SystemExit, cli_app_settings_command.app_settings_reset_command, mock_args_bool)
        mock_write_error.assert_not_called()
        mock_write_success.assert_called()
        mock_exit.called_with(0)

    @mock.patch('tethys_cli.app_settings_commands.write_success')
    @mock.patch('tethys_cli.app_settings_commands.write_error')
    @mock.patch('tethys_cli.app_settings_commands.exit', side_effect=SystemExit)
    def test_app_settings_reset_non_existant_setting(self, mock_exit, mock_write_error, mock_write_success):
        """Test against the installed test app."""
        # Boolean Custom Setting
        mock_args_bool = mock.MagicMock(
            app='test_app',
            setting='foo',  # Setting doesn't exist for test_app
        )

        self.assertRaises(SystemExit, cli_app_settings_command.app_settings_reset_command, mock_args_bool)
        mock_write_error.assert_called()
        mock_write_success.assert_not_called()
        mock_exit.assert_called_with(1)

    @mock.patch('tethys_cli.app_settings_commands.write_success')
    @mock.patch('tethys_cli.app_settings_commands.write_error')
    @mock.patch('tethys_cli.app_settings_commands.exit', side_effect=SystemExit)
    def test_app_settings_reset_non_existant_app(self, mock_exit, mock_write_error, mock_write_success):
        """Test against the installed test app."""
        # Boolean Custom Setting
        mock_args_bool = mock.MagicMock(
            app='foo',  # App foo doesn't exist
            setting='enable_feature',
        )

        self.assertRaises(SystemExit, cli_app_settings_command.app_settings_reset_command, mock_args_bool)
        mock_write_error.assert_called()
        mock_write_success.assert_not_called()
        mock_exit.assert_called_with(1)
