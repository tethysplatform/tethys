"""
********************************************************************************
* Name: persistent store
* Author: Nathan Swain
* Created On: September 22, 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

import sys

from django.conf import settings
from django.db import DatabaseError

from sqlalchemy import create_engine

class TethysFunctionExtractor(object):
    """
    Base class for PersistentStore and HandoffHandler that returns a function handle from a string path to the function.

    Attributes:
        path (str): The path to a function in the form "app_name.module_name.function_name".
    """
    PATH_PREFIX = 'tethys_apps.tethysapp'

    def __init__(self, path):
        self.path = path
        self._valid = None
        self._function = None

    @property
    def valid(self):
        """
        True if function is valid otherwise False.
        """
        if self._valid is None:
            self.function
        return self._valid

    @property
    def function(self):
        """
        The function pointed to by the path_str attribute.

        Returns:
            A handle to a Python function or None if function is not valid.
        """
        if not self._function and self._valid is None:
            try:
                # Split into parts and extract function name
                module_path, function_name = self.path.rsplit('.', 1)

                #Pre-process handler path
                full_module_path = '.'.join((self.PATH_PREFIX, module_path))

                # Import module
                module = __import__(full_module_path, fromlist=[function_name])
            except (ValueError, ImportError):
                self._valid = False
            else:
                # Get the function
                self._function = getattr(module, function_name)
                self._valid = True

        return self._function


class PersistentStore(TethysFunctionExtractor):
    """
    An object that stores the registration data for a Tethys Persistent Store.

    Args:
      name(string): The name of the persistent store.
      initializer(string): Path to the initialization function for the persistent store. Use dot-notation with a colon delineating the function (e.g.: "foo.bar:function").
      spatial(bool, optional): PostGIS spatial extension will be enabled on the persistent store if True. Defaults to False.
      postgis(bool, deprecated): PostGIS spatial extension will be enabled on the persistent store if True. Defaults to False. Deprecated, use spatial instead.

    """

    def __init__(self, name, initializer, spatial=False, postgis=False):
        """
        Constructor
        """
        # Validate
        ## TODO: Validate persistent store object
        self.name = name
        self.initializer = initializer
        self.postgis = postgis
        self.spatial = spatial
        super(PersistentStore, self).__init__(self.initializer)

    def __repr__(self):
        """
        String representation
        """
        if hasattr(self, 'spatial'):
            return '<Persistent Store: name={0}, initializer={1}, spatial={2}>'.format(self.name,
                                                                                       self.initializer,
                                                                                       self.spatial)
        else:
            return '<Persistent Store: name={0}, initializer={1}, spatial={2}>'.format(self.name,
                                                                                       self.initializer,
                                                                                       self.postgis)

    @property
    def initializer_is_valid(self):
        return self.valid

    @property
    def initializer_function(self):
        """
        The function pointed to by the initializer attribute.

        Returns:
            A handle to a Python function that will initialize the database or None if function is not valid.
        """
        return self.function


def get_persistent_store_engine(app_name, persistent_store_name):
    """
    Creates an SQLAlchemy engine object for the app and persistent store given.

    Args:
      app_name(string): Name of the app to which the persistent store belongs. More specifically, the app package name.
      persistent_store_name(string): Name of the persistent store for which to retrieve the engine.

    Returns:
      object: An SQLAlchemy engine object for the persistent store requested.
    """
    print('DEPRECTATION WARNING: The ".utilities.get_persistent_store" method has been deprecated. Use the '
          '"get_persistent_store" method on the App Class instead (e.g.: MyApp.get_persistent_store("name") ).')
    # Create the unique store name
    unique_store_name = '_'.join([app_name, persistent_store_name])

    # Get database manager
    database_manager_db = settings.TETHYS_DATABASES['tethys_db_manager']
    database_manager_url = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(database_manager_db['USER'] if 'USER' in database_manager_db else 'tethys_db_manager',
                                                                     database_manager_db['PASSWORD'] if 'PASSWORD' in database_manager_db else 'pass',
                                                                     database_manager_db['HOST'] if 'HOST' in database_manager_db else '127.0.0.1',
                                                                     database_manager_db['PORT'] if 'PORT' in database_manager_db else '5435',
                                                                     database_manager_db['NAME'] if 'NAME' in database_manager_db else 'tethys_db_manager')

    # Create connection engine
    engine = create_engine(database_manager_url)
    connection = engine.connect()

    # Check for Database
    existing_dbs_statement = '''
                             SELECT d.datname as name
                             FROM pg_catalog.pg_database d
                             LEFT JOIN pg_catalog.pg_user u ON d.datdba = u.usesysid
                             ORDER BY 1;
                             '''

    existing_dbs = connection.execute(existing_dbs_statement)

    # Compile list of db names
    existing_db_names = []

    for existing_db in existing_dbs:
        existing_db_names.append(existing_db.name)

    # Check to make sure that the persistent store exists
    if unique_store_name in existing_db_names:
        # Retrieve the database manager url.
        # The database manager database user is the owner of all the app databases.
        database_manager_db = settings.TETHYS_DATABASES['tethys_db_manager']

        # Assemble url for persistent store with that name
        persistent_store_url = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(database_manager_db['USER'] if 'USER' in database_manager_db else 'tethys_db_manager',
                                                                         database_manager_db['PASSWORD'] if 'PASSWORD' in database_manager_db else 'pass',
                                                                         database_manager_db['HOST'] if 'HOST' in database_manager_db else '127.0.0.1',
                                                                         database_manager_db['PORT'] if 'PORT' in database_manager_db else '5435',
                                                                         unique_store_name)

        # Return SQLAlchemy Engine
        return create_engine(persistent_store_url)

    else:
        raise DatabaseError('No persistent store "{0}" for app "{1}". Make sure you register the persistent store in app.py '
                            'and reinstall app.'.format(persistent_store_name, app_name))