from __future__ import print_function
import subprocess

from builtins import input

from tethys_apps.cli.manage_commands import get_manage_path
from tethys_apps.cli.cli_colors import TC_WARNING, TC_ENDC


def syncstores_command(args):
    """
    Sync persistent stores.
    """
    # Get the path to manage.py
    manage_path = get_manage_path(args)

    # This command is a wrapper for a custom Django manage.py method called syncstores.
    # See tethys_apps.mangement.commands.syncstores
    process = ['python', manage_path, 'syncstores']

    if args.refresh:
        valid_inputs = ('y', 'n', 'yes', 'no')
        no_inputs = ('n', 'no')
        proceed = input('{1}WARNING:{2} You have specified the database refresh option. This will drop all of the '
                        'databases for the following apps: {0}. This could result in significant data loss and '
                        'cannot be undone. Do you wish to continue? (y/n): '.format(', '.join(args.app),
                                                                                    TC_WARNING,
                                                                                    TC_ENDC)).lower()

        while proceed not in valid_inputs:
            proceed = input('Invalid option. Do you wish to continue? (y/n): ').lower()

        if proceed not in no_inputs:
            process.extend(['-r'])
        else:
            print('Operation cancelled by user.')
            exit(0)

    if args.firsttime:
        process.extend(['-f'])

    if args.database:
        process.extend(['-d', args.database])

    if args.app:
        process.extend(args.app)

    try:
        subprocess.call(process)
    except KeyboardInterrupt:
        pass
