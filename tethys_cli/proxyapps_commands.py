from tethys_cli.cli_colors import (
    write_error,
    write_success,
    write_info,
)

from tethys_cli.cli_helpers import setup_django

from django.db import IntegrityError


def add_proxyapps_parser(subparsers):
    # Setup list command
    proxyapps_parser = subparsers.add_parser(
        "proxyapp", help="Add proxy apps and list proxy apps into the Tethys Platform"
    )
    proxyapps_subparsers = proxyapps_parser.add_subparsers(title="Options")

    proxyapps_list_parser = proxyapps_subparsers.add_parser(
        "list", help="list available proxy apps in the current tethys installation"
    )
    proxyapps_list_parser.set_defaults(func=list_proxyapps)

    proxyapps_add_parser = proxyapps_subparsers.add_parser(
        "add",
        help="Add a new proxy app. Arguments: proxy_app_name endpoint [description] [logo_url] [tags] [enabled] [show_in_apps_library] [back_url] [open_new_tab] [display_external_icon] [app_order]",
    )
    proxyapps_add_parser.add_argument(
        "proxy_app_name",
        help="The proxy app name",
    )
    proxyapps_add_parser.add_argument(
        "proxy_app_endpoint",
        help="The proxy app endpoint",
    )
    proxyapps_add_parser.add_argument(
        "proxy_app_description", help="The proxy app description", nargs="?", default=""
    )
    proxyapps_add_parser.add_argument(
        "proxy_app_logo_url", help="The proxy app logo url", nargs="?", default=""
    )

    proxyapps_add_parser.add_argument(
        "proxy_app_tags", help="The proxy app tags", nargs="?", default=""
    )
    proxyapps_add_parser.add_argument(
        "proxy_app_enabled",
        help="Defines if the proxy app is enabled or not",
        nargs="?",
        default=True,
    )
    proxyapps_add_parser.add_argument(
        "proxy_app_show_in_apps_library",
        help="Defines if the proxy app is enabled or not",
        nargs="?",
        default=True,
    )
    proxyapps_add_parser.add_argument(
        "proxy_app_back_url",
        help="Defines a custom back url for the proxy app",
        nargs="?",
        default="",
    )
    proxyapps_add_parser.add_argument(
        "proxy_app_open_new_tab",
        help="Defines if the proxy app opens in a new tab",
        nargs="?",
        default=True,
    )
    proxyapps_add_parser.add_argument(
        "proxy_app_display_external_icon",
        help="Defines if the proxy app opens in a new tab",
        nargs="?",
        default=False,
    )
    proxyapps_add_parser.add_argument(
        "proxy_app_order",
        help="Defines if the proxy app opens in a new tab",
        nargs="?",
        default=0,
    )

    proxyapps_add_parser.set_defaults(func=add_proxyapp)

    proxyapps_update_parser = proxyapps_subparsers.add_parser(
        "update",
        help="Update a new proxy app. Arguments: proxy_app_name key_value new_value",
    )
    proxyapps_update_parser.add_argument(
        "proxy_app_name",
        help="The proxy app name",
    )
    proxyapps_update_parser.add_argument(
        "proxy_app_key",
        help="The proxy app key that needs to be changed: [name] [endpoint] [description] [logo_url] [tags] [enabled] [show_in_apps_library] [back_url] [open_new_tab] [display_external_icon] [app_order] ",
    )
    proxyapps_update_parser.add_argument(
        "proxy_app_key_value",
        help="Th new value for the proxy app's key",
    )

    proxyapps_update_parser.set_defaults(func=update_proxyapp)


def list_proxyapps(args):
    setup_django()
    from tethys_apps.models import ProxyApp

    proxy_apps = ProxyApp.objects.all()

    write_info("Proxy Apps:")
    for proxy_app in proxy_apps:
        print(f"  {proxy_app.name}")


def update_proxyapp(args):
    setup_django()
    from tethys_apps.models import ProxyApp

    app_name = args.proxy_app_name
    app_key = args.proxy_app_key
    app_value = args.proxy_app_key_value

    try:
        proxy_app = ProxyApp.objects.get(name=app_name)
        # breakpoint()
        if not hasattr(proxy_app, app_key):
            write_error(f"Attribute {app_key} does not exists in Proxy app {app_name}")
            exit(1)

        setattr(proxy_app, app_key, app_value)
        proxy_app.save()
        write_success(f"Proxy app {app_name} was updated")
        exit(0)

    except ProxyApp.DoesNotExist:
        write_error(f"Proxy app {app_name} does not exits")
        exit(1)


def add_proxyapp(args):
    """
    Add Proxy app
    """
    setup_django()

    from tethys_apps.models import ProxyApp

    app_name = args.proxy_app_name
    app_endpoint = args.proxy_app_endpoint
    app_description = args.proxy_app_description
    app_logo_url = args.proxy_app_logo_url
    app_tags = args.proxy_app_tags
    app_enabled = args.proxy_app_enabled
    app_show_in_app_library = args.proxy_app_show_in_apps_library
    app_back_url = args.proxy_app_back_url
    app_open_new_tab = args.proxy_app_open_new_tab
    app_display_external_icon = args.proxy_app_display_external_icon
    app_order = args.proxy_app_order
    try:
        proxy_app = ProxyApp.objects.get(name=app_name)
        write_error(f"There is already a proxy app with that name: {app_name}")
        exit(1)

    except ProxyApp.DoesNotExist:
        try:
            proxy_app = ProxyApp(
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
                order=app_order,
            )

            proxy_app.save()
            write_success(f"Proxy app {app_name} added")
            exit(0)
        except IntegrityError:
            write_error(f"Not possible to add the proxy app: {app_name}")
            exit(1)
