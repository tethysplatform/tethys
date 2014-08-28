'''
********************************************************************************
* Name: app_harvester
* Author: Nathan Swain and Scott Christensen
* Created On: August 19, 2013
* Copyright: (c) Brigham Young University 2013
* License: BSD 2-Clause
********************************************************************************
'''

import os, inspect
from ckanext.tethys_apps.lib.app_base import AppBase
from ckanext.tethys_apps.lib.app_global_store import SingletonAppGlobalStore

class SingletonAppHarvester(object):
    '''
    Collects information for building apps
    '''
    apps = []
    controllers = []
    templateDirs = []
    resources = []
    publicDirs = []
    _instance = None

    def addApp(self, name, index, icon):
        '''
        Add app to CKAN:
        
        name = name of app to appear on apps index page
        index = name of controller to index/main page of app
        icon = path to image in static directory
        config = dictionary of configuration parameters that will
                 be global to the app these are to be read-only
        '''
        
        if icon[0] != '/':
            icon = '/' + icon
            
        app = {
               'name': name,
               'index': index,
               'icon': icon
               }
        
        self.apps.append(app)
        
    def addAppGlobalStore(self, store_name, dictionary):
        '''
        Add globals to the app at runtime. These should be considered read only.
        name = name of the store or the app
        dictionary = dictionary of key-value global pairs
        '''
        global_store = SingletonAppGlobalStore()
        global_store.addGlobalStore(store_name, dictionary)
        
    def addController(self, name, url, controller, action=None):
        '''
        Add app controllers to CKAN
        '''
        
        controller = {
                      'name': name,
                      'url': '/'.join(['/apps', url]),
                      'controller': '.'.join(['ckanext.tethys_apps.ckanapp', controller]),
                      'action': action
                      }
        
        self.controllers.append(controller)
        
    def addTemplateDirectory(self, directory):
        '''
        Add app template directories to CKAN
        '''
        directory = os.path.join('ckanapp', directory)
        self.templateDirs.append(directory)
        
    def addPublicDirectory(self, directory):
        '''
        Add app public content directories to CKAN
        '''
        directory = os.path.join('ckanapp', directory)
        
        self.publicDirs.append(directory)
        
    def addResource(self, directory, name):
        '''
        Add app resource directories to CKAN
        '''
        directory = os.path.join('ckanapp', directory)
        
        self.resources.append({
                               'directory': directory,
                               'name': name,
                               })
        
    def __new__(self):
        '''
        Make App Harvester a Singleton
        '''
        if not self._instance:
            self._instance = super(SingletonAppHarvester, self).__new__(self)
            
        return self._instance
        
    def harvestApps(self):
        '''
        Searches the apps package for apps
        '''
        print 'Harvesting Apps:'        
        # List the apps packages in directory
        appsDir = os.path.join(os.path.split(os.path.dirname(__file__))[0],'ckanapp')
        app_packages_list = os.listdir(appsDir)
        
        # Collect App Instances
        app_instance_list = self._harvestAppInstances(app_packages_list)
        
        # Put the harvester to work
        self._putHarvesterToWork(app_instance_list)
        
                
    def _harvestAppInstances(self, app_packages_list):
        '''
        Search each app package for the app.py module. Find the AppBase class in the app.py 
        module and instantiate it. Returns a list of instantiated AppBase classes.
        '''
        instance_list = []
        
        for app_package in app_packages_list:
            # Collect data from each app package in the apps directory
            if app_package not in ['__init__.py', '__init__.pyc', '.gitignore']:
                # Create the path to the app module in the custom app package
                app_module_name = '.'.join(['ckanext.tethys_apps.ckanapp', app_package, 'app'])

                # Import the app.py module from the custom app package programmatically
                # (e.g.: apps.apps.<custom_package>.app)
                app_module = __import__(app_module_name, fromlist=[''])
                
                for name, obj in inspect.getmembers(app_module):
                    # Retrieve the members of the app_module and iterate through
                    # them to find the the class that inherits from AppBase.
                    try:
                        # issubclass() will fail if obj is not a class
                        if (issubclass(obj, AppBase)) and (obj is not AppBase):
                            # Assign a handle to the class
                            _appClass = getattr(app_module, name)
                    
                            app_instance = _appClass()
                            instance_list.append(app_instance)
                            print app_package
                            
                    except TypeError:
                        '''DO NOTHING'''
                    except:
                        raise
            
        return instance_list
        
    def _putHarvesterToWork(self, app_instance_list):
        '''
        Call each method of the AppBase on each app_instance
        passing the collector (self) through to collect the 
        appropriate parameters.
        '''
        
        for app_instance in app_instance_list:
            # Call each method of AppBase on the instance
            app_instance.registerApp(self)
            app_instance.registerControllers(self)
            app_instance.registerTemplateDirectories(self)
            app_instance.registerResources(self)
            app_instance.registerPublicDirectories(self)          
            
        