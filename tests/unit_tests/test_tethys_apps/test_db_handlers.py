from tethys_sdk.testing import TethysTestCase
from tethys_apps.db_handlers import (
    PostgresDatabaseHandler,
    SQLiteDatabaseHandler,
    PersistentStoreDatabaseHandler,
)
from tethys_apps.exceptions import (
    PersistentStorePermissionError,
)
from unittest import mock
from tethys_portal.optional_dependencies import optional_import

sqlalchemy = optional_import("sqlalchemy")


class PersistentStoreDatabaseHandlerTests(TethysTestCase):

    def test_create_database_not_implemented(self):
        handler = PersistentStoreDatabaseHandler()
        with self.assertRaises(NotImplementedError):
            handler.create_database(None, None, None, None)

    def test_drop_database_not_implemented(self):
        handler = PersistentStoreDatabaseHandler()
        with self.assertRaises(NotImplementedError):
            handler.drop_database(None, None, None, None)

    def test_database_exists_not_implemented(self):
        handler = PersistentStoreDatabaseHandler()
        with self.assertRaises(NotImplementedError):
            handler.database_exists(None, None, None, None)

    def test_enable_postgis_extension_not_implemented(self):
        handler = PersistentStoreDatabaseHandler()
        try:
            handler.enable_spatial_extension(None, None, None, None)
        except NotImplementedError:
            self.fail(
                "enable_spatial_extension should not raise NotImplementedError by default"
            )


