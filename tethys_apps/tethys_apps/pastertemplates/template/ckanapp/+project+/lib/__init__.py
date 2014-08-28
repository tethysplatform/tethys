import os
from ckanext.tethys_apps.lib.persistent_store import get_persistent_store_engine as gpse

def get_persistent_store_engine(persistent_store_name):
    '''
    Wrapper for the get_persistent_store_engine method that makes it easier to use
    '''
    # Derive app name
    app_name = os.path.split(os.path.dirname(os.path.dirname(__file__)))[1]
    
    # Get engine
    return gpse(app_name, persistent_store_name)