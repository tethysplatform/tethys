"""
********************************************************************************
* Name: workspace.py
* Author: tbayer
* Created On: February 5, 2019
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""

from django.contrib.auth.models import User
from tethys_apps.models import TethysApp
from tethys_apps.base.paths import (
    _get_user_workspace,
    _get_app_workspace,
    _get_user_media,
    _get_app_media,
)
from tethys_apps.harvester import SingletonHarvester
from tethys_quotas.handlers.base import ResourceQuotaHandler


class WorkspaceQuotaHandler(ResourceQuotaHandler):
    """
    Defines quotas for workspace (and media) storage for the given entity (User or TethysApp).

    inherits from ResourceQuotaHandler
    """  # noqa: E501

    codename = "workspace_quota"
    name = "Workspace Quota"
    description = "Set quota on workspace storage for apps and users."
    default = 1
    units = "GB"
    help = "You have exceeded your quota on storage. Please visit the storage management pages and clean workspaces."
    applies_to = ["django.contrib.auth.models.User", "tethys_apps.models.TethysApp"]

    def get_current_use(self):
        """
        calculates/retrieves the current use of the resource

        Returns:
            Int: current use of resource
        """
        current_use = 0.0

        if isinstance(self.entity, User):
            harvester = SingletonHarvester()
            installed_apps = harvester.apps

            for app in installed_apps:
                workspace = _get_user_workspace(app, self.entity, bypass_quota=True)
                media = _get_user_media(app, self.entity, bypass_quota=True)
                current_use += float(workspace.get_size(self.units)) + float(
                    media.get_size(self.units)
                )

        elif isinstance(self.entity, TethysApp):
            harvester = SingletonHarvester()
            installed_apps = harvester.apps

            tethys_app = next(
                (x for x in installed_apps if x.name == self.entity.name), None
            )

            if tethys_app is not None:
                workspace = _get_app_workspace(tethys_app, bypass_quota=True)
                media = _get_app_media(tethys_app, bypass_quota=True)
                current_use = float(workspace.get_size(self.units)) + float(
                    media.get_size(self.units)
                )

        return current_use
