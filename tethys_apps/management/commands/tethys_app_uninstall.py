"""
********************************************************************************
* Name: tethys_app_uninstall.py
* Author: Nathan Swain
* Created On: August 6, 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""

import site
import subprocess
import sys
import warnings
from pathlib import Path

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from tethys_apps.base import TethysAppBase, TethysExtensionBase
from tethys_apps.utilities import delete_secrets, get_installed_tethys_items


class Command(BaseCommand):
    """
    Command class that handles the uninstall command for uninstall Tethys apps.
    """

    def add_arguments(self, parser):
        parser.add_argument("app_or_extension", nargs="+", type=str)
        parser.add_argument(
            "-e", "--extension", dest="is_extension", default=False, action="store_true"
        )
        parser.add_argument(
            "-f", "--force", dest="is_forced", default=False, action="store_true"
        )

    def handle(self, *args, **options):
        """
        Remove the app from disk and in the database
        """
        from tethys_apps.models import TethysApp, TethysExtension

        if options["is_extension"]:
            TethysModel = TethysExtension
            TethysBaseClass = TethysExtensionBase
        else:
            TethysModel = TethysApp
            TethysBaseClass = TethysAppBase

        verbose_name = TethysModel._meta.verbose_name
        PREFIX = TethysBaseClass.package_namespace
        item_name = options["app_or_extension"][0]

        # Check for app files installed
        installed_items = get_installed_tethys_items(
            apps=not options["is_extension"], extensions=options["is_extension"]
        )

        if PREFIX in item_name:
            prefix_length = len(PREFIX) + 1
            item_name = item_name[prefix_length:]

        module_found = True
        if item_name not in installed_items:
            module_found = False

        # Check for app/extension in database
        db_app = None
        db_found = True

        try:
            db_app = TethysModel.objects.get(package=item_name)
        except TethysModel.DoesNotExist:
            db_found = False

        if not module_found and not db_found:
            warnings.warn(
                f'WARNING: {verbose_name} with name "{item_name}" cannot be uninstalled, '
                f"because it is not installed or not a {verbose_name}.",
                stacklevel=2,
            )
            exit(0)

        # Confirm
        item_with_prefix = f"{PREFIX}-{item_name}"

        valid_inputs = ("y", "n", "yes", "no")
        no_inputs = ("n", "no")

        confirmation_message = (
            f'Are you sure you want to uninstall "{item_with_prefix}"? (y/n): '
        )

        if not options["is_forced"]:
            overwrite_input = input(confirmation_message).lower()

            while overwrite_input not in valid_inputs:
                overwrite_input = input(
                    f"Invalid option. {confirmation_message}"
                ).lower()

            if overwrite_input in no_inputs:
                self.stdout.write("Uninstall cancelled by user.")
                exit(0)

        # Remove app from database
        if db_found and db_app:
            db_app.delete()

            # Get the TethysApp content type
            app_content_type = ContentType.objects.get(
                app_label=TethysModel._meta.app_label,
                model=TethysModel._meta.model_name,
            )

            # Remove any permissions associated to the app/extension
            db_app_permissions = (
                Permission.objects.filter(content_type=app_content_type)
                .filter(name__icontains=f"{db_app.package} | ")
                .all()
            )

            for db_app_permission in db_app_permissions:
                db_app_permission.delete()

            # Remove any groups associated to the app/extension
            db_app_groups = Group.objects.filter(
                name__icontains=f"{db_app.package}:"
            ).all()

            for db_app_group in db_app_groups:
                db_app_group.delete()

        # Uninstall using pip
        process = [sys.executable, "-m", "pip", "uninstall", "-y", item_with_prefix]

        try:
            subprocess.Popen(
                process, stderr=subprocess.STDOUT, stdout=subprocess.PIPE
            ).communicate()[0]
        except KeyboardInterrupt:
            pass

        # Remove the namespace package file if applicable.
        for site_package in site.getsitepackages():
            try:
                Path(
                    f'{site_package}/{PREFIX}-{item_name.replace("_", "-")}-nspkg.pth'
                ).unlink()
            except Exception:
                continue
        delete_secrets(item_name)

        self.stdout.write(
            f'{verbose_name} "{item_with_prefix}" successfully uninstalled.'
        )
