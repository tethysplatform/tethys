"""
********************************************************************************
* Name: views.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse

from tethys_apps.app_harvester import SingletonAppHarvester
from tethys_apps.base.app_base import TethysAppBase


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

    manager = TethysAppBase.get_handoff_manager()
    handlers = manager.get_capabilities(app_name)

    # filter out request arguments and internal handlers
    for handler in handlers:
        try:
            index = handler['arguments'].index('request')
        except ValueError:
            pass
        else:
            handler['arguments'].pop(index)

    return HttpResponse(json.dumps(handlers), content_type='application/javascript')


@login_required()
def handoff(request, app_name, handler_name):
    """
    Handle handoff requests.
    """
    app_name = app_name.replace('-', '_')

    manager = TethysAppBase.get_handoff_manager()

    return manager.handoff(request, handler_name, app_name, **request.GET.dict())
