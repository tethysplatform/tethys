"""
********************************************************************************
* Name: tethys_layouts/views/base.py
* Author: Nathan Swain
* Created On: December 10, 2016
* Copyright: (c) Nathan Swain 2016
* License: BSD 2-Clause
********************************************************************************
"""
from django.views.generic.base import TemplateView


class TethysLayoutController(TemplateView):
    """
    Base class for all class based layout controllers.
    """
