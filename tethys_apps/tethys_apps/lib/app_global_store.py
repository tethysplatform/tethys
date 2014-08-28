'''
********************************************************************************
* Name: app_global_store
* Author: Nathan Swain
* Created On: January 7, 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
'''

from exceptions import RuntimeError

class SingletonAppGlobalStore(object):
    '''
    Object Used to Store Globals for each app
    '''
    
    _app_global_store = dict()
    _instance = None
    
    def __new__(self):
        '''
        Make App Global Store a Singleton
        '''
        if not self._instance:
            self._instance = super(SingletonAppGlobalStore, self).__new__(self)
            
        return self._instance
    
    def addGlobalStore(self, store_name, dictionary):
        '''
        Add new global store.
        name = name of the store used for looking up values (must be unique, cannot overwrite
        dictionary = dictionary of key-value global pairs
        '''
        if store_name not in self._app_global_store:
            self._app_global_store[store_name] = dictionary
        else:
            raise RuntimeError('GLOBAL STORE NAME CONFLICT: {0} is already being used as an app global store name'.format(name))
        
    def getValueForStore(self, store_name, key):
        '''
        Get a value at the key in the store
        '''
        if store_name in self._app_global_store:
            store = self._app_global_store[store_name]
            return store[key]
        else:
            return None
        
    def getGlobalStore(self, store_name):
        '''
        Get the entire store
        '''
        if store_name in self._app_global_store:
            return self._app_global_store[store_name]
        else:
            return None