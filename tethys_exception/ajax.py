# -*- coding: utf-8 -*-
"""ajax.py

    This is for handling ajax exceptions.

    Author: Alan D. Snow
    Created: September 20, 2017
    License: BSD 3-Clause
"""
class TethysError(Exception):
    """This is an exception for Tethys Platform ajax errors."""
    __prepend__ = "Tethys"
    
    @property
    def ajax_error_message(self):
        return "{prepend} error: {exception}" \
               .format(prepend=self.__prepend__,
                       exception=self)
    pass


class DatabaseError(TethysError):
    """This is an exception for database errors."""
    __prepend__ = "Database"
    pass


class GeoServerError(TethysError):
    """This is an exception for GeoServer errors."""
    __prepend__ = "GeoServer"
    pass


class InvalidDataError(TethysError):
    """This is an exception for request input validation errors."""
    __prepend__ = "Invalid data"
    pass


class NotFoundError(TethysError):
    """This is an exception for items not found."""
    __prepend__ = "Not found"
    pass


class SettingsError(TethysError):
    """This is an exception for app settings errors."""
    __prepend__ = "Settings"
    pass


class UploadError(TethysError):
    """This is an exception for uploading errors."""
    __prepend__ = "Upload"
    pass


