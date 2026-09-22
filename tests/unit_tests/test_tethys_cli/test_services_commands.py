import pytest

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
    services_remove_wps_command,
    services_create_secure_map_command,
    services_remove_secure_map_command
)
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import IntegrityError


class ServicesCommandsTest(unittest.TestCase):
    """
    Tests for tethys_cli.services_commands
    """

    # Dictionary used in some of the tests
    my_postgres_dict = {
        "id": "Id_foo",
        "name": "Name_foo",
        "host": "Host_foo",
        "port": "Port_foo",
        "endpoint": "EndPoint_foo",
        "public_endpoint": "PublicEndPoint_bar",
        "apikey": "APIKey_foo",
    }

    my_secure_map_dict = {
        "id": "Id_baz",
        "name": "Name_baz",
        "legend_title": "LegendTitle_baz",
        "endpoint": "EndPoint_baz",
        "authentication_method": "api_key",
        "api_key": "APIKey_baz",
        "service_type": "ServiceType_baz",
        "params": {"param1": "value1"},
        "use_proxy": False,
    }

    my_sqlite_dict = {"id": "Id_bar", "name": "Name_bar", "dir_path": "DirPath_bar"}

    def setUp(self):
        setup_django_patcher = mock.patch("tethys_cli.services_commands.setup_django")
        setup_django_patcher.start()
        self.addCleanup(setup_django_patcher.stop)

    def tearDown(self):
        pass

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.PostgresPersistentStoreService")
    def test_services_create_postgres_persistent_command(
        self, mock_service, mock_pretty_output
    ):
        """
        Test for services_create_persistent_command.
        For running the test without any errors or problems.
        :param mock_service:  mock for PostgresPersistentStoreService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock(type="postgres")
        services_create_persistent_command(mock_args)
        mock_service.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual(
            "Successfully created new PostgreSQL Persistent Store Service!",
            po_call_args[0][0][0],
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.PostgresPersistentStoreService")
    def test_services_create_postgres_persistent_command_exception_attributeerror(
        self, mock_service, mock_pretty_output
    ):
        """
        Test for services_create_persistent_command.
        For running the test with an IndexError exception thrown.
        :param mock_service:  mock for PostgresPersistentStoreService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock(type="postgres")
        mock_args.connection = AttributeError
        services_create_persistent_command(mock_args)

        mock_service.assert_not_called()
        mock_service.objects.get().save.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "Missing Input Parameters. Please check your input.", po_call_args[0][0][0]
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.PostgresPersistentStoreService")
    def test_services_create_postgres_persistent_command_exception_indexerror(
        self, mock_service, mock_pretty_output
    ):
        """
        Test for services_create_persistent_command.
        For running the test with an IndexError exception thrown.
        :param mock_service:  mock for PostgresPersistentStoreService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock(type="postgres")
        mock_service.side_effect = IndexError
        services_create_persistent_command(mock_args)

        mock_service.assert_called()
        mock_service.objects.get().save.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "The connection argument (-c) must be of the form", po_call_args[0][0][0]
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.PostgresPersistentStoreService")
    def test_services_create_postgres_persistent_command_exception_integrityerror(
        self, mock_service, mock_pretty_output
    ):
        """
        Test for services_create_postgres_persistent_command.
        For running the test with an IntegrityError exception thrown.
        :param mock_service:  mock for PostgresPersistentStoreService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock(type="postgres")
        mock_service.side_effect = IntegrityError
        services_create_persistent_command(mock_args)

        mock_service.assert_called()
        mock_service.objects.get().save.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn("Persistent Store Service with name", po_call_args[0][0][0])
        self.assertIn("already exists. Command aborted.", po_call_args[0][0][0])

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.SQLitePersistentStoreService")
    def test_services_create_sqlite_persistent_command(
        self, mock_service, mock_pretty_output
    ):
        """
        Test for services_create_persistent_command.
        For running the test without any errors or problems.
        :param mock_service:  mock for SQLitePersistentStoreService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock(type="sqlite")
        services_create_persistent_command(mock_args)
        mock_service.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual(
            "Successfully created new SQLite Persistent Store Service!",
            po_call_args[0][0][0],
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.SQLitePersistentStoreService")
    @mock.patch("tethys_services.models.PostgresPersistentStoreService")
    def test_services_create_unknown_persistent_command(
        self, mock_postgres_service, mock_sqlite_service, mock_pretty_output
    ):
        """
        Test for services_create_persistent_command.
        For running the test with an unknown persistent store type.
        :param mock_postgres_service:  mock for PostgresPersistentStoreService
        :param mock_sqlite_service:  mock for SQLitePersistentStoreService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock(type="unknown")
        services_create_persistent_command(mock_args)
        mock_postgres_service.assert_not_called()
        mock_sqlite_service.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual(
            "Unknown persistent store type: unknown",
            po_call_args[0][0][0],
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_cli.services_commands.exit")
    @mock.patch("tethys_services.models.PostgresPersistentStoreService")
    @mock.patch("tethys_services.models.SQLitePersistentStoreService")
    def test_services_remove_persistent_command_Exceptions(
        self, mock_sqlite_service, mock_postgres_service, mock_exit, mock_pretty_output
    ):
        """
        Test for services_remove_persistent_command
        Test for handling all exceptions thrown by the function.
        :param mock_sqlite_service:  mock for SQLitePersistentStoreService
        :param mock_postgres_service:  mock for PostgresPersistentStoreService
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output: mock for pretty_output text
        :return:
        """

        mock_args = mock.MagicMock()
        mock_args.force = True
        mock_postgres_service.__str__.return_value = "Postgres Persistent Store"
        mock_postgres_service.objects.get.side_effect = [ValueError, ObjectDoesNotExist]
        mock_sqlite_service.__str__.return_value = "SQLite Persistent Store"
        mock_sqlite_service.objects.get.side_effect = [ValueError, ObjectDoesNotExist]
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, services_remove_persistent_command, mock_args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn("A Persistent Store Service with ID/Name", po_call_args[0][0][0])
        self.assertIn("does not exist", po_call_args[0][0][0])

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_cli.services_commands.exit")
    @mock.patch("tethys_services.models.PostgresPersistentStoreService")
    def test_services_remove_persistent_command_force(
        self, mock_service, mock_exit, mock_pretty_output
    ):
        """
        Test for services_remove_persistent_command
        Test for forcing a delete of the service
        :param mock_service:  mock for PostgresPersistentStoreService
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output: mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock()
        mock_args.force = True
        mock_service.__str__.return_value = "Persistent Store"

        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, services_remove_persistent_command, mock_args)

        mock_service.objects.get().delete.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "Successfully removed Persistent Store Service", po_call_args[0][0][0]
        )

    @mock.patch("tethys_cli.services_commands.input")
    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_cli.services_commands.exit")
    @mock.patch("tethys_services.models.PostgresPersistentStoreService")
    def test_services_remove_persistent_command_no_proceed_invalid_char(
        self, mock_service, mock_exit, mock_pretty_output, mock_input
    ):
        """
        Test for services_remove_persistent_command
        Handles answering the prompt to delete with invalid characters, and answering no.
        :param mock_service:  mock for PostgresPersistentStoreService
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
        mock_input.side_effect = ["foo", "N"]
        mock_service.__str__.return_value = "Persistent Store"

        self.assertRaises(SystemExit, services_remove_persistent_command, mock_args)

        mock_service.objects.get().delete.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual(
            "Aborted. Persistent Store Service not removed.", po_call_args[0][0][0]
        )

        po_call_args = mock_input.call_args_list
        self.assertEqual(2, len(po_call_args))
        self.assertEqual(
            "Are you sure you want to delete this Persistent Store Service? [y/n]: ",
            po_call_args[0][0][0],
        )
        self.assertEqual('Please enter either "y" or "n": ', po_call_args[1][0][0])

    @mock.patch("tethys_cli.services_commands.input")
    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_cli.services_commands.exit")
    @mock.patch("tethys_services.models.PostgresPersistentStoreService")
    def test_services_remove_persistent_command_proceed(
        self, mock_service, mock_exit, mock_pretty_output, mock_input
    ):
        """
        Test for services_remove_persistent_command
        Handles answering the prompt to delete with invalid characters by answering yes
        :param mock_service:  mock for PostgresPersistentStoreService
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output:  mock for pretty_output text
        :param mock_input:  mock for handling raw_input requests
        :return:
        """
        mock_args = mock.MagicMock()
        mock_service.__str__.return_value = "Persistent Store"
        mock_args.force = False
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit
        mock_input.side_effect = ["y"]

        self.assertRaises(SystemExit, services_remove_persistent_command, mock_args)

        mock_service.objects.get().delete.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "Successfully removed Persistent Store Service", po_call_args[0][0][0]
        )

        po_call_args = mock_input.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual(
            "Are you sure you want to delete this Persistent Store Service? [y/n]: ",
            po_call_args[0][0][0],
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.SpatialDatasetService")
    def test_services_create_spatial_command_IndexError(
        self, mock_service, mock_pretty_output
    ):
        """
        Test for services_create_spatial_command
        Handles an IndexError exception
        :param mock_service:  mock for SpatialDatasetService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock()
        mock_args.connection = "IndexError:9876@IndexError"  # No 'http' or '://'
        mock_args.type = "GeoServer"

        services_create_spatial_command(mock_args)

        mock_service.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "The connection argument (-c) must be of the form", po_call_args[0][0][0]
        )
        self.assertIn(
            '"<username>:<password>@<protocol>//<host>:<port>".', po_call_args[0][0][0]
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.SpatialDatasetService")
    def test_services_create_spatial_command_FormatError(
        self, mock_service, mock_pretty_output
    ):
        """
        Test for services_create_spatial_command
        Handles an FormatError exception
        :param mock_service:  mock for SpatialDatasetService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock()
        mock_args.connection = "foo:pass@http:://foo:1234"
        mock_args.public_endpoint = "foo@foo:foo"  # No 'http' or '://'
        mock_args.type = "GeoServer"

        services_create_spatial_command(mock_args)

        mock_service.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "The public_endpoint argument (-p) must be of the form ",
            po_call_args[0][0][0],
        )
        self.assertIn('"<protocol>//<host>:<port>".', po_call_args[0][0][0])

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.SpatialDatasetService")
    def test_services_create_spatial_command_IntegrityError(
        self, mock_service, mock_pretty_output
    ):
        """
        Test for services_create_spatial_command
        Handles an IntegrityError exception
        :param mock_service:  mock for SpatialDatasetService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock()
        mock_args.connection = "foo:pass@http:://foo:1234"
        mock_args.public_endpoint = "http://foo:1234"
        mock_args.type = "GeoServer"
        mock_service.side_effect = IntegrityError

        services_create_spatial_command(mock_args)

        mock_service.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn("Spatial Dataset Service with name ", po_call_args[0][0][0])
        self.assertIn("already exists. Command aborted.", po_call_args[0][0][0])

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.SpatialDatasetService")
    def test_services_create_spatial_command_geoserver(
        self, mock_service, mock_pretty_output
    ):
        """
        Test for services_create_spatial_command
        For going through the function and saving
        :param mock_service:  mock for SpatialDatasetService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock(
            connection="foo:pass@http://localhost:8181/geoserver/rest/",
            public_endpoint="https://www.example.com:443/geoserver/rest/",
            apikey="apikey123",
            type="GeoServer",
        )
        mock_args.name = "test_geoserver"

        services_create_spatial_command(mock_args)

        mock_service.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual(
            "Successfully created new Spatial Dataset Service!", po_call_args[0][0][0]
        )
        mock_service.assert_called_with(
            name="test_geoserver",
            endpoint="http://localhost:8181/geoserver/rest/",
            public_endpoint="https://www.example.com:443/geoserver/rest/",
            apikey="apikey123",
            username="foo",
            password="pass",
            engine=mock_service.GEOSERVER,
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.SpatialDatasetService")
    def test_services_create_spatial_command_thredds_with_endpoint(
        self, mock_service, mock_pretty_output
    ):
        """
        Test for services_create_spatial_command
        For going through the function and saving
        :param mock_service:  mock for SpatialDatasetService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock(
            endpoint="http://localhost:8181/thredds/catalog.xml",
            public_endpoint="https://www.example.com:443/thredds/catalog.xml",
            apikey="apikey123",
            type="THREDDS",
            connection=None,
        )
        mock_args.name = "test_thredds"
        services_create_spatial_command(mock_args)

        mock_service.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual(
            "Successfully created new Spatial Dataset Service!", po_call_args[0][0][0]
        )
        mock_service.assert_called_with(
            name="test_thredds",
            endpoint="http://localhost:8181/thredds/catalog.xml",
            public_endpoint="https://www.example.com:443/thredds/catalog.xml",
            apikey="apikey123",
            username="",
            password="",
            engine=mock_service.THREDDS,
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.SpatialDatasetService")
    def test_services_create_spatial_command_thredds_with_connection(
        self, mock_service, mock_pretty_output
    ):
        """
        Test for services_create_spatial_command
        For going through the function and saving
        :param mock_service:  mock for SpatialDatasetService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock(
            connection="foo:pass@http://localhost:8181/thredds/catalog.xml",
            public_endpoint="https://www.example.com:443/thredds/catalog.xml",
            apikey="apikey123",
            type="THREDDS",
        )
        mock_args.name = "test_thredds"

        services_create_spatial_command(mock_args)

        mock_service.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual(
            "Successfully created new Spatial Dataset Service!", po_call_args[0][0][0]
        )
        mock_service.assert_called_with(
            name="test_thredds",
            endpoint="http://localhost:8181/thredds/catalog.xml",
            public_endpoint="https://www.example.com:443/thredds/catalog.xml",
            apikey="apikey123",
            username="foo",
            password="pass",
            engine=mock_service.THREDDS,
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.SpatialDatasetService")
    def test_services_create_spatial_command_thredds_no_connection_no_endpoint(
        self, mock_service, mock_pretty_output
    ):
        """
        Test for services_create_spatial_command
        For when neither connection nor endpoint is provided
        :param mock_service:  mock for SpatialDatasetService
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock(
            connection=None,
            endpoint=None,
            public_endpoint=None,
            apikey=None,
            type="THREDDS",
        )
        mock_args.name = "test_thredds"
        services_create_spatial_command(mock_args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "Either connection or endpoint argument must be provided.",
            po_call_args[0][0][0],
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    def test_services_create_secure_map_command_non_dict_params(self, mock_pretty_output):
        """
        Test for services_create_secure_map_command
        For when invalid params are provided
        :return:
        """
        # test for non-dict after loading json.loads
        mock_args = mock.MagicMock(
            name="test_secure_map",
            endpoint="http://localhost:8000/secure_map",
            public_endpoint="https://www.example.com:443/secure_map",
            auth_method="api_key",
            api_key="apikey123",
            service_type="geojson",
            params="5",
        )
        services_create_secure_map_command(mock_args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "'params' must be a JSON object, got int. Example: '{\"key\": \"value\"}'.",
            po_call_args[0][0][0],
        )
    @mock.patch("tethys_cli.services_commands.pretty_output")
    def test_services_create_secure_map_command_api_type_with_oauth2_provider(self, mock_pretty_output):
        """
        Test for services_create_secure_map_command when an oauth2 provider is
        provided with api_key chosen as the authentication method
        :return:
        """
        mock_args = mock.MagicMock(
            name="test_secure_map",
            endpoint="http://localhost:8000/secure_map",
            public_endpoint="https://www.example.com:443/secure_map",
            auth_method="api_key",
            oauth2_provider="provider_xyz",
            service_type="geojson",
            params='{"test": "value"}',
        )
        services_create_secure_map_command(mock_args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "OAuth2 provider should not be provided if the authentication method is 'API key'",
            po_call_args[0][0][0],
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    def test_services_create_secure_map_command_api_type_without_api_key(self, mock_pretty_output):
        """
        Test for services_create_secure_map_command when an oauth2 provider is
        provided with api_key chosen as the authentication method
        :return:
        """
        mock_args = mock.MagicMock(
            name="test_secure_map",
            endpoint="http://localhost:8000/secure_map",
            public_endpoint="https://www.example.com:443/secure_map",
            auth_method="api_key",
            service_type="geojson",
            api_key=None,
            oauth2_provider=None,
            params='{"test": "value"}',
        )
        services_create_secure_map_command(mock_args)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "API key is required for api_key authentication.",
            po_call_args[0][0][0],
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    def test_services_create_secure_map_command_oauth2_type_with_api_key(self, mock_pretty_output):
        """
        Test for services_create_secure_map_command when an api_key is
        provided with oauth2 chosen as the authentication method
        :return:
        """
        mock_args = mock.MagicMock(
            name="test_secure_map",
            endpoint="http://localhost:8000/secure_map",
            public_endpoint="https://www.example.com:443/secure_map",
            auth_method="oauth2",
            service_type="geojson",
            api_key="some_api_key",
            params='{"test": "value"}',
        )
        services_create_secure_map_command(mock_args)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "API key should not be provided if the authentication method is 'OAuth2'",
            po_call_args[0][0][0],
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    def test_services_create_secure_map_command_oauth2_type_without_provider(self, mock_pretty_output):
        """
        Test for services_create_secure_map_command when oauth2 is chosen as the authentication method
        but no oauth2_provider is provided
        :return:
        """
        mock_args = mock.MagicMock(
            name="test_secure_map",
            endpoint="http://localhost:8000/secure_map",
            public_endpoint="https://www.example.com:443/secure_map",
            auth_method="oauth2",
            service_type="geojson",
            api_key=None,
            oauth2_provider=None,
            params='{"test": "value"}',
        )
        services_create_secure_map_command(mock_args)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "OAuth2 provider is required for oauth2 authentication.",
            po_call_args[0][0][0],
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    def test_services_create_secure_map_command_invalid_authentication_type(self, mock_pretty_output):
        """
        Test for services_create_secure_map_command when an invalid authentication method is provided
        :return:
        """
        mock_args = mock.MagicMock(
            name="test_secure_map",
            endpoint="http://localhost:8000/secure_map",
            public_endpoint="https://www.example.com:443/secure_map",
            auth_method="invalid_auth",
            service_type="geojson",
            api_key=None,
            oauth2_provider=None,
            params='{"test": "value"}',
        )
        services_create_secure_map_command(mock_args)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "Authentication method must be either 'api_key' or 'oauth2'.",
            po_call_args[0][0][0],
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.SecureMapService")
    def test_services_create_secure_map(self, mock_service, mock_pretty_output):
        """
        Test for services_create_secure_map_command with valid inputs
        :return:
        """
        # Test successfully creating a secure map service with API key authentication
        mock_args = mock.MagicMock(
            endpoint="http://localhost:8000/secure_map",
            legend_title="test_legend_title",
            auth_method="api_key",
            service_type="geojson",
            api_key="test_api_key",
            oauth2_provider=None,
            params='{"test": "value"}',
            use_proxy=True,
            connection_timeout=5,
            read_timeout=10,
        )
        mock_args.name = "test_secure_map"
        services_create_secure_map_command(mock_args)
        mock_service.assert_called()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual(
            "Successfully created new Secure Map Service!",
            po_call_args[0][0][0],
        )

        mock_service.assert_called_with(
            name="test_secure_map",
            endpoint="http://localhost:8000/secure_map",
            legend_title="test_legend_title",
            authentication_method="api_key",
            service_type="GeoJSON",
            api_key="test_api_key",
            params={"test": "value"},
            use_proxy=True,
            connection_timeout=5,
            read_timeout=10,
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.SecureMapService")
    def test_services_create_secure_map_with_oauth2(self, mock_service, mock_pretty_output):
        # Test successfully creating a secure map service with OAuth2 authentication
        mock_args = mock.MagicMock(
            endpoint="http://localhost:8000/secure_map",
            legend_title="test_legend_title",
            auth_method="oauth2",
            service_type="geojson",
            api_key=None,
            oauth2_provider="test_oauth2_provider",
            params='{"test": "value"}',
            use_proxy=True,
            connection_timeout=5,
            read_timeout=10,
        )
        mock_args.name = "test_secure_map_oauth2"
        services_create_secure_map_command(mock_args)
        mock_service.assert_called()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual(
            "Successfully created new Secure Map Service!",
            po_call_args[0][0][0],
        )

        mock_service.assert_called_with(
            name="test_secure_map_oauth2",
            endpoint="http://localhost:8000/secure_map",
            legend_title="test_legend_title",
            authentication_method="oauth2",
            service_type="GeoJSON",
            oauth2_provider="test_oauth2_provider",
            params={"test": "value"},
            use_proxy=True,
            connection_timeout=5,
            read_timeout=10,
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    def test_services_create_secure_map_json_decode_error(self, mock_pretty_output):
        mock_args = mock.MagicMock(
            endpoint="http://localhost:8000/secure_map",
            legend_title="test_legend_title",
            auth_method="api_key",
            service_type="geojson",
            api_key="test_api_key",
            oauth2_provider=None,
            params='invalid json',
            use_proxy=True,
            connection_timeout=5,
            read_timeout=10,
        )
        mock_args.name = "test_secure_map_json_decode_error"

        services_create_secure_map_command(mock_args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn('Invalid JSON provided for \'params\': Expected a valid JSON object (e.g. \'{"key": "value"}\').', po_call_args[0][0][0])

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.SecureMapService")
    def test_services_create_secure_map_json_validation_error(self, mock_service, mock_pretty_output):
        mock_args = mock.MagicMock(
            endpoint="localhost:8000/secure_map",
            legend_title="test_legend_title",
            auth_method="api_key",
            service_type="geojson",
            api_key="test_api_key",
            oauth2_provider=None,
            params='{"test": "value"}',
            use_proxy=True,
            connection_timeout=5,
            read_timeout=10,
        )
        mock_args.name = "test_secure_map_service"

        mock_service.return_value.full_clean.side_effect = ValidationError(
            {"endpoint": ["Invalid Endpoint: Must be prefixed with \"http://\" or \"https://\""]}
        )

        services_create_secure_map_command(mock_args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(2, len(po_call_args))
        self.assertIn('Validation errors occured attempting to create the service:', po_call_args[0][0][0])
        self.assertIn("- endpoint: Invalid Endpoint: Must be prefixed with \"http://\" or \"https://\"", po_call_args[1][0][0])

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.SecureMapService")
    def test_services_create_secure_map_integrity_error(self, mock_service, mock_pretty_output):
        mock_args = mock.MagicMock(
            endpoint="http://localhost:8000/secure_map",
            legend_title="test_legend_title",
            auth_method="api_key",
            service_type="geojson",
            api_key="test_api_key",
            oauth2_provider=None,
            params='{"test": "value"}',
            use_proxy=True,
            connection_timeout=5,
            read_timeout=10,
        )
        mock_args.name = "duplicate_secure_map_service"

        mock_service.return_value.save.side_effect = IntegrityError

        services_create_secure_map_command(mock_args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            'Secure Map Service with name "duplicate_secure_map_service" already exists. Command aborted.',
            po_call_args[0][0][0],
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_cli.services_commands.exit")
    @mock.patch("tethys_services.models.WebProcessingService")
    def test_services_remove_wps_command_Exceptions(
        self, mock_service, mock_exit, mock_pretty_output
    ):
        """
        Test for services_remove_wps_command
        Handles testing all of the exceptions thrown
        :param mock_service:  mock for Web Processing Service
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock()
        mock_service._meta.verbose_name = "Web Processing"

        mock_service.objects.get.side_effect = [ValueError, ObjectDoesNotExist]
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, services_remove_wps_command, mock_args)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn("A Web Processing Service with ID/Name", po_call_args[0][0][0])
        self.assertIn("does not exist.", po_call_args[0][0][0])

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_cli.services_commands.exit")
    @mock.patch("tethys_services.models.SpatialDatasetService")
    def test_services_remove_spatial_command_force(
        self, mock_service, mock_exit, mock_pretty_output
    ):
        """
        Test for services_remove_spatial_command
        For when a delete is forced
        :param mock_service:  mock for SpatialDatasetService
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock()
        mock_service._meta.verbose_name = "Spatial Dataset Service"

        mock_args.force = True
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, services_remove_spatial_command, mock_args)

        mock_service.objects.get().delete.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "Successfully removed Spatial Dataset Service", po_call_args[0][0][0]
        )

    @mock.patch("tethys_cli.services_commands.input")
    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_cli.services_commands.exit")
    @mock.patch("tethys_services.models.SpatialDatasetService")
    def test_services_remove_spatial_command_no_proceed_invalid_char(
        self, mock_service, mock_exit, mock_pretty_output, mock_input
    ):
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
        mock_service._meta.verbose_name = "Spatial Dataset Service"

        mock_args.force = False
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit
        mock_input.side_effect = ["foo", "N"]

        self.assertRaises(SystemExit, services_remove_spatial_command, mock_args)

        mock_service.objects.get().delete.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual(
            "Aborted. Spatial Dataset Service not removed.", po_call_args[0][0][0]
        )

        po_call_args = mock_input.call_args_list
        self.assertEqual(2, len(po_call_args))
        self.assertEqual(
            "Are you sure you want to delete this Spatial Dataset Service? [y/n]: ",
            po_call_args[0][0][0],
        )
        self.assertEqual('Please enter either "y" or "n": ', po_call_args[1][0][0])

    @mock.patch("tethys_cli.services_commands.input")
    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_cli.services_commands.exit")
    @mock.patch("tethys_services.models.SpatialDatasetService")
    def test_services_remove_spatial_command_proceed(
        self, mock_service, mock_exit, mock_pretty_output, mock_input
    ):
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
        mock_service._meta.verbose_name = "Spatial Dataset Service"

        mock_args.force = False
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit
        mock_input.side_effect = ["y"]

        self.assertRaises(SystemExit, services_remove_spatial_command, mock_args)

        mock_service.objects.get().delete.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "Successfully removed Spatial Dataset Service 1", po_call_args[0][0][0]
        )

        po_call_args = mock_input.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual(
            "Are you sure you want to delete this Spatial Dataset Service? [y/n]: ",
            po_call_args[0][0][0],
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_cli.services_commands.exit")
    @mock.patch("tethys_services.models.SecureMapService")
    def test_services_remove_secure_map_command_force(self, mock_service, mock_exit, mock_pretty_output):
        """
        Test for services_remove_secure_map_command
        For when a delete is forced
        :param mock_service:  mock for SecureMapService
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output:  mock for pretty_output text
        :return:
        """
        mock_args = mock.MagicMock()
        mock_service._meta.verbose_name = "Secure Map Service"

        mock_args.force = True
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, services_remove_secure_map_command, mock_args)

        mock_service.objects.get().delete.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "Successfully removed Secure Map Service", po_call_args[0][0][0]
        )

    @mock.patch("tethys_cli.services_commands.input")
    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_cli.services_commands.exit")
    @mock.patch("tethys_services.models.SecureMapService")
    def test_services_remove_secure_map_command_no_proceed_invalid_char(self, mock_service, mock_exit, mock_pretty_output, mock_input):
        """
        Test for services_remove_secure_map_command
        For when deleting is not forced, and when prompted, giving an invalid answer, then no delete
        :param mock_service:  mock for SecureMapService
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output:  mock for pretty_output text
        :param mock_input:  mock for handling raw_input requests
        :return:
        """
        mock_args = mock.MagicMock()
        mock_service._meta.verbose_name = "Secure Map Service"

        mock_args.force = False
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit
        mock_input.side_effect = ["foo", "N"]

        self.assertRaises(SystemExit, services_remove_secure_map_command, mock_args)

        mock_service.objects.get().delete.assert_not_called()
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "Aborted. Secure Map Service not removed.", po_call_args[0][0][0]
        )

        po_call_args = mock_input.call_args_list
        self.assertEqual(2, len(po_call_args))
        self.assertEqual(
            "Are you sure you want to delete this Secure Map Service? [y/n]: ",
            po_call_args[0][0][0]
        )
        self.assertEqual('Please enter either "y" or "n": ', po_call_args[1][0][0])


    @mock.patch("tethys_cli.services_commands.input")
    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_cli.services_commands.exit")
    @mock.patch("tethys_services.models.SecureMapService")
    def test_services_remove_secure_map_command_proceed(self, mock_service, mock_exit, mock_pretty_output, mock_input):
        """
        Test for services_remove_secure_map_command
        For when deleting is not forced, and when prompted, giving a valid answer to delete
        :param mock_service:  mock for SecureMapService
        :param mock_exit:  mock for handling exit() code in function
        :param mock_pretty_output:  mock for pretty_output text
        :param mock_input:  mock for handling raw_input requests
        :return:
        """
        mock_args = mock.MagicMock()
        mock_service._meta.verbose_name = "Secure Map Service"

        mock_args.force = False
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit
        mock_input.side_effect = ["y"]

        self.assertRaises(SystemExit, services_remove_secure_map_command, mock_args)

        mock_service.objects.get().delete.assert_called_once()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "Successfully removed Secure Map Service 1",
            po_call_args[0][0][0]
        )

    @mock.patch("tethys_cli.services_commands.print")
    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.PostgresPersistentStoreService")
    @mock.patch("tethys_services.models.SpatialDatasetService")
    @mock.patch("tethys_cli.services_commands.model_to_dict")
    @pytest.mark.django_db
    def test_services_list_command_not_spatial_not_persistent(
        self, mock_mtd, mock_spatial, mock_persistent, mock_pretty_output, mock_print
    ):
        """
        Test for services_list_command
        Both spatial and persistent are not set, so both are processed
        :param mock_mtd:  mock for model_to_dict to return a dictionary
        :param mock_spatial:  mock for SpatialDatasetService
        :param mock_persistent:  mock for PostgresPersistentStoreService
        :param mock_pretty_output: mock for pretty_output text
        :param mock_stdout:  mock for text written with print statements
        :return:
        """
        mock_mtd.return_value = self.my_postgres_dict
        mock_args = mock.MagicMock()
        mock_args.spatial = False
        mock_args.persistent = False
        mock_args.dataset = False
        mock_args.wps = False
        mock_args.secure_map = False
        mock_spatial.objects.order_by("id").all.return_value = [
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
        ]
        mock_persistent.objects.order_by("id").all.return_value = [
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
        ]
        services_list_command(mock_args)

        # Check expected pretty_output
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(4, len(po_call_args))
        self.assertIn("Persistent Store Services:", po_call_args[0][0][0])
        self.assertIn("ID", po_call_args[1][0][0])
        self.assertIn("Name", po_call_args[1][0][0])
        self.assertIn("Host", po_call_args[1][0][0])
        self.assertIn("Port", po_call_args[1][0][0])
        self.assertNotIn("Endpoint", po_call_args[1][0][0])
        self.assertNotIn("Public Endpoint", po_call_args[1][0][0])
        self.assertNotIn("API Key", po_call_args[1][0][0])
        self.assertIn("Spatial Dataset Services:", po_call_args[2][0][0])
        self.assertIn("ID", po_call_args[3][0][0])
        self.assertIn("Name", po_call_args[3][0][0])
        self.assertNotIn("Host", po_call_args[3][0][0])
        self.assertNotIn("Port", po_call_args[3][0][0])
        self.assertIn("Endpoint", po_call_args[3][0][0])
        self.assertIn("Public Endpoint", po_call_args[3][0][0])
        self.assertIn("API Key", po_call_args[3][0][0])

        # Check text written with Python's print
        rts_call_args = mock_print.call_args_list
        self.assertIn(self.my_postgres_dict["id"], rts_call_args[0][0][0])
        self.assertIn(self.my_postgres_dict["name"], rts_call_args[0][0][0])
        self.assertIn(self.my_postgres_dict["host"], rts_call_args[0][0][0])
        self.assertIn(self.my_postgres_dict["port"], rts_call_args[0][0][0])
        self.assertIn(self.my_postgres_dict["id"], rts_call_args[4][0][0])
        self.assertIn(self.my_postgres_dict["name"], rts_call_args[4][0][0])
        self.assertNotIn(self.my_postgres_dict["host"], rts_call_args[4][0][0])
        self.assertNotIn(self.my_postgres_dict["port"], rts_call_args[4][0][0])
        self.assertIn(self.my_postgres_dict["endpoint"], rts_call_args[4][0][0])
        self.assertIn(self.my_postgres_dict["public_endpoint"], rts_call_args[4][0][0])
        self.assertIn(self.my_postgres_dict["apikey"], rts_call_args[4][0][0])

    @mock.patch("tethys_cli.services_commands.print")
    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.SpatialDatasetService")
    @mock.patch("tethys_cli.services_commands.model_to_dict")
    def test_services_list_command_spatial(
        self, mock_mtd, mock_spatial, mock_pretty_output, mock_print
    ):
        """
        Test for services_list_command
        Only spatial is set
        :param mock_mtd:  mock for model_to_dict to return a dictionary
        :param mock_spatial:  mock for SpatialDatasetService
        :param mock_pretty_output:  mock for pretty_output text
        :param mock_stdout:  mock for text written with print statements
        :return:
        """
        mock_mtd.return_value = self.my_postgres_dict
        mock_args = mock.MagicMock()
        mock_args.spatial = True
        mock_args.persistent = False
        mock_args.dataset = False
        mock_args.wps = False
        mock_args.secure_map = False
        mock_spatial.objects.order_by("id").all.return_value = [
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
        ]

        services_list_command(mock_args)

        # Check expected pretty_output
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(2, len(po_call_args))
        self.assertIn("Spatial Dataset Services:", po_call_args[0][0][0])
        self.assertIn("ID", po_call_args[1][0][0])
        self.assertIn("Name", po_call_args[1][0][0])
        self.assertNotIn("Host", po_call_args[1][0][0])
        self.assertNotIn("Port", po_call_args[1][0][0])
        self.assertIn("Endpoint", po_call_args[1][0][0])
        self.assertIn("Public Endpoint", po_call_args[1][0][0])
        self.assertIn("API Key", po_call_args[1][0][0])

        # Check text written with Python's print
        rts_call_args = mock_print.call_args_list

        self.assertIn(self.my_postgres_dict["id"], rts_call_args[2][0][0])
        self.assertIn(self.my_postgres_dict["name"], rts_call_args[2][0][0])
        self.assertNotIn(self.my_postgres_dict["host"], rts_call_args[2][0][0])
        self.assertNotIn(self.my_postgres_dict["port"], rts_call_args[2][0][0])
        self.assertIn(self.my_postgres_dict["endpoint"], rts_call_args[2][0][0])
        self.assertIn(self.my_postgres_dict["public_endpoint"], rts_call_args[2][0][0])
        self.assertIn(self.my_postgres_dict["apikey"], rts_call_args[2][0][0])

    @mock.patch("tethys_cli.services_commands.print")
    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.PostgresPersistentStoreService")
    @mock.patch("tethys_services.models.SQLitePersistentStoreService")
    @mock.patch("tethys_cli.services_commands.model_to_dict")
    def test_services_list_command_persistent(
        self,
        mock_mtd,
        mock_sqlite_persistent,
        mock_postgres_persistent,
        mock_pretty_output,
        mock_print,
    ):
        """
        Test for services_list_command
        Only persistent is set
        :param mock_mtd:  mock for model_to_dict to return a dictionary
        :param mock_postgres_persistent:  mock for PostgresPersistentStoreService
        :param mock_pretty_output:  mock for pretty_output text
        :param mock_stdout:  mock for text written with print statements
        :return:
        """
        mock_mtd.side_effect = [self.my_postgres_dict, self.my_sqlite_dict]
        mock_args = mock.MagicMock()
        mock_args.spatial = False
        mock_args.persistent = True
        mock_args.dataset = False
        mock_args.wps = False
        mock_args.secure_map = False
        mock_postgres_persistent.objects.order_by("id").all.return_value = [
            mock.MagicMock()
        ]
        mock_sqlite_persistent.objects.order_by("id").all.return_value = [
            mock.MagicMock()
        ]

        services_list_command(mock_args)

        # Check expected pretty_output
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(4, len(po_call_args))  # 2 for postgres, 2 for sqlite
        self.assertIn("PostgreSQL Persistent Store Services:", po_call_args[0][0][0])
        self.assertIn("ID", po_call_args[1][0][0])
        self.assertIn("Name", po_call_args[1][0][0])
        self.assertIn("Host", po_call_args[1][0][0])
        self.assertIn("Port", po_call_args[1][0][0])
        self.assertNotIn("Endpoint", po_call_args[1][0][0])
        self.assertNotIn("Public Endpoint", po_call_args[1][0][0])
        self.assertNotIn("API Key", po_call_args[1][0][0])

        self.assertIn("SQLite Persistent Store Services:", po_call_args[2][0][0])
        self.assertIn("ID", po_call_args[3][0][0])
        self.assertIn("Name", po_call_args[3][0][0])
        self.assertIn("Dir Path", po_call_args[3][0][0])

        # Check text written with Python's print
        rts_call_args = mock_print.call_args_list

        self.assertIn(self.my_postgres_dict["id"], rts_call_args[0][0][0])
        self.assertIn(self.my_postgres_dict["name"], rts_call_args[0][0][0])
        self.assertIn(self.my_postgres_dict["host"], rts_call_args[0][0][0])
        self.assertIn(self.my_postgres_dict["port"], rts_call_args[0][0][0])
        self.assertNotIn(self.my_postgres_dict["endpoint"], rts_call_args[0][0][0])
        self.assertNotIn(
            self.my_postgres_dict["public_endpoint"], rts_call_args[0][0][0]
        )
        self.assertNotIn(self.my_postgres_dict["apikey"], rts_call_args[0][0][0])

        self.assertIn(self.my_sqlite_dict["id"], rts_call_args[1][0][0])
        self.assertIn(self.my_sqlite_dict["name"], rts_call_args[1][0][0])
        self.assertIn(self.my_sqlite_dict["dir_path"], rts_call_args[1][0][0])

    @mock.patch("tethys_cli.services_commands.print")
    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.DatasetService")
    @mock.patch("tethys_cli.services_commands.model_to_dict")
    def test_services_list_command_dataset(
        self, mock_mtd, mock_dataset, mock_pretty_output, mock_print
    ):
        """
        Test for services_list_command
        Only dataset is set
        :param mock_mtd:  mock for model_to_dict to return a dictionary
        :param mock_dataset:  mock for DatasetService
        :param mock_pretty_output:  mock for pretty_output text
        :param mock_stdout:  mock for text written with print statements
        :return:
        """
        mock_mtd.return_value = self.my_postgres_dict
        mock_args = mock.MagicMock()
        mock_args.spatial = False
        mock_args.persistent = False
        mock_args.dataset = True
        mock_args.wps = False
        mock_args.secure_map = False
        mock_dataset.objects.order_by("id").all.return_value = [
            mock.MagicMock(),
            mock.MagicMock(),
        ]

        services_list_command(mock_args)

        # Check expected pretty_output
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(2, len(po_call_args))
        self.assertIn("Dataset Services:", po_call_args[0][0][0])
        self.assertIn("ID", po_call_args[1][0][0])
        self.assertIn("Name", po_call_args[1][0][0])
        self.assertIn("Endpoint", po_call_args[1][0][0])
        self.assertIn("Public Endpoint", po_call_args[1][0][0])
        self.assertIn("API Key", po_call_args[1][0][0])
        self.assertNotIn("Host", po_call_args[1][0][0])
        self.assertNotIn("Port", po_call_args[1][0][0])

        # Check text written with Python's print
        rts_call_args = mock_print.call_args_list

        self.assertIn(self.my_postgres_dict["id"], rts_call_args[1][0][0])
        self.assertIn(self.my_postgres_dict["name"], rts_call_args[1][0][0])
        self.assertIn(self.my_postgres_dict["endpoint"], rts_call_args[1][0][0])
        self.assertIn(self.my_postgres_dict["public_endpoint"], rts_call_args[1][0][0])
        self.assertIn(self.my_postgres_dict["apikey"], rts_call_args[1][0][0])
        self.assertNotIn(self.my_postgres_dict["host"], rts_call_args[1][0][0])
        self.assertNotIn(self.my_postgres_dict["port"], rts_call_args[1][0][0])

    @mock.patch("tethys_cli.services_commands.print")
    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.WebProcessingService")
    @mock.patch("tethys_cli.services_commands.model_to_dict")
    def test_services_list_command_wps(
        self, mock_mtd, mock_wps, mock_pretty_output, mock_print
    ):
        """
        Test for services_list_command
        Only wps is set
        :param mock_mtd:  mock for model_to_dict to return a dictionary
        :param mock_wps:  mock for WebProcessingService
        :param mock_pretty_output:  mock for pretty_output text
        :param mock_stdout:  mock for text written with print statements
        :return:
        """
        mock_mtd.return_value = self.my_postgres_dict
        mock_args = mock.MagicMock()
        mock_args.spatial = False
        mock_args.persistent = False
        mock_args.dataset = False
        mock_args.wps = True
        mock_args.secure_map = False
        mock_wps.objects.order_by("id").all.return_value = [
            mock.MagicMock(),
            mock.MagicMock(),
        ]

        services_list_command(mock_args)
        # Check expected pretty_output
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(2, len(po_call_args))
        self.assertIn("Web Processing Services:", po_call_args[0][0][0])
        self.assertIn("ID", po_call_args[1][0][0])
        self.assertIn("Name", po_call_args[1][0][0])
        self.assertIn("Endpoint", po_call_args[1][0][0])
        self.assertIn("Public Endpoint", po_call_args[1][0][0])
        self.assertNotIn("Host", po_call_args[1][0][0])
        self.assertNotIn("Port", po_call_args[1][0][0])
        self.assertNotIn("API Key", po_call_args[1][0][0])

        # Check text written with Python's print
        rts_call_args = mock_print.call_args_list

        self.assertIn(self.my_postgres_dict["id"], rts_call_args[1][0][0])
        self.assertIn(self.my_postgres_dict["name"], rts_call_args[1][0][0])
        self.assertIn(self.my_postgres_dict["endpoint"], rts_call_args[1][0][0])
        self.assertIn(self.my_postgres_dict["public_endpoint"], rts_call_args[1][0][0])
        self.assertNotIn(self.my_postgres_dict["host"], rts_call_args[1][0][0])
        self.assertNotIn(self.my_postgres_dict["port"], rts_call_args[1][0][0])
        self.assertNotIn(self.my_postgres_dict["apikey"], rts_call_args[1][0][0])

    @mock.patch("tethys_cli.services_commands.print")
    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.SecureMapService")
    @mock.patch("tethys_cli.services_commands.model_to_dict")
    def test_services_list_command_secure_map(self, mock_mtd, mock_secure_map, mock_pretty_output, mock_print):
        """
        Test for services_list_command
        Only wps is set
        :param mock_mtd:  mock for model_to_dict to return a dictionary
        :param mock_secure_map:  mock for SecureMapService
        :param mock_pretty_output:  mock for pretty_output text
        :param mock_stdout:  mock for text written with print statements
        :return:
        """
        mock_mtd.return_value = self.my_secure_map_dict
        mock_args = mock.MagicMock()
        mock_args.spatial = False
        mock_args.persistent = False
        mock_args.dataset = False
        mock_args.wps = False
        mock_args.secure_map = True

        mock_secure_map.objects.order_by("id").all.return_value = [
            mock.MagicMock(),
            mock.MagicMock(),
        ]
        services_list_command(mock_args)

        # Check expected pretty_output
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(2, len(po_call_args))
        self.assertIn("Secure Map Services:", po_call_args[0][0][0])
        self.assertIn("ID", po_call_args[1][0][0])
        self.assertIn("Name", po_call_args[1][0][0])
        self.assertIn("Legend", po_call_args[1][0][0])
        self.assertIn("Auth", po_call_args[1][0][0])
        self.assertIn("Credential/Provider", po_call_args[1][0][0])
        self.assertIn("Type", po_call_args[1][0][0])
        self.assertIn("Proxy", po_call_args[1][0][0])
        self.assertIn("Endpoint", po_call_args[1][0][0])

        # Check text written with python's print
        rts_call_args = mock_print.call_args_list
        self.assertIn(self.my_secure_map_dict["id"], rts_call_args[1][0][0])
        self.assertIn(self.my_secure_map_dict["name"], rts_call_args[1][0][0])
        self.assertIn(self.my_secure_map_dict["legend_title"], rts_call_args[1][0][0])
        self.assertIn(
            self.my_secure_map_dict["authentication_method"], rts_call_args[1][0][0]
        )
        self.assertIn("API Key Set", rts_call_args[1][0][0])
        self.assertIn(self.my_secure_map_dict["service_type"], rts_call_args[1][0][0])
        self.assertIn("No", rts_call_args[1][0][0])
        self.assertIn(self.my_secure_map_dict["endpoint"], rts_call_args[1][0][0])

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.DatasetService")
    def test_services_create_dataset_command_IndexError(
        self, mock_service, mock_pretty_output
    ):
        mock_args = mock.MagicMock()
        mock_args.connection = "IndexError:9876@IndexError"  # No 'http' or '://'
        mock_args.type = "HydroShare"

        services_create_dataset_command(mock_args)

        mock_service.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "The connection argument (-c) must be of the form", po_call_args[0][0][0]
        )
        self.assertIn(
            '"<username>:<password>@<protocol>//<host>:<port>".', po_call_args[0][0][0]
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.DatasetService")
    def test_services_create_dataset_command_FormatError(
        self, mock_service, mock_pretty_output
    ):
        mock_args = mock.MagicMock()
        mock_args.connection = "foo:pass@http:://foo:1234"
        mock_args.public_endpoint = "foo@foo:foo"  # No 'http' or '://'
        mock_args.type = "HydroShare"

        services_create_dataset_command(mock_args)

        mock_service.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "The public_endpoint argument (-p) must be of the form ",
            po_call_args[0][0][0],
        )
        self.assertIn('"<protocol>//<host>:<port>".', po_call_args[0][0][0])

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.DatasetService")
    def test_services_create_dataset_command_IntegrityError(
        self, mock_service, mock_pretty_output
    ):
        mock_args = mock.MagicMock()
        mock_args.connection = "foo:pass@http:://foo:1234"
        mock_args.public_endpoint = "http://foo:1234"
        mock_args.type = "HydroShare"
        mock_service.side_effect = IntegrityError

        services_create_dataset_command(mock_args)

        mock_service.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn("Dataset Service with name ", po_call_args[0][0][0])
        self.assertIn("already exists. Command aborted.", po_call_args[0][0][0])

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.DatasetService")
    def test_services_create_dataset_command_hydroshare(
        self, mock_service, mock_pretty_output
    ):
        mock_args = mock.MagicMock(
            connection="foo:pass@http://localhost:80",
            public_endpoint="http://www.example.com:80",
            apikey="apikey123",
            type="HydroShare",
        )
        mock_args.name = "test_hydroshare"

        services_create_dataset_command(mock_args)

        mock_service.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual(
            "Successfully created new Dataset Service!", po_call_args[0][0][0]
        )
        mock_service.assert_called_with(
            name="test_hydroshare",
            endpoint="http://localhost:80",
            public_endpoint="http://www.example.com:80",
            apikey="apikey123",
            username="foo",
            password="pass",
            engine=mock_service.HYDROSHARE,
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.DatasetService")
    def test_services_create_dataset_command_ckan(
        self, mock_service, mock_pretty_output
    ):
        mock_args = mock.MagicMock(
            connection="foo:pass@http://localhost:80",
            public_endpoint="http://www.example.com:80",
            apikey="apikey123",
            type="CKAN",
        )
        mock_args.name = "test_ckan"

        services_create_dataset_command(mock_args)

        mock_service.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual(
            "Successfully created new Dataset Service!", po_call_args[0][0][0]
        )
        mock_service.assert_called_with(
            name="test_ckan",
            endpoint="http://localhost:80",
            public_endpoint="http://www.example.com:80",
            apikey="apikey123",
            username="foo",
            password="pass",
            engine=mock_service.CKAN,
        )

    @mock.patch("tethys_cli.services_commands.input")
    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_cli.services_commands.exit")
    @mock.patch("tethys_services.models.DatasetService")
    def test_services_remove_dataset_command_proceed(
        self, mock_service, mock_exit, mock_pretty_output, mock_input
    ):
        mock_args = mock.MagicMock()
        mock_service._meta.verbose_name = "Dataset Service"

        mock_args.force = False
        mock_exit.side_effect = SystemExit
        mock_input.side_effect = ["y"]

        self.assertRaises(SystemExit, services_remove_dataset_command, mock_args)

        mock_service.objects.get().delete.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn("Successfully removed Dataset Service", po_call_args[0][0][0])

        po_call_args = mock_input.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual(
            "Are you sure you want to delete this Dataset Service? [y/n]: ",
            po_call_args[0][0][0],
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.WebProcessingService")
    def test_services_create_wps_command_IndexError(
        self, mock_service, mock_pretty_output
    ):
        mock_args = mock.MagicMock()
        mock_args.connection = "IndexError:9876@IndexError"  # No 'http' or '://'

        services_create_wps_command(mock_args)

        mock_service.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "The connection argument (-c) must be of the form", po_call_args[0][0][0]
        )
        self.assertIn(
            '"<username>:<password>@<protocol>//<host>:<port>".', po_call_args[0][0][0]
        )

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.WebProcessingService")
    def test_services_create_wps_command_IntegrityError(
        self, mock_service, mock_pretty_output
    ):
        mock_args = mock.MagicMock()
        mock_args.connection = "foo:pass@http:://foo:1234"
        mock_args.public_endpoint = "http://foo:1234"
        mock_service.side_effect = IntegrityError

        services_create_wps_command(mock_args)

        mock_service.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn("Web Processing Service with name ", po_call_args[0][0][0])
        self.assertIn("already exists. Command aborted.", po_call_args[0][0][0])

    @mock.patch("tethys_cli.services_commands.pretty_output")
    @mock.patch("tethys_services.models.WebProcessingService")
    def test_services_create_wps_command(self, mock_service, mock_pretty_output):
        mock_args = mock.MagicMock()
        mock_args.connection = "foo:pass@http:://foo:1234"
        mock_service.return_value = mock.MagicMock()

        services_create_wps_command(mock_args)

        mock_service.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual(
            "Successfully created new Web Processing Service!", po_call_args[0][0][0]
        )
