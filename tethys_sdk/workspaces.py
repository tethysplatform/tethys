"""
********************************************************************************
* Name: workspaces.py
* Author: Nathan Swain
* Created On: 7 August 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""

# flake8: noqa
# DO NOT ERASE
from tethys_apps.base.workspace import (
    TethysWorkspace,
    get_app_workspace_old as get_app_workspace,
    get_user_workspace_old as get_user_workspace,
)

from tethys_apps.base.paths import (
    app_workspace,
    user_workspace,
)
