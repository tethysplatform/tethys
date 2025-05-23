from os import chdir
from pathlib import Path
import sys
import webbrowser
from argparse import Namespace
from tethys_apps.utilities import get_installed_tethys_items
from tethys_cli.cli_helpers import get_manage_path, run_process, setup_django
from tethys_cli.db_commands import configure_tethys_db, process_args
from tethys_cli.gen_commands import (
    get_destination_path,
    generate_command,
    GEN_PORTAL_OPTION,
)
from tethys_cli.scaffold_commands import scaffold_command, APP_PREFIX
from tethys_cli.install_commands import install_command
from tethys_cli.settings_commands import settings_command
from tethys_cli.cli_colors import write_warning


def add_start_parser(subparsers):
    # Setup list command
    start_parser = subparsers.add_parser("start", help="Start the tethys server.")
    start_parser.add_argument(
        "-p",
        "--port",
        type=str,
        help="Host and/or port on which to bind the development server.",
    )
    start_parser.set_defaults(func=start_command)


def add_quickstart_parser(subparsers):
    # Setup list command
    quickstart_parser = subparsers.add_parser(
        "quickstart",
        help="Start the tethys server for the first time after install, "
        "which will generate a portal config file, configure the database, "
        "and scaffold a hello_world app as well.",
    )

    quickstart_parser.set_defaults(func=quickstart_command)


def start_command(args):
    manage_path = get_manage_path(args)
    if args.port:
        primary_process = [sys.executable, manage_path, "runserver", args.port]
    else:
        primary_process = [sys.executable, manage_path, "runserver"]

    run_process(primary_process)


def quickstart_command(args):
    """
    This command installs tethys, generates a portal config file, configures the database,
    scaffolds and installs a Hello World app and starts up the server.
    """
    portal_config_args = Namespace(
        type=GEN_PORTAL_OPTION,
        directory=None,
        overwrite=False,
        tethys_portal_settings={},
    )
    portal_config_path = get_destination_path(portal_config_args, check_existence=False)
    if Path(portal_config_path).exists():
        write_warning(
            'An existing portal configuration was already found. Please use "tethys start" instead to start your server.'
        )
        exit(1)

    generate_command(portal_config_args)

    db_config_args = Namespace(
        command="configure",
        db_alias="default",
        username="tethys_default",
        password="pass",
        superuser_name="tethys_super",
        superuser_password="pass",
        portal_superuser_name="admin",
        portal_superuser_email="",
        portal_superuser_password="pass",
        no_confirmation=False,
    )
    db_config_options = process_args(db_config_args)
    if not Path(db_config_options["db_name"]).exists():
        configure_tethys_db(**db_config_options)

    setup_django()
    installed_apps = get_installed_tethys_items(apps=True)
    if not installed_apps:
        # Automatically scaffolds and installs an app
        app_scaffold_args = Namespace(
            name="hello_world",
            extension=False,
            template="default",
            prefix=str(Path.cwd()),
            use_defaults=True,
            overwrite=False,
        )
        scaffold_command(app_scaffold_args)
        chdir(f"{APP_PREFIX}-hello_world")
        app_install_args = Namespace(
            develop=True,
            file=None,
            without_dependencies=False,
            only_dependencies=False,
            verbose=False,
            no_db_sync=False,
            force_services=False,
            services_file=None,
            quiet=True,
            no_sync_stores=False,
            update_installed=False,
        )
        install_command(app_install_args)

        update_settings_args = Namespace(
            set_kwargs=[
                (
                    "TETHYS_PORTAL_CONFIG",
                    """
                    MULTIPLE_APP_MODE: False
                    STANDALONE_APP: hello_world
                """,
                )
            ]
        )
        settings_command(update_settings_args)

    webbrowser.open("http://127.0.0.1:8000/")
    start_args = Namespace(port=None)
    start_command(start_args)
