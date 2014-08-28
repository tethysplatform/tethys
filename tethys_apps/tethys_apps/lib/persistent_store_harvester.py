import os, ConfigParser

from sqlalchemy import create_engine

class PersistentStoreHarvester():
    '''
    Definition for object that collects information about persistent
    stores for apps
    '''
    
    def __init__(self):
        '''
        Constructor for persistent store harvester
        '''
        self.requested_stores = []
        self.db_initialization_scripts = []
        
    def addPersistentStore(self, persistent_store_name):
        '''
        Method used to request a persistent store. These databases
        will automatically be provisioned during app installation.
        '''

        self.requested_stores.append(persistent_store_name)
        
    def addInitializationScript(self, script):
        '''
        Method used to add a database initialization script. These scripts
        will be run after all databases have been provisioned.
        '''

        self.db_initialization_scripts.append(script)
        
    def provisionPersistentStores(self, app_name, database_manager_url):
        '''
        Provision all persistent stores in the requestsed_stores property
        '''
        print 'Provisioning Persistent Stores...'
        
        # Get db credentials from CKAN config
        database_manager_name = database_manager_url.split('://')[1].split(':')[0]
        
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
            
        for requested_db in self.requested_stores:
            full_db_name = '_'.join((app_name, requested_db))
            
            # Make sure the database doesn't exist
            if full_db_name not in existing_db_names:
                # Provide Update for User
                print 'Creating database "{0}" for app "{1}"...'.format(requested_db, app_name)
                
                # Create db
                create_db_statement = '''
                                      CREATE DATABASE {0}
                                      WITH OWNER {1}
                                      TEMPLATE template0
                                      ENCODING 'UTF8'
                                      '''.format(full_db_name, database_manager_name)
                
                # Close transaction first and then execute
                connection.execute('commit')                       
                connection.execute(create_db_statement)
                
                # Get URL for Tethys Superuser
                tethys_apps_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                config_path = os.path.join(tethys_apps_path, 'tethys_apps.ini')
                config = ConfigParser.RawConfigParser()
                config.read(config_path)
                super_url = config.get('tethys:main', 'tethys.superuser_url')
                super_parts = super_url.split('/')
                new_db_url = '{0}//{1}/{2}'.format(super_parts[0], super_parts[2], full_db_name)
                
                # Connect to new database
                new_db_engine = create_engine(new_db_url)
                new_db_connection = new_db_engine.connect()
                
                # Enable PostGIS extension
                print 'Creating PostGIS extension...'
                enable_postgis_statement = 'CREATE EXTENSION IF NOT EXISTS postgis'
                
                # Close transaction first and then execute
#                 new_db_connection.execute('commit')
                new_db_connection.execute(enable_postgis_statement)
                
            else:
                # Provide Update for User
                print 'Database "{0}" already exists for app "{1}", skipping...'.format(requested_db, app_name)
            
        connection.close()
        
    def runInitializationScripts(self):
        '''
        Run the initialization scripts
        '''
        print 'Initializing Persistent Stores...'
        
        for script in self.db_initialization_scripts:
            # Provide feedback for user
            print 'Running {0}'.format(script)
        
            # Add the ckanapp namespace
            script = '.'.join(['ckanext.tethys_apps.ckanapp', script])
            
            # Run the module by importing it
            __import__(script)
            
        
        