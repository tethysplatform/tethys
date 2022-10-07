"""
********************************************************************************
* Name: context_processors.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""


def tethys_gizmos_context(request):
    """
    Add the gizmos_rendered context to the global context.
    """

    # Setup variables
    context = {"gizmos_rendered": []}
    return context
