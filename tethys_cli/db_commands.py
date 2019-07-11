"""
********************************************************************************
* Name: db_commands.py
* Author: Scott Christensen
* Created On: 2019
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from pathlib import Path

from django.conf import settings

from tethys_cli.cli_helpers import get_manage_path, run_process, load_apps
from tethys_apps.utilities import get_tethys_home_dir


def add_db_parser(subparsers):
    # DB COMMANDS
    db_parser = subparsers.add_parser('db', help='Tethys Database Server utility commands.')

    # Setup db commands
    db_parser.add_argument('command',
                           help='DB command to run.',
                           choices=list(DB_COMMANDS.keys()))
    db_parser.add_argument('-d', '--database', dest='db_alias',
                           help="Name of the database options from settings.py to use (e.g. 'default').")
    db_parser.add_argument('-n', '--username', dest='username',
                           help="Name of database user to add to database when creating.")
    db_parser.add_argument('-p', '--password', dest='password',
                           help="Password for the database user.")
    db_parser.add_argument('-N', '--superuser-name', dest='superuser_name',
                           help="Name of database super user to add to database when creating.")
    db_parser.add_argument('-P', '--superuser-password', dest='superuser_password',
                           help="Password for the database super user.")
    db_parser.add_argument('--portal-superuser-name', '--pn', dest='portal_superuser_name',
                           help="Name for the Tethys portal super user.")
    db_parser.add_argument('--portal-superuser-email', '--email', '--pe', dest='portal_superuser_email',
                           help="Email of the Tethys portal super user.")
    db_parser.add_argument('--portal-superuser-password', '--pp', dest='portal_superuser_password',
                           help="Password for the Tethys portal super user.")
    db_parser.set_defaults(func=db_command, db_alias='default', username='tethys_default', password='pass',
                           superuser_name='tethys_super', superuser_password='pass',
                           portal_superuser_name='admin', portal_superuser_email='', portal_superuser_password='pass')


def init_db_server(db_dir=None, **kwargs):
    args = ['initdb', '-U', 'postgres', '-D', f'{db_dir}/data']
    run_process(args)


def start_db_server(db_dir=None, port=None, **kwargs):
    args = ['pg_ctl', '-U', 'postgres', '-D', f'{db_dir}/data', '-l', f'{db_dir}/logfile', 'start', '-o', f'-p {port}']
    run_process(args)


def stop_db_server(db_dir=None, **kwargs):
    args = ['pg_ctl', '-U', 'postgres', '-D', f'{db_dir}/data', 'stop']
    run_process(args)


def create_db_user(hostname=None, port=None, username=None, password=None, db_name=None, is_superuser=False, **kwargs):
    db_name = db_name or username

    if is_superuser:
        command = f"CREATE USER {username} WITH CREATEDB NOCREATEROLE SUPERUSER PASSWORD '{password}';"
    else:
        command = f"CREATE USER {username} WITH NOCREATEDB NOCREATEROLE NOSUPERUSER PASSWORD '{password}';"

    args = ['psql', '-h', hostname, '-U', 'postgres', '-p', f'{port}', '--command', command]
    run_process(args)
    if not is_superuser:
        args = ['createdb', '-h', hostname, '-U', 'postgres', '-p', f'{port}', '-O', username, db_name, '-E', 'utf-8',
                '-T', 'template0']
        run_process(args)


def create_tethys_db(hostname=None, port=None, db_name=None, username=None, password=None,
                     superuser_name=None, superuser_password=None, **kwargs):
    create_db_user(hostname=hostname, port=port, username=username, password=password, db_name=db_name)
    if superuser_name is not None and superuser_password is not None:
        create_db_user(hostname=hostname, port=port,
                       username=superuser_name, password=superuser_password,
                       is_superuser=True)


def migrate_tethys_db(db_alias=None, **kwargs):
    manage_path = get_manage_path(None)
    db_alias = db_alias or 'default'
    args = ['python', manage_path, 'migrate', '--database', db_alias]
    run_process(args)


def sync_tethys_apps_db(**kwargs):
    load_apps()
    from tethys_apps.harvester import SingletonHarvester
    harvester = SingletonHarvester()
    harvester.harvest()


def create_portal_superuser(portal_superuser_name='admin', portal_superuser_email='', portal_superuser_password='pass',
                            **kwargs):
    load_apps()
    from django.contrib.auth.models import User  # noqa: E402
    User.objects.create_superuser(portal_superuser_name, portal_superuser_email, portal_superuser_password)


def configure_tethys_db(**kwargs):
    if kwargs.get('db_dir') is not None:
        init_db_server(**kwargs)
        start_db_server(**kwargs)
    create_tethys_db(**kwargs)
    migrate_tethys_db(**kwargs)
    create_portal_superuser(**kwargs)


def process_args(args):
    db_settings = settings.DATABASES[args.db_alias]
    db_dir = db_settings.get('DIR')
    if db_dir is None:
        if args.command in ['init', 'start', 'stop']:
            raise RuntimeError(f'The tethys db {args.command} command can only be used with local databases.')
    else:
        if not Path(db_dir).is_absolute():
            db_dir = Path(get_tethys_home_dir()) / db_dir

    options = vars(args)
    options.update(
        db_alias=args.db_alias,
        db_dir=db_dir,
        hostname=db_settings.get('HOST'),
        port=db_settings.get('PORT'),
        db_name=db_settings.get('NAME'),
    )

    return options


DB_COMMANDS = dict(
    init=init_db_server,
    start=start_db_server,
    stop=stop_db_server,
    create=create_tethys_db,
    migrate=migrate_tethys_db,
    createsuperuser=create_portal_superuser,
    configure=configure_tethys_db,
    sync=sync_tethys_apps_db,
)


def db_command(args):
    options = process_args(args)
    DB_COMMANDS[args.command](**options)
