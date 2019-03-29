"""
********************************************************************************
* Name: views.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from tethys_sdk.permissions import login_required
from django.shortcuts import render

from .utilities import get_wps_service_engine, list_wps_service_engines, abstract_is_link


@login_required()
def datasets_home(request):
    """
    Home page for Tethys Datasets tool
    """
    context = {}

    return render(request, 'tethys_services/tethys_datasets/home.html', context)


@login_required()
def wps_home(request):
    """
    Home page for Tethys WPS tool. Lists all the WPS services that are linked.
    """
    wps_services = list_wps_service_engines()

    context = {'wps_services': wps_services}

    return render(request, 'tethys_services/tethys_wps/home.html', context)


@login_required()
def wps_service(request, service):
    """
    View that lists the processes for a given service.
    """

    wps = get_wps_service_engine(service)

    context = {'wps': wps,
               'service': service}

    return render(request, 'tethys_services/tethys_wps/service.html', context)


@login_required()
def wps_process(request, service, identifier):
    """
    View that displays a detailed description for a WPS process.
    """
    wps = get_wps_service_engine(service)
    wps_process = wps.describeprocess(identifier)

    context = {'process': wps_process,
               'service': service,
               'is_link': abstract_is_link(wps_process)}

    return render(request, 'tethys_services/tethys_wps/process.html', context)
