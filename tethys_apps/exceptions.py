"""
********************************************************************************
* Name: exceptions.py
* Author: Nathan Swain
* Created On: March 25, 2017
* Copyright:
* License: BSD 2-Clause
********************************************************************************
"""


class TethysAppSettingDoesNotExist(Exception):
    def __init__(self, setting_type, setting_name, app_name, *args, **kwargs):
        msg = 'A {0} named "{1}" does not exist in the {2} app.'.format(
            setting_type, setting_name, app_name.encode("utf-8")
        )
        super().__init__(msg, *args, **kwargs)


class TethysAppSettingNotAssigned(Exception):
    pass


class PersistentStoreDoesNotExist(Exception):
    pass


class PersistentStoreExists(Exception):
    pass


class PersistentStorePermissionError(Exception):
    pass


class PersistentStoreInitializerError(Exception):
    pass
