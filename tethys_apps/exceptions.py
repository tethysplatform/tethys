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
    pass


class TethysAppSettingNotAssigned(Exception):
    pass


class PersistentStoreDoesNotExist(Exception):
    pass


class PersistentStoreExists(Exception):
    pass