class PostgresDatabaseHandlerTests(TethysTestCase):

    def test_create_database(self):
        mock_engine = mock.MagicMock()
        mock_model = mock.MagicMock()
        mock_url = mock.MagicMock(username="some user")
        namespaced_ps_name = "test_database"
        handler = PostgresDatabaseHandler()

        handler.create_database(mock_model, mock_engine, mock_url, namespaced_ps_name)

        rts_call_args = mock_engine.connect().execute.call_args_list
        self.assertEqual("commit", rts_call_args[0][0][0])
        self.assertEqual(
            f"""
            CREATE DATABASE "{namespaced_ps_name}"
            WITH OWNER {mock_url.username}
            ENCODING 'UTF8'
        """,
            rts_call_args[1][0][0],
        )

        mock_engine.connect().close.assert_called_once()

    def test_create_database_permission_error(self):
        mock_engine = mock.MagicMock()
        mock_model = mock.MagicMock()
        mock_url = mock.MagicMock(username="some user")
        namespaced_ps_name = "test_database"
        handler = PostgresDatabaseHandler()

        # Configure the mock to raise a ProgrammingError when execute is called
        mock_engine.connect().execute.side_effect = [
            sqlalchemy.exc.ProgrammingError(statement=None, params=None, orig=None)
        ]

        with self.assertRaises(PersistentStorePermissionError) as context:
            handler.create_database(
                mock_model, mock_engine, mock_url, namespaced_ps_name
            )

        self.assertIn(
            f'Database user "{mock_url.username}" has insufficient permissions to create '
            f'the persistent store database "{mock_model.name}": must have CREATE DATABASES permission at a minimum.',
            str(context.exception),
        )

        mock_engine.connect().close.assert_called_once()

    def test_drop_database(self):
        mock_engine = mock.MagicMock()
        mock_model = mock.MagicMock()
        mock_url = mock.MagicMock(username="some user")
        namespaced_ps_name = "test_database"
        handler = PostgresDatabaseHandler()

        handler.drop_database(mock_model, mock_engine, mock_url, namespaced_ps_name)

        rts_call_args = mock_engine.connect().execute.call_args_list
        self.assertEqual("commit", rts_call_args[0][0][0])
        self.assertEqual(
            f'DROP DATABASE IF EXISTS "{namespaced_ps_name}"', rts_call_args[1][0][0]
        )

        mock_engine.connect().close.assert_called_once()

    def test_drop_database_in_use_on_execute(self):
        mock_engine = mock.MagicMock()
        mock_model = mock.MagicMock()
        mock_url = mock.MagicMock(username="some user")
        namespaced_ps_name = "test_database"
        handler = PostgresDatabaseHandler()

        # Configure the mock to raise an Exception indicating the database is being accessed by other users
        mock_engine.connect().execute.side_effect = [
            None,
            Exception("being accessed by other users"),
            None,
            None,
            None,
        ]

        handler.drop_database(mock_model, mock_engine, mock_url, namespaced_ps_name)

        rts_call_args = mock_engine.connect().execute.call_args_list
        self.assertEqual("commit", rts_call_args[0][0][0])
        self.assertEqual(
            f'DROP DATABASE IF EXISTS "{namespaced_ps_name}"', rts_call_args[1][0][0]
        )

        # Check that the disconnect sessions statement was executed
        disconnect_sessions_statement = f"""
                                                SELECT pg_terminate_backend(pg_stat_activity.pid)
                                                FROM pg_stat_activity
                                                WHERE pg_stat_activity.datname = '{namespaced_ps_name}'
                                                AND pg_stat_activity.pid <> pg_backend_pid();
                                                """
        self.assertEqual(disconnect_sessions_statement, rts_call_args[2][0][0])
        self.assertEqual("commit", rts_call_args[3][0][0])

        # Check that the drop database statement was attempted again after disconnecting sessions
        self.assertEqual(
            f'DROP DATABASE IF EXISTS "{namespaced_ps_name}"', rts_call_args[4][0][0]
        )

        mock_engine.connect().close.assert_called_once()

    def test_drop_database_in_use_on_connect(self):
        mock_engine = mock.MagicMock()
        mock_model = mock.MagicMock()
        mock_url = mock.MagicMock(username="some user")
        namespaced_ps_name = "test_database"
        handler = PostgresDatabaseHandler()

        # Configure the mock to raise an Exception indicating the database is being accessed by other users
        mock_engine.connect.side_effect = Exception("being accessed by other users")

        handler.drop_database(mock_model, mock_engine, mock_url, namespaced_ps_name)

        mock_engine.connect.assert_called_once()

    def test_drop_database_other_exception(self):
        mock_engine = mock.MagicMock()
        mock_model = mock.MagicMock()
        mock_url = mock.MagicMock(username="some user")
        namespaced_ps_name = "test_database"
        handler = PostgresDatabaseHandler()

        # Configure the mock to raise a generic Exception
        mock_engine.connect().execute.side_effect = Exception("some other error")

        with self.assertRaises(Exception) as context:
            handler.drop_database(mock_model, mock_engine, mock_url, namespaced_ps_name)

        self.assertIn("some other error", str(context.exception))

        mock_engine.connect().close.assert_called_once()

    def test_database_exists(self):
        mock_engine = mock.MagicMock()
        mock_model = mock.MagicMock()
        mock_url = mock.MagicMock(username="some user")
        namespaced_ps_name = "test_database"
        handler = PostgresDatabaseHandler()

        # Configure the mock to return a result indicating the database exists
        mock_result = mock.MagicMock()
        mock_result.name = namespaced_ps_name
        mock_engine.connect().execute.return_value = [mock_result]

        exists = handler.database_exists(
            mock_model, mock_engine, mock_url, namespaced_ps_name
        )

        self.assertTrue(exists)
        rts_call_args = mock_engine.connect().execute.call_args_list
        self.assertEqual(
            f"""
            SELECT d.datname as name
            FROM pg_catalog.pg_database d
            LEFT JOIN pg_catalog.pg_user u ON d.datdba = u.usesysid
            WHERE d.datname = '{namespaced_ps_name}';
        """,
            rts_call_args[0][0][0],
        )
        mock_engine.connect().close.assert_called_once()

    def test_database_not_exists(self):
        mock_engine = mock.MagicMock()
        mock_model = mock.MagicMock()
        mock_url = mock.MagicMock(username="some user")
        namespaced_ps_name = "test_database"
        handler = PostgresDatabaseHandler()

        # Configure the mock to return a result indicating the database does not exist
        mock_result = mock.MagicMock()
        mock_result.name = "some other name"
        mock_engine.connect().execute.return_value = [mock_result]

        exists = handler.database_exists(
            mock_model, mock_engine, mock_url, namespaced_ps_name
        )

        self.assertFalse(exists)
        rts_call_args = mock_engine.connect().execute.call_args_list
        self.assertEqual(
            f"""
            SELECT d.datname as name
            FROM pg_catalog.pg_database d
            LEFT JOIN pg_catalog.pg_user u ON d.datdba = u.usesysid
            WHERE d.datname = '{namespaced_ps_name}';
        """,
            rts_call_args[0][0][0],
        )
        mock_engine.connect().close.assert_called_once()

    @mock.patch("tethys_apps.db_handlers.logging")
    def test_enable_postgis_extension_version_2_5_detected(self, mock_db_handler_log):
        mock_new_engine = mock.MagicMock()
        mock_model = mock.MagicMock()
        mock_model.get_value.return_value = mock_new_engine
        mock_url = mock.MagicMock(username="some user")
        handler = PostgresDatabaseHandler()

        mock_db_connection = mock_new_engine.connect()
        mock_db_connection.execute.side_effect = [
            mock.MagicMock(),  # Enable PostGIS Statement
            [
                mock.MagicMock(postgis_version="2.5 USE_GEOS=1 USE_PROJ=1 USE_STATS=1")
            ],  # Check PostGIS Version
            mock.MagicMock(),  # Enable PostGIS Raster Statement
        ]

        handler.enable_spatial_extension(mock_model, mock.MagicMock(), mock_url, "")

        rts_call_args = mock_new_engine.connect().execute.call_args_list
        self.assertEqual(
            "CREATE EXTENSION IF NOT EXISTS postgis;", rts_call_args[0][0][0]
        )
        self.assertEqual("SELECT PostGIS_Version();", rts_call_args[1][0][0])

        mock_new_engine.connect().close.assert_called_once()

        mock_db_handler_log_info_calls = (
            mock_db_handler_log.getLogger().info.call_args_list
        )
        self.assertEqual(1, len(mock_db_handler_log_info_calls))
        check_log = "Detected PostGIS version 2.5"
        self.assertEqual(check_log, mock_db_handler_log_info_calls[0][0][0])

    @mock.patch("tethys_apps.db_handlers.logging")
    def test_enable_postgis_extension_version_3_5_detected(self, mock_db_handler_log):
        mock_new_engine = mock.MagicMock()
        mock_model = mock.MagicMock()
        mock_model.name = "spatial_db"
        mock_model.tethys_app.package = "test_app"
        mock_model.get_value.return_value = mock_new_engine
        mock_url = mock.MagicMock(username="some user")
        handler = PostgresDatabaseHandler()

        mock_db_connection = mock_new_engine.connect()
        mock_db_connection.execute.side_effect = [
            mock.MagicMock(),  # Enable PostGIS Statement
            [
                mock.MagicMock(postgis_version="3.5 USE_GEOS=1 USE_PROJ=1 USE_STATS=1")
            ],  # Check PostGIS Version
            mock.MagicMock(),  # Enable PostGIS Raster Statement
        ]

        handler.enable_spatial_extension(mock_model, mock.MagicMock(), mock_url, "")

        mock_new_engine.connect().close.assert_called_once()

        mock_execute_calls = mock_db_connection.execute.call_args_list
        self.assertEqual(3, len(mock_execute_calls))
        execute1 = "CREATE EXTENSION IF NOT EXISTS postgis;"
        execute2 = "SELECT PostGIS_Version();"
        execute3 = "CREATE EXTENSION IF NOT EXISTS postgis_raster;"
        self.assertEqual(execute1, mock_execute_calls[0][0][0])
        self.assertEqual(execute2, mock_execute_calls[1][0][0])
        self.assertEqual(execute3, mock_execute_calls[2][0][0])

        mock_db_handler_log_info_calls = (
            mock_db_handler_log.getLogger().info.call_args_list
        )
        self.assertEqual(2, len(mock_db_handler_log_info_calls))
        check_log3 = "Detected PostGIS version 3.5"
        check_log4 = (
            'Enabling PostGIS Raster on database "spatial_db" for app "test_app"...'
        )
        self.assertEqual(check_log3, mock_db_handler_log_info_calls[0][0][0])
        self.assertEqual(check_log4, mock_db_handler_log_info_calls[1][0][0])

    @mock.patch("tethys_apps.db_handlers.logging")
    def test_enable_postgis_extension_bad_version_string(self, mock_db_handler_log):
        mock_new_engine = mock.MagicMock()
        mock_model = mock.MagicMock()
        mock_model.name = "spatial_db"
        mock_model.tethys_app.package = "test_app"
        mock_model.get_value.return_value = mock_new_engine
        mock_url = mock.MagicMock(username="some user")
        handler = PostgresDatabaseHandler()

        mock_db_connection = mock_new_engine.connect()
        mock_db_connection.execute.side_effect = [
            mock.MagicMock(),  # Enable PostGIS Statement
            [
                mock.MagicMock(postgis_version="BAD VERSION STRING")
            ],  # Check PostGIS Version
            mock.MagicMock(),  # Enable PostGIS Raster Statement
        ]

        handler.enable_spatial_extension(mock_model, mock.MagicMock(), mock_url, "")

        mock_new_engine.connect().close.assert_called_once()

        # Check mock calls
        mock_execute_calls = mock_db_connection.execute.call_args_list
        self.assertEqual(2, len(mock_execute_calls))
        execute1 = "CREATE EXTENSION IF NOT EXISTS postgis;"
        execute2 = "SELECT PostGIS_Version();"
        self.assertEqual(execute1, mock_execute_calls[0][0][0])
        self.assertEqual(execute2, mock_execute_calls[1][0][0])

        mock_db_handler_log_warning_calls = (
            mock_db_handler_log.getLogger().warning.call_args_list
        )
        self.assertEqual(1, len(mock_db_handler_log_warning_calls))
        check_log1 = 'Could not parse PostGIS version from "BAD VERSION STRING"'
        self.assertEqual(check_log1, mock_db_handler_log_warning_calls[0][0][0])

    def test_enable_postgis_extension_permission_error(self):
        mock_new_engine = mock.MagicMock()
        mock_model = mock.MagicMock()
        mock_model.get_value.return_value = mock_new_engine
        mock_url = mock.MagicMock(username="some user")
        handler = PostgresDatabaseHandler()

        mock_db_connection = mock_new_engine.connect()
        # Configure the mock to raise a ProgrammingError when execute is called
        mock_db_connection.execute.side_effect = [
            sqlalchemy.exc.ProgrammingError(statement=None, params=None, orig=None)
        ]

        with self.assertRaises(PersistentStorePermissionError) as context:
            handler.enable_spatial_extension(mock_model, mock.MagicMock(), mock_url, "")

        self.assertIn(
            f'Database user "{mock_url.username}" has insufficient permissions to enable spatial extension on persistent store database "{mock_model.name}": must be a superuser.',
            str(context.exception),
        )

        mock_db_connection.close.assert_called_once()


