"""
********************************************************************************
* Name: app_harvester
* Author: Nathan Swain and Scott Christensen
* Created On: August 19, 2013
* Copyright: (c) Brigham Young University 2013
* License: BSD 2-Clause
********************************************************************************
"""

import os
import inspect

from tethys_apps.base.app_base import AppBase


def django_url_preprocessor(url, root):
    """
    Convert url from the simplified string version for app developers to
    Django regular expressions.

    e.g.:

        '/example/resource/{variable_name}/'
        r'^/example/resource/?P<variable_name>[1-9A-Za-z\-]+/$'
    """
    # Default Django expression that will be matched
    DEFAULT_EXPRESSION = '[1-9A-Za-z-]+'

    # Split the url into parts
    url_parts = url.split('/')
    django_url_parts = []

    # Remove the root of the url if it is present
    if root in url_parts:
        index = url_parts.index(root)
        url_parts.pop(index)

    # Look for variables
    for part in url_parts:
        # Process variables
        if '{' in part or '}' in part:
            variable_name = part.replace('{', '').replace('}', '')
            part = '(?P<{0}>{1})'.format(variable_name, DEFAULT_EXPRESSION)

        # Collect processed parts
        django_url_parts.append(part)

    # Join the process parts again
    django_url_joined = '/'.join(django_url_parts)

    # Final django-formatted url
    if django_url_joined != '':
        django_url = r'^{0}/$'.format(django_url_joined)
    else:
        # Handle empty string case
        django_url = r'^$'

    return django_url


class SingletonAppHarvester(object):
    """
    Collects information for building apps
    """
    apps = []
    controllers = []
    _instance = None

    def add_app(self, name, index, icon):
        """
        Add app to Tethys

        name = name of app to appear on apps index page
        index = name of controller to index/main page of app
        icon = path to image in static directory
        config = dictionary of configuration parameters that will
                 be global to the app these are to be read-only
        """
        
        if icon[0] != '/':
            icon = '/' + icon
            
        app = {
               'name': name,
               'index': index,
               'icon': icon
               }
        
        self.apps.append(app)
        
    def add_controller(self, name, url, controller, root, django=True, action=None):
        """
        Add app controllers to Tethys
        """

        if django:
            # Pre-process the URL into the Django format
            url = django_url_preprocessor(url, root)

            if root == '' or root is None:
                raise ValueError("Argument 'root' cannot be None or the empty string.")
        
        controller = {'name': name,
                      'url': url,
                      'controller': '.'.join(['tethys_apps.tethysapp', controller]),
                      'root': root}
        
        self.controllers.append(controller)
        
    def __new__(self):
        """
        Make App Harvester a Singleton
        """
        if not self._instance:
            self._instance = super(SingletonAppHarvester, self).__new__(self)
            
        return self._instance
        
    def harvest_apps(self):
        """
        Searches the apps package for apps
        """
        print 'Harvesting Apps:'        
        # List the apps packages in directory
        apps_dir = os.path.join(os.path.split(os.path.dirname(__file__))[0], 'tethysapp')
        app_packages_list = os.listdir(apps_dir)
        
        # Collect App Instances
        app_instance_list = self._harvest_app_instances(app_packages_list)
        
        # Put the harvester to work
        self._put_harvester_to_work(app_instance_list)

    @staticmethod
    def _harvest_app_instances(app_packages_list):
        """
        Search each app package for the app.py module. Find the AppBase class in the app.py
        module and instantiate it. Returns a list of instantiated AppBase classes.
        """
        instance_list = []
        
        for app_package in app_packages_list:
            # Collect data from each app package in the apps directory
            if app_package not in ['__init__.py', '__init__.pyc', '.gitignore']:
                # Create the path to the app module in the custom app package
                app_module_name = '.'.join(['tethys_apps.tethysapp', app_package, 'app'])

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
        
    def _put_harvester_to_work(self, app_instance_list):
        """
        Call each method of the AppBase on each app_instance
        passing the collector (self) through to collect the
        appropriate parameters.
        """
        
        for app_instance in app_instance_list:
            # Call each method of AppBase on the instance
            app_instance.register_app(self)
            app_instance.register_controllers(self)
