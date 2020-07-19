"""
********************************************************************************
* Name: settings_commands.py
* Author: Scott Christensen
* Created On: 2019
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from pathlib import Path
from pprint import pformat
from argparse import Namespace

import yaml

from .gen_commands import generate_command
from tethys_cli.cli_colors import write_info, write_warning, write_error
from tethys_apps.utilities import get_tethys_home_dir

from django.conf import settings


TETHYS_HOME = Path(get_tethys_home_dir())


def add_settings_parser(subparsers):
    settings_parser = subparsers.add_parser('settings', help='Tethys settings configuration command.')
    settings_parser.add_argument(
        '-s', '--set',
        dest='set_kwargs',
        help='Key Value pairs to add to the settings in the portal_config.yml file. Hierarchical keys can be '
             'specified with dot notation. (e.g. DATABASES.default.NAME)',
        nargs=2,
        action='append',
    )
    settings_parser.add_argument(
        '-g', '--get',
        dest='get_key',
        help='Retrieve the resolved value of a key from settings if it exists. Otherwise, attempt to return the value '
             'of the key from the portal_config.yml',
        nargs='?',
        const='all',
    )
    settings_parser.add_argument(
        '-r', '--rm', '--remove',
        dest='rm_key',
        help='Removes a key from the portal_config.yml file if it exists. Hierarchical keys can be specified with '
             'dot notation. (e.g. DATABASES.default.NAME)',
        nargs=1,
    )
    settings_parser.set_defaults(
        func=settings_command,
    )


def read_settings():
    portal_yaml_file = TETHYS_HOME / 'portal_config.yml'
    tethys_settings = {}
    if portal_yaml_file.exists():
        with portal_yaml_file.open() as portal_yaml:
            tethys_settings = yaml.safe_load(portal_yaml).get('settings') or {}
    return tethys_settings


def generate_portal_config_file():
    write_warning('No Tethys Portal configuration file was found. Generating one now...')
    args = Namespace(type='portal_config', directory=None, overwrite=False)
    generate_command(args)


def write_settings(tethys_settings):
    portal_yaml_file = TETHYS_HOME / 'portal_config.yml'
    if not portal_yaml_file.exists():
        generate_portal_config_file()
    with portal_yaml_file.open('r') as portal_yaml:
        portal_settings = yaml.safe_load(portal_yaml) or {}
    portal_settings['settings'] = tethys_settings
    with portal_yaml_file.open('w') as portal_yaml:
        yaml.safe_dump(portal_settings, portal_yaml)


def set_settings(tethys_settings, kwargs):
    for key, value in kwargs:
        result = _get_dict_key_handle(tethys_settings, key, not_exists_okay=True)
        value = yaml.safe_load(value)
        if result is not None:
            d, k = result
            d[k] = value
    write_settings(tethys_settings)


def get_setting(tethys_settings, key):
    if key == 'all':
        all_settings = {k: getattr(settings, k) for k in dir(settings) if not k.startswith('_')
                        and not k == 'is_overridden'}
        write_info(pformat(all_settings))
        return
    try:
        value = getattr(settings, key)
        write_info(f'{key}: {pformat(value)}')
    except AttributeError:
        result = _get_dict_key_handle(tethys_settings, key)
        if result is not None:
            d, k = result
            write_info(f'{key}: {pformat(d[k])}')


def remove_setting(tethys_settings, key):
    result = _get_dict_key_handle(tethys_settings, key)
    if result is not None:
        d, k = result
        del d[k]
        write_settings(tethys_settings)


def _get_dict_key_handle(d, key, not_exists_okay=False):
    keys = key.split('.')
    values = [d]
    for k in keys:
        try:
            values.append(values[-1][k])
        except Exception:
            if not_exists_okay:
                if len(keys) > len(values):
                    values[-1][k] = {}
                    values.append(values[-1][k])
                else:
                    return values[-1], k
            else:
                write_error(f'The setting {key} does not exists.')
                return

    return values[-2], k


SETTINGS_COMMANDS = dict(
    set=set_settings,
    get=get_setting,
    remove=remove_setting,
)


def settings_command(args):
    tethys_settings = read_settings()
    if args.set_kwargs:
        set_settings(tethys_settings, args.set_kwargs)
    elif args.get_key:
        get_setting(tethys_settings, args.get_key)
    elif args.rm_key:
        remove_setting(tethys_settings, args.rm_key[0])
