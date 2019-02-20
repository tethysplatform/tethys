import subprocess

from tethys_apps.cli.manage_commands import get_manage_path


def uninstall_command(args):
    """
    Uninstall an app command.
    """
    # Get the path to manage.py
    manage_path = get_manage_path(args)
    item_name = args.app_or_extension
    process = ['python', manage_path, 'tethys_app_uninstall', item_name]
    if args.is_extension:
        process.append('-e')
    if args.is_forced:
        process.append('-f')
    try:
        subprocess.call(process)
    except KeyboardInterrupt:
        pass
