"""
********************************************************************************
* Name: persistent store
* Author: Nathan Swain
* Created On: August 11, 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""

class HandoffHandler(object):
    """
    An object that is used to reagister a Handoff handler functions.

    Attributes:
      name(str): Name of the handoff handler.
      handler(str): Path to the handler function for the handoff interaction. Use dot-notation with a colon delineating the function (e.g.: "foo.bar:function").
    """

    def __init__(self):