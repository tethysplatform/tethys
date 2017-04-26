"""
********************************************************************************
* Name: models.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
import sqlalchemy
from django.db import models
from django.core.exceptions import ValidationError
from model_utils.managers import InheritanceManager
from tethys_apps.exceptions import TethysAppSettingNotAssigned, PersistentStorePermissionError, \
    PersistentStoreInitializerError
from tethys_compute.utilities import ListField
from tethys_services.models import (DatasetService, SpatialDatasetService,
                                    WebProcessingService, PersistentStoreService)

from tethys_apps.base.function_extractor import TethysFunctionExtractor


class TethysApp(models.Model):
    """
    DB Model for Tethys Apps
    """
    # The package is enforced to be unique by the file system
    package = models.CharField(max_length=200, unique=True, default='')

    # Portal admin first attributes
    name = models.CharField(max_length=200, default='')
    description = models.TextField(max_length=1000, blank=True, default='')
    enable_feedback = models.BooleanField(default=False)
    feedback_emails = ListField(default='', blank=True)
    tags = models.CharField(max_length=200, blank=True,  default='')

    # Developer first attributes
    index = models.CharField(max_length=200, default='')
    icon = models.CharField(max_length=200, default='')
    root_url = models.CharField(max_length=200, default='')
    color = models.CharField(max_length=10, default='')

    # Portal admin only attributes
    enabled = models.BooleanField(default=True)
    show_in_apps_library = models.BooleanField(default=True)

    class Meta:
        permissions = (
            ('view_app', 'Can see app in library'),
            ('access_app', 'Can access app'),
        )
        verbose_name = 'Tethys App'
        verbose_name_plural = 'Installed Apps'

    def __unicode__(self):
        return unicode(self.name)

    def add_settings(self, setting_list):
        """
        Associate setting with app in database
        """
        if setting_list is not None:
            for setting in setting_list:
                setting.tethys_app = self
                setting.save()

    @property
    def settings(self):
        return self.settings_set.select_subclasses()

    @property
    def custom_settings(self):
        return self.settings_set.exclude(customsetting__isnull=True) \
                .select_subclasses('customsetting')

    @property
    def dataset_service_settings(self):
        return self.settings_set.exclude(datasetservicesetting__isnull=True) \
                .select_subclasses('datasetservicesetting')

    @property
    def spatial_dataset_services_settings(self):
        return self.settings_set.exclude(spatialdatasetservicesetting__isnull=True) \
                .select_subclasses('spatialdatasetservicesetting')

    @property
    def wps_services_settings(self):
        return self.settings_set.exclude(webprocessingservicesetting__isnull=True) \
                .select_subclasses('webprocessingservicesetting')

    @property
    def persistent_store_connection_settings(self):
        return self.settings_set.exclude(persistentstoreconnectionsetting__isnull=True) \
            .select_subclasses('persistentstoreconnectionsetting')

    @property
    def persistent_store_database_settings(self):
        return self.settings_set.exclude(persistentstoredatabasesetting__isnull=True) \
            .select_subclasses('persistentstoredatabasesetting')


class TethysAppSetting(models.Model):
    """
    DB Model for Tethys App Settings
    """
    objects = InheritanceManager()

    tethys_app = models.ForeignKey(TethysApp, on_delete=models.CASCADE,
                                   related_name='settings_set')
    name = models.CharField(max_length=200, default='')
    description = models.TextField(max_length=1000, blank=True, default='')
    required = models.BooleanField(default=True)
    initializer = models.CharField(max_length=1000, default='')
    initialized = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    @property
    def initializer_function(self):
        """
        The function pointed to by the initializer attribute.

        Returns:
            A handle to a Python function that will initialize the database or None if function is not valid.
        """
        func_ext = TethysFunctionExtractor(self.initializer)
        return func_ext.function

    def initialize(self):
        """
        Initialize.
        """
        self.initializer_function(self.initialized)
        self.initialized = True


class CustomSetting(TethysAppSetting):
    """
    DB Model for Tethys App General Setting
    """
    TYPE_STRING = 'STRING'
    TYPE_INTEGER = 'INTEGER'
    TYPE_FLOAT = 'FLOAT'
    TYPE_BOOLEAN = 'BOOLEAN'
    VALID_TYPES = (TYPE_STRING, TYPE_INTEGER, TYPE_FLOAT, TYPE_BOOLEAN)
    VALID_BOOL_STRINGS = ('true', 'false', 'yes', 'no', 't', 'f', 'y', 'n', '1', '0')
    TRUTHY_BOOL_STRINGS = ('true', 'yes', 't', 'y', '1')
    TYPE_CHOICES = (
        (TYPE_STRING, 'String'),
        (TYPE_INTEGER, 'Integer'),
        (TYPE_FLOAT, 'Float'),
        (TYPE_BOOLEAN, 'Boolean'),
    )
    value = models.CharField(max_length=1024, blank=True)
    type = models.CharField(max_length=200, choices=TYPE_CHOICES, default=TYPE_STRING)

    def clean(self):
        """
        Validate prior to saving changes.
        """
        if self.value == '' and self.required:
            raise ValidationError('Required.')

        if self.value != '' and self.type == self.TYPE_FLOAT:
            try:
                float(self.value)
            except:
                raise ValidationError('Value must be a float.')

        elif self.value != '' and self.type == self.TYPE_INTEGER:
            try:
                int(self.value)
            except:
                raise ValidationError('Value must be an integer.')

        elif self.value != '' and self.type == self.TYPE_BOOLEAN:
            if self.value.lower() not in self.VALID_BOOL_STRINGS:
                raise ValidationError('Value must be a boolean.')

    def get_value(self):
        """
        Get the value, automatically casting it to the correct type.
        """
        if self.value == '':
            return None
        elif self.type == self.TYPE_STRING:
            return self.value
        elif self.type == self.TYPE_FLOAT:
            return float(self.value)
        elif self.type == self.TYPE_INTEGER:
            return int(self.value)
        elif self.type == self.TYPE_BOOLEAN:
            return self.value.lower() in self.TRUTHY_BOOL_STRINGS

    def initialize(self, first_time):
        """
        Initialize the setting
        """
        if first_time:
            self.value = self.initializer


class DatasetServiceSetting(TethysAppSetting):
    """
    DB Model for Tethys App DatasetService Setting
    """
    CKAN = DatasetService.CKAN
    HYSROSHARE = DatasetService.HYDROSHARE

    dataset_service = models.ForeignKey(DatasetService, blank=True, null=True)
    engine = models.CharField(max_length=200,
                              choices=DatasetService.ENGINE_CHOICES,
                              default=DatasetService.CKAN)

    def clean(self):
        """
        Validate prior to saving changes.
        """
        if not self.dataset_service and self.required:
            raise ValidationError('Required.')


class SpatialDatasetServiceSetting(TethysAppSetting):
    """
    DB Model for Tethys App SpatialDatasetService Setting
    """
    GEOSERVER = SpatialDatasetService.GEOSERVER

    spatial_dataset_service = models.ForeignKey(SpatialDatasetService, blank=True, null=True)
    engine = models.CharField(max_length=200,
                              choices=SpatialDatasetService.ENGINE_CHOICES,
                              default=SpatialDatasetService.GEOSERVER)

    def clean(self):
        """
        Validate prior to saving changes.
        """
        if not self.spatial_dataset_service and self.required:
            raise ValidationError('Required.')


class WebProcessingServiceSetting(TethysAppSetting):
    """
    DB Model for Tethys App WebProcessingService Setting
    """
    web_processing_service = models.ForeignKey(WebProcessingService, blank=True, null=True)

    def clean(self):
        """
        Validate prior to saving changes.
        """
        if not self.web_processing_service and self.required:
            raise ValidationError('Required.')


class PersistentStoreConnectionSetting(TethysAppSetting):
    """
    DB Model for Tethys App PersistentStoreService Setting
    """
    persistent_store_service = models.ForeignKey(PersistentStoreService, blank=True, null=True)

    def clean(self):
        """
        Validate prior to saving changes.
        """
        if not self.persistent_store_service and self.required:
            raise ValidationError('Required.')

    def get_engine(self, as_url=False):
        """
        Get the SQLAlchemy engine from the connected persistent store service
        """
        ps_service = self.persistent_store_service

        # Validate connection service
        if ps_service is None:
            raise TethysAppSettingNotAssigned('Cannot create engine or url for PersistentStoreConnection "{0}" for app '
                                              '"{1}": no PersistentStoreService found.'.format(self.name,
                                                                                               self.tethys_app.package))

        if as_url:
            return ps_service.get_url()

        return ps_service.get_engine()


class PersistentStoreDatabaseSetting(TethysAppSetting):
    """
    DB Model for Tethys App PersistentStoreDatabase Setting
    """
    spatial = models.BooleanField(default=False)
    dynamic = models.BooleanField(default=False)
    persistent_store_service = models.ForeignKey(PersistentStoreService, blank=True, null=True)

    def clean(self):
        """
        Validate prior to saving changes.
        """
        if not self.persistent_store_service and self.required:
            raise ValidationError('Required.')

    def initialize(self):
        """
        Initialize persistent store database setting.
        """
        self.create_persistent_store_database()

    def get_namespaced_persistent_store_name(self):
        """
        Return the namespaced persistent store database name (e.g. my_first_app_db).
        """
        from django.conf import settings
        # Convert name given by user to database safe name
        safe_name = self.name.lower().replace(' ', '_')

        # If testing environment, the engine for the "test" version of the persistent store should be fetched
        if hasattr(settings, 'TESTING') and settings.TESTING:
            safe_name = 'test_{0}'.format(safe_name)

        return '_'.join((self.tethys_app.package, safe_name))

    def get_engine(self, with_db=True, as_url=False):
        """
        Get the SQLAlchemy engine from the connected persistent store service
        """
        ps_service = self.persistent_store_service

        # Validate connection service
        if ps_service is None:
            raise TethysAppSettingNotAssigned('Cannot create engine or url for PersistentStoreDatabase "{0}" for app '
                                              '"{1}": no PersistentStoreService found.'.format(self.name,
                                                                                               self.tethys_app.package))

        if with_db:
            ps_service.database = self.get_namespaced_persistent_store_name()

        if as_url:
            return ps_service.get_url()

        return ps_service.get_engine()

    def persistent_store_database_exists(self):
        """
        Returns True if the persistent store database exists.
        """
        # Get the database engine
        engine = self.get_engine(with_db=False)
        namespaced_name = self.get_namespaced_persistent_store_name()

        # Cannot create databases in a transaction: connect and commit to close transaction
        connection = engine.connect()

        # Check for Database
        existing_query = """
                         SELECT d.datname as name
                         FROM pg_catalog.pg_database d
                         LEFT JOIN pg_catalog.pg_user u ON d.datdba = u.usesysid
                         WHERE d.datname = '{0}';
                         """.format(namespaced_name)

        existing_dbs = connection.execute(existing_query)
        connection.close()

        for existing_db in existing_dbs:
            if existing_db.name == namespaced_name:
                return True

        return False

    def drop_persistent_store_database(self):
        """
        Drop the persistent store database.
        """
        if not self.persistent_store_database_exists():
            return

        # TODO: Implement logging
        # Provide update for user
        # self.stdout.write('Dropping database "{0}" for app "{1}"...'.format(
        #     self.name,
        #     self.tethys_app.package
        # ))

        # Get the database engine
        engine = self.get_engine(with_db=False)

        # Connection
        drop_connection = engine.connect()

        namespaced_ps_name = self.get_namespaced_persistent_store_name()

        # Drop db
        drop_db_statement = 'DROP DATABASE IF EXISTS {0}'.format(namespaced_ps_name)

        try:
            drop_connection = engine.connect()
            drop_connection.execute('commit')
            drop_connection.execute(drop_db_statement)
        except Exception as e:
            if 'being accessed by other users' in str(e):
                # Force disconnect all other connections to the database
                disconnect_sessions_statement = '''
                                                SELECT pg_terminate_backend(pg_stat_activity.pid)
                                                FROM pg_stat_activity
                                                WHERE pg_stat_activity.datname = '{0}'
                                                AND pg_stat_activity.pid <> pg_backend_pid();
                                                '''.format(namespaced_ps_name)
                drop_connection.execute(disconnect_sessions_statement)

                # Try again to drop the database
                drop_connection.execute('commit')
                drop_connection.execute(drop_db_statement)
                drop_connection.close()
            else:
                raise e
        finally:
            drop_connection.close()

    def create_persistent_store_database(self, refresh=False, force_first_time=False):
        """
        Provision all persistent stores for all apps or for only the app name given.
        """
        # Connection engine
        url = self.get_engine(with_db=False, as_url=True)
        engine = self.get_engine(with_db=False)
        namespaced_ps_name = self.get_namespaced_persistent_store_name()
        db_exists = self.persistent_store_database_exists()

        # -------------------------------------------------------------------------------------------------------------#
        # 1. Drop database if refresh option is included
        # -------------------------------------------------------------------------------------------------------------#
        if db_exists and refresh:
            self.drop_persistent_store_database()
            self.initialized = False
            self.save()
            db_exists = False

        # -------------------------------------------------------------------------------------------------------------#
        # 2. Create the database if it does not already exist
        # -------------------------------------------------------------------------------------------------------------#
        if not db_exists:
            # Provide Update for User
            # self.stdout.write('Creating database "{0}" for app "{1}"...'.format(
            #     self.name,
            #     self.tethys_app.package
            # ))

            # Cannot create databases in a transaction: connect and commit to close transaction
            create_connection = engine.connect()

            # Create db
            create_db_statement = '''
                                  CREATE DATABASE {0}
                                  WITH OWNER {1}
                                  TEMPLATE template0
                                  ENCODING 'UTF8'
                                  '''.format(namespaced_ps_name, url.username)

            # Close transaction first and then execute
            create_connection.execute('commit')
            try:
                create_connection.execute(create_db_statement)
            except sqlalchemy.exc.ProgrammingError:
                raise PersistentStorePermissionError('Database user "{0}" has insufficient permissions to create '
                                                     'the persistent store database "{1}": must have CREATE DATABASES '
                                                     'permission at a minimum.'.format(url.username, self.name))
            finally:
                create_connection.close()

        # -------------------------------------------------------------------------------------------------------------#
        # 3. Enable PostGIS extension
        # -------------------------------------------------------------------------------------------------------------#
        if self.spatial:
            # Connect to new database
            new_db_connection = engine.connect()

            # Notify user
            # self.stdout.write('Enabling PostGIS on database "{0}" for app "{1}"...'.format(
            #     self.name,
            #     self.tethys_app.package,
            # ))

            enable_postgis_statement = 'CREATE EXTENSION IF NOT EXISTS postgis'

            # Execute postgis statement
            try:
                new_db_connection.execute(enable_postgis_statement)
            except sqlalchemy.exc.ProgrammingError:
                raise PersistentStorePermissionError('Database user "{0}" has insufficient permissions to enable '
                                                     'spatial extension on persistent store database "{1}": must be a '
                                                     'superuser.'.format(url.username, self.name))
            finally:
                new_db_connection.close()

        # -------------------------------------------------------------------------------------------------------------#
        # 4. Run initialization function
        # -------------------------------------------------------------------------------------------------------------#
        if self.initializer:
            try:
                if force_first_time:
                    self.initializer_function(self.get_engine(), True)
                else:
                    self.initializer_function(self.get_engine(), not self.initialized)
            except Exception as e:
                print(type(e))
                raise PersistentStoreInitializerError()

        # Update initialization
        self.initialized = True
        self.save()
