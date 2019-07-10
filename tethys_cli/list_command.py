from tethys_apps.helpers import get_installed_tethys_apps, get_installed_tethys_extensions
from tethys_cli.cli_helpers import load_apps


def add_list_parser(subparsers):
    # Setup list command
    list_parser = subparsers.add_parser('list', help='List installed apps and extensions.')
    list_parser.set_defaults(func=list_command)


def list_command(args):
    """
    List installed apps.
    """
    load_apps()
    installed_apps = get_installed_tethys_apps()
    installed_extensions = get_installed_tethys_extensions()

    if installed_apps:
        print('Apps:')
        for item in installed_apps:
            print('  {}'.format(item))

    if installed_extensions:
        print('Extensions:')
        for item in installed_extensions:
            print('  {}'.format(item))
