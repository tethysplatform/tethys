from __future__ import print_function
from tethys_apps.helpers import get_installed_tethys_apps, get_installed_tethys_extensions


def list_command(args):
    """
    List installed apps.
    """
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
