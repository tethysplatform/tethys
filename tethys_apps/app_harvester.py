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

from tethys_apps.base import TethysAppBase
from terminal_colors import TerminalColors


class SingletonAppHarvester(object):
    """
    Collects information for initiating apps
    """

    apps = []
    _instance = None

    def harvest_apps(self):
        """
        Searches the apps package for apps
        """
        # Notify user harvesting is taking place
        print(TerminalColors.BLUE + 'Loading Tethys Apps...' + TerminalColors.ENDC)

        # List the apps packages in directory
        apps_dir = os.path.join(os.path.dirname(__file__), 'tethysapp')
        app_packages_list = os.listdir(apps_dir)

        # Harvest App Instances
        self._harvest_app_instances(app_packages_list)
        
    def __new__(self):
        """
        Make App Harvester a Singleton
        """
        if not self._instance:
            self._instance = super(SingletonAppHarvester, self).__new__(self)
            
        return self._instance

    @staticmethod
    def _validate_app(app):
        """
        Validate the app data that needs to be validated. Returns either the app if valid or None if not valid.
        """
        # Remove prepended slash if included
        if app.icon != '' and app.icon[0] == '/':
            app.icon = app.icon[1:]

        # Validate color
        if app.color != '' and app.color[0] != '#':
            # Add hash
            app.color = '#{0}'.format(app.color)

        # Must be 6 or 3 digit hex color (7 or 4 with hash symbol)
        if len(app.color) != 7 and len(app.color) != 4:
            app.color = ''

        return app

    def _harvest_app_instances(self, app_packages_list):
        """
        Search each app package for the app.py module. Find the AppBase class in the app.py
        module and instantiate it. Save the list of instantiated AppBase classes.
        """
        valid_app_instance_list = []
        loaded_apps = []
        
        for app_package in app_packages_list:
            # Collect data from each app package in the apps directory
            if app_package not in ['__init__.py', '__init__.pyc', '.gitignore', '.DS_Store']:
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
                        if (issubclass(obj, TethysAppBase)) and (obj is not TethysAppBase):
                            # Assign a handle to the class
                            _appClass = getattr(app_module, name)

                            # Instantiate app and validate
                            app_instance = _appClass()
                            validated_app_instance = self._validate_app(app_instance)

                            # compile valid apps
                            if validated_app_instance:
                                valid_app_instance_list.append(validated_app_instance)

                                # Notify user that the app has been loaded
                                loaded_apps.append(app_package)

                    except TypeError:
                        '''DO NOTHING'''
                    except:
                        raise

        # Save valid apps
        self.apps = valid_app_instance_list

        # Update user
        print('Tethys Apps Loaded: {0}'.format(' '.join(loaded_apps)))
