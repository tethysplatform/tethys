import logging
import os
from tethys_apps.exceptions import (
    PersistentStorePermissionError,
)
from tethys_portal.optional_dependencies import optional_import

sqlalchemy = optional_import("sqlalchemy")
geoalchemy2 = optional_import("geoalchemy2")


class PersistentStoreDatabaseHandler:
    """Base handler for persistent store DB operations."""

    def create_database(self, model):
        raise NotImplementedError()

    def drop_database(self, model):
        raise NotImplementedError()

    def database_exists(self, model):
        raise NotImplementedError()

    def enable_spatial_extension(self, model):
        # optionally implemented by database handlers that support spatial extensions
        pass


class PostgresDatabaseHandler(PersistentStoreDatabaseHandler):
    def create_database(self, model):
        namespaced_ps_name = model.get_namespaced_persistent_store_name()
        url = model.get_value(as_url=True)
        engine = model.get_value(as_engine=True)

        create_connection = engine.connect()
        create_db_statement = f"""
            CREATE DATABASE "{namespaced_ps_name}"
            WITH OWNER {url.username}
            ENCODING 'UTF8'
        """

        try:
            create_connection.execute("commit")
            create_connection.execute(create_db_statement)
        except sqlalchemy.exc.ProgrammingError:
            raise PersistentStorePermissionError(
                f'Database user "{url.username}" has insufficient permissions to create '
                f'the persistent store database "{model.name}": must have CREATE DATABASES permission at a minimum.'
            )
        finally:
            create_connection.close()

    def drop_database(self, model):
        namespaced_ps_name = model.get_namespaced_persistent_store_name()
        engine = model.get_value(as_engine=True)

        drop_db_statement = f'DROP DATABASE IF EXISTS "{namespaced_ps_name}"'
        drop_connection = None

        try:
            drop_connection = engine.connect()
            drop_connection.execute("commit")
            drop_connection.execute(drop_db_statement)
        except Exception as e:
            if "being accessed by other users" in str(e):
                # Force disconnect all other connections to the database
                disconnect_sessions_statement = """
                                                SELECT pg_terminate_backend(pg_stat_activity.pid)
                                                FROM pg_stat_activity
                                                WHERE pg_stat_activity.datname = '{0}'
                                                AND pg_stat_activity.pid <> pg_backend_pid();
                                                """.format(
                    namespaced_ps_name
                )
                if drop_connection:
                    drop_connection.execute(disconnect_sessions_statement)

                    # Try again to drop the database
                    drop_connection.execute("commit")
                    drop_connection.execute(drop_db_statement)
            else:
                raise e
        finally:
            if drop_connection:
                drop_connection.close()

    def database_exists(self, model):
        namespaced_ps_name = model.get_namespaced_persistent_store_name()
        engine = model.get_value(as_engine=True)

        connection = engine.connect()
        existing_query = f"""
            SELECT d.datname as name
            FROM pg_catalog.pg_database d
            LEFT JOIN pg_catalog.pg_user u ON d.datdba = u.usesysid
            WHERE d.datname = '{namespaced_ps_name}';
        """
        existing_dbs = connection.execute(existing_query)
        connection.close()
        for existing_db in existing_dbs:
            if existing_db.name == namespaced_ps_name:
                return True
        return False

    def enable_spatial_extension(self, model):
        log = logging.getLogger("tethys")

        url = model.get_value(as_url=True)
        new_db_engine = model.get_value(with_db=True, as_engine=True)
        new_db_connection = new_db_engine.connect()

        try:
            new_db_connection.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
            ret = new_db_connection.execute("SELECT PostGIS_Version();")
            postgis_version = None
            for r in ret:
                try:
                    postgis_version = float(r.postgis_version.split(" ")[0])
                    log.info(f"Detected PostGIS version {postgis_version}")
                    break
                except Exception:
                    log.warning(
                        f'Could not parse PostGIS version from "{r.postgis_version}"'
                    )
                    continue
            if postgis_version is not None and postgis_version >= 3.0:
                log.info(
                    f'Enabling PostGIS Raster on database "{model.name}" for app "{model.tethys_app.package}"...'
                )
                new_db_connection.execute(
                    "CREATE EXTENSION IF NOT EXISTS postgis_raster;"
                )
        except sqlalchemy.exc.ProgrammingError:
            raise PersistentStorePermissionError(
                f'Database user "{url.username}" has insufficient permissions to enable spatial extension on persistent store database "{model.name}": must be a superuser.'
            )
        finally:
            new_db_connection.close()


class SQLiteDatabaseHandler(PersistentStoreDatabaseHandler):
    def create_database(self, model):
        db_path = model.get_value(with_db=True, as_url=True)
        db_path = db_path.replace("sqlite:///", "")
        if not os.path.isfile(db_path):
            import sqlite3

            sqlite3.connect(db_path).close()

    def drop_database(self, model):
        db_path = model.get_value(with_db=True, as_url=True)
        db_path = db_path.replace("sqlite:///", "")
        if os.path.isfile(db_path):
            os.remove(db_path)

    def database_exists(self, model):
        db_path = model.get_value(with_db=True, as_url=True)
        db_path = db_path.replace("sqlite:///", "")
        return os.path.isfile(db_path)

    def enable_spatial_extension(self, model):
        log = logging.getLogger("tethys")
        engine = model.get_value(as_engine=True)

        try:
            sqlalchemy.event.listen(engine, "connect", geoalchemy2.load_spatialite)
            engine.connect().close()
            log.info(f"SpatiaLite extension enabled on database {model.name}")
        except Exception as e:
            log.warning(
                f"Could not enable SpatiaLite extension on database {model.name}: {e}"
            )
            if "The SPATIALITE_LIBRARY_PATH environment variable is not set" in str(e):
                log.warning(
                    "To enable SpatiaLite support, Install and set the SPATIALITE_LIBRARY_PATH environment variable to the path of the SpatiaLite library on your system. Check https://www.gaia-gis.it/fossil/libspatialite/home for installation instructions."
                )
