try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO  # noqa: F401
import unittest
from unittest import mock

from tethys_cli.services_commands import (
    services_create_persistent_command,
    services_remove_persistent_command,
    services_create_spatial_command,
    services_remove_spatial_command,
    services_list_command,
    services_create_dataset_command,
    services_remove_dataset_command,
    services_create_wps_command,
    services_remove_wps_command
)
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError


class ServicesCommandsTest(unittest.TestCase):
    """
    Tests for tethys_cli.services_commands
    """

    # Dictionary used in some of the tests
    my_dict = {'id': 'Id_foo', 'name': 'Name_foo', 'host': 'Host_foo', 'port': 'Port_foo', 'endpoint': 'EndPoint_foo',
               'public_endpoint': 'PublicEndPoint_bar', 'apikey': 'APIKey_foo'}

    def setUp(self):
        load_apps_patcher = mock.patch('tethys_cli.services_commands.load_apps')
        load_apps_patcher.start()
        self.addCleanup(load_apps_patcher.stop)

    def tearDown(self):
        pass

    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.PersistentStoreService')
    def test_services_create_persistent_command(self, mock_service, mock_pretty_output):
        """
        Test for services_create_persistent_command.
        For running the test without any errors or problems.
        :param mock_service:  mock for PersistentStoreService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock()
        services_create_persistent_command(mock_args)
        mock_service.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual('Successfully created new Persistent Store Service!', po_call_args[0][0][0])

    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.PersistentStoreService')
    def test_services_create_persistent_command_exception_attributeerror(self, mock_service, mock_pretty_output):
        """
        Test for services_create_persistent_command.
        For running the test with an IndexError exception thrown.
        :param mock_service:  mock for PersistentStoreService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock()
        mock_args.connection = AttributeError
        services_create_persistent_command(mock_args)

        mock_service.assert_not_called()
        mock_service.objects.get().save.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('Missing Input Parameters. Please check your input.', po_call_args[0][0][0])

    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.PersistentStoreService')
    def test_services_create_persistent_command_exception_indexerror(self, mock_service, mock_pretty_output):
        """
        Test for services_create_persistent_command.
        For running the test with an IndexError exception thrown.
        :param mock_service:  mock for PersistentStoreService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock()
        mock_service.side_effect = IndexError
        services_create_persistent_command(mock_args)

        mock_service.assert_called()
        mock_service.objects.get().save.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('The connection argument (-c) must be of the form', po_call_args[0][0][0])

    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.PersistentStoreService')
    def test_services_create_persistent_command_exception_integrityerror(self, mock_service, mock_pretty_output):
        """
        Test for services_create_persistent_command.
        For running the test with an IntegrityError exception thrown.
        :param mock_service:  mock for PersistentStoreService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock()
        mock_service.side_effect = IntegrityError
        services_create_persistent_command(mock_args)

        mock_service.assert_called()
        mock_service.objects.get().save.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('Persistent Store Service with name', po_call_args[0][0][0])
        self.assertIn('already exists. Command aborted.', po_call_args[0][0][0])

    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_cli.services_commands.exit')
    @mock.patch('tethys_services.models.PersistentStoreService')
    def test_services_remove_persistent_command_Exceptions(self, mock_service, mock_exit, mock_pretty_output):
        """
        Test for services_remove_persistent_command
        Test for handling all exceptions thrown by the function.
        :param mock_service:  mock for PersistentStoreService
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output: mock for pretty_output text
        :return:
        """

        mock_args = mock.MagicMock()
        mock_service.__str__.return_value = 'Persistent Store'
        mock_args.force = True
        mock_service.objects.get.side_effect = [ValueError, ObjectDoesNotExist]
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, services_remove_persistent_command, mock_args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('A Persistent Store Service with ID/Name', po_call_args[0][0][0])
        self.assertIn('does not exist', po_call_args[0][0][0])

    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_cli.services_commands.exit')
    @mock.patch('tethys_services.models.PersistentStoreService')
    def test_services_remove_persistent_command_force(self, mock_service, mock_exit, mock_pretty_output):
        """
        Test for services_remove_persistent_command
        Test for forcing a delete of the service
        :param mock_service:  mock for PersistentStoreService
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output: mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock()
        mock_args.force = True
        mock_service.__str__.return_value = 'Persistent Store'

        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, services_remove_persistent_command, mock_args)

        mock_service.objects.get().delete.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('Successfully removed Persistent Store Service', po_call_args[0][0][0])

    @mock.patch('tethys_cli.services_commands.input')
    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_cli.services_commands.exit')
    @mock.patch('tethys_services.models.PersistentStoreService')
    def test_services_remove_persistent_command_no_proceed_invalid_char(self, mock_service, mock_exit,
                                                                        mock_pretty_output, mock_input):
        """
        Test for services_remove_persistent_command
        Handles answering the prompt to delete with invalid characters, and answering no.
        :param mock_service:  mock for PersistentStoreService
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output:  mock for pretty_output text
        :param mock_input:  mock for handling raw_input requests
        :return:
        """
        mock_args = mock.MagicMock()
        mock_args.force = False
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit
        mock_input.side_effect = ['foo', 'N']
        mock_service.__str__.return_value = 'Persistent Store'

        self.assertRaises(SystemExit, services_remove_persistent_command, mock_args)

        mock_service.objects.get().delete.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual('Aborted. Persistent Store Service not removed.', po_call_args[0][0][0])

        po_call_args = mock_input.call_args_list
        self.assertEqual(2, len(po_call_args))
        self.assertEqual(
            'Are you sure you want to delete this Persistent Store Service? [y/n]: ', po_call_args[0][0][0])
        self.assertEqual('Please enter either "y" or "n": ', po_call_args[1][0][0])

    @mock.patch('tethys_cli.services_commands.input')
    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_cli.services_commands.exit')
    @mock.patch('tethys_services.models.PersistentStoreService')
    def test_services_remove_persistent_command_proceed(self, mock_service, mock_exit, mock_pretty_output, mock_input):
        """
        Test for services_remove_persistent_command
        Handles answering the prompt to delete with invalid characters by answering yes
        :param mock_service:  mock for PersistentStoreService
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output:  mock for pretty_output text
        :param mock_input:  mock for handling raw_input requests
        :return:
        """
        mock_args = mock.MagicMock()
        mock_service.__str__.return_value = 'Persistent Store'
        mock_args.force = False
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit
        mock_input.side_effect = ['y']

        self.assertRaises(SystemExit, services_remove_persistent_command, mock_args)

        mock_service.objects.get().delete.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('Successfully removed Persistent Store Service', po_call_args[0][0][0])

        po_call_args = mock_input.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual(
            'Are you sure you want to delete this Persistent Store Service? [y/n]: ', po_call_args[0][0][0])

    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.SpatialDatasetService')
    def test_services_create_spatial_command_IndexError(self, mock_service, mock_pretty_output):
        """
        Test for services_create_spatial_command
        Handles an IndexError exception
        :param mock_service:  mock for SpatialDatasetService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock()
        mock_args.connection = 'IndexError:9876@IndexError'  # No 'http' or '://'
        mock_args.type = 'GeoServer'

        services_create_spatial_command(mock_args)

        mock_service.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('The connection argument (-c) must be of the form', po_call_args[0][0][0])
        self.assertIn('"<username>:<password>@<protocol>//<host>:<port>".', po_call_args[0][0][0])

    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.SpatialDatasetService')
    def test_services_create_spatial_command_FormatError(self, mock_service, mock_pretty_output):
        """
        Test for services_create_spatial_command
        Handles an FormatError exception
        :param mock_service:  mock for SpatialDatasetService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock()
        mock_args.connection = 'foo:pass@http:://foo:1234'
        mock_args.public_endpoint = 'foo@foo:foo'  # No 'http' or '://'
        mock_args.type = 'GeoServer'

        services_create_spatial_command(mock_args)

        mock_service.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('The public_endpoint argument (-p) must be of the form ', po_call_args[0][0][0])
        self.assertIn('"<protocol>//<host>:<port>".', po_call_args[0][0][0])

    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.SpatialDatasetService')
    def test_services_create_spatial_command_IntegrityError(self, mock_service, mock_pretty_output):
        """
        Test for services_create_spatial_command
        Handles an IntegrityError exception
        :param mock_service:  mock for SpatialDatasetService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock()
        mock_args.connection = 'foo:pass@http:://foo:1234'
        mock_args.public_endpoint = 'http://foo:1234'
        mock_args.type = 'GeoServer'
        mock_service.side_effect = IntegrityError

        services_create_spatial_command(mock_args)

        mock_service.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('Spatial Dataset Service with name ', po_call_args[0][0][0])
        self.assertIn('already exists. Command aborted.', po_call_args[0][0][0])

    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.SpatialDatasetService')
    def test_services_create_spatial_command_geoserver(self, mock_service, mock_pretty_output):
        """
        Test for services_create_spatial_command
        For going through the function and saving
        :param mock_service:  mock for SpatialDatasetService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock(
            connection='foo:pass@http://localhost:8181/geoserver/rest/',
            public_endpoint='https://www.example.com:443/geoserver/rest/',
            apikey='apikey123',
            type='GeoServer'
        )
        mock_args.name = 'test_geoserver'

        services_create_spatial_command(mock_args)

        mock_service.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual('Successfully created new Spatial Dataset Service!', po_call_args[0][0][0])
        mock_service.assert_called_with(
            name='test_geoserver',
            endpoint='http://localhost:8181/geoserver/rest/',
            public_endpoint='https://www.example.com:443/geoserver/rest/',
            apikey='apikey123',
            username='foo',
            password='pass',
            engine=mock_service.GEOSERVER
        )

    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.SpatialDatasetService')
    def test_services_create_spatial_command_thredds(self, mock_service, mock_pretty_output):
        """
        Test for services_create_spatial_command
        For going through the function and saving
        :param mock_service:  mock for SpatialDatasetService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock(
            connection='foo:pass@http://localhost:8181/thredds/catalog.xml',
            public_endpoint='https://www.example.com:443/thredds/catalog.xml',
            apikey='apikey123',
            type='THREDDS'
        )
        mock_args.name = 'test_thredds'

        services_create_spatial_command(mock_args)

        mock_service.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual('Successfully created new Spatial Dataset Service!', po_call_args[0][0][0])
        mock_service.assert_called_with(
            name='test_thredds',
            endpoint='http://localhost:8181/thredds/catalog.xml',
            public_endpoint='https://www.example.com:443/thredds/catalog.xml',
            apikey='apikey123',
            username='foo',
            password='pass',
            engine=mock_service.THREDDS
        )

    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_cli.services_commands.exit')
    @mock.patch('tethys_services.models.WebProcessingService')
    def test_services_remove_wps_command_Exceptions(self, mock_service, mock_exit, mock_pretty_output):
        """
        Test for services_remove_wps_command
        Handles testing all of the exceptions thrown
        :param mock_service:  mock for Web Processing Service
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock()
        mock_service.__str__.return_value = 'Web Processing'

        mock_service.objects.get.side_effect = [ValueError, ObjectDoesNotExist]
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, services_remove_wps_command, mock_args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('A Web Processing Service with ID/Name', po_call_args[0][0][0])
        self.assertIn('does not exist.', po_call_args[0][0][0])

    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_cli.services_commands.exit')
    @mock.patch('tethys_services.models.SpatialDatasetService')
    def test_services_remove_spatial_command_force(self, mock_service, mock_exit, mock_pretty_output):
        """
        Test for services_remove_spatial_command
        For when a delete is forced
        :param mock_service:  mock for SpatialDatasetService
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock()
        mock_service.__str__.return_value = 'Spatial Dataset'

        mock_args.force = True
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, services_remove_spatial_command, mock_args)

        mock_service.objects.get().delete.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('Successfully removed Spatial Dataset Service', po_call_args[0][0][0])

    @mock.patch('tethys_cli.services_commands.input')
    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_cli.services_commands.exit')
    @mock.patch('tethys_services.models.SpatialDatasetService')
    def test_services_remove_spatial_command_no_proceed_invalid_char(self, mock_service, mock_exit,
                                                                     mock_pretty_output, mock_input):
        """
        Test for services_remove_spatial_command
        For when deleting is not forced, and when prompted, giving an invalid answer, then no delete
        :param mock_service:  mock for SpatialDatasetService
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output:  mock for pretty_output text
        :param mock_input:  mock for handling raw_input requests
        :return:
        """
        mock_args = mock.MagicMock()
        mock_service.__str__.return_value = 'Spatial Dataset'

        mock_args.force = False
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit
        mock_input.side_effect = ['foo', 'N']

        self.assertRaises(SystemExit, services_remove_spatial_command, mock_args)

        mock_service.objects.get().delete.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual('Aborted. Spatial Dataset Service not removed.', po_call_args[0][0][0])

        po_call_args = mock_input.call_args_list
        self.assertEqual(2, len(po_call_args))
        self.assertEqual('Are you sure you want to delete this Spatial Dataset Service? [y/n]: ', po_call_args[0][0][0])
        self.assertEqual('Please enter either "y" or "n": ', po_call_args[1][0][0])

    @mock.patch('tethys_cli.services_commands.input')
    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_cli.services_commands.exit')
    @mock.patch('tethys_services.models.SpatialDatasetService')
    def test_services_remove_spatial_command_proceed(self, mock_service, mock_exit, mock_pretty_output, mock_input):
        """
        Test for services_remove_spatial_command
        For when deleting is not forced, and when prompted, giving a valid answer to delete
        :param mock_service:  mock for SpatialDatasetService
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output:  mock for pretty_output text
        :param mock_input:  mock for handling raw_input requests
        :return:
        """
        mock_args = mock.MagicMock()
        mock_service.__str__.return_value = 'Spatial Dataset'

        mock_args.force = False
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit
        mock_input.side_effect = ['y']

        self.assertRaises(SystemExit, services_remove_spatial_command, mock_args)

        mock_service.objects.get().delete.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('Successfully removed Spatial Dataset Service', po_call_args[0][0][0])

        po_call_args = mock_input.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual('Are you sure you want to delete this Spatial Dataset Service? [y/n]: ', po_call_args[0][0][0])

    @mock.patch('tethys_cli.services_commands.print')
    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.PersistentStoreService')
    @mock.patch('tethys_services.models.SpatialDatasetService')
    @mock.patch('tethys_cli.services_commands.model_to_dict')
    def test_services_list_command_not_spatial_not_persistent(self, mock_mtd, mock_spatial, mock_persistent,
                                                              mock_pretty_output, mock_print):
        """
        Test for services_list_command
        Both spatial and persistent are not set, so both are processed
        :param mock_mtd:  mock for model_to_dict to return a dictionary
        :param mock_spatial:  mock for SpatialDatasetService
        :param mock_persistent:  mock for PersistentStoreService
        :param mock_pretty_output: mock for pretty_output text
        :param mock_stdout:  mock for text written with print statements
        :return:
        """
        mock_mtd.return_value = self.my_dict
        mock_args = mock.MagicMock()
        mock_args.spatial = False
        mock_args.persistent = False
        mock_args.dataset = False
        mock_args.wps = False
        mock_spatial.objects.order_by('id').all.return_value = [mock.MagicMock(), mock.MagicMock(), mock.MagicMock(),
                                                                mock.MagicMock()]
        mock_persistent.objects.order_by('id').all.return_value = [mock.MagicMock(), mock.MagicMock(), mock.MagicMock(),
                                                                   mock.MagicMock()]

        services_list_command(mock_args)

        # Check expected pretty_output
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(4, len(po_call_args))
        self.assertIn('Persistent Store Services:', po_call_args[0][0][0])
        self.assertIn('ID', po_call_args[1][0][0])
        self.assertIn('Name', po_call_args[1][0][0])
        self.assertIn('Host', po_call_args[1][0][0])
        self.assertIn('Port', po_call_args[1][0][0])
        self.assertNotIn('Endpoint', po_call_args[1][0][0])
        self.assertNotIn('Public Endpoint', po_call_args[1][0][0])
        self.assertNotIn('API Key', po_call_args[1][0][0])
        self.assertIn('Spatial Dataset Services:', po_call_args[2][0][0])
        self.assertIn('ID', po_call_args[3][0][0])
        self.assertIn('Name', po_call_args[3][0][0])
        self.assertNotIn('Host', po_call_args[3][0][0])
        self.assertNotIn('Port', po_call_args[3][0][0])
        self.assertIn('Endpoint', po_call_args[3][0][0])
        self.assertIn('Public Endpoint', po_call_args[3][0][0])
        self.assertIn('API Key', po_call_args[3][0][0])

        # Check text written with Python's print
        rts_call_args = mock_print.call_args_list
        self.assertIn(self.my_dict['id'], rts_call_args[0][0][0])
        self.assertIn(self.my_dict['name'], rts_call_args[0][0][0])
        self.assertIn(self.my_dict['host'], rts_call_args[0][0][0])
        self.assertIn(self.my_dict['port'], rts_call_args[0][0][0])
        self.assertIn(self.my_dict['id'], rts_call_args[4][0][0])
        self.assertIn(self.my_dict['name'], rts_call_args[4][0][0])
        self.assertNotIn(self.my_dict['host'], rts_call_args[4][0][0])
        self.assertNotIn(self.my_dict['port'], rts_call_args[4][0][0])
        self.assertIn(self.my_dict['endpoint'], rts_call_args[4][0][0])
        self.assertIn(self.my_dict['public_endpoint'], rts_call_args[4][0][0])
        self.assertIn(self.my_dict['apikey'], rts_call_args[4][0][0])

    @mock.patch('tethys_cli.services_commands.print')
    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.SpatialDatasetService')
    @mock.patch('tethys_cli.services_commands.model_to_dict')
    def test_services_list_command_spatial(self, mock_mtd, mock_spatial, mock_pretty_output, mock_print):
        """
        Test for services_list_command
        Only spatial is set
        :param mock_mtd:  mock for model_to_dict to return a dictionary
        :param mock_spatial:  mock for SpatialDatasetService
        :param mock_pretty_output:  mock for pretty_output text
        :param mock_stdout:  mock for text written with print statements
        :return:
        """
        mock_mtd.return_value = self.my_dict
        mock_args = mock.MagicMock()
        mock_args.spatial = True
        mock_args.persistent = False
        mock_args.dataset = False
        mock_args.wps = False
        mock_spatial.objects.order_by('id').all.return_value = [mock.MagicMock(), mock.MagicMock(), mock.MagicMock()]

        services_list_command(mock_args)

        # Check expected pretty_output
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(2, len(po_call_args))
        self.assertIn('Spatial Dataset Services:', po_call_args[0][0][0])
        self.assertIn('ID', po_call_args[1][0][0])
        self.assertIn('Name', po_call_args[1][0][0])
        self.assertNotIn('Host', po_call_args[1][0][0])
        self.assertNotIn('Port', po_call_args[1][0][0])
        self.assertIn('Endpoint', po_call_args[1][0][0])
        self.assertIn('Public Endpoint', po_call_args[1][0][0])
        self.assertIn('API Key', po_call_args[1][0][0])

        # Check text written with Python's print
        rts_call_args = mock_print.call_args_list

        self.assertIn(self.my_dict['id'], rts_call_args[2][0][0])
        self.assertIn(self.my_dict['name'], rts_call_args[2][0][0])
        self.assertNotIn(self.my_dict['host'], rts_call_args[2][0][0])
        self.assertNotIn(self.my_dict['port'], rts_call_args[2][0][0])
        self.assertIn(self.my_dict['endpoint'], rts_call_args[2][0][0])
        self.assertIn(self.my_dict['public_endpoint'], rts_call_args[2][0][0])
        self.assertIn(self.my_dict['apikey'], rts_call_args[2][0][0])

    @mock.patch('tethys_cli.services_commands.print')
    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.PersistentStoreService')
    @mock.patch('tethys_cli.services_commands.model_to_dict')
    def test_services_list_command_persistent(self, mock_mtd, mock_persistent, mock_pretty_output, mock_print):
        """
        Test for services_list_command
        Only persistent is set
        :param mock_mtd:  mock for model_to_dict to return a dictionary
        :param mock_persistent:  mock for PersistentStoreService
        :param mock_pretty_output:  mock for pretty_output text
        :param mock_stdout:  mock for text written with print statements
        :return:
        """
        mock_mtd.return_value = self.my_dict
        mock_args = mock.MagicMock()
        mock_args.spatial = False
        mock_args.persistent = True
        mock_args.dataset = False
        mock_args.wps = False
        mock_persistent.objects.order_by('id').all.return_value = [mock.MagicMock(), mock.MagicMock()]

        services_list_command(mock_args)

        # Check expected pretty_output
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(2, len(po_call_args))
        self.assertIn('Persistent Store Services:', po_call_args[0][0][0])
        self.assertIn('ID', po_call_args[1][0][0])
        self.assertIn('Name', po_call_args[1][0][0])
        self.assertIn('Host', po_call_args[1][0][0])
        self.assertIn('Port', po_call_args[1][0][0])
        self.assertNotIn('Endpoint', po_call_args[1][0][0])
        self.assertNotIn('Public Endpoint', po_call_args[1][0][0])
        self.assertNotIn('API Key', po_call_args[1][0][0])

        # Check text written with Python's print
        rts_call_args = mock_print.call_args_list

        self.assertIn(self.my_dict['id'], rts_call_args[1][0][0])
        self.assertIn(self.my_dict['name'], rts_call_args[1][0][0])
        self.assertIn(self.my_dict['host'], rts_call_args[1][0][0])
        self.assertIn(self.my_dict['port'], rts_call_args[1][0][0])
        self.assertNotIn(self.my_dict['endpoint'], rts_call_args[1][0][0])
        self.assertNotIn(self.my_dict['public_endpoint'], rts_call_args[1][0][0])
        self.assertNotIn(self.my_dict['apikey'], rts_call_args[1][0][0])

    @mock.patch('tethys_cli.services_commands.print')
    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.DatasetService')
    @mock.patch('tethys_cli.services_commands.model_to_dict')
    def test_services_list_command_dataset(self, mock_mtd, mock_dataset, mock_pretty_output, mock_print):
        """
        Test for services_list_command
        Only dataset is set
        :param mock_mtd:  mock for model_to_dict to return a dictionary
        :param mock_dataset:  mock for DatasetService
        :param mock_pretty_output:  mock for pretty_output text
        :param mock_stdout:  mock for text written with print statements
        :return:
        """
        mock_mtd.return_value = self.my_dict
        mock_args = mock.MagicMock()
        mock_args.spatial = False
        mock_args.persistent = False
        mock_args.dataset = True
        mock_args.wps = False
        mock_dataset.objects.order_by('id').all.return_value = [mock.MagicMock(), mock.MagicMock()]

        services_list_command(mock_args)

        # Check expected pretty_output
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(2, len(po_call_args))
        self.assertIn('Dataset Services:', po_call_args[0][0][0])
        self.assertIn('ID', po_call_args[1][0][0])
        self.assertIn('Name', po_call_args[1][0][0])
        self.assertIn('Endpoint', po_call_args[1][0][0])
        self.assertIn('Public Endpoint', po_call_args[1][0][0])
        self.assertIn('API Key', po_call_args[1][0][0])
        self.assertNotIn('Host', po_call_args[1][0][0])
        self.assertNotIn('Port', po_call_args[1][0][0])

        # Check text written with Python's print
        rts_call_args = mock_print.call_args_list

        self.assertIn(self.my_dict['id'], rts_call_args[1][0][0])
        self.assertIn(self.my_dict['name'], rts_call_args[1][0][0])
        self.assertIn(self.my_dict['endpoint'], rts_call_args[1][0][0])
        self.assertIn(self.my_dict['public_endpoint'], rts_call_args[1][0][0])
        self.assertIn(self.my_dict['apikey'], rts_call_args[1][0][0])
        self.assertNotIn(self.my_dict['host'], rts_call_args[1][0][0])
        self.assertNotIn(self.my_dict['port'], rts_call_args[1][0][0])

    @mock.patch('tethys_cli.services_commands.print')
    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.WebProcessingService')
    @mock.patch('tethys_cli.services_commands.model_to_dict')
    def test_services_list_command_wps(self, mock_mtd, mock_wps, mock_pretty_output, mock_print):
        """
        Test for services_list_command
        Only dataset is set
        :param mock_mtd:  mock for model_to_dict to return a dictionary
        :param mock_wps:  mock for WebProcessingService
        :param mock_pretty_output:  mock for pretty_output text
        :param mock_stdout:  mock for text written with print statements
        :return:
        """
        mock_mtd.return_value = self.my_dict
        mock_args = mock.MagicMock()
        mock_args.spatial = False
        mock_args.persistent = False
        mock_args.dataset = False
        mock_args.wps = True
        mock_wps.objects.order_by('id').all.return_value = [mock.MagicMock(), mock.MagicMock()]

        services_list_command(mock_args)

        # Check expected pretty_output
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(2, len(po_call_args))
        self.assertIn('Web Processing Services:', po_call_args[0][0][0])
        self.assertIn('ID', po_call_args[1][0][0])
        self.assertIn('Name', po_call_args[1][0][0])
        self.assertIn('Endpoint', po_call_args[1][0][0])
        self.assertIn('Public Endpoint', po_call_args[1][0][0])
        self.assertNotIn('Host', po_call_args[1][0][0])
        self.assertNotIn('Port', po_call_args[1][0][0])
        self.assertNotIn('API Key', po_call_args[1][0][0])

        # Check text written with Python's print
        rts_call_args = mock_print.call_args_list

        self.assertIn(self.my_dict['id'], rts_call_args[1][0][0])
        self.assertIn(self.my_dict['name'], rts_call_args[1][0][0])
        self.assertIn(self.my_dict['endpoint'], rts_call_args[1][0][0])
        self.assertIn(self.my_dict['public_endpoint'], rts_call_args[1][0][0])
        self.assertNotIn(self.my_dict['host'], rts_call_args[1][0][0])
        self.assertNotIn(self.my_dict['port'], rts_call_args[1][0][0])
        self.assertNotIn(self.my_dict['apikey'], rts_call_args[1][0][0])

    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.DatasetService')
    def test_services_create_dataset_command_IndexError(self, mock_service, mock_pretty_output):

        mock_args = mock.MagicMock()
        mock_args.connection = 'IndexError:9876@IndexError'  # No 'http' or '://'
        mock_args.type = 'HydroShare'

        services_create_dataset_command(mock_args)

        mock_service.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('The connection argument (-c) must be of the form', po_call_args[0][0][0])
        self.assertIn('"<username>:<password>@<protocol>//<host>:<port>".', po_call_args[0][0][0])

    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.DatasetService')
    def test_services_create_dataset_command_FormatError(self, mock_service, mock_pretty_output):

        mock_args = mock.MagicMock()
        mock_args.connection = 'foo:pass@http:://foo:1234'
        mock_args.public_endpoint = 'foo@foo:foo'  # No 'http' or '://'
        mock_args.type = 'HydroShare'

        services_create_dataset_command(mock_args)

        mock_service.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('The public_endpoint argument (-p) must be of the form ', po_call_args[0][0][0])
        self.assertIn('"<protocol>//<host>:<port>".', po_call_args[0][0][0])

    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.DatasetService')
    def test_services_create_dataset_command_IntegrityError(self, mock_service, mock_pretty_output):

        mock_args = mock.MagicMock()
        mock_args.connection = 'foo:pass@http:://foo:1234'
        mock_args.public_endpoint = 'http://foo:1234'
        mock_args.type = 'HydroShare'
        mock_service.side_effect = IntegrityError

        services_create_dataset_command(mock_args)

        mock_service.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('Dataset Service with name ', po_call_args[0][0][0])
        self.assertIn('already exists. Command aborted.', po_call_args[0][0][0])

    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.DatasetService')
    def test_services_create_dataset_command_hydroshare(self, mock_service, mock_pretty_output):
        mock_args = mock.MagicMock(
            connection='foo:pass@http://localhost:80',
            public_endpoint='http://www.example.com:80',
            apikey='apikey123',
            type='HydroShare'
        )
        mock_args.name = 'test_hydroshare'

        services_create_dataset_command(mock_args)

        mock_service.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual('Successfully created new Dataset Service!', po_call_args[0][0][0])
        mock_service.assert_called_with(
            name='test_hydroshare',
            endpoint='http://localhost:80',
            public_endpoint='http://www.example.com:80',
            apikey='apikey123',
            username='foo',
            password='pass',
            engine=mock_service.HYDROSHARE
        )

    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.DatasetService')
    def test_services_create_dataset_command_ckan(self, mock_service, mock_pretty_output):
        mock_args = mock.MagicMock(
            connection='foo:pass@http://localhost:80',
            public_endpoint='http://www.example.com:80',
            apikey='apikey123',
            type='CKAN'
        )
        mock_args.name = 'test_ckan'

        services_create_dataset_command(mock_args)

        mock_service.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual('Successfully created new Dataset Service!', po_call_args[0][0][0])
        mock_service.assert_called_with(
            name='test_ckan',
            endpoint='http://localhost:80',
            public_endpoint='http://www.example.com:80',
            apikey='apikey123',
            username='foo',
            password='pass',
            engine=mock_service.CKAN
        )

    @mock.patch('tethys_cli.services_commands.input')
    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_cli.services_commands.exit')
    @mock.patch('tethys_services.models.DatasetService')
    def test_services_remove_dataset_command_proceed(self, mock_service, mock_exit, mock_pretty_output, mock_input):

        mock_args = mock.MagicMock()
        mock_service.__str__.return_value = 'Dataset'

        mock_args.force = False
        mock_exit.side_effect = SystemExit
        mock_input.side_effect = ['y']

        self.assertRaises(SystemExit, services_remove_dataset_command, mock_args)

        mock_service.objects.get().delete.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('Successfully removed Dataset Service', po_call_args[0][0][0])

        po_call_args = mock_input.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual('Are you sure you want to delete this Dataset Service? [y/n]: ', po_call_args[0][0][0])

    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.WebProcessingService')
    def test_services_create_wps_command_IndexError(self, mock_service, mock_pretty_output):

        mock_args = mock.MagicMock()
        mock_args.connection = 'IndexError:9876@IndexError'  # No 'http' or '://'

        services_create_wps_command(mock_args)

        mock_service.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('The connection argument (-c) must be of the form', po_call_args[0][0][0])
        self.assertIn('"<username>:<password>@<protocol>//<host>:<port>".', po_call_args[0][0][0])

    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.WebProcessingService')
    def test_services_create_wps_command_IntegrityError(self, mock_service, mock_pretty_output):

        mock_args = mock.MagicMock()
        mock_args.connection = 'foo:pass@http:://foo:1234'
        mock_args.public_endpoint = 'http://foo:1234'
        mock_service.side_effect = IntegrityError

        services_create_wps_command(mock_args)

        mock_service.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('Web Processing Service with name ', po_call_args[0][0][0])
        self.assertIn('already exists. Command aborted.', po_call_args[0][0][0])

    @mock.patch('tethys_cli.services_commands.pretty_output')
    @mock.patch('tethys_services.models.WebProcessingService')
    def test_services_create_wps_command(self, mock_service, mock_pretty_output):
        mock_args = mock.MagicMock()
        mock_args.connection = 'foo:pass@http:://foo:1234'
        mock_service.return_value = mock.MagicMock()

        services_create_wps_command(mock_args)

        mock_service.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual('Successfully created new Web Processing Service!', po_call_args[0][0][0])
