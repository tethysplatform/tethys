from tethys_cli.cli_colors import (
    write_error,
    write_success,
    write_info,
)

from pathlib import Path

from sqlalchemy import create_engine, exc
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from tethys_apps.utilities import (
    get_tethys_home_dir,
)
from .settings_commands import read_settings

TETHYS_HOME = Path(get_tethys_home_dir())


def add_proxyapps_parser(subparsers):
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
        help="Add a new proxy app. Arguments: proxy_app_name endpoint [description] [logo_url] [tags] [enabled] [show_in_apps_library] [back_url] [open_new_tab] [display_external_icon] [app_order]",
        nargs="+",
    )
    proxyapps_parser.add_argument(
        "-u",
        "--update",
        help="Update a new proxy app. Arguments: proxy_app_name property new_value ",
        nargs="+",
    )

    proxyapps_parser.set_defaults(func=proxyapp_command, urls=False)


def list_proxyapps():
    engine = get_engine()
    if engine:
        Session = sessionmaker(bind=engine)
        session = Session()

        Base = automap_base()
        Base.prepare(engine, reflect=True)

        ProxyAppsClass = Base.classes.tethys_apps_proxyapp
        proxy_apps = session.query(ProxyAppsClass).all()

        write_info("Proxy Apps:")
        for proxy_app in proxy_apps:
            print(f"  {proxy_app.name}")

        session.close()


def get_engine():
    engine = None

    tethys_settings = read_settings()
    database_settings = tethys_settings.get("DATABASES", "")

    if database_settings == "":
        write_error(f"No database settings defined in the portal_config.yml file")
        return engine

    database_default_settings = database_settings.get("default", "")

    if database_default_settings == "":
        write_error(f"No default database defined in the portal_config.yml file")
        return engine

    database_engine = database_default_settings.get("ENGINE", "")
    database_name = database_default_settings.get("NAME", "")
    database_host = database_default_settings.get("HOST", "")
    database_password = database_default_settings.get("PASSWORD", "")
    database_port = database_default_settings.get("PORT", "")
    database_user = database_default_settings.get("USER", "")
    try:
        if database_engine == "django.db.backends.postgresql":
            postgres_uri = f"postgresql://{database_user}:{database_password}@{database_host}:{database_port}/{database_name}"
        else:
            postgres_uri = f"sqlite:///{database_name}"
        engine = create_engine(postgres_uri, pool_pre_ping=True)

    except Exception as e:
        write_error(f"Error when connecting to the database")

    return engine


def proxyapp_command(args):
    if args.list:
        list_proxyapps()
    elif args.add:
        add_proxyapp(args.add)
    elif args.update:
        update_proxyapp(args.update)


def update_proxyapp(args):
    app_name = args[0] if len(args) > 0 else None
    app_key = args[1] if len(args) > 1 else None
    app_value = args[2] if len(args) > 2 else None

    if app_name is None:
        write_error(f"proxy_app_name cannot be empty")
        return
    if app_key is None:
        write_error(f"proxy_app_key cannot be empty")
        return
    if app_value is None:
        write_error(f"proxy_app_value cannot be empty")
        return

    engine = get_engine()

    if engine:
        Session = sessionmaker(bind=engine)
        session = Session()

        Base = automap_base()
        Base.prepare(engine, reflect=True)

        ProxyAppsClass = Base.classes.tethys_apps_proxyapp

        proxy_app = (
            session.query(ProxyAppsClass)
            .filter(ProxyAppsClass.name == app_name)
            .first()
        )
        if proxy_app:
            if not hasattr(proxy_app, app_key):
                write_error(
                    f"Attribute {app_key} does not exists in Proxy app {app_name}"
                )
                return
            setattr(proxy_app, app_key, app_value)
            session.commit()
            write_success(f"Proxy app {app_name} was updated")
        else:
            write_error(f"Proxy app {app_name} does not exits")
        session.close()


def add_proxyapp(args):
    """
    Add Proxy app
    """

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
    app_order = args[10] if len(args) > 10 else 0

    if app_name == "":
        write_error(f"proxy_app_name argument cannot be empty")
        return
    if app_endpoint == "":
        write_error(f"proxy_app_endpoint argument cannot be empty")
        return
    engine = get_engine()
    if engine:
        Session = sessionmaker(bind=engine)
        session = Session()

        Base = automap_base()
        Base.prepare(engine, reflect=True)

        ProxyAppsClass = Base.classes.tethys_apps_proxyapp
        try:
            proxy_app = ProxyAppsClass(
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
            session.add(proxy_app)
            session.commit()
            write_success(f"Proxy app {app_name} added")

        except exc.IntegrityError:
            # Handle the IntegrityError here
            write_error(f"There is already a proxy app with that name: {app_name}")
        session.close()
