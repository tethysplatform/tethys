from tethys_apps.utilities import link_service_to_app_setting
from tethys_cli.cli_colors import pretty_output, FG_RED


def add_link_parser(subparsers):
    # LINK COMMANDS
    link_parser = subparsers.add_parser(
        "link", help="Link a Service to a Tethys app Setting."
    )

    # tethys link
    link_parser.add_argument(
        "service",
        help="Service to link to a target app. Of the form "
        '"<service_type(condor|dask|dataset|persistent|spatial|wps)>:<service_id|service_name>" '
        '(i.e. "persistent_connection:super_conn")',
    )
    link_parser.add_argument(
        "setting",
        help="Setting of an app with which to link the specified service."
        'Of the form "<app_namespace>:'
        "<setting_type(ps_database|ps_connection|ds_spatial|ds_dataset|ss_scheduler|wps)>:"
        '<setting_id|setting_name>" (i.e. "epanet:ps_database:epanet_2")',
    )
    link_parser.set_defaults(func=link_command)


def link_command(args):
    """
    Interact with Tethys Services (Spatial/Persistent Stores) to create them and/or link them to existing apps
    """
    try:
        service = args.service
        setting = args.setting

        service_parts = service.split(":")
        setting_parts = setting.split(":")
        service_type = None
        service_uid = None
        setting_app_package = None
        setting_type = None
        setting_uid = None

        try:
            service_type = service_parts[0]
            service_uid = service_parts[1]

            setting_app_package = setting_parts[0]
            setting_type = setting_parts[1]
            setting_uid = setting_parts[2]
        except IndexError:
            with pretty_output(FG_RED) as p:
                p.write(
                    'Incorrect argument format. \nUsage: "tethys link <spatial|persistent>:<service_id|service_name> '
                    '<app_package>:<setting_type (ps_database|ps_connection|ds_spatial)><setting_id|setting_name>"'
                    "\nCommand aborted."
                )
            exit(1)

        success = link_service_to_app_setting(
            service_type, service_uid, setting_app_package, setting_type, setting_uid
        )

        if not success:
            exit(1)

        exit(0)

    except Exception as e:
        with pretty_output(FG_RED) as p:
            p.write(e)
            p.write("An unexpected error occurred. Please try again.")
        exit(1)
