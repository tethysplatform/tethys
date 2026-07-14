"""
********************************************************************************
* Name: run_commands.py
* Author: Gage Larsen
* Created On: July 2026
* Copyright:
* License: BSD 2-Clause
********************************************************************************
"""

import os
import secrets
import shutil
import subprocess
import sys
import threading
import webbrowser
from hashlib import sha256
from importlib.util import find_spec
from pathlib import Path

import yaml

from tethys_cli.cli_colors import write_error, write_info, write_success
from tethys_cli.cli_helpers import get_manage_path


def add_run_parser(subparsers):
    # Setup run command
    run_parser = subparsers.add_parser(
        "run",
        help="Run a single-file Tethys app without configuring a portal (express mode).",
    )
    run_parser.add_argument(
        "app_file",
        nargs="?",
        default="app.py",
        help='Path to the single-file app to run. Defaults to "app.py" in the current directory.',
    )
    run_parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Port on which to serve the app. Defaults to 8000.",
    )
    run_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host on which to serve the app. Defaults to 127.0.0.1.",
    )
    run_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open the app in a web browser after starting the server.",
    )
    run_parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Do not restart the server when the app file changes.",
    )
    run_parser.add_argument(
        "--clean",
        action="store_true",
        help="Discard the app's saved state (database and generated config) before running.",
    )
    run_parser.set_defaults(func=run_command)


def run_command(args):
    """
    Run a single-file component app with zero configuration (express mode). Generates an
    isolated TETHYS_HOME with a portal config (single-app mode, open portal) and a SQLite
    database for the app, then starts the development server pointed at it.
    """
    # import here so the CLI works without a configured Django settings module
    from tethys_apps.base.express import (
        TETHYS_EXPRESS_APP_ENV,
        find_component_app_class_node,
        get_express_package_name,
    )
    from tethys_apps.utilities import get_tethys_home_dir

    app_file = Path(args.app_file).resolve()
    if not app_file.is_file():
        write_error(f'Cannot find the file "{app_file}".')
        exit(1)

    if find_component_app_class_node(app_file) is None:
        write_error(
            f'No app class found in "{app_file}". A Tethys express app must define a '
            "class that subclasses ComponentBase (from tethys_sdk.components)."
        )
        exit(1)

    if find_spec("reactpy_django") is None:
        write_error(
            'The "tethys run" command requires the "reactpy" and "reactpy_django" packages. '
            'Install them and try again (e.g. "pip install reactpy-django").'
        )
        exit(1)

    package = get_express_package_name(app_file)
    app_file_hash = sha256(str(app_file).encode()).hexdigest()[:8]
    express_home = (
        Path(get_tethys_home_dir()) / "express" / f"{package}_{app_file_hash}"
    )

    if args.clean and express_home.exists():
        shutil.rmtree(express_home)
        write_info(f'Removed saved state for "{app_file.name}".')

    express_home.mkdir(parents=True, exist_ok=True)
    write_portal_config(express_home / "portal_config.yml", package)

    env = os.environ.copy()
    env["TETHYS_HOME"] = str(express_home)
    env[TETHYS_EXPRESS_APP_ENV] = str(app_file)

    manage_path = get_manage_path(args)

    database_path = express_home / "tethys_platform.sqlite"
    if not database_path.exists():
        write_info("Initializing app environment (first run only)...")
    result = subprocess.run(
        [sys.executable, manage_path, "migrate", "--no-input"],
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        # Remove the database so the next run starts from a clean slate
        database_path.unlink(missing_ok=True)
        write_error(
            "Failed to initialize the app environment. See output above for details."
        )
        exit(1)

    url = f"http://{args.host}:{args.port}/"
    write_success(f'Running "{app_file.name}" at {url} (CTRL+C to quit)')

    if not args.no_browser:
        threading.Timer(2, webbrowser.open, args=[url]).start()

    command = [sys.executable, manage_path, "runserver"]
    if args.no_reload:
        command.append("--noreload")
    command.append(f"{args.host}:{args.port}")

    try:
        subprocess.call(command, env=env)
    except KeyboardInterrupt:
        pass


def write_portal_config(config_path, package):
    """
    Write the generated express-mode portal config, preserving the SECRET_KEY across runs
    so sessions survive server restarts.
    """
    existing_secret_key = None
    if config_path.exists():
        existing_config = yaml.safe_load(config_path.read_text()) or {}
        existing_secret_key = (existing_config.get("settings") or {}).get("SECRET_KEY")

    config = {
        "version": 2.0,
        "name": f"{package} (tethys express)",
        "apps": {},
        "settings": {
            "SECRET_KEY": existing_secret_key or secrets.token_urlsafe(48),
            "DEBUG": True,
            "ALLOWED_HOSTS": ["*"],
            "TETHYS_PORTAL_CONFIG": {
                "MULTIPLE_APP_MODE": False,
                "STANDALONE_APP": package,
                "ENABLE_OPEN_PORTAL": True,
            },
        },
    }
    config_path.write_text(yaml.safe_dump(config))
