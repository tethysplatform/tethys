"""
********************************************************************************
* Name: pre_collectstatic.py
* Author: Nathan Swain
* Created On: February 2015
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
    Command class that handles the collectstatic command for apps an extensions.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-l",
            "--link",
            action="store_true",
            default=False,
            help="Link static directories of apps into STATIC_ROOT instead of copying them. "
            "Not recommended.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            default=False,
            help="Clear the STATIC_ROOT directory before collecting static files.",
        )

    def handle(self, *args, **kwargs):
        """
        Symbolically link the static directories of each app into the static/public directory specified by the
        STATIC_ROOT parameter of the settings.py. Do this prior to running Django's collectstatic method.
        """  # noqa: E501
        if not settings.STATIC_ROOT:
            print(
                "WARNING: Cannot find the STATIC_ROOT setting. Please provide the path to the static directory using "
                "the STATIC_ROOT setting in the portal_config.yml file and try again."
            )
            exit(1)

        # Read settings
        static_root = settings.STATIC_ROOT

        # Handle clear option
        if kwargs.get("clear"):
            for item in Path(static_root).iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            print("INFO: Cleared STATIC_ROOT directory.")

        # Get a list of installed apps and extensions
        installed_apps_and_extensions = get_installed_tethys_items(
            apps=True, extensions=True
        )

        # Provide feedback to user
        print(
            'INFO: Collecting static and public directories of apps and extensions to "{0}".'.format(
                static_root
            )
        )

        # Get the link option
        link_opt = kwargs.get("link")

        for item, path in installed_apps_and_extensions.items():
            # Check for both variants of the static directory (named either public or static)
            public_path = Path(path) / "public"
            static_path = Path(path) / "static"

            if public_path.is_dir():
                item_static_source_dir = public_path
            elif static_path.is_dir():
                item_static_source_dir = static_path
            else:
                print(
                    f'WARNING: Cannot find a directory named "static" or "public" for app "{item}". Skipping...'
                )
                continue

            # Path for app in the STATIC_ROOT directory
            item_static_root_dir = Path(static_root) / item

            # Clear out old symbolic links/directories if necessary
            try:
                # Remove link
                item_static_root_dir.unlink()
            except OSError:
                try:
                    # Remove directory
                    shutil.rmtree(item_static_root_dir)
                except OSError:
                    pass
                    # No file to remove

            # Create appropriate symbolic link
            if link_opt:
                item_static_source_dir.symlink_to(item_static_root_dir)
                print(
                    'INFO: Successfully linked public directory to STATIC_ROOT for app "{0}".'.format(
                        item
                    )
                )

            else:
                shutil.copytree(item_static_source_dir, item_static_root_dir)
                print(
                    'INFO: Successfully copied public directory to STATIC_ROOT for app "{0}".'.format(
                        item
                    )
                )
