'''
********************************************************************************
* Name: lib
* Author: Nathan Swain
* Copyright: (c) Brigham Young University 2013
* License: BSD 2-Clause
********************************************************************************
'''

import json
import time
import os
import ConfigParser
from datetime import datetime

from pylons import session
from tethys_apps.harvesters.app_harvester import SingletonAppHarvester
from app_global_store import SingletonAppGlobalStore


def set_session_global(key, value):
    '''
    Set a session variable on the session object
    '''
    session[key] = value
    session.save()
        
def set_session_globals(kv):
    '''
    Set multiple session variables on the session object
    '''
    for key, value in kv.iteritems():
        session[key] = value
    session.save()
            
    
def get_session_global(key):
    '''
    Get the value of a global variable from the session object
    '''
    return session[key]

def get_value_from_app_global_store(store_name, key):
    '''
    Retrieve the app global configuration from the singleton harvester
    '''
    global_store = SingletonAppGlobalStore()
    return global_store.getValueForStore(store_name, key)

def get_app_definition(app_index):
    '''
    Retrieve the definition object given the name
    '''
    # Retrieve harvester
    harvester = SingletonAppHarvester()
    apps = harvester.apps
    
    for app in apps:
        if app['index'] == app_index:
            return app
    
    return None

def json_date_handler(obj):
    if isinstance(obj, datetime):
        return time.mktime(obj.timetuple()) * 1000
    else:
        return obj

def jsonify(data):
    '''
    Convert python data structures into a JSON string
    '''
    return json.dumps(data, default=json_date_handler)

def get_ckanapp_directory():
    '''
    Get the location of the ckanapp directory from the tethys configuration file
    '''
    tethys_apps_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(tethys_apps_path, 'tethys_apps.ini')
    config = ConfigParser.RawConfigParser()
    config.read(config_path)
    return config.get('tethys:main', 'tethys.ckanapp_directory')
    
    
    
    