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
from tethys_cli.cli_colors import write_info, write_error
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


def _run_process(args, msg, err_msg='ERROR!!!'):
    write_info(msg)
    err_code = run_process(args)
    if err_code:
        write_error(err_msg)
        exit(err_code)


def init_db_server(db_dir=None, **kwargs):
    msg = f'Initializing Postgresql database server in "{db_dir}/data"...'
    err_msg = 'Could not initialize the Postgresql database.'
    args = ['initdb', '-U', 'postgres', '-D', f'{db_dir}/data']
    _run_process(args, msg, err_msg)


def start_db_server(db_dir=None, port=None, **kwargs):
    msg = f'Starting Postgresql database server in "{db_dir}/data" on port {port}...'
    err_msg = 'There was an error while starting the Postgresql database.'
    args = ['pg_ctl', '-U', 'postgres', '-D', f'{db_dir}/data', '-l', f'{db_dir}/logfile', 'start', '-o', f'-p {port}']
    _run_process(args, msg, err_msg)


def stop_db_server(db_dir=None, **kwargs):
    msg = 'Stopping Postgresql database server...'
    err_msg = 'There was an error while stopping the Posgresql database.'
    args = ['pg_ctl', '-U', 'postgres', '-D', f'{db_dir}/data', 'stop']
    _run_process(args, msg, err_msg)


def status_db_server(db_dir=None, **kwargs):
    msg = 'Checking status of Postgresql database server...'
    err_msg = ''
    args = ['pg_ctl', 'status', '-D', f'{db_dir}/data']
    _run_process(args, msg, err_msg)


def create_db_user(hostname=None, port=None, username=None, password=None, db_name=None, is_superuser=False, **kwargs):
    msg = f'Creating Tethys database user "{username}"...'

    db_name = db_name or username

    if is_superuser:
        create_user_command = f"CREATE USER {username} WITH CREATEDB NOCREATEROLE SUPERUSER PASSWORD '{password}';"
    else:
        create_user_command = f"CREATE USER {username} WITH NOCREATEDB NOCREATEROLE NOSUPERUSER PASSWORD '{password}';"

    # Check if the user already exists when we create it
    # See: https://stackoverflow.com/questions/8092086/create-postgresql-role-user-if-it-doesnt-exist/13863830
    create_user_command = f"DO " \
                          f"$do$ " \
                          f"BEGIN " \
                          f"  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{username}') THEN " \
                          f"    {create_user_command} " \
                          f"  END IF; " \
                          f"END " \
                          f"$do$;"

    args = ['psql', '-h', hostname, '-U', 'postgres', '-p', f'{port}', '--command', create_user_command]
    _run_process(args, msg)

    args = ['createdb', '-h', hostname, '-U', 'postgres', '-E', 'utf-8', '-T', 'template0', '-p', f'{port}',
            '-O', username, db_name]
    _run_process(args, msg)


def create_tethys_db(hostname=None, port=None, db_name=None, username=None, password=None,
                     superuser_name=None, superuser_password=None, **kwargs):
    # Create superusers first, so that if there are conflicts in the names, the user created will be a superuser
    if superuser_name is not None and superuser_password is not None:
        create_db_user(
            hostname=hostname,
            port=port,
            username=superuser_name,
            password=superuser_password,
            is_superuser=True
        )
    # Create Tethys db user next
    create_db_user(hostname=hostname, port=port, username=username, password=password, db_name=db_name)


def migrate_tethys_db(db_alias=None, **kwargs):
    msg = 'Running migrations for Tethys database...'
    manage_path = get_manage_path(None)
    db_alias = db_alias or 'default'
    args = ['python', manage_path, 'migrate', '--database', db_alias]
    _run_process(args, msg)


def sync_tethys_apps_db(**kwargs):
    write_info('Syncing the Tethys database with installed apps and extensions...')
    load_apps()
    from tethys_apps.harvester import SingletonHarvester
    harvester = SingletonHarvester()
    harvester.harvest()


def create_portal_superuser(portal_superuser_name='admin', portal_superuser_email='', portal_superuser_password='pass',
                            **kwargs):
    write_info(f'Creating Tethys Portal superuser "{portal_superuser_name}"...')
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
    status=status_db_server,
    create=create_tethys_db,
    migrate=migrate_tethys_db,
    createsuperuser=create_portal_superuser,
    configure=configure_tethys_db,
    sync=sync_tethys_apps_db,
)


def db_command(args):
    options = process_args(args)
    DB_COMMANDS[args.command](**options)
