"""
********************************************************************************
* Name: handoff.py
* Author: Nathan Swain and Scott Christensen
* Created On: August 11, 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""
import inspect
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponse

from tethys_apps.app_harvester import *

#TODO add docstrings
class HandoffManager(object):
    """

    """
    def __init__(self, app):
        """
        Constructor
        """
        self.app = app
        self.handlers = app.handoff_handlers()

    def get_capabilities(self, app_name=None):
        """
        Gets a list of the handoff handlers.
        """
        manager = self.get_handoff_manager_for_app(app_name)

        handlers = []

        if manager:
            for handoff_handler in manager.handlers:
                handler = self._get_handler_function(handoff_handler)
                args = inspect.getargspec(handler)
                handlers.append({"arguments": args.args,
                                 "name": handoff_handler.name})
        return handlers

    def handoff(self, request, handler_name, app_name=None, **kwargs):
        """
        Calls handler if it exists for the app.
        """

        error = {"message": "",
                 "code": 400,
                 "status": "error",
                 "app_name": self.app.name,
                 "handler_name": handler_name}

        manager = self.get_handoff_manager_for_app(app_name)

        if manager:
            handler = manager.get_handler(handler_name)

            try:
                urlish = handler(request, **kwargs)
                if isinstance(urlish, tuple):
                    return redirect(*urlish)
                return redirect(urlish)
            except TypeError as e:
                error['message'] = "HTTP 400 Bad Request: {0}. ".format(e.message)
                return HttpResponseBadRequest(json.dumps(error), content_type='application/javascript')

        error['message'] = "HTTP 400 Bad Request: No handoff handler '{0}' for app '{1}' found.".format(self.app.name, handler_name)
        return HttpResponseBadRequest(json.dumps(error), content_type='application/javascript')

    def get_handler(self, handler_name):
        """
        Returns the handler function with name == handler_name
        """
        for handoff_handler in self.handlers:
            if handoff_handler.name == handler_name:
                handler = self._get_handler_function(handoff_handler)

                return handler

    def get_handoff_manager_for_app(self, app_name):
        """
        Returns the app manager for app with package == app_name if that app is installed.
        """

        if not app_name:
            return self

        # Get the app
        harvester = SingletonAppHarvester()
        apps = harvester.apps

        for app in apps:
            if app.package == app_name:
                manager = app.get_handoff_manager()
                return manager

    def _get_handler_function(self, handoff_handler):
        """
        Returns the function of a handoff_handler object
        """

        if ':' in handoff_handler.handler: #TODO DEPRECATE: delete deprecated code
            print('DEPRECATION WARNING: handler controllers should now be in the form: "my_first_app.controllers.my_handler"')
            # Split into module name and function name
            handler_mod, handler_function = handoff_handler.handler.split(':')

            # Pre-process handler path
            handler_path = '.'.join(('tethys_apps.tethysapp', self.app.package, handler_mod))
        else:
            # Split into parts and extract function name
            handler_parts = handoff_handler.handler.split('.')
            handler_function = handler_parts[-1]

            #Pre-process handler path
            handler_path_parts = handler_parts[:-1]
            handler_path_parts.insert(0, 'tethys_apps.tethysapp')
            handler_path = '.'.join(handler_path_parts)

        # Import module
        module = __import__(handler_path, fromlist=[handler_function])

        # Get the function
        handler = getattr(module, handler_function)

        return handler


class HandoffHandler(object):
    """
    An object that is used to register a Handoff handler functions.

    Attributes:
      name(str): Name of the handoff handler.
      handler(str): Path to the handler function for the handoff interaction. Use dot-notation with a colon delineating the function (e.g.: "foo.bar:function").
    """

    def __init__(self, name, handler):
        """
        Constructor
        """
        self.name = name
        self.handler = handler

    def __repr__(self):
        """
        String representation
        """
        return '<Handoff Handler: name={0}, handler={1}>'.format(self.name, self.handler)