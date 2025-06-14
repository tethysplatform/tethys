import subprocess
import sys

from tethys_cli.cli_helpers import get_manage_path
from tethys_cli.cli_colors import TC_WARNING, TC_ENDC


def add_syncstores_parser(subparsers):
    # Sync stores command
    syncstores_parser = subparsers.add_parser(
        "syncstores", help="Management command for App Persistent Stores."
    )
    syncstores_parser.add_argument(
        "app",
        help='Name of the target on which to perform persistent store sync OR "all" '
        "to sync all of them.",
        nargs="+",
    )
    syncstores_parser.add_argument(
        "-r",
        "--refresh",
        help="When called with this option, the tables will be dropped prior to syncing"
        " resulting in a refreshed database.",
        action="store_true",
        dest="refresh",
    )
    syncstores_parser.add_argument(
        "-f",
        "--firsttime",
        help="Call with this option to force the initializer functions to be executed with "
        '"first_time" parameter True.',
        action="store_true",
        dest="firsttime",
    )
    syncstores_parser.add_argument("-d", "--database", help="Name of database to sync.")
    syncstores_parser.add_argument(
        "-m",
        "--manage",
        help="Absolute path to manage.py for " "Tethys Platform installation.",
    )
    syncstores_parser.set_defaults(
        func=syncstores_command, refresh=False, firstime=False
    )


def syncstores_command(args):
    """
    Sync persistent stores.
    """
    # Get the path to manage.py
    manage_path = get_manage_path(args)

    # This command is a wrapper for a custom Django manage.py method called syncstores.
    # See tethys_apps.mangement.commands.syncstores
    process = [sys.executable, manage_path, "syncstores"]

    if args.refresh:
        valid_inputs = ("y", "n", "yes", "no")
        no_inputs = ("n", "no")
        proceed = input(
            "{1}WARNING:{2} You have specified the database refresh option. This will drop all of the "
            "databases for the following apps: {0}. This could result in significant data loss and "
            "cannot be undone. Do you wish to continue? (y/n): ".format(
                ", ".join(args.app), TC_WARNING, TC_ENDC
            )
        ).lower()

        while proceed not in valid_inputs:
            proceed = input("Invalid option. Do you wish to continue? (y/n): ").lower()

        if proceed not in no_inputs:
            process.extend(["-r"])
        else:
            print("Operation cancelled by user.")
            exit(0)

    if args.firsttime:
        process.extend(["-f"])

    if args.database:
        process.extend(["-d", args.database])

    if args.app:
        process.extend(args.app)

    try:
        subprocess.call(process)
    except KeyboardInterrupt:
        pass
