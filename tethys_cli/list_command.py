from tethys_apps.utilities import get_installed_tethys_items, SingletonHarvester
from tethys_cli.cli_helpers import setup_django
from tethys_cli.cli_colors import write_info, write_msg


def add_list_parser(subparsers):
    # Setup list command
    list_parser = subparsers.add_parser(
        "list", help="List installed apps and extensions."
    )
    list_parser.add_argument(
        "--urls",
        action="store_true",
        help="List URLMaps for apps",
    )
    list_parser.set_defaults(func=list_command, urls=False)


def list_command(args):
    """
    List installed apps.
    """
    setup_django()
    installed_apps = get_installed_tethys_items(apps=True)
    installed_extensions = get_installed_tethys_items(extensions=True)

    if args.urls:
        for app in SingletonHarvester().apps:
            write_info(f"{app.package}")
            for url_map in app.registered_url_maps:
                write_msg(f"{url_map.display('  ')}")
        return

    if installed_apps:
        write_info("Apps:")
        for item, _ in installed_apps.items():
            print(f"  {item}")

    if installed_extensions:
        write_info("Extensions:")
        for item in installed_extensions:
            print(f"  {item}")
