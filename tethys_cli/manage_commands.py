"""
********************************************************************************
* Name: manage_commands.py
* Author: Nathan Swain
* Created On: 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""

import sys
from django.core.management import get_commands
from django.conf import settings

from tethys_cli.cli_helpers import get_manage_path, run_process
from tethys_cli.cli_colors import write_warning
from tethys_utils import deprecation_warning, DOCS_BASE_URL


MANAGE_START = "start"
MANAGE_COLLECTSTATIC = "collectstatic"
MANAGE_COLLECTWORKSPACES = "collectworkspaces"
MANAGE_COLLECT = "collectall"
MANAGE_GET_PATH = "path"
MANAGE_TENANTS = [
    "migrate_schemas",
    "tenant_command",
    "all_tenants_command",
    "create_tenant_superuser",
    "create_tenant",
    "delete_tenant",
    "clone_tenant",
    "rename_schema",
    "create_missing_schemas",
]


def add_manage_parser(subparsers):
    # sub-command choices
    TETHYS_COMMANDS = [
        MANAGE_START,
        MANAGE_COLLECTSTATIC,
        MANAGE_COLLECTWORKSPACES,
        MANAGE_COLLECT,
        MANAGE_GET_PATH,
    ]
    DJANGO_COMMANDS = [
        i for i in sorted(list(get_commands().keys())) if i not in TETHYS_COMMANDS
    ]
    manage_parser = subparsers.add_parser(
        "manage", help="Management commands for Tethys Platform."
    )
    manage_parser.add_argument(
        "command",
        help="Management command to run."
        f'\n{{{", ".join(e for e in [*TETHYS_COMMANDS, *DJANGO_COMMANDS])}}}'
        "\n Also accepts any valid manage.py command from Django (see --django-help).",
    )
    manage_parser.add_argument(
        "-m",
        "--manage",
        help="Absolute path to manage.py for Tethys Platform installation.",
    )
    manage_parser.add_argument(
        "-p",
        "--port",
        type=str,
        help="Host and/or port on which to bind the development server.",
    )
    manage_parser.add_argument(
        "--noinput",
        action="store_true",
        help="Pass the --noinput argument to the manage.py command. Deprecated. This is now the default behavior.",
    )
    manage_parser.add_argument(
        "--clear",
        action="store_true",
        help="Pass the --clear argument to the manage.py command.",
    )
    manage_parser.add_argument(
        "-f",
        "--force",
        required=False,
        action="store_true",
        help="Used only with {} to force the overwrite the app directory into its collect-to "
        "location.",
    )
    manage_parser.add_argument(
        "-l",
        "--link",
        required=False,
        action="store_true",
        help="Only used with collectstatic command. Link static directory to STATIC_ROOT "
        "instead of copying it. Not recommended.",
    )
    manage_parser.add_argument(
        "--django-help",
        action="store_true",
        help="Display the help for specific commands coming from Django. "
        'E.g. "tethys manage <django command> --django-help"',
    )
    manage_parser.set_defaults(
        func=manage_command, parsing_method="accepts_unknown_args"
    )


def manage_command(args, unknown_args=None):
    """
    Management commands.
    """
    if not unknown_args:
        unknown_args = []

    # Get the path to manage.py
    manage_path = get_manage_path(args)

    # Define the process to be run
    primary_process = None

    if args.command == MANAGE_START:
        if args.port:
            primary_process = [sys.executable, manage_path, "runserver", args.port]
        else:
            primary_process = [sys.executable, manage_path, "runserver"]

    elif args.command == MANAGE_COLLECTSTATIC:
        # Run pre_collectstatic
        intermediate_process = [sys.executable, manage_path, "pre_collectstatic"]

        if args.link:
            intermediate_process.append("--link")

        if args.clear:
            intermediate_process.append("--clear")

        run_process(intermediate_process)

        # Setup for main collectstatic
        primary_process = [sys.executable, manage_path, "collectstatic"]

        # Prevent the overwrite files prompt every time
        primary_process.append("--noinput")

    elif args.command == MANAGE_COLLECTWORKSPACES:
        # Run collectworkspaces command
        deprecation_warning(
            version="5.0",
            feature='the "collectworkspaces" command',
            message="The Workspaces API has been replaced by the new Paths API. After converting apps to using the "
            'the Paths API the "collectworkspaces" command will not be necessary '
            f"(see {DOCS_BASE_URL}tethys_sdk/paths.html#centralized-paths).\n"
            f"For a full guide to transitioning to the Paths API see "
            f"{DOCS_BASE_URL}/tethys_sdk/workspaces.html#transition-to-paths-guide",
        )
        if args.force:
            primary_process = [
                sys.executable,
                manage_path,
                "collectworkspaces",
                "--force",
            ]
        else:
            primary_process = [sys.executable, manage_path, "collectworkspaces"]

    elif args.command == MANAGE_COLLECT:
        # Convenience command to run collectstatic and collectworkspaces
        deprecation_warning(
            version="5.0",
            feature='the "collectall" command',
            message="The Workspaces API has been replaced by the new Paths API. After converting apps to using the "
            'the Paths API the "collectworkspaces" command will not be necessary and thus "collectstatic" '
            'should be run in place of "collectall" '
            f"(see {DOCS_BASE_URL}tethys_sdk/paths.html#centralized-paths).\n"
            f"For a full guide to transitioning to the Paths API see "
            f"{DOCS_BASE_URL}/tethys_sdk/workspaces.html#transition-to-paths-guide",
        )

        # Run pre_collectstatic
        intermediate_process = [sys.executable, manage_path, "pre_collectstatic"]
        if args.clear:
            intermediate_process.append("--clear")

        run_process(intermediate_process)

        # Setup for main collectstatic
        intermediate_process = [sys.executable, manage_path, "collectstatic"]

        # Prevent the overwrite files prompt every time
        intermediate_process.append("--noinput")

        run_process(intermediate_process)

        # Run collectworkspaces command
        primary_process = [sys.executable, manage_path, "collectworkspaces"]

    elif args.command == MANAGE_GET_PATH:
        print(manage_path)

    elif args.command in MANAGE_TENANTS:
        DATABASES = getattr(settings, "DATABASES", {})
        if not getattr(settings, "TENANTS_ENABLED", False):
            write_warning(
                "Multi-tenancy features are not enabled. To enable multi-tenancy, set 'TENANTS_CONFIG.ENABLED "
                "to true in your portal_config.yml file. "
                "You can use the following command to do so:\n\n"
                "tethys settings --set TENANTS_CONFIG.ENABLED true\n\n"
                "For more information, see the documentation at "
                f"{DOCS_BASE_URL}tethys_portal/multi_tenancy.html"
            )
            sys.exit(1)
        elif DATABASES["default"]["ENGINE"] != "django_tenants.postgresql_backend":
            write_warning(
                "The database engine for the default database must be set to "
                "'django_tenants.postgresql_backend' to use multi-tenancy features.\n"
                "Please update your portal_config.yml file accordingly."
                "You can use the following command to do so:\n\n"
                "tethys settings --set DATABASES.default.ENGINE django_tenants.postgresql_backend\n\n"
                "For more information, see the documentation at "
                f"{DOCS_BASE_URL}tethys_portal/multi_tenancy.html"
            )
            sys.exit(1)
        else:
            primary_process = [sys.executable, manage_path, args.command, *unknown_args]

    else:
        if args.django_help:
            primary_process = [sys.executable, manage_path, args.command, "--help"]
        else:
            primary_process = [sys.executable, manage_path, args.command, *unknown_args]

    if primary_process:
        run_process(primary_process)