class SQLiteDatabaseHandlerTests(TethysTestCase):

    def test_create_database(self):
        handler = SQLiteDatabaseHandler()
        mock_model = mock.MagicMock()
        namespaced_ps_name = "test_db"
        dir_path = "/fake/path"
        db_path = f"{dir_path}/{namespaced_ps_name}.sqlite"
        mock_model.get_value.return_value = f"sqlite:///{db_path}"

        with (
            mock.patch("os.path.isfile") as mock_isfile,
            mock.patch("sqlite3.connect") as mock_sqlite_connect,
        ):
            # Simulate that the database file does not exist
            mock_isfile.return_value = False

            handler.create_database(mock_model, None, None, namespaced_ps_name)

            # Check that sqlite3.connect was called to create the database file
            mock_sqlite_connect.assert_called_once_with(db_path)

    def test_create_database_existing_file(self):
        handler = SQLiteDatabaseHandler()
        mock_model = mock.MagicMock()
        namespaced_ps_name = "test_db"
        dir_path = "/fake/path"
        db_path = f"{dir_path}/{namespaced_ps_name}.sqlite"
        mock_model.get_value.return_value = f"sqlite:///{db_path}"

        with (
            mock.patch("os.path.isfile") as mock_isfile,
            mock.patch("sqlite3.connect") as mock_sqlite_connect,
        ):
            # Simulate that the database file exists
            mock_isfile.return_value = True

            handler.create_database(mock_model, None, None, namespaced_ps_name)

            # Check that sqlite3.connect was not called since the database file exists
            mock_sqlite_connect.assert_not_called()

    def test_drop_database(self):
        handler = SQLiteDatabaseHandler()
        mock_model = mock.MagicMock()
        namespaced_ps_name = "test_db"
        dir_path = "/fake/path"
        db_path = f"{dir_path}/{namespaced_ps_name}.sqlite"
        mock_model.get_value.return_value = f"sqlite:///{db_path}"

        with (
            mock.patch("os.path.isfile") as mock_isfile,
            mock.patch("os.remove") as mock_os_remove,
        ):
            # Simulate that the database file exists
            mock_isfile.return_value = True

            handler.drop_database(mock_model, None, None, namespaced_ps_name)

            # Check that os.remove was called to delete the database file
            mock_os_remove.assert_called_once_with(db_path)

    def test_drop_database_nonexistent_file(self):
        handler = SQLiteDatabaseHandler()
        mock_model = mock.MagicMock()
        namespaced_ps_name = "test_db"
        dir_path = "/fake/path"
        db_path = f"{dir_path}/{namespaced_ps_name}.sqlite"
        mock_model.get_value.return_value = f"sqlite:///{db_path}"

        with (
            mock.patch("os.path.isfile") as mock_isfile,
            mock.patch("os.remove") as mock_os_remove,
        ):
            # Simulate that the database file does not exist
            mock_isfile.return_value = False

            handler.drop_database(mock_model, None, None, namespaced_ps_name)

            # Check that os.remove was not called since the database file does not exist
            mock_os_remove.assert_not_called()

    def test_database_exists(self):
        handler = SQLiteDatabaseHandler()
        mock_model = mock.MagicMock()
        namespaced_ps_name = "test_db"
        dir_path = "/fake/path"
        mock_model.get_value.return_value = f"sqlite:///{dir_path}"

        with mock.patch("os.path.isfile") as mock_isfile:
            # Simulate that the database file exists
            mock_isfile.return_value = True

            exists = handler.database_exists(mock_model, None, None, namespaced_ps_name)

            self.assertTrue(exists)

            # Simulate that the database file does not exist
            mock_isfile.return_value = False

            exists = handler.database_exists(mock_model, None, None, namespaced_ps_name)

            self.assertFalse(exists)

    def test_database_exists_bad_url(self):
        handler = SQLiteDatabaseHandler()
        mock_model = mock.MagicMock()
        namespaced_ps_name = "test_db"
        dir_path = "/fake/path"
        mock_model.get_value.return_value = dir_path  # Not a valid SQLite URL

        exists = handler.database_exists(mock_model, None, None, namespaced_ps_name)

        self.assertFalse(exists)
