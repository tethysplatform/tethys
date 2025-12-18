import argparse
from django.conf import settings
from pathlib import Path
import shutil

from tethys_cli.cli_colors import (
    write_msg,
    write_info,
    write_warning,
    write_success,
    write_error,
)
from tethys_quotas.utilities import (
    _convert_storage_units,
    can_add_file_to_path,
    get_resource_available,
)

from tethys_apps.base.paths import (
    _get_app_workspace,
    _get_user_workspace,
    _get_app_media,
    _get_user_media,
    get_app_public,
    get_app_resources,
)
from tethys_apps.base.workspace import _get_app_workspace_old, _get_user_workspace_old


def get_path_config(path_type):
    from tethys_cli.cli_helpers import setup_django

    setup_django()

    if settings.USE_OLD_WORKSPACES_API:
        app_workspace_func = _get_app_workspace_old
        user_workspace_func = _get_user_workspace_old
    else:
        app_workspace_func = _get_app_workspace
        user_workspace_func = _get_user_workspace

    path_types = {
        "app_workspace": {
            "function": app_workspace_func,
            "path_name": "App Workspace",
            "quota": True,
        },
        "user_workspace": {
            "function": user_workspace_func,
            "path_name": "User Workspace",
            "quota": True,
        },
        "app_media": {
            "function": _get_app_media,
            "path_name": "App Media",
            "quota": True,
        },
        "user_media": {
            "function": _get_user_media,
            "path_name": "User Media",
            "quota": True,
        },
        "app_public": {
            "function": get_app_public,
            "path_name": "App Public",
            "quota": False,
        },
        "app_resources": {
            "function": get_app_resources,
            "path_name": "App Resources",
            "quota": False,
        },
    }

    return path_types.get(path_type, None)


def add_paths_parser(subparsers):
    # Paths API commands
    paths_parser = subparsers.add_parser(
        "paths",
        help="Get Tethys Paths information and manage Tethys Paths.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    paths_subparsers = paths_parser.add_subparsers(
        title="Paths Commands", dest="paths_command"
    )
    paths_subparsers.required = True

    # Get Path Command
    get_parser = paths_subparsers.add_parser(
        "get",
        help="Get Tethys Paths information.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    get_parser.add_argument(
        "-t",
        "--type",
        required=True,
        choices=[
            "app_workspace",
            "user_workspace",
            "app_media",
            "user_media",
            "app_public",
            "app_resources",
        ],
        help="Type of path to get.",
    )
    get_parser.add_argument("-a", "--app", required=True, help="Tethys app name.")
    get_parser.add_argument(
        "-u", "--user", help="Username (required for user-specific paths)."
    )
    get_parser.set_defaults(func=get_path)

    # Add File to Path Command
    add_parser = paths_subparsers.add_parser(
        "add",
        help="Add files to Tethys Paths.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    add_parser.add_argument(
        "-t",
        "--type",
        required=True,
        choices=[
            "app_workspace",
            "user_workspace",
            "app_media",
            "user_media",
            "app_public",
            "app_resources",
        ],
        help="Type of path to add file to.",
    )
    add_parser.add_argument("-a", "--app", required=True, help="Tethys app name.")
    add_parser.add_argument(
        "-u", "--user", help="Username (required for user-specific paths)."
    )
    add_parser.add_argument(
        "-f", "--file", required=True, help="Path to the file to add."
    )
    add_parser.set_defaults(func=add_file_to_path)


def get_path(args):
    """
    Get Tethys path based on command line arguments.
    """
    if args.type in ["user_workspace", "user_media"] and not args.user:
        write_error(f"The '--user' argument is required for path type '{args.type}'.")
        return

    path_config = get_path_config(args.type)
    if not path_config:
        write_error(f"Invalid path type: '{args.type}'.")
        return

    is_user_path = args.type in ["user_workspace", "user_media"]

    if is_user_path:
        user = get_user(args.user)
        if not user:
            write_warning(f"User '{args.user}' was not found.")

    app = get_tethys_app(args.app)
    if not app:
        write_warning(f"Tethys app '{args.app}' is not installed.")

    if not app or is_user_path and not user:
        return

    if is_user_path:
        path = resolve_path(path_config, app, user)
    else:
        path = resolve_path(path_config, app)

    if not path:
        write_error(f"Could not find {path_config.get('path_name')}.")
        return

    if is_user_path:
        write_info(
            f"{path_config.get('path_name')} for user '{args.user}' and app '{args.app}':"
        )
    else:
        write_info(f"{path_config.get('path_name')} for app '{args.app}':")

    write_msg(str(path))


