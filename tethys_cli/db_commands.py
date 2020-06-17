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
import shutil

from django.conf import settings
from django.db.utils import IntegrityError

from tethys_cli.cli_helpers import get_manage_path, run_process, load_apps
from tethys_cli.cli_colors import write_info, write_error
from tethys_apps.utilities import get_tethys_home_dir


def add_db_parser(subparsers):
    # DB COMMANDS
    db_parser = subparsers.add_parser('db', help='Tethys Database Server utility commands.')

    # Setup db commands
    db_parser.add_argument('command',
                           help='Performs operations on the Tethys Database.\n'
                                '  * init - Creates a new, locally running PostgreSQL database server.\n'
                                '  * start - Starts the local database server.\n'
                                '  * stop - Stops the local database server.\n'
                                '  * status - Gets the current status of the local database server.\n'
                                '  * create - Creates the Tethys Portal database on the database server configured '
                                'in the `portal-config.yml` (this could be local or remote).\n'
                                '  * migrate - Runs migrations on the Tethys Portal database.\n'
                                '  * createsuperuser - Creates a Tethys Portal superuser account.\n'
                                '  * configure - A shortcut for running: init, start, create, migrate, and '
                                'createsuperuser. Note: if the DIR parameter is not defined in your DATABASES.default '
                                'configuration in portal_config.yml then the init and start commands are skipped.\n'
                                '  * sync - Syncs the Tethys Portal database with installed apps and extensions.\n'
                                '  * purge - Stops database server and removes the database cluster directory.\n',
                           choices=list(DB_COMMANDS.keys()))
    db_parser.add_argument('-d', '--database', dest='db_alias',
                           help="Name of the database options from portal_config.yml to use (e.g. 'default').")
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
    db_parser.add_argument('-y', '--yes', dest='no_confirmation', action='store_true',
                           help='Do not ask for confirmation. Applies only to the configure and the purge commands.')
    db_parser.set_defaults(func=db_command, db_alias='default', username='tethys_default', password='pass',
                           superuser_name='tethys_super', superuser_password='pass',
                           portal_superuser_name='admin', portal_superuser_email='', portal_superuser_password='pass',
                           no_confirmation=False)


def _run_process(args, msg, err_msg='ERROR!!!', exit_on_error=True, **kwargs):
    """Run a process while outputting messages. If error then either exit or return error code.

    Args:
        args: args for process
        msg: Message to output before running process
        err_msg: Message to output if there is an error
        exit_on_error: If True then exit if process returns and error code
        **kwargs: processed key word arguments from commandline

    Returns: error code

    """
    write_info(msg)
    err_code = run_process(args)
    if err_code:
        write_error(err_msg)
        if exit_on_error:
            exit(err_code)

        return err_code


def init_db_server(db_dir=None, **kwargs):
    """Creates a new, local PostgreSQL database server.

    Args:
        db_dir: directory to create the database server cluster in
        **kwargs: processed key word arguments from commandline

    Returns: error code

    """
    msg = f'Initializing Postgresql database server in "{db_dir}/data"...'
    err_msg = 'Could not initialize the Postgresql database.'
    args = ['initdb', '-U', 'postgres', '-D', f'{db_dir}/data']
    return _run_process(args, msg, err_msg, **kwargs)


def start_db_server(db_dir=None, port=None, **kwargs):
    """Starts the local database server.

    Args:
        db_dir: directory of database server cluster
        port: port to start the server on
        **kwargs: processed key word arguments from commandline

    Returns: error code

    """
    msg = f'Starting Postgresql database server in "{db_dir}/data" on port {port}...'
    err_msg = 'There was an error while starting the Postgresql database.'
    args = ['pg_ctl', '-U', 'postgres', '-D', f'{db_dir}/data', '-l', f'{db_dir}/logfile', 'start', '-o', f'-p {port}']
    return _run_process(args, msg, err_msg, **kwargs)


def stop_db_server(db_dir=None, **kwargs):
    """Stops the locally running database server

    Args:
        db_dir: directory of database server cluster
        **kwargs: processed key word arguments from commandline

    Returns: error code

    """
    msg = 'Stopping Postgresql database server...'
    err_msg = 'There was an error while stopping the Posgresql database.'
    args = ['pg_ctl', '-U', 'postgres', '-D', f'{db_dir}/data', 'stop']
    return _run_process(args, msg, err_msg, **kwargs)


def status_db_server(db_dir=None, **kwargs):
    """Gets the status of the locally running database server

    Args:
        db_dir: directory of database server cluster
        **kwargs: processed key word arguments from commandline

    Returns: error code

    """
    msg = 'Checking status of Postgresql database server...'
    err_msg = ''
    args = ['pg_ctl', 'status', '-D', f'{db_dir}/data']
    return _run_process(args, msg, err_msg, **kwargs)


def purge_db_server(**kwargs):
    """Stop Tethys db server (if running) and then remove the db directory.

    Args:
        **kwargs: processed key word arguments from commandline
    """
    kwargs['exit_on_error'] = False
    stop_db_server(**kwargs)
    if kwargs['db_dir']:
        write_error("This action will permanently delete the database. DATA WILL BE LOST!")
        response = 'y' if kwargs['no_confirmation'] else input("Are you sure you want to continue? [y/N]: ")
        if response.lower() in ['y', 'yes']:
            shutil.rmtree(kwargs['db_dir'])


