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
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest

import tethys_apps.app_harvester

class HandoffManager(object):
    """
    An object that is used to interact with HandoffHandlers.

    Attributes:
      app (str): Instance of a TethysAppBase object.
      handlers (str): A list of HandoffHandlers registered in the app.
    """

    def __init__(self, app):
        """
        Constructor
        """

        self.app = app
        self.handlers = app.handoff_handlers() or []

    def __repr__(self):
        """
        String representation
        """
        return '<Handoff Manager: app={0}, handlers={1}>'.format(self.app, self.handlers)

    def get_capabilities(self, app_name=None):
        """
        Gets a list of the handoff handlers.

        Args:
            app_name (str, optional): The name of another app whose capabilities should be listed. Defaults to None in which case the capabilities of the current app will be listed.

        Returns:
            A list of dictionary objects containing the handoff capabilities of app_name.
        """
        manager = self.get_handoff_manager_for_app(app_name)

        handlers = []

        if manager:
            for handoff_handler in manager.handlers:
                handler = manager._get_handler_function(handoff_handler)
                args = inspect.getargspec(handler)
                handlers.append({"arguments": args.args,
                                 "name": handoff_handler.name})
        return handlers

    def handoff(self, request, handler_name, app_name=None, **kwargs):
        """
        Calls handler if it exists for the app.

        Args:
            request (HttpRequest): The request object passed by the http call.
            handler_name (str): The name of the HandoffHandler object to handle the handoff.
            app_name (str, optional): The name of another app where the handler should exist. Defaults to None in which case the current app will attempt to handle the handoff.
            **kwargs: Key-value pairs to be passed on to the handler.

        Returns:
            HttpResponse object.
        """

        error = {"message": "",
                 "code": 400,
                 "status": "error",
                 "app_name": app_name or self.app.name,
                 "handler_name": handler_name}

        manager = self.get_handoff_manager_for_app(app_name)

        if manager:
            handler = manager.get_handler(handler_name)

            try:
                urlish = handler(request, **kwargs)
                return redirect(urlish)
            except TypeError as e:
                error['message'] = "HTTP 400 Bad Request: {0}. ".format(e.message)
                return HttpResponseBadRequest(json.dumps(error), content_type='application/javascript')

        error['message'] = "HTTP 400 Bad Request: No handoff handler '{0}' for app '{1}' found.".format(self.app.name, handler_name)
        return HttpResponseBadRequest(json.dumps(error), content_type='application/javascript')

    def get_handler(self, handler_name, app_name=None):
        """
        Returns the handler function with name == handler_name.

        Args:
            handler_name (str): the name of a HandoffHandler object.
            app_name (str, optional): the name of the app with handler_name. Defaults to None in which case the current app will be used.

        Returns:
            A HandoffHandler object where the name attribute is equal to handler_name or None if no HandoffHandler with that name is found.
        """
        manager = self.get_handoff_manager_for_app(app_name)

        if manager:
            for handoff_handler in manager.handlers:
                if handoff_handler.name == handler_name:
                    handler = manager._get_handler_function(handoff_handler)

                    return handler

    def get_handoff_manager_for_app(self, app_name):
        """
        Returns the app manager for app with package == app_name if that app is installed.

        Args:
            app_name (str): The name of another Tethys app whose HandoffManager should be returned. If None then self is returned.

        Returns:
            A HandoffManager object for the app with the name app_name or None if no app with that name is found.
        """

        if not app_name:
            return self

        # Get the app
        harvester = tethys_apps.app_harvester.SingletonAppHarvester()
        apps = harvester.apps

        for app in apps:
            if app.package == app_name:
                manager = app.get_handoff_manager()
                return manager

    def _get_handler_function(self, handoff_handler):
        """
        Returns the function of a handoff_handler object.

        Args:
            handoff_handler (HandoffHandler): The HandoffHandler object whose Python function should be returned.

        Returns:
            A handle to a Python function that will process the handoff.
        """

        if ':' in handoff_handler.handler: #TODO DEPRECATE: delete deprecated code
            print('DEPRECATION WARNING: The handler attribute of a HandoffHandler should now be in the form: "my_first_app.controllers.my_handler". The form "handoff:my_handler" is now deprecated.')

            # Split into module name and function name
            handler_mod, handler_function = handoff_handler.handler.split(':')

            # Pre-process handler path
            handler_path = '.'.join(('tethys_apps.tethysapp', self.app.package, handler_mod))
        else:
            # Split into parts and extract function name
            handler_mod, handler_function = handoff_handler.handler.rsplit('.', 1)

            #Pre-process handler path
            handler_path = '.'.join(('tethys_apps.tethysapp', handler_mod))

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
      handler(str): Path to the handler function for the handoff interaction. Use dot-notation (e.g.: "foo.bar.function").
    """

    def __init__(self, name, handler, internal=False):
        """
        Constructor
        """
        self.name = name
        self.handler = handler
        self.internal = internal

    def __repr__(self):
        """
        String representation
        """
        return '<Handoff Handler: name={0}, handler={1}>'.format(self.name, self.handler)

    def __json__(self):
        """
        JSON representation
        """
        return {'name': self.name,
                'arguments': self.json_arguments,
                }

    @property
    def function(self):
        pass