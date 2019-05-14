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
from tethys_cli.syncstores_command import add_syncstores_parser
from tethys_cli.test_command import add_test_parser
from tethys_cli.uninstall_command import add_uninstall_parser

# from tethys_cli.docker_commands import docker_command, docker_container_inputs, add_docker_parser
# from tethys_cli.db_commands import add_db_parser
# from tethys_cli.list_command import add_list_parser
# from tethys_cli.scaffold_commands import scaffold_command, add_scaffold_parser
# from tethys_cli.syncstores_command import add_syncstores_parser
# from tethys_cli.test_command import add_test_parser
# from tethys_cli.uninstall_command import add_uninstall_parser
# from tethys_cli.manage_commands import (manage_command, MANAGE_START, MANAGE_SYNCDB,
#                                         MANAGE_COLLECTSTATIC, MANAGE_COLLECTWORKSPACES, MANAGE_SYNC,
#                                         MANAGE_COLLECT, MANAGE_CREATESUPERUSER, add_manage_parser)
# from tethys_cli.services_commands import (services_create_persistent_command, services_create_spatial_command,
#                                           services_list_command, services_remove_persistent_command,
#                                           services_remove_spatial_command, add_services_parser)
# from tethys_cli.link_commands import link_command, add_link_parser
# from tethys_cli.app_settings_commands import (app_settings_list_command, app_settings_create_ps_database_command,
#                                               app_settings_remove_command, add_app_settings_parser)
# from tethys_cli.scheduler_commands import (schedulers_list_command, schedulers_remove_command,
#                                            condor_scheduler_create_command, dask_scheduler_create_command, add_scheduler_parser)
# from tethys_cli.gen_commands import VALID_GEN_OBJECTS, generate_command, add_gen_parser


# Module level variables
# PREFIX = 'tethysapp'


def tethys_command():
    """
    Tethys commandline interface function.
    """
    # Create parsers
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='Commands', dest='require at least one argument')
    subparsers.required = True

    add_app_settings_parser(subparsers)
    add_db_parser(subparsers)
    add_docker_parser(subparsers)
    add_gen_parser(subparsers)
    add_link_parser(subparsers)
    add_list_parser(subparsers)
    add_manage_parser(subparsers)
    add_scaffold_parser(subparsers)
    add_scheduler_parser(subparsers)
    add_services_parser(subparsers)
    add_syncstores_parser(subparsers)
    add_test_parser(subparsers)
    add_uninstall_parser(subparsers)

    # Parse the args and call the default function
    args = parser.parse_args()
    args.func(args)
