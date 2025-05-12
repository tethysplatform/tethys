import subprocess
import sys

from tethys_cli.cli_helpers import get_manage_path


def add_uninstall_parser(subparsers):
    # Setup uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall an app.")
    uninstall_parser.add_argument(
        "app_or_extension", help="Name of the app or extension to uninstall."
    )
    uninstall_parser.add_argument(
        "-e",
        "--extension",
        dest="is_extension",
        default=False,
        action="store_true",
        help="Flag to denote an extension is being uninstalled",
    )
    uninstall_parser.add_argument(
        "-f",
        "--force",
        dest="is_forced",
        default=False,
        action="store_true",
        help="Flag to denote force removal without showing a warning",
    )
    uninstall_parser.set_defaults(func=uninstall_command)


def uninstall_command(args):
    """
    Uninstall an app command.
    """
    # Get the path to manage.py
    manage_path = get_manage_path(args)
    item_name = args.app_or_extension
    process = [sys.executable, manage_path, "tethys_app_uninstall", item_name]
    if args.is_extension:
        process.append("-e")
    if args.is_forced:
        process.append("-f")
    try:
        subprocess.call(process)
    except KeyboardInterrupt:
        pass
