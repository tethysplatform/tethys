# -*- coding: utf-8 -*-
"""middleware.py

    This is for handling ajax exceptions.

    Author: Alan D. Snow
    Created: September 20, 2017
    License: BSD 3-Clause
"""
from django.http import HttpResponseBadRequest

from .ajax import TethysError


class ErrorMiddleware(object):
    def process_exception(self, request, exception):
        """
        This processes the exeption of the request.
        """
        if isinstance(exception, TethysError):
            return HttpResponseBadRequest(exception.ajax_error_message)
