from pathlib import Path

from tethys_apps.helpers import get_installed_tethys_apps, get_installed_tethys_extensions
from tethys_apps.utilities import get_tethys_src_dir
from tethys_cli.cli_helpers import load_apps
from tethys_cli.cli_colors import write_info


def add_list_parser(subparsers):
    # Setup list command
    list_parser = subparsers.add_parser('list', help='List installed apps and extensions.')
    list_parser.add_argument('-s', '--settings', dest='settings', action='store_true',)
    list_parser.set_defaults(func=list_command, settings=False)


def list_command(args):
    """
    List installed apps.
    """
    if args.settings is True:
        print(Path(get_tethys_src_dir()) / 'tethys_portal' / 'settings.py')
        return

    load_apps()
    installed_apps = get_installed_tethys_apps()
    installed_extensions = get_installed_tethys_extensions()

    if installed_apps:
        write_info('Apps:')
        for item in installed_apps:
            print('  {}'.format(item))

    if installed_extensions:
        write_info('Extensions:')
        for item in installed_extensions:
            print('  {}'.format(item))
