from tethys_cli.cli_colors import (
    write_error,
    write_success,
    write_info,
)
from django.db import IntegrityError


def add_proxyapps_parser(subparsers):
    import django

    django.setup()

    # Setup list command
    proxyapps_parser = subparsers.add_parser(
        "proxyapp", help="Add proxy apps and list proxy apps into the Tethys Platform"
    )
    proxyapps_parser.add_argument(
        "-l",
        "--list",
        help="list available proxy apps in the current tethys installation",
        action="store_true",
    )
    proxyapps_parser.add_argument(
        "-a",
        "--add",
        help="Add a new proxy app. Arguments: proxy_app_name endpoint description [logo_url] [tags] [enabled] [show_in_apps_library] [back_url] [open_new_tab] [display_external_icon]",
        nargs="+",
    )
    proxyapps_parser.add_argument(
        "-u",
        "--update",
        help="Update a new proxy app. Arguments: proxy_app_name property new_value ",
        nargs="+",
    )

    proxyapps_parser.set_defaults(func=proxyapp_command, urls=False)


def list_apps():
    from tethys_apps.models import ProxyApp

    # Function to list proxy apps
    proxy_apps = ProxyApp.objects.all()
    write_info("Proxy Apps:")
    for proxy_app in proxy_apps:
        print(f"  {proxy_app.name}")


def proxyapp_command(args):
    if args.list:
        list_apps()
    elif args.add:
        add_proxyapp(args.add)
    elif args.update:
        update_proxyapp(args.update)


def update_proxyapp(args):
    from tethys_apps.models import ProxyApp

    app_name = args[0] if len(args) > 0 else None
    app_key = args[1] if len(args) > 1 else None
    app_value = args[2] if len(args) > 2 else None

    if app_name is None:
        write_error(f"proxy_app_name cannot be empty")
        return
    if app_key is None:
        write_error(f"proxy_app_name cannot be empty")
        return
    if app_value is None:
        write_error(f"proxy_app_name cannot be empty")
        return
    try:
        proxy_app = ProxyApp.objects.get(name=app_name)
        if not hasattr(proxy_app, app_key):
            write_error(f"Attribute {app_key} does not exists in Proxy app {app_name}")
            return
        setattr(proxy_app, app_key, app_value)
        proxy_app.save()
        write_success(f"Proxy app {app_name} was updated")
    except ProxyApp.DoesNotExist:
        write_error(f"Proxy app {app_name} does not exits")


def add_proxyapp(args):
    """
    Add Proxy app
    """

    from tethys_apps.models import ProxyApp

    app_name = args[0] if len(args) > 0 else ""
    app_endpoint = args[1] if len(args) > 1 else ""
    app_description = args[2] if len(args) > 2 else ""
    app_logo_url = args[3] if len(args) > 3 else ""
    app_tags = args[4] if len(args) > 4 else ""
    app_enabled = args[5] if len(args) > 5 else True
    app_show_in_app_library = args[6] if len(args) > 6 else True
    app_back_url = args[7] if len(args) > 7 else ""
    app_open_new_tab = args[8] if len(args) > 8 else True
    app_display_external_icon = args[9] if len(args) > 9 else False

    if app_name == "":
        write_error(f"proxy_app_name cannot be empty")
        return
    if app_endpoint == "":
        write_error(f"proxy_app_endpoint cannot be empty")
        return
    if app_description == "":
        write_error(f"proxy_app_description cannot be empty")
        return
    try:
        proxy_app = ProxyApp.objects.create(
            name=app_name,
            endpoint=app_endpoint,
            logo_url=app_logo_url,
            back_url=app_back_url,
            description=app_description,
            tags=app_tags,
            show_in_apps_library=app_show_in_app_library,
            enabled=app_enabled,
            open_in_new_tab=app_open_new_tab,
            display_external_icon=app_display_external_icon,
        )
        proxy_app.save()

        write_success(f"Proxy app {app_name} added")
    except IntegrityError as e:
        # Handle the IntegrityError here
        write_error(f"there is already a proxy app with that name: {app_name}")
        return
