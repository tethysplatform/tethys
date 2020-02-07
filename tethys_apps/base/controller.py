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


class TethysController(View):

    @classmethod
    def as_controller(cls, **kwargs):
        """
        Thin veneer around the as_view method to make interface more consistent with Tethys terminology.
        """
        return cls.as_view(**kwargs)