def create_db_user(hostname=None, port=None, username=None, password=None, db_name=None, is_superuser=False, **kwargs):
    """Creates a database user and associated database.

    Args:
        hostname: hostname for the database server
        port: port for the database server
        username: default user account for tethys portal database
        password: password for `username` account
        db_name: name for database to create
        is_superuser: if user should have superuser privileges
        **kwargs: processed key word arguments from commandline

    Returns: error code

    """
    msg = f'Creating Tethys database user "{username}"...'
    err_msg = f'Failed to create Tethys database user for "{username}"'

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
    result_1 = _run_process(args, msg, err_msg, **kwargs)
    args = ['createdb', '-h', hostname, '-U', 'postgres', '-E', 'utf-8', '-T', 'template0', '-p', f'{port}',
            '-O', username, db_name]
    err_msg = f'Failed to create default database for database user "{username}"'
    result_2 = _run_process(args, msg, err_msg, **kwargs)
    return result_1 or result_2


def create_tethys_db(hostname=None, port=None, db_name=None, username=None, password=None,
                     superuser_name=None, superuser_password=None, **kwargs):
    """Create default user and superuser and associated databases for Tethys Portal

    Args:
        hostname: hostname for the database server
        port: port for the database server
        db_name: name for Tethys Portal database
        username: default user account for tethys portal database
        password: password for `username` account
        superuser_name: superuser account name for Tethys Portal database
        superuser_password: password for `superuser_name` account
        **kwargs: processed key word arguments from commandline

    Returns: error code

    """
    result_1 = None
    # Create superusers first, so that if there are conflicts in the names, the user created will be a superuser
    if superuser_name is not None and superuser_password is not None:
        result_1 = create_db_user(
            hostname=hostname,
            port=port,
            username=superuser_name,
            password=superuser_password,
            is_superuser=True,
            **kwargs
        )
    # Create Tethys db user next
    result_2 = create_db_user(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
        db_name=db_name,
        **kwargs
    )
    return result_1 or result_2


def migrate_tethys_db(db_alias=None, **kwargs):
    """Run migrations for the Tethys Portal database

    Args:
        db_alias: name of the database as specified in the `settings.py` file.
        **kwargs: processed key word arguments from commandline

    Returns: error code

    """
    msg = 'Running migrations for Tethys database...'
    manage_path = get_manage_path(None)
    db_alias = db_alias or 'default'
    args = ['python', manage_path, 'migrate', '--database', db_alias]
    return _run_process(args, msg, **kwargs)


def sync_tethys_apps_db(**kwargs):
    """Sync the Tethys database with the installed apps and extensions

    Args:
        **kwargs: processed key word arguments from commandline
    """
    write_info('Syncing the Tethys database with installed apps and extensions...')
    load_apps()
    from tethys_apps.harvester import SingletonHarvester
    harvester = SingletonHarvester()
    harvester.harvest()


def create_portal_superuser(portal_superuser_name='admin', portal_superuser_email='', portal_superuser_password='pass',
                            **kwargs):
    """Create a superuser account for Tethys Portal

    Args:
        portal_superuser_name: username for the Tethys Portal superuser account
        portal_superuser_email: email for the Tethys Portal superuser account
        portal_superuser_password: password for the Tethys Portal superuser
        **kwargs: processed key word arguments from commandline
    """
    write_info(f'Creating Tethys Portal superuser "{portal_superuser_name}"...')
    load_apps()
    from django.contrib.auth.models import User  # noqa: E402
    try:
        User.objects.create_superuser(portal_superuser_name, portal_superuser_email, portal_superuser_password)
    except IntegrityError:
        write_error(f'Tethys Portal Superuser "{portal_superuser_name}" already exists.')


def _prompt_if_error(fn, **kwargs):
    """Call function and then prompt user to continue if an error code is returned.

    Args:
        fn: function to call
        **kwargs: key word arguments to pass to `fn`
    """
    kwargs['exit_on_error'] = False
    err_code = fn(**kwargs)
    if err_code:
        response = 'y' if kwargs['no_confirmation'] else \
            input(f"There was an error with the {fn.__name__} step of the database configuration.\n"
                  f"Do you want to attempt to continue? [Y/n]: ")
        if response.lower() not in ['', 'yes', 'y']:
            exit(err_code)


def configure_tethys_db(**kwargs):
    """Shortcut for the following commands:
        * `init_db_server`
        * `start_db_server`
        * `create_tethys_db`
        * `migrate_tethys_db`
        * `create_portal_superuser`

    Args:
        **kwargs: processed key word arguments from commandline
    """
    if kwargs.get('db_dir') is not None:
        _prompt_if_error(init_db_server, **kwargs)
        _prompt_if_error(start_db_server, **kwargs)
    _prompt_if_error(create_tethys_db, **kwargs)
    migrate_tethys_db(**kwargs)
    create_portal_superuser(**kwargs)


def process_args(args):
    """Process the command line arguments to provide kwargs to command functions.

    Args:
        args: command line argument object

    Returns: dict of kwargs

    """
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
    purge=purge_db_server,
)


def db_command(args):
    options = process_args(args)
    DB_COMMANDS[args.command](**options)