def add_file_to_path(args):
    """
    Add file to Tethys path based on command line arguments.
    """
    if args.type in ["user_workspace", "user_media"] and not args.user:
        write_error(f"The '--user' argument is required for path type '{args.type}'.")
        return

    path_config = get_path_config(args.type)
    if not path_config:
        write_error(f"Invalid path type: '{args.type}'.")
        return

    is_user_path = args.type in ["user_workspace", "user_media"]

    if is_user_path:
        user = get_user(args.user)
        if not user:
            write_warning(f"User '{args.user}' was not found.")

    app = get_tethys_app(args.app)
    if not app:
        write_warning(f"Tethys app '{args.app}' is not installed.")

    if not app or is_user_path and not user:
        return

    if is_user_path:
        path = resolve_path(path_config, app, user)
    else:
        path = resolve_path(path_config, app)

    if not path:
        write_error(f"Could not find {path_config.get('path_name')}.")
        return

    source_file = Path(args.file)
    if not source_file.is_file():
        write_error(
            f"The specified file '{args.file}' does not exist or is not a file."
        )
        return

    destination_file = path / source_file.name
    if destination_file.exists():
        write_warning(
            f"The file '{source_file.name}' already exists in the intended {path_config.get('path_name')}."
        )
        return

    if is_user_path:
        codename = "user_workspace_quota"
        can_add_file = can_add_file_to_path(user, codename, source_file)
        resource_available = get_resource_available(user, codename)

        if resource_available and resource_available["resource_available"] <= 0:
            write_error(
                f"Cannot add file to {path_config.get('path_name')}. Quota has already been met."
            )
            return

        elif not can_add_file:
            file_size = _convert_storage_units("bytes", source_file.stat().st_size)
            resource_available = _convert_storage_units(
                "GB", resource_available["resource_available"]
            )
            write_error(
                f"Cannot add file to {path_config.get('path_name')}. File size ({file_size}) exceeds available quota ({resource_available})."
            )
            return

        else:
            shutil.copy(source_file, destination_file)
            write_success(
                f"File '{source_file}' has been added to the {path_config.get('path_name')} at '{destination_file}'."
            )
            return

    else:
        codename = "tethysapp_workspace_quota"
        can_add_file = can_add_file_to_path(app, codename, source_file)
        resource_available = get_resource_available(app, codename)
        if resource_available and resource_available["resource_available"] <= 0:
            write_error(
                f"Cannot add file to {path_config.get('path_name')}. Quota has already been met."
            )
            return

        elif not can_add_file:
            file_size = _convert_storage_units("bytes", source_file.stat().st_size)
            resource_available = _convert_storage_units(
                "GB", resource_available["resource_available"]
            )
            write_error(
                f"Cannot add file to {path_config.get('path_name')}. File size ({file_size}) exceeds available quota ({resource_available})."
            )
            return

        else:
            shutil.copy(source_file, destination_file)
            write_success(
                f"File '{source_file}' has been added to the {path_config.get('path_name')} at '{destination_file}'."
            )
            return


def get_tethys_app(app_name):
    """
    Get Tethys app from database.
    """
    import django

    django.setup()
    from tethys_apps.models import TethysApp

    db_app = TethysApp.objects.filter(package=app_name).first()
    return db_app


def get_user(username):
    """
    Get Django user from database.
    """
    import django

    django.setup()
    from django.contrib.auth.models import User

    user = User.objects.filter(username=username).first()
    return user


def resolve_path(path_config, app, user=None):
    """
    Resolve the path using a path config, app, and user.
    """
    func = path_config["function"]
    has_quota = path_config["quota"]

    args = {}
    if has_quota:
        args["bypass_quota"] = True

    if user:
        return Path(func(app, user, **args).path)

    return Path(func(app, **args).path)
