import argparse
from tethys_cli.cli_colors import write_warning, write_success, write_error
from tethys_apps.base.paths import (
    get_app_workspace, get_user_workspace, get_app_media, 
    get_user_media, get_app_public, get_app_resources
)

PATH_TYPES = {
    "app_workspace": 
    {
        "function": get_app_workspace,
        "path_name": "App Workspace"
    },
    "user_workspace": {
        "function": get_user_workspace,
        "path_name": "User Workspace"
    },
    "app_media": {
        "function": get_app_media,
        "path_name": "App Media"
    },
    "user_media": {
        "function": get_user_media,
        "path_name": "User Media"
    },
    "app_public": {
        "function": get_app_public,
        "path_name": "App Public"
    },
    "app_resources": {
        "function": get_app_resources,
        "path_name": "App Resources"
    },
}

def add_paths_parser(subparsers):
    # Paths API commands
    paths_parser = subparsers.add_parser(
        "paths",
        help="Get Tethys Paths information and manage Tethys Paths.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    paths_subparsers = paths_parser.add_subparsers(
        title="Paths Commands",
        dest="paths_command"
    )
    paths_subparsers.required = True

    # Get Path Command
    get_parser = paths_subparsers.add_parser(
        "get",
        help="Get Tethys Paths information.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    get_parser.add_argument(
        "-t",
        "--type",
        required=True,
        choices=["app_workspace", "user_workspace", "app_media", "user_media", "app_public", "app_resources"],
        help="Type of path to get."
    )
    get_parser.add_argument(
        "-a",
        "--app",
        required=True,
        help="Tethys app name."
    )
    get_parser.add_argument(
        "-u",
        "--user",
        help="Username (required for user-specific paths)."
    )
    get_parser.set_defaults(func=get_path)

    # Add File to Path Command
    add_parser = paths_subparsers.add_parser(
        "add",
        help="Add files to Tethys Paths.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    add_parser.add_argument(
        "-t",
        "--type",
        required=True,
        choices=["app_workspace", "user_workspace", "app_media", "user_media", "app_public", "app_resources"],
        help="Type of path to add file to."
    )
    add_parser.add_argument(
        "-a",
        "--app",
        required=True,
        help="Tethys app name."
    )
    add_parser.add_argument(
        "-u",
        "--user",
        help="Username (required for user-specific paths)."
    )
    add_parser.add_argument(
        "-f",
        "--file",
        required=True,
        help="Path to the file to add."
    )
    add_parser.set_defaults(func=add_file_to_path)

def get_path(args):
    """
    Get Tethys path based on command line arguments.
    """
    if args.type in ["user_workspace", "user_media"] and not args.user:
        write_error(f"The '--user' argument is required for path type '{args.type}'.")
        return
    
    path_dict = PATH_TYPES.get(args.type)
    if not path_dict:
        write_error(f"Invalid path type: {args.type}")
        return

    func = path_dict.get("function")

    is_user_path = args.type in ["user_workspace", "user_media"]

    if is_user_path:
        user = get_user(args.user)
        if not user:
            write_warning(f"User '{args.user}' does not exist.")

    app = get_tethys_app(args.app)
    if not app:
        write_warning(f"Tethys app '{args.app}' is not installed.")

    if not app or is_user_path and not user:
        return

    if is_user_path:
        path = func(app, user)
    else:
        path = func(app)

    if not path:
        write_error(f"Could not find {path_dict.get('path_name')}.")
        return
    
    print(f"{path_dict.get('path_name')} for app '{args.app}':")
    print(path.path)

def add_file_to_path(args):
    """
    Add file to Tethys path based on command line arguments.
    """
    from pathlib import Path
    import shutil

    if args.type in ["user_workspace", "user_media"] and not args.user:
        write_error(f"The '--user' argument is required for path type '{args.type}'.")
        return
    
    path_dict = PATH_TYPES.get(args.type)
    if not path_dict:
        write_error(f"Invalid path type: {args.type}")
        return
    
    func = path_dict.get("function")

    is_user_path = args.type in ["user_workspace", "user_media"]

    if is_user_path:
        user = get_user(args.user)
        if not user:
            write_warning(f"User '{args.user}' does not exist.")

    app = get_tethys_app(args.app)
    if not app:
        write_warning(f"Tethys app '{args.app}' is not installed.")
    
    if not app or is_user_path and not user:
        return

    if is_user_path:
        path = func(app, user)
    else:
        path = func(app)

    if not path:
        write_error(f"Could not find {path_dict.get('path_name')}.")
        return
    
    source_file = Path(args.file)
    if not source_file.is_file():
        write_error(f"The specified file '{args.file}' does not exist or is not a file.")
        return
    
    destination_file = path.path / source_file.name
    if Path(destination_file).exists():
        write_warning(f"The file '{source_file.name}' already exists in the intended {path_dict.get('path_name')}.")
        return

    shutil.copy(source_file, destination_file)
    write_success(f"File '{source_file}' has been added to the {path_dict.get('path_name')} at '{destination_file}'.")

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