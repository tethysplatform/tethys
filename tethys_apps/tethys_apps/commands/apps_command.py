'''
********************************************************************************
* Name: apps_command.py
* Author: Nathan Swain
* Created On: April 3, 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
'''

import sys

import ckan.plugins as p

from sqlalchemy import create_engine

from ckan.lib.base import config

class AppsCommand(p.toolkit.CkanCommand):
    '''
    Performs operations related to setting up this plugin
    
    Usage:
        test initdb
            Creates the necessary tables. 
            
    This command should be run from the ckanext-test directory and expects 
    a development.ini file to be present. Usually you will specify the 
    config explicitly.
        
        --config=[path to config]
    '''
    
    summary = __doc__.split('/n')[0]
    usage = __doc__
    max_args = 2
    min_args = 0
    
    def command(self):
        self._load_config()
        
        cmd = self.args[0]
        
        if cmd == 'initdb':
            self.initdb()
        elif cmd =='loadsampledata':
            self.load_sample_data()
        else:
            print 'Command %s not recognized' % cmd
        
    
    def initdb(self):
        from ckanext.test.model.gsshapy import init_tables
        
        engine = create_engine(config.get('gsshapy.url'))
        
        init_tables(engine)
        
        print 'DB tables created'
        
    def load_sample_data(self):
        from ckanext.test.model.gsshapy import DBSession
        from ckanext.test.model.gsshapy.test.orm.bootstrap import orm_test_data
        
        engine = create_engine(config.get('gsshapy.url'))
        
        DBSession.configure(bind=engine)
        
        orm_test_data(DBSession)
        
        DBSession.commit()
        
        print 'Sample Data Loaded'
        
        