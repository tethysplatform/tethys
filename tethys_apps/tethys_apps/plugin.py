'''
********************************************************************************
* Name: plugin.py
* Author: Nathan Swain
* Created On: April 3, 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
'''

import ckan.plugins as p
import ckan.model as model

from ckanext.tethys_apps.lib.app_harvester import SingletonAppHarvester
from ckanext.tethys_apps.lib import get_session_global, get_app_definition, jsonify


class AppsExtension(p.SingletonPlugin):
    
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IAuthFunctions, inherit=True)
    p.implements(p.ITemplateHelpers, inherit=True)
    p.implements(p.IMiddleware, inherit=True)
    
    #: Instantiate SingletonAppHarvester
    harvester = SingletonAppHarvester()
    harvester.harvest_apps()
    
    def after_map(self, map):        
        # Controller for the apps plugin
        map.connect('apps', '/apps',
                    controller='ckanext.tethys_apps.controllers.apps_main:AppsController',
                    action='index')
        
        # Controller for secret snippets showcase page
        map.connect('snippet-showcase', '/apps/snippet-showcase',
                    controller='ckanext.tethys_apps.controllers.snippet_showcase:SnippetShowcaseController',
                    action='index')
        
        map.connect('snippet-showcase-action', '/apps/snippet-showcase/{action}',
                    controller='ckanext.tethys_apps.controllers.snippet_showcase:SnippetShowcaseController')

        map.connect('snippet-ajax', '/apps/snippets-ajax/fetchclimate/{action}',
                    controller='ckanext.tethys_apps.controllers.snippets.fetchclimate:FetchClimateSnippetController')
        
        # Loop through harvester and add controllers
        controllers = self.harvester.controllers
        
        for controller in controllers:
            map.connect(controller['name'], controller['url'],
                        controller=controller['controller'],
                        action=controller['action'])
        return map
    
    def update_config(self, config):
        # add template directory for the apps plugin
        p.toolkit.add_template_directory(config, 'templates')
        
        # add public/static directories for apps plugin
        p.toolkit.add_public_directory(config, 'public')
        
        # add resources
        p.toolkit.add_resource('public', 'ckanext_apps')
        
        # Loop through harvester and add public and template directories
        templateDirs = self.harvester.templateDirs
        resources = self.harvester.resources
        publicDirs = self.harvester.publicDirs
        
        for templateDir in templateDirs:
            p.toolkit.add_template_directory(config, templateDir)
            
        for publicDir in publicDirs:
            p.toolkit.add_public_directory(config, publicDir)
            
        for resource in resources:
            p.toolkit.add_resource(resource['directory'], 
                                   resource['name'])
            
    def get_auth_functions(self):
        '''
        Add new/modify existing authorization functions to ckan
        '''
        return {'apps_read': self.apps_read}
    
    def apps_read(self, context, data_dict):
        '''
        Custom authorization function for the apps page
        '''
        _ = p.toolkit._
            
        authorized_user = model.User.get(context.get('user'))
        if not authorized_user:
            return {'success': False, 'msg': _('Not authorized')}
        
        return {'success': True}
    
    def get_helpers(self):
        '''
        Add app global method to template helpers
        '''
        return {'get_session_global': get_session_global,
                'get_app_definition': get_app_definition,
                'jsonify': jsonify}
        
    def make_middleware(self, app, config):
        '''
        Middleware hook
        '''
        return app
        
        
        
        

            
        
