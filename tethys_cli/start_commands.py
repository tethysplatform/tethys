import os
import webbrowser
from argparse import Namespace
from tethys_apps.utilities import (
    get_installed_tethys_items,
    get_tethys_home_dir,
    relative_to_tethys_home,
)
from tethys_cli.cli_helpers import get_manage_path, run_process, setup_django
from tethys_cli.db_commands import configure_tethys_db, process_args
from tethys_cli.gen_commands import (
    get_destination_path,
    generate_command,
    generate_secret_key,
    GEN_PORTAL_OPTION,
)
from tethys_cli.scaffold_commands import scaffold_command, APP_PREFIX
from tethys_cli.install_commands import install_command
from tethys_cli.settings_commands import settings_command


def add_start_parser(subparsers):
    # Setup list command
    start_parser = subparsers.add_parser(
        "start",
        help="Start the tethys server. "
        "If being done for the first time, this will also generate a portal config file, "
        "configure the database, and prompt to scaffold an app as well.",
    )
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
        primary_process = ["python", manage_path, "runserver", args.port]
    else:
        primary_process = ["python", manage_path, "runserver"]

    run_process(primary_process)


def quickstart_command(args):
    """
    "Start the tethys server. If being done for the first time, this will also generate a portal config file, configure the database, and prompt to scaffold an app as well."
    """
    portal_config_args = Namespace(
        type=GEN_PORTAL_OPTION,
        directory=None,
        overwrite=False,
        tethys_portal_settings={},
    )
    portal_config_path = get_destination_path(portal_config_args, check_existence=False)
    if not os.path.exists(portal_config_path):
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
    if not os.path.exists(db_config_options["db_name"]):
        configure_tethys_db(**db_config_options)

    setup_django()
    installed_apps = get_installed_tethys_items(apps=True)
    if not installed_apps:
        # Automatically scaffolds and installs an app
        app_scaffold_args = Namespace(
            name="hello_world",
            extension=False,
            template="default",
            use_defaults=True,
            overwrite=False,
            prefix=f"{get_tethys_home_dir()}/apps",
        )
        scaffold_command(app_scaffold_args)
        os.chdir(relative_to_tethys_home(f"apps/{APP_PREFIX}-hello_world", as_str=True))
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
        )
        install_command(app_install_args, do_exit=False)

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
