"""
********************************************************************************
* Name: views.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
import inspect
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponse

from tethys_apps.app_harvester import SingletonAppHarvester


@login_required()
def library(request):
    """
    Handle the library view
    """
    # Retrieve the app harvester
    harvester = SingletonAppHarvester()

    # Define the context object
    context = {'apps': harvester.apps}

    return render(request, 'tethys_apps/app_library.html', context)

@login_required()
def handoff_capabilities(request, app_name):
    """
    Show handoff capabilities of the app name provided.
    """
    app_name = app_name.replace('-', '_')

    # Get the app
    harvester = SingletonAppHarvester()
    apps = harvester.apps

    handlers = []

    for app in apps:
        if app.package == app_name and app.handoff_handlers():
            for handoff_handler in app.handoff_handlers():
                handler_mod, handler_function = handoff_handler.handler.split(':')

                # Pre-process handler path
                handler_path = '.'.join(('tethys_apps.tethysapp', app.package, handler_mod))

                # Import module
                module = __import__(handler_path, fromlist=[handler_function])

                # Get the function
                handler = getattr(module, handler_function)
                args = inspect.getargspec(handler)
                handlers.append({"arguments": args.args,
                                 "name": handoff_handler.name})

    return HttpResponse(json.dumps(handlers), content_type='application/javascript')


@login_required()
def handoff(request, app_name, handler_name):
    """
    Handle handoff requests.
    """
    app_name = app_name.replace('-', '_')

    error = {"message": "",
             "code": 400,
             "status": "error",
             "app_name": app_name,
             "handler_name": handler_name}

    # Get the app
    harvester = SingletonAppHarvester()
    apps = harvester.apps

    for app in apps:
        if app.package == app_name and app.handoff_handlers():
            for handoff_handler in app.handoff_handlers():
                if handoff_handler.name == handler_name:
                    # Split into module name and function name
                    handler_mod, handler_function = handoff_handler.handler.split(':')

                    # Pre-process handler path
                    handler_path = '.'.join(('tethys_apps.tethysapp', app.package, handler_mod))

                    # Import module
                    module = __import__(handler_path, fromlist=[handler_function])

                    # Get the function
                    handler = getattr(module, handler_function)

                    try:
                        urlish = handler(request, **request.GET.dict())
                        return redirect(urlish)
                    except TypeError as e:
                        error['message'] = "HTTP 400 Bad Request: {0}. ".format(e.message)
                        return HttpResponseBadRequest(json.dumps(error), content_type='application/javascript')

    error['message'] = "HTTP 400 Bad Request: No handoff handler '{0}' for app '{1}' found.".format(app_name, handler_name)
    return HttpResponseBadRequest(json.dumps(error), content_type='application/javascript')