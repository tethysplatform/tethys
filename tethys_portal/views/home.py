"""
********************************************************************************
* Name: home.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from django.shortcuts import render, redirect
from django.conf import settings
from tethys_config.models import Setting


def home(request):
    # Some installations may wish to bypass the default home page
    # The BYPASS_TETHYS_HOME_PAGE setting in portal_config.yml allows them to do so
    if hasattr(settings, 'BYPASS_TETHYS_HOME_PAGE') and settings.BYPASS_TETHYS_HOME_PAGE:
        return redirect('app_library')

    ENABLE_OPEN_PORTAL = getattr(settings, 'ENABLE_OPEN_PORTAL', False)

    custom_template = Setting.objects.get(name='Home Page Template').content
    if custom_template:
        template = custom_template.lstrip('/') if custom_template.startswith('/') else custom_template
    else:
        template = 'tethys_portal/home.html'

    return render(request, template, {"ENABLE_OPEN_SIGNUP": settings.ENABLE_OPEN_SIGNUP,
                                      "ENABLE_OPEN_PORTAL": ENABLE_OPEN_PORTAL})
