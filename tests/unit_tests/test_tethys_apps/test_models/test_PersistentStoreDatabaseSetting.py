import pytest
from tethys_sdk.testing import TethysTestCase
from tethys_apps.models import (
    TethysApp,
    PersistentStoreDatabaseSetting,
    PersistentStoreService,
)
from django.core.exceptions import ValidationError
from tethys_apps.exceptions import (
    TethysAppSettingNotAssigned,
    PersistentStorePermissionError,
    PersistentStoreInitializerError,
)
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from unittest import mock


class PersistentStoreDatabaseSettingTests(TethysTestCase):
    def set_up(self):
        self.test_app = TethysApp.objects.get(package="test_app")

        self.conn = {
            "USER": "tethys_super",
            "PASSWORD": "pass",
            "HOST": "localhost",
            "PORT": "5435",
        }

        self.expected_url = "postgresql://{}:{}@{}:{}".format(
            self.conn["USER"],
            self.conn["PASSWORD"],
            self.conn["HOST"],
            self.conn["PORT"],
        )

        self.pss = PersistentStoreService(
            name="test_ps",
            host=self.conn["HOST"],
            port=self.conn["PORT"],
            username=self.conn["USER"],
            password=self.conn["PASSWORD"],
        )

        self.pss.save()

    def tear_down(self):
        pass

    def test_clean_validation_error(self):
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = None
        ps_ds_setting.save()
        # Check ValidationError
        self.assertRaises(
            ValidationError,
            self.test_app.settings_set.select_subclasses().get(name="spatial_db").clean,
        )

    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.create_persistent_store_database"
    )
    def test_initialize(self, mock_create):
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = self.pss
        ps_ds_setting.save()

        # Execute
        self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        ).initialize()

        mock_create.assert_called()

    @mock.patch("tethys_apps.models.is_testing_environment")
    def test_get_namespaced_persistent_store_name(self, mock_ite):
        mock_ite.return_value = False
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = self.pss
        ps_ds_setting.save()

        # Execute
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="spatial_db")
            .get_namespaced_persistent_store_name()
        )

        # Check result
        self.assertEqual("test_app_spatial_db", ret)

    @mock.patch("tethys_apps.models.is_testing_environment")
    def test_get_namespaced_persistent_store_name_testing(self, mock_ite):
        mock_ite.return_value = True
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = self.pss
        ps_ds_setting.save()

        # Execute
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="spatial_db")
            .get_namespaced_persistent_store_name()
        )

        # Check result
        self.assertEqual("test_app_tethys-testing_spatial_db", ret)

    def test_get_value(self):
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = self.pss
        ps_ds_setting.save()

        # Execute
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="spatial_db")
            .get_value(with_db=True)
        )

        # Check results
        self.assertIsInstance(ret, PersistentStoreService)
        self.assertEqual("test_ps", ret.name)
        self.assertEqual(self.conn["HOST"], ret.host)
        self.assertEqual(int(self.conn["PORT"]), ret.port)
        self.assertEqual(self.conn["USER"], ret.username)
        self.assertEqual(self.conn["PASSWORD"], ret.password)

    def test_get_value_none(self):
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = None
        ps_ds_setting.save()

        self.assertRaises(
            TethysAppSettingNotAssigned,
            PersistentStoreDatabaseSetting.objects.get(name="spatial_db").get_value,
        )

    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.get_namespaced_persistent_store_name"
    )
    def test_get_value_with_db(self, mock_gn):
        mock_gn.return_value = "test_database"
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = self.pss
        ps_ds_setting.save()

        # Execute
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="spatial_db")
            .get_value(with_db=True)
        )

        self.assertIsInstance(ret, PersistentStoreService)
        self.assertEqual("test_database", ret.database)

    def test_get_value_as_engine(self):
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = self.pss
        ps_ds_setting.save()

        # Execute
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="spatial_db")
            .get_value(as_engine=True)
        )

        self.assertIsInstance(ret, Engine)
        self.assertEqual(self.expected_url, str(ret.url))

    def test_get_value_as_sessionmaker(self):
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = self.pss
        ps_ds_setting.save()

        # Execute
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="spatial_db")
            .get_value(as_sessionmaker=True)
        )

        self.assertIsInstance(ret, sessionmaker)
        self.assertEqual(self.expected_url, str(ret.kw["bind"].url))

    def test_get_value_as_url(self):
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = self.pss
        ps_ds_setting.save()

        # Execute
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="spatial_db")
            .get_value(as_url=True)
        )

        # check URL
        self.assertEqual(self.expected_url, str(ret))

    def test_persistent_store_database_exists(self):
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = self.pss
        ps_ds_setting.save()

        ps_ds_setting.get_namespaced_persistent_store_name = mock.MagicMock(
            return_value="foo_bar"
        )
        ps_ds_setting.get_value = mock.MagicMock()
        mock_engine = ps_ds_setting.get_value()
        mock_db = mock.MagicMock()
        mock_db.name = "foo_bar"
        mock_engine.connect().execute.return_value = [mock_db]

        # Execute
        ret = ps_ds_setting.persistent_store_database_exists()

        self.assertTrue(ret)

    def test_persistent_store_database_exists_false(self):
        ps_ds_setting = self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        )
        ps_ds_setting.persistent_store_service = self.pss
        ps_ds_setting.save()

        ps_ds_setting.get_namespaced_persistent_store_name = mock.MagicMock(
            return_value="foo_bar"
        )
        ps_ds_setting.get_value = mock.MagicMock()
        mock_engine = ps_ds_setting.get_value()
        mock_engine.connect().execute.return_value = []

        # Execute
        ret = ps_ds_setting.persistent_store_database_exists()

        self.assertFalse(ret)

    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.persistent_store_database_exists"
    )
    def test_drop_persistent_store_database_not_exists(self, mock_psd):
        mock_psd.return_value = False

        # Execute
        ret = (
            self.test_app.settings_set.select_subclasses()
            .get(name="spatial_db")
            .drop_persistent_store_database()
        )

        self.assertIsNone(ret)

    @mock.patch("tethys_apps.models.logging")
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting.get_value")
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.persistent_store_database_exists"
    )
    @pytest.mark.django_db
    def test_drop_persistent_store_database(self, mock_psd, mock_get, mock_log):
        mock_psd.return_value = True

        # Execute
        self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        ).drop_persistent_store_database()

        # Check
        mock_log.getLogger().info.assert_called_with(
            'Dropping database "spatial_db" for app "test_app"...'
        )
        mock_get().connect.assert_called()
        rts_call_args = mock_get().connect().execute.call_args_list
        self.assertEqual("commit", rts_call_args[0][0][0])
        self.assertEqual(
            'DROP DATABASE IF EXISTS "test_app_tethys-testing_spatial_db"',
            rts_call_args[1][0][0],
        )
        mock_get().connect().close.assert_called()

    @mock.patch("tethys_apps.models.logging")
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting.get_value")
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.persistent_store_database_exists"
    )
    def test_drop_persistent_store_database_exception(
        self, mock_psd, mock_get, mock_log
    ):
        mock_psd.return_value = True
        mock_get().connect().execute.side_effect = [
            Exception("Message: being accessed by other users"),
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
        ]

        # Execute
        self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        ).drop_persistent_store_database()

        # Check
        mock_log.getLogger().info.assert_called_with(
            'Dropping database "spatial_db" for app "test_app"...'
        )
        mock_get().connect.assert_called()
        rts_call_args = mock_get().connect().execute.call_args_list
        self.assertEqual("commit", rts_call_args[0][0][0])
        self.assertIn(
            "SELECT pg_terminate_backend(pg_stat_activity.pid)", rts_call_args[1][0][0]
        )
        mock_get().connect().close.assert_called()

    @mock.patch("tethys_apps.models.logging")
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting.get_value")
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.persistent_store_database_exists"
    )
    def test_drop_persistent_store_database_connection_exception(
        self, mock_psd, mock_get, mock_log
    ):
        mock_psd.return_value = True
        mock_get().connect.side_effect = [
            Exception("Message: being accessed by other users"),
            mock.MagicMock(),
            mock.MagicMock(),
        ]
        # Execute
        self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        ).drop_persistent_store_database()

        # Check
        mock_log.getLogger().info.assert_called_with(
            'Dropping database "spatial_db" for app "test_app"...'
        )
        mock_get().connect.assert_called()
        mock_get().connect().execute.assert_not_called()
        mock_get().connect().close.assert_not_called()

    @mock.patch("tethys_apps.models.logging")
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting.get_value")
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.persistent_store_database_exists"
    )
    def test_drop_persistent_store_database_exception_else(self, mock_psd, mock_get, _):
        mock_psd.return_value = True
        mock_get().connect().execute.side_effect = [
            Exception("Error Message"),
            mock.MagicMock(),
        ]

        # Execute
        self.assertRaises(
            Exception,
            PersistentStoreDatabaseSetting.objects.get(
                name="spatial_db"
            ).drop_persistent_store_database,
        )

        # Check
        mock_get().connect().close.assert_called()

    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.drop_persistent_store_database"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.get_namespaced_persistent_store_name"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.persistent_store_database_exists"
    )
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting.get_value")
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.initializer_function"
    )
    @mock.patch("tethys_apps.models.logging")
    def test_create_persistent_store_database(
        self, mock_log, mock_init, mock_get, mock_ps_de, mock_gn, mock_drop
    ):
        # Mock Get Name
        mock_gn.return_value = "spatial_db"

        # Mock Drop Database
        mock_drop.return_value = ""

        # Mock persistent_store_database_exists
        mock_ps_de.return_value = True

        # Mock get_values
        mock_url = mock.MagicMock(username="test_app")
        mock_engine = mock.MagicMock()
        mock_new_db_engine = mock.MagicMock()
        mock_init_param = mock.MagicMock()
        mock_get.side_effect = [
            mock_url,
            mock_engine,
            mock_new_db_engine,
            mock_init_param,
        ]

        # Execute
        self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        ).create_persistent_store_database(refresh=True, force_first_time=True)

        # Check mock called
        mock_log_info_calls = mock_log.getLogger().info.call_args_list
        check_log1 = 'Creating database "spatial_db" for app "test_app"...'
        check_log2 = 'Enabling PostGIS on database "spatial_db" for app "test_app"...'
        check_log3 = (
            'Initializing database "spatial_db" for app "test_app" '
            'with initializer "appsettings.model.init_spatial_db"...'
        )
        self.assertEqual(check_log1, mock_log_info_calls[0][0][0])
        self.assertEqual(check_log2, mock_log_info_calls[1][0][0])
        self.assertEqual(check_log3, mock_log_info_calls[2][0][0])
        mock_init.assert_called()

    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.drop_persistent_store_database"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.get_namespaced_persistent_store_name"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.persistent_store_database_exists"
    )
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting.get_value")
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.initializer_function"
    )
    @mock.patch("tethys_apps.models.logging")
    def test_create_persistent_store_database_postgis2(
        self, mock_log, mock_init, mock_get, mock_ps_de, mock_gn, mock_drop
    ):
        # Mock Get Name
        mock_gn.return_value = "spatial_db"

        # Mock Drop Database
        mock_drop.return_value = ""

        # Mock persistent_store_database_exists
        mock_ps_de.return_value = False  # DB does not exist

        # Mock get_values
        mock_url = mock.MagicMock(username="test_app")
        mock_engine = mock.MagicMock()
        mock_new_db_engine = mock.MagicMock()
        mock_db_connection = mock_new_db_engine.connect()
        mock_init_param = mock.MagicMock()
        mock_get.side_effect = [
            mock_url,
            mock_engine,
            mock_new_db_engine,
            mock_init_param,
        ]
        mock_db_connection.execute.side_effect = [
            mock.MagicMock(),  # Enable PostGIS Statement
            [
                mock.MagicMock(postgis_version="2.5 USE_GEOS=1 USE_PROJ=1 USE_STATS=1")
            ],  # Check PostGIS Version
            mock.MagicMock(),  # Enable PostGIS Raster Statement
        ]

        # Execute
        self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        ).create_persistent_store_database(refresh=False, force_first_time=False)

        # Check mock calls
        mock_execute_calls = mock_db_connection.execute.call_args_list
        self.assertEqual(2, len(mock_execute_calls))
        execute1 = "CREATE EXTENSION IF NOT EXISTS postgis;"
        execute2 = "SELECT PostGIS_Version();"
        self.assertEqual(execute1, mock_execute_calls[0][0][0])
        self.assertEqual(execute2, mock_execute_calls[1][0][0])

        mock_log_info_calls = mock_log.getLogger().info.call_args_list
        self.assertEqual(4, len(mock_log_info_calls))
        check_log1 = 'Creating database "spatial_db" for app "test_app"...'
        check_log2 = 'Enabling PostGIS on database "spatial_db" for app "test_app"...'
        check_log3 = "Detected PostGIS version 2.5"
        check_log4 = (
            'Initializing database "spatial_db" for app "test_app" '
            'with initializer "appsettings.model.init_spatial_db"...'
        )
        self.assertEqual(check_log1, mock_log_info_calls[0][0][0])
        self.assertEqual(check_log2, mock_log_info_calls[1][0][0])
        self.assertEqual(check_log3, mock_log_info_calls[2][0][0])
        self.assertEqual(check_log4, mock_log_info_calls[3][0][0])
        mock_init.assert_called()

    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.drop_persistent_store_database"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.get_namespaced_persistent_store_name"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.persistent_store_database_exists"
    )
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting.get_value")
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.initializer_function"
    )
    @mock.patch("tethys_apps.models.logging")
    def test_create_persistent_store_database_postgis3(
        self, mock_log, mock_init, mock_get, mock_ps_de, mock_gn, mock_drop
    ):
        # Mock Get Name
        mock_gn.return_value = "spatial_db"

        # Mock Drop Database
        mock_drop.return_value = ""

        # Mock persistent_store_database_exists
        mock_ps_de.return_value = False  # DB does not exist

        # Mock get_values
        mock_url = mock.MagicMock(username="test_app")
        mock_engine = mock.MagicMock()
        mock_new_db_engine = mock.MagicMock()
        mock_db_connection = mock_new_db_engine.connect()
        mock_init_param = mock.MagicMock()
        mock_get.side_effect = [
            mock_url,
            mock_engine,
            mock_new_db_engine,
            mock_init_param,
        ]
        mock_db_connection.execute.side_effect = [
            mock.MagicMock(),  # Enable PostGIS Statement
            [
                mock.MagicMock(postgis_version="3.5 USE_GEOS=1 USE_PROJ=1 USE_STATS=1")
            ],  # Check PostGIS Version
            mock.MagicMock(),  # Enable PostGIS Raster Statement
        ]

        # Execute
        self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        ).create_persistent_store_database(refresh=False, force_first_time=False)

        # Check mock calls
        mock_execute_calls = mock_db_connection.execute.call_args_list
        self.assertEqual(3, len(mock_execute_calls))
        execute1 = "CREATE EXTENSION IF NOT EXISTS postgis;"
        execute2 = "SELECT PostGIS_Version();"
        execute3 = "CREATE EXTENSION IF NOT EXISTS postgis_raster;"
        self.assertEqual(execute1, mock_execute_calls[0][0][0])
        self.assertEqual(execute2, mock_execute_calls[1][0][0])
        self.assertEqual(execute3, mock_execute_calls[2][0][0])

        mock_log_info_calls = mock_log.getLogger().info.call_args_list
        self.assertEqual(5, len(mock_log_info_calls))
        check_log1 = 'Creating database "spatial_db" for app "test_app"...'
        check_log2 = 'Enabling PostGIS on database "spatial_db" for app "test_app"...'
        check_log3 = "Detected PostGIS version 3.5"
        check_log4 = (
            'Enabling PostGIS Raster on database "spatial_db" for app "test_app"...'
        )
        check_log5 = (
            'Initializing database "spatial_db" for app "test_app" '
            'with initializer "appsettings.model.init_spatial_db"...'
        )
        self.assertEqual(check_log1, mock_log_info_calls[0][0][0])
        self.assertEqual(check_log2, mock_log_info_calls[1][0][0])
        self.assertEqual(check_log3, mock_log_info_calls[2][0][0])
        self.assertEqual(check_log4, mock_log_info_calls[3][0][0])
        self.assertEqual(check_log5, mock_log_info_calls[4][0][0])
        mock_init.assert_called()

    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.drop_persistent_store_database"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.get_namespaced_persistent_store_name"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.persistent_store_database_exists"
    )
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting.get_value")
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.initializer_function"
    )
    @mock.patch("tethys_apps.models.logging")
    def test_create_persistent_store_database_postgis3_bad_version_string(
        self, mock_log, mock_init, mock_get, mock_ps_de, mock_gn, mock_drop
    ):
        # Mock Get Name
        mock_gn.return_value = "spatial_db"

        # Mock Drop Database
        mock_drop.return_value = ""

        # Mock persistent_store_database_exists
        mock_ps_de.return_value = False  # DB does not exist

        # Mock get_values
        mock_url = mock.MagicMock(username="test_app")
        mock_engine = mock.MagicMock()
        mock_new_db_engine = mock.MagicMock()
        mock_db_connection = mock_new_db_engine.connect()
        mock_init_param = mock.MagicMock()
        mock_get.side_effect = [
            mock_url,
            mock_engine,
            mock_new_db_engine,
            mock_init_param,
        ]
        mock_db_connection.execute.side_effect = [
            mock.MagicMock(),  # Enable PostGIS Statement
            [
                mock.MagicMock(postgis_version="BAD VERSION STRING")
            ],  # Check PostGIS Version
            mock.MagicMock(),  # Enable PostGIS Raster Statement
        ]

        # Execute
        self.test_app.settings_set.select_subclasses().get(
            name="spatial_db"
        ).create_persistent_store_database(refresh=False, force_first_time=False)

        # Check mock calls
        mock_execute_calls = mock_db_connection.execute.call_args_list
        self.assertEqual(2, len(mock_execute_calls))
        execute1 = "CREATE EXTENSION IF NOT EXISTS postgis;"
        execute2 = "SELECT PostGIS_Version();"
        self.assertEqual(execute1, mock_execute_calls[0][0][0])
        self.assertEqual(execute2, mock_execute_calls[1][0][0])

        mock_log_warning_calls = mock_log.getLogger().warning.call_args_list
        self.assertEqual(1, len(mock_log_warning_calls))
        check_log1 = 'Could not parse PostGIS version from "BAD VERSION STRING"'
        self.assertEqual(check_log1, mock_log_warning_calls[0][0][0])

        mock_log_info_calls = mock_log.getLogger().info.call_args_list
        self.assertEqual(3, len(mock_log_info_calls))
        check_log1 = 'Creating database "spatial_db" for app "test_app"...'
        check_log2 = 'Enabling PostGIS on database "spatial_db" for app "test_app"...'
        check_log3 = (
            'Initializing database "spatial_db" for app "test_app" '
            'with initializer "appsettings.model.init_spatial_db"...'
        )
        self.assertEqual(check_log1, mock_log_info_calls[0][0][0])
        self.assertEqual(check_log2, mock_log_info_calls[1][0][0])
        self.assertEqual(check_log3, mock_log_info_calls[2][0][0])
        mock_init.assert_called()

    @mock.patch("sqlalchemy.exc")
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.drop_persistent_store_database"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.get_namespaced_persistent_store_name"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.persistent_store_database_exists"
    )
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting.get_value")
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.initializer_function"
    )
    @mock.patch("tethys_apps.models.logging")
    def test_create_persistent_store_database_perm_error(
        self, _, __, mock_get, mock_ps_de, mock_gn, mock_drop, mock_e
    ):
        # Mock Get Name
        mock_gn.return_value = "spatial_db"

        # Mock Drop Database
        mock_drop.return_value = ""

        # Mock persistent_store_database_exists
        mock_ps_de.return_value = True

        # Mock get_values
        mock_url = mock.MagicMock(username="test_app")
        mock_engine = mock.MagicMock()
        mock_e.ProgrammingError = Exception
        mock_engine.connect().execute.side_effect = [mock.MagicMock(), Exception]
        mock_get.side_effect = [mock_url, mock_engine]

        # Execute
        self.assertRaises(
            PersistentStorePermissionError,
            PersistentStoreDatabaseSetting.objects.get(
                name="spatial_db"
            ).create_persistent_store_database,
            refresh=True,
        )

    @mock.patch("sqlalchemy.exc")
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.drop_persistent_store_database"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.get_namespaced_persistent_store_name"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.persistent_store_database_exists"
    )
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting.get_value")
    @mock.patch("tethys_apps.models.logging")
    def test_create_persistent_store_database_ext_perm_error(
        self, _, mock_get, mock_ps_de, mock_gn, mock_drop, mock_e
    ):
        # Mock Get Name
        mock_gn.return_value = "spatial_db"

        # Mock Drop Database
        mock_drop.return_value = ""

        # Mock persistent_store_database_exists
        mock_ps_de.return_value = True

        # Mock get_values
        mock_url = mock.MagicMock(username="test_app")
        mock_engine = mock.MagicMock()
        mock_e.ProgrammingError = Exception
        mock_new_db_engine = mock.MagicMock()
        mock_new_db_engine.connect().execute.side_effect = Exception
        mock_get.side_effect = [mock_url, mock_engine, mock_new_db_engine]

        # Execute
        self.assertRaises(
            PersistentStorePermissionError,
            PersistentStoreDatabaseSetting.objects.get(
                name="spatial_db"
            ).create_persistent_store_database,
        )

    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.drop_persistent_store_database"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.get_namespaced_persistent_store_name"
    )
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.persistent_store_database_exists"
    )
    @mock.patch("tethys_apps.models.PersistentStoreDatabaseSetting.get_value")
    @mock.patch(
        "tethys_apps.models.PersistentStoreDatabaseSetting.initializer_function"
    )
    @mock.patch("tethys_apps.models.logging")
    def test_create_persistent_store_database_exception(
        self, _, mock_init, mock_get, mock_ps_de, mock_gn, mock_drop
    ):
        # Mock initializer_function
        mock_init.side_effect = Exception("Initializer Error")
        # Mock Get Name
        mock_gn.return_value = "spatial_db"

        # Mock Drop Database
        mock_drop.return_value = ""

        # Mock persistent_store_database_exists
        mock_ps_de.return_value = True

        # Mock get_values
        mock_url = mock.MagicMock(username="test_app")
        mock_engine = mock.MagicMock()
        mock_new_db_engine = mock.MagicMock()
        mock_init_param = mock.MagicMock()
        mock_get.side_effect = [
            mock_url,
            mock_engine,
            mock_new_db_engine,
            mock_init_param,
        ]

        # Execute
        self.assertRaises(
            PersistentStoreInitializerError,
            PersistentStoreDatabaseSetting.objects.get(
                name="spatial_db"
            ).create_persistent_store_database,
        )
