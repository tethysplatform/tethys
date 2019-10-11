"""
********************************************************************************
* Name: cli/__init__.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
# Commandline interface for Tethys
import argparse

from tethys_cli.version_command import add_version_parser
from tethys_cli.app_settings_commands import add_app_settings_parser
from tethys_cli.db_commands import add_db_parser
from tethys_cli.docker_commands import add_docker_parser
from tethys_cli.gen_commands import add_gen_parser
from tethys_cli.link_commands import add_link_parser
from tethys_cli.list_command import add_list_parser
from tethys_cli.manage_commands import add_manage_parser
from tethys_cli.scaffold_commands import add_scaffold_parser
from tethys_cli.scheduler_commands import add_scheduler_parser
from tethys_cli.services_commands import add_services_parser
from tethys_cli.settings_commands import add_settings_parser
from tethys_cli.site_commands import add_site_parser
from tethys_cli.syncstores_command import add_syncstores_parser
from tethys_cli.test_command import add_test_parser
from tethys_cli.install_commands import add_install_parser
from tethys_cli.uninstall_command import add_uninstall_parser


def tethys_command_parser():
    """
    Tethys commandline interface function.
    """
    # Create parsers
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='Commands', dest='sub-command')
    subparsers.required = True

    add_version_parser(subparsers)
    add_app_settings_parser(subparsers)
    add_db_parser(subparsers)
    add_docker_parser(subparsers)
    add_gen_parser(subparsers)
    add_install_parser(subparsers)
    add_uninstall_parser(subparsers)
    add_link_parser(subparsers)
    add_list_parser(subparsers)
    add_manage_parser(subparsers)
    add_scaffold_parser(subparsers)
    add_scheduler_parser(subparsers)
    add_services_parser(subparsers)
    add_settings_parser(subparsers)
    add_site_parser(subparsers)
    add_syncstores_parser(subparsers)
    add_test_parser(subparsers)

    return parser


def tethys_command():
    parser = tethys_command_parser()
    # Parse the args and call the default function
    args = parser.parse_args()
    args.func(args)
