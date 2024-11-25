"""
********************************************************************************
* Name: collectworkspaces.py
* Author: Nathan Swain
* Created On: August 6, 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""

from pathlib import Path
import shutil

from django.core.management.base import BaseCommand
from django.conf import settings

from tethys_apps.utilities import get_installed_tethys_items


class Command(BaseCommand):
    """
    Command class that handles the collectworkspaces command.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            default=False,
            help="Force the overwrite the app directory into its collected-to location.",
        )

    def handle(self, *args, **options):
        """
        Symbolically link the static directories of each app into the static/public directory specified by the
        STATIC_ROOT parameter of the settings.py. Do this prior to running Django's collectstatic method.
        """
        if not hasattr(settings, "TETHYS_WORKSPACES_ROOT") or (
            hasattr(settings, "TETHYS_WORKSPACES_ROOT")
            and not settings.TETHYS_WORKSPACES_ROOT
        ):
            print(
                "WARNING: Cannot find the TETHYS_WORKSPACES_ROOT setting. "
                "Please provide the path to the static directory using the TETHYS_WORKSPACES_ROOT "
                "setting in the portal_config.yml file and try again."
            )
            exit(1)
        # Get optional force arg
        force = options["force"]

        # Read settings
        workspaces_root = settings.TETHYS_WORKSPACES_ROOT

        # Get a list of installed apps
        installed_apps = get_installed_tethys_items(apps=True)

        # Provide feedback to user
        print(
            f'INFO: Moving workspace directories of apps to "{workspaces_root}" and linking back.'
        )

        for app, path in installed_apps.items():
            # Check for both variants of the static directory (public and static)
            app_ws_path = Path(path) / "workspaces"
            tethys_ws_root_path = Path(workspaces_root) / app

            # Only perform if workspaces_path is a directory
            if not app_ws_path.is_dir():
                print(
                    f'WARNING: The workspace_path for app "{app}" is not a directory. Making workspace directory...'
                )
                app_ws_path.mkdir(parents=True, exist_ok=True)

            if not app_ws_path.is_symlink():
                if not tethys_ws_root_path.exists():
                    # Move the directory to workspace root path
                    shutil.move(app_ws_path, tethys_ws_root_path)
                else:
                    if force:
                        # Clear out old symbolic links/directories in workspace root if necessary
                        try:
                            # Remove link
                            tethys_ws_root_path.unlink()
                        except OSError:
                            shutil.rmtree(tethys_ws_root_path, ignore_errors=True)

                        # Move the directory to workspace root path
                        shutil.move(app_ws_path, tethys_ws_root_path)
                    else:
                        print(
                            f'WARNING: Workspace directory for app "{app}" already exists in the TETHYS_WORKSPACES_'
                            f"ROOT directory. A symbolic link is being created to the existing directory. To force "
                            f'overwrite the existing directory, re-run the command with the "-f" argument.'
                        )
                        shutil.rmtree(app_ws_path, ignore_errors=True)

                # Create appropriate symbolic link
                if tethys_ws_root_path.is_dir():
                    tethys_ws_root_path.symlink_to(app_ws_path)
                    print(
                        'INFO: Successfully linked "workspaces" directory to TETHYS_WORKSPACES_ROOT for app '
                        '"{0}".'.format(app)
                    )
