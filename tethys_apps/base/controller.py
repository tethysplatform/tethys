"""
********************************************************************************
* Name: controller.py
* Author: Nathan Swain
* Created On: August 2013
* Copyright: (c) Brigham Young University 2013
* License: BSD 2-Clause
********************************************************************************
"""
from django.views.generic import View
from .url_map import UrlMapBase


def app_controller_maker(root_url):
    """
    Returns an AppController class that is bound to a specific root url. This method is deprecated. Use url_map_maker.
    """
    properties = {'root_url': root_url}
    return type('UrlMap', (UrlMapBase,), properties)


class TethysController(View):

    @classmethod
    def as_controller(cls, **kwargs):
        """
        Thin veneer around the as_view method to make interface more consistent with Tethys terminology.
        """
        return cls.as_view(**kwargs)
