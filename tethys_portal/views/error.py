"""
********************************************************************************
* Name: error.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from django.shortcuts import render


def handler_400(request):
    """
    Handle 400 errors
    """
    context = {'error_code': '400',
               'error_title': 'Bad Request',
               'error_message': "Sorry, but we can't process your request. Try something different.",
               'error_image': '/static/tethys_portal/images/error_500.png'}
    return render(request, 'tethys_portal/error.html', context, status=400)


def handler_403(request):
    """
    Handle 403 errors
    """
    context = {'error_code': '403',
               'error_title': 'Forbidden',
               'error_message': "We apologize, but this operation is not permitted.",
               'error_image': '/static/tethys_portal/images/error_403.png'}
    return render(request, 'tethys_portal/error.html', context, status=403)


def handler_404(request):
    """
    Handle 404 errors
    """
    context = {'error_code': '404',
               'error_title': 'Page Not Found',
               'error_message': "We are unable to find the page you requested. Please, check the address and try "
                                "again.",
               'error_image': '/static/tethys_portal/images/error_404.png'}
    return render(request, 'tethys_portal/error.html', context, status=404)


def handler_500(request):
    """
    Handle 500 errors
    """
    context = {'error_code': '500',
               'error_title': 'Internal Server Error',
               'error_message': "We're sorry, but we seem to have a problem. Please, come back later and try again.",
               'error_image': '/static/tethys_portal/images/error_500.png'}
    return render(request, 'tethys_portal/error.html', context, status=500)
