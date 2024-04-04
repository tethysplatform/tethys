from tethys_cli.cli_colors import write_error, write_success, write_info, write_warning

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
    proxyapps_list_parser.add_argument(
        "-v",
        "--verbose",
        help="List all the attributes of each available proxy app",
        action="store_true",
    )

    proxyapps_list_parser.set_defaults(func=list_proxyapps)

    proxyapps_add_parser = proxyapps_subparsers.add_parser(
        "add",
        help="Add a new proxy app.",
    )
    proxyapps_add_parser.add_argument(
        "name",
        help='The proxy app name (e.g.: "My App").',
    )
    proxyapps_add_parser.add_argument(
        "endpoint",
        help='The proxy app endpoint (e.g.: "https://myproxyapp.com").',
    )
    proxyapps_add_parser.add_argument(
        "description",
        help='The proxy app description (e.g.: "The following proxy app is a proxy app").',
        nargs="?",
        default="",
    )
    proxyapps_add_parser.add_argument(
        "icon",
        help='A URL to a logo image to use for the proxy app icon (e.g.: "https://the-logo-of-myproxy-app.png").',
        nargs="?",
        default="",
    )

    proxyapps_add_parser.add_argument(
        "tags",
        help='The proxy app tags separated by commas (e.g.: "tag1", "tag2", "tag3", "tag with space").',
        nargs="?",
        default="",
    )
    proxyapps_add_parser.add_argument(
        "enabled",
        help="Defines if the proxy app is enabled or not (e.g.: True/False).",
        nargs="?",
        default=True,
    )
    proxyapps_add_parser.add_argument(
        "show_in_apps_library",
        help="Defines if the proxy app is shown in the apps library page or not (e.g.: True/False).",
        nargs="?",
        default=True,
    )
    proxyapps_add_parser.add_argument(
        "back_url",
        help='Defines a custom back url for the proxy app (e.g.: "https://back-url-of-myproxy-app.com").',
        nargs="?",
        default="",
    )
    proxyapps_add_parser.add_argument(
        "open_new_tab",
        help="Defines if the proxy app opens in a new tab (e.g.: True/False).",
        nargs="?",
        default=True,
    )
    proxyapps_add_parser.add_argument(
        "display_external_icon",
        help="Defines if the proxy app should appear with an icon on it to differentiate it from normal apps (e.g.: True/False).",
        nargs="?",
        default=False,
    )
    proxyapps_add_parser.add_argument(
        "order",
        help="An arbitrary integer value that is used for ordering apps on the App Library page (e.g.: 0).",
        nargs="?",
        default=0,
    )

    proxyapps_add_parser.set_defaults(func=add_proxyapp)

    proxyapps_update_parser = proxyapps_subparsers.add_parser(
        "update",
        help="Update a new proxy app. Arguments: name [key_value new_value]",
    )

    proxyapps_update_parser.add_argument(
        "name",
        help="The proxy app name",
    )

    proxyapps_update_parser.add_argument(
        "-s",
        "--set",
        dest="set_kwargs",
        help="Key Value pairs to update proxyapps settings: <key> <value>"
        "Available keys for update: [name] [endpoint] [description] [icon] [tags] [enabled] [show_in_apps_library] [back_url] [open_new_tab] [display_external_icon] [app_order]",
        nargs=2,
        action="append",
    )

    proxyapps_update_parser.set_defaults(func=update_proxyapp)


def list_proxyapps(args):
    setup_django()
    from tethys_apps.models import ProxyApp

    proxy_apps = ProxyApp.objects.all()

    write_info("Proxy Apps:")
    for proxy_app in proxy_apps:
        if args.verbose:
            print(
                f"  {proxy_app.name}:\n"
                f"    endpoint: {proxy_app.endpoint}\n"
                f"    description: {proxy_app.description}\n"
                f"    icon: {proxy_app.icon}\n"
                f"    tags: {proxy_app.tags}\n"
                f"    enabled: {proxy_app.enabled}\n"
                f"    show_in_apps_library: {proxy_app.show_in_apps_library}\n"
                f"    back_url: {proxy_app.back_url}\n"
                f"    open_in_new_tab: {proxy_app.open_in_new_tab}\n"
                f"    display_external_icon: {proxy_app.display_external_icon}\n"
                f"    order: {proxy_app.order}"
            )
        else:
            print(f"  {proxy_app.name}: {proxy_app.endpoint}")


def update_proxyapp(args):
    setup_django()
    from tethys_apps.models import ProxyApp

    app_name = args.name
    for key, value in args.set_kwargs:
        app_key = key
        app_value = value

        try:
            proxy_app = ProxyApp.objects.get(name=app_name)
            if not hasattr(proxy_app, app_key):
                write_warning(f"Attribute {app_key} does not exist")
                continue

            setattr(proxy_app, app_key, app_value)
            proxy_app.save()

            write_info(f"Attribute {app_key} was updated successfully with {app_value}")

        except ProxyApp.DoesNotExist:
            write_error(f"Proxy app named '{app_name}' does not exist")
            exit(1)

    write_success(f"Proxy app '{app_name}' was updated successfully")
    exit(0)


def add_proxyapp(args):
    """
    Add Proxy app
    """
    setup_django()

    from tethys_apps.models import ProxyApp

    app_name = args.name
    app_endpoint = args.endpoint
    app_description = args.description
    app_icon = args.icon
    app_tags = args.tags
    app_enabled = args.enabled
    app_show_in_app_library = args.show_in_apps_library
    app_back_url = args.back_url
    app_open_new_tab = args.open_new_tab
    app_display_external_icon = args.display_external_icon
    app_order = args.order
    try:
        proxy_app = ProxyApp.objects.get(name=app_name)
        write_error(f"There is already a proxy app with that name: {app_name}")
        exit(1)

    except ProxyApp.DoesNotExist:
        try:
            proxy_app = ProxyApp(
                name=app_name,
                endpoint=app_endpoint,
                icon=app_icon,
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
            write_error(
                f'Not possible to add the proxy app "{app_name}" because one or more values of the wrong type were provided. Run "tethys proxyapp add --help" to see examples for each argument.'
            )
            exit(1)
