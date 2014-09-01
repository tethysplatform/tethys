import os
import sys
import ConfigParser

from sqlalchemy import create_engine
from .tethys_apps.harvesters.persistent_store_harvester import PersistentStoreHarvester
from .app_base import AppBase

def provision_persistent_stores(app_module_path):
    '''
    Used to create new databases for apps during installation
    '''
    # Get tethys app manager url from config
    database_manager_url = get_database_manager_url()
    
    # Get app name from app module path
    app_module_parts = app_module_path.split('.')
    
    # Assume first argument is the app package name
    app_name = app_module_parts[0]
    
    # Prepend app module path with ckanapp namespace path
    app_module_path ='.'.join(['ckanext.tethys_apps.ckanapp', app_module_path])
    
    # Harvest persistent store info from app.py
    # Create persistent store harvester
    persistent_store_harvester = PersistentStoreHarvester()
    
    # Instantiate app
    app_module_string, app_class_string = app_module_path.split(':')
    AppModule = __import__(app_module_string, fromlist=[app_class_string])
    AppClass = getattr(AppModule, app_class_string)
    app = AppClass()
    
    # Call register persistent store method on app instance to mine information
    if isinstance(app, AppBase):
        app.registerPersistentStores(persistent_store_harvester)
        persistent_store_harvester.provisionPersistentStores(app_name, database_manager_url)
        persistent_store_harvester.runInitializationScripts()
    
def get_database_manager_url():
    '''
    Parse tethys_apps.ini and retrieve the database_manager_url
    '''
    tethys_apps_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(tethys_apps_path, 'tethys_apps.ini')
    config = ConfigParser.RawConfigParser()
    config.read(config_path)
    return config.get('tethys:main', 'tethys.database_manager_url')

def get_existing_database_list():
    '''
    Returns a list of the existing databases
    '''
    # Get database manager
    database_manager_url = get_database_manager_url()
    
    # Create connection engine
    engine = create_engine(database_manager_url)
    
    # Cannot create databases in a transactions
    # Connect and commit to close transaction
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
        
    return existing_db_names
    
def get_persistent_store_engine(app_name, persistent_store_name):
    '''
    Returns an sqlalchemy engine for the given store
    '''
    # Create the unique store name
    unique_store_name = '_'.join([app_name, persistent_store_name])
    
    # Check to make sure that the persistent store exists
    if unique_store_name in get_existing_database_list():
        # Retrieve the database manager url.
        # The database manager database user is the owner of all the app databases.
        database_manager_url = get_database_manager_url()
        url_parts = database_manager_url.split('/')
        
            
        # Assemble url for persistent store with that name
        persistent_store_url = '{0}//{1}/{2}'.format(url_parts[0], url_parts[2], unique_store_name)
    
        # Return SQLAlchemy Engine
        return create_engine(persistent_store_url)
    
    else:
        print 'ERROR: No persisent store "{0}" for app "{1}". Make sure you register the persistent store in app.py and reinstall app.'.format(persistent_store_name, app_name)
        sys.exit()
    
    
    
    