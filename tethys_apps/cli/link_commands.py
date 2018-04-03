def link_command(args):
    """
    Interact with Tethys Services (Spatial/Persistent Stores) to create them and/or link them to existing apps
    """
    from ..utilities import link_service_to_app_setting
    from .cli_colors import pretty_output, FG_RED

    try:
        service = args.service
        setting = args.setting

        service_parts = service.split(':')
        setting_parts = setting.split(':')
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
                    '\nCommand aborted.')
            exit(1)

        success = link_service_to_app_setting(service_type, service_uid, setting_app_package, setting_type, setting_uid)

        if not success:
            exit(1)

        exit(0)

    except Exception as e:
        print e
        with pretty_output(FG_RED) as p:
            p.write('An unexpected error occurred. Please try again.')
        exit(1)
