import unittest
import warnings
from unittest import mock

from django.test.utils import override_settings

from tethys_cli.db_commands import db_command, process_args, create_db_user, _run_process


class TestCommandTests(unittest.TestCase):

    def setUp(self):
        run_process_patcher = mock.patch('tethys_cli.db_commands._run_process')
        self.mock_run_process = run_process_patcher.start()
        self.addCleanup(run_process_patcher.stop)

        self.options = {
            'db_dir': 'foo',
            'db_alias': 'test',
            'hostname': 'localhost',
            'port': '0000',
            'db_name': 'db_name',
            'username': 'foo',
            'password': 'bar',
            'superuser_name': 'Foo',
            'superuser_password': 'Bar',
            'portal_superuser_name': 'PFoo',
            'portal_superuser_email': 'PEmail',
            'portal_superuser_password': 'PBar',
        }

        process_args_patcher = mock.patch('tethys_cli.db_commands.process_args', return_value=self.options)
        self.mock_process_args = process_args_patcher.start()
        self.addCleanup(process_args_patcher.stop)

        # suppress warning about overriding DATABASES setting.
        warnings.simplefilter('ignore', UserWarning)

    def tearDown(self):
        # revert to normal warnings
        warnings.simplefilter("default", UserWarning)

    @mock.patch('tethys_cli.db_commands.write_error')
    @mock.patch('tethys_cli.db_commands.write_info')
    @mock.patch('tethys_cli.db_commands.run_process')
    def tests_db_command__run_process(self, mock_run_process, mock_write_info, mock_write_error):
        mock_args = mock.MagicMock()
        msg = 'test msg'
        err_msg = 'test err msg'

        self.assertRaises(SystemExit, _run_process, mock_args, msg, err_msg)
        mock_run_process.assert_called_with(mock_args)
        mock_write_info.assert_called_with(msg)
        mock_write_error.assert_called_with(err_msg)

    @mock.patch('tethys_cli.db_commands.Path')
    @mock.patch('tethys_cli.db_commands.vars')
    @override_settings(DATABASES={'test': {
                'NAME': 'db_name',
                'HOST': 'localhost',
                'PORT': '0000',
                'DIR': 'foo'
    }})
    def test_db_command_process_args(self, mock_vars, mock_path):
        path = mock.MagicMock()
        mock_path.return_value = path
        path.is_absolute.return_value = False
        mock_args = mock.MagicMock(command='init', db_alias='test')
        mock_vars.return_value = dict(
            username='foo',
            password='bar',
            superuser_name='Foo',
            superuser_password='Bar',
            portal_superuser_name='PFoo',
            portal_superuser_email='PEmail',
            portal_superuser_password='PBar',
        )
        self.mock_run_process.return_value = 0

        options = process_args(mock_args)
        expected = self.options.copy()
        expected.update(db_dir=path/'foo')
        self.assertDictEqual(options, expected)

    @mock.patch('tethys_cli.db_commands.Path')
    @mock.patch('tethys_cli.db_commands.vars')
    @override_settings(DATABASES={'test': {
        'NAME': 'db_name',
        'PORT': '0000',
    }})
    def test_db_command_process_args_with_error(self, mock_vars, mock_path):
        path = mock.MagicMock()
        mock_path.return_value = path
        path.is_absolute.return_value = False
        mock_args = mock.MagicMock()
        mock_args.command = 'init'
        mock_args.db_alias = 'test'
        mock_vars.return_value = dict(
            username='foo',
            password='bar',
            superuser_name='Foo',
            superuser_password='Bar',
            portal_superuser_name='PFoo',
            portal_superuser_email='PEmail',
            portal_superuser_password='PBar',
        )
        self.mock_run_process.return_value = 0
        self.assertRaises(RuntimeError, process_args, mock_args)

    def test_db_command_init(self):
        mock_args = mock.MagicMock()
        mock_args.command = 'init'
        db_command(mock_args)
        self.mock_run_process.assert_called_with(['initdb', '-U', 'postgres', '-D', 'foo/data'],
                                                 'Initializing Postgresql database server in "foo/data"...',
                                                 'Could not initialize the Postgresql database.')

    @mock.patch('tethys_cli.db_commands.create_db_user')
    def test_db_command_create(self, mock_create_db_user):
        mock_args = mock.MagicMock()
        mock_args.command = 'create'
        db_command(mock_args)
        call_args = mock_create_db_user.call_args_list
        self.assertEqual(call_args[0], mock.call(hostname=self.options['hostname'], port=self.options['port'],
                                                 username=self.options['username'], password=self.options['password'],
                                                 db_name=self.options['db_name']))
        mock_create_db_user.assert_called_with(hostname=self.options['hostname'], port=self.options['port'],
                                               username=self.options['superuser_name'],
                                               password=self.options['superuser_password'], is_superuser=True)

    def test_db_command_create_db_user(self):
        create_db_user(**self.options)
        call_args = self.mock_run_process.call_args_list
        command = f"CREATE USER {self.options['username']} WITH NOCREATEDB NOCREATEROLE NOSUPERUSER PASSWORD " \
            f"'{self.options['password']}';"
        self.assertEqual(call_args[0][0][0], ['psql', '-h', self.options['hostname'], '-U', 'postgres', '-p', '0000',
                                              '--command', command])
        args = ['createdb', '-h', self.options['hostname'], '-U', 'postgres', '-p', self.options['port'], '-O',
                self.options['username'], self.options['db_name'], '-E', 'utf-8', '-T', 'template0']
        self.mock_run_process.assert_called_with(args, 'Creating Tethys database user "foo"...')

    def test_db_command_create_db_user_with_superuser(self):
        create_db_user(is_superuser=True, **self.options)
        call_args = self.mock_run_process.call_args_list
        command = f"CREATE USER {self.options['username']} WITH CREATEDB NOCREATEROLE SUPERUSER PASSWORD " \
            f"'{self.options['password']}';"
        self.assertEqual(call_args[0][0][0], ['psql', '-h', self.options['hostname'], '-U', 'postgres', '-p', '0000',
                                              '--command', command])

    def test_db_command_start(self):
        mock_args = mock.MagicMock()
        mock_args.command = 'start'
        db_command(mock_args)
        self.mock_run_process.assert_called_with(['pg_ctl', '-U', 'postgres', '-D', 'foo/data', '-l',
                                                  'foo/logfile', 'start', '-o', '-p 0000'],
                                                 'Starting Postgresql database server in "foo/data" on port 0000...',
                                                 'There was an error while starting the Postgresql database.')

    def test_db_command_stop(self):
        mock_args = mock.MagicMock()
        mock_args.command = 'stop'
        db_command(mock_args)
        self.mock_run_process.assert_called_with(['pg_ctl', '-U', 'postgres', '-D', 'foo/data', 'stop'],
                                                 'Stopping Postgresql database server...',
                                                 'There was an error while stopping the Posgresql database.')

    def test_db_command_status(self):
        mock_args = mock.MagicMock()
        mock_args.command = 'status'
        db_command(mock_args)
        self.mock_run_process.assert_called_with(['pg_ctl', 'status', '-D', 'foo/data'],
                                                 'Checking status of Postgresql database server...',
                                                 '')

    @mock.patch('tethys_cli.db_commands.get_manage_path', return_value='foo/manage.py')
    def test_db_command_migrate(self, mock_get_manage_path):
        mock_args = mock.MagicMock()
        mock_args.command = 'migrate'
        db_command(mock_args)
        mock_get_manage_path.assert_called()
        self.mock_run_process.assert_called_with(['python', 'foo/manage.py', 'migrate', '--database', 'test'],
                                                 'Running migrations for Tethys database...')

    @mock.patch('tethys_cli.db_commands.write_info')
    @mock.patch('django.contrib.auth.models.User.objects.create_superuser')
    @mock.patch('tethys_cli.db_commands.load_apps')
    def test_db_command_createsuperuser(self, mock_load_apps, mock_create_superuser, _):
        mock_args = mock.MagicMock()
        mock_args.command = 'createsuperuser'
        db_command(mock_args)
        mock_load_apps.assert_called()
        mock_create_superuser.assert_called_with('PFoo', 'PEmail', 'PBar')

    @mock.patch('tethys_cli.db_commands.create_portal_superuser')
    @mock.patch('tethys_cli.db_commands.migrate_tethys_db')
    @mock.patch('tethys_cli.db_commands.create_tethys_db')
    @mock.patch('tethys_cli.db_commands.start_db_server')
    @mock.patch('tethys_cli.db_commands.init_db_server')
    def test_db_command_configure(self, mock_init, mock_start, mock_create, mock_migrate, mock_createsuperuser):
        mock_args = mock.MagicMock()
        mock_args.command = 'configure'
        db_command(mock_args)
        mock_init.assert_called_with(**self.options)
        mock_start.assert_called_with(**self.options)
        mock_create.assert_called_with(**self.options)
        mock_migrate.assert_called_with(**self.options)
        mock_createsuperuser.assert_called_with(**self.options)

    @mock.patch('tethys_cli.db_commands.write_info')
    @mock.patch('tethys_apps.harvester.SingletonHarvester')
    def test_db_command_sync(self, MockSingletonHarvester, _):
        # mock the input args
        args = mock.MagicMock(manage='', command='sync', port='8080')

        # call the testing method with the mock args
        db_command(args)

        # mock the singleton harvester
        MockSingletonHarvester.assert_called()
        MockSingletonHarvester().harvest.assert_called()
