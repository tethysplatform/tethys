from django.shortcuts import render

from tethys_apps.app_harvester import SingletonAppHarvester


def library(request):
    """
    Handle the library view
    """
    # Retrieve the app harvester
    harvester = SingletonAppHarvester()

    # Define the context object
    context = {'apps': harvester.apps}

    return render(request, 'tethys_apps/app_library.html', context)
