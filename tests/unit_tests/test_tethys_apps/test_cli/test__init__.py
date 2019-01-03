import sys
import unittest
import mock
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from tethys_apps.cli import tethys_command


class TethysCommandTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def assert_returns_help(self, stdout):
        self.assertIn('usage: tethys', stdout)
        self.assertIn('scaffold', stdout)
        self.assertIn('gen', stdout)
        self.assertIn('manage', stdout)
        self.assertIn('schedulers', stdout)
        self.assertIn('services', stdout)
        self.assertIn('app_settings', stdout)
        self.assertIn('link', stdout)
        self.assertIn('test', stdout)
        self.assertIn('uninstall', stdout)
        self.assertIn('list', stdout)
        self.assertIn('syncstores', stdout)
        self.assertIn('docker', stdout)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('sys.stderr', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    def test_tethys_with_no_subcommand(self, mock_exit, mock_stderr, mock_stdout):
            mock_exit.side_effect = SystemExit
            testargs = ['tethys']

            with mock.patch.object(sys, 'argv', testargs):
                self.assertRaises(SystemExit, tethys_command)

            if mock_stdout.getvalue():
                # Python 3
                self.assert_returns_help(mock_stdout.getvalue())
            else:
                # Python 2
                self.assert_returns_help(mock_stderr.getvalue())

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    def test_tethys_help(self, mock_exit, mock_stdout):
        mock_exit.side_effect = SystemExit
        testargs = ['tethys', '-h']

        with mock.patch.object(sys, 'argv', testargs):
            self.assertRaises(SystemExit, tethys_command)

        mock_exit.assert_called_with(0)
        self.assert_returns_help(mock_stdout.getvalue())

    @mock.patch('tethys_apps.cli.scaffold_command')
    def test_scaffold_subcommand(self, mock_scaffold_command):
        testargs = ['tethys', 'scaffold', 'foo']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_scaffold_command.assert_called()
        call_args = mock_scaffold_command.call_args_list
        self.assertEqual('foo', call_args[0][0][0].name)
        self.assertEqual('default', call_args[0][0][0].template)
        self.assertFalse(call_args[0][0][0].overwrite)
        self.assertFalse(call_args[0][0][0].extension)
        self.assertFalse(call_args[0][0][0].use_defaults)

    @mock.patch('tethys_apps.cli.scaffold_command')
    def test_scaffold_subcommand_with_options(self, mock_scaffold_command):
        testargs = ['tethys', 'scaffold', 'foo', '-e', '-t', 'my_template', '-o', '-d']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_scaffold_command.assert_called()
        call_args = mock_scaffold_command.call_args_list
        self.assertEqual('foo', call_args[0][0][0].name)
        self.assertEqual('my_template', call_args[0][0][0].template)
        self.assertTrue(call_args[0][0][0].overwrite)
        self.assertTrue(call_args[0][0][0].extension)
        self.assertTrue(call_args[0][0][0].use_defaults)

    @mock.patch('tethys_apps.cli.scaffold_command')
    def test_scaffold_subcommand_with_verbose_options(self, mock_scaffold_command):
        testargs = ['tethys', 'scaffold', 'foo', '--extension', '--template', 'my_template', '--overwrite',
                    '--defaults']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_scaffold_command.assert_called()
        call_args = mock_scaffold_command.call_args_list
        self.assertEqual('foo', call_args[0][0][0].name)
        self.assertEqual('my_template', call_args[0][0][0].template)
        self.assertTrue(call_args[0][0][0].overwrite)
        self.assertTrue(call_args[0][0][0].extension)
        self.assertTrue(call_args[0][0][0].use_defaults)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    @mock.patch('tethys_apps.cli.scaffold_command')
    def test_scaffold_subcommand_help(self, mock_scaffold_command, mock_exit, mock_stdout):
        mock_exit.side_effect = SystemExit
        testargs = ['tethys', 'scaffold', '-h']

        with mock.patch.object(sys, 'argv', testargs):
            self.assertRaises(SystemExit, tethys_command)

        mock_scaffold_command.assert_not_called()
        mock_exit.assert_called_with(0)

        self.assertIn('--help', mock_stdout.getvalue())
        self.assertIn('--template', mock_stdout.getvalue())
        self.assertIn('--extension', mock_stdout.getvalue())
        self.assertIn('--defaults', mock_stdout.getvalue())
        self.assertIn('--overwrite', mock_stdout.getvalue())

    @mock.patch('tethys_apps.cli.generate_command')
    def test_generate_subcommand_settings_defaults(self, mock_gen_command):
        testargs = ['tethys', 'gen', 'settings']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_gen_command.assert_called()
        call_args = mock_gen_command.call_args_list
        self.assertEqual(None, call_args[0][0][0].allowed_host)
        self.assertEqual(None, call_args[0][0][0].allowed_hosts)
        self.assertEqual('75M', call_args[0][0][0].client_max_body_size)
        self.assertEqual('pass', call_args[0][0][0].db_password)
        self.assertEqual(5436, call_args[0][0][0].db_port)
        self.assertEqual('tethys_default', call_args[0][0][0].db_username)
        self.assertEqual(None, call_args[0][0][0].directory)
        self.assertFalse(call_args[0][0][0].overwrite)
        self.assertFalse(call_args[0][0][0].production)
        self.assertEqual('settings', call_args[0][0][0].type)
        self.assertEqual(10, call_args[0][0][0].uwsgi_processes)

    @mock.patch('tethys_apps.cli.generate_command')
    def test_generate_subcommand_settings_directory(self, mock_gen_command):
        testargs = ['tethys', 'gen', 'settings', '--directory', '/tmp/foo/bar']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_gen_command.assert_called()
        call_args = mock_gen_command.call_args_list
        self.assertEqual(None, call_args[0][0][0].allowed_host)
        self.assertEqual(None, call_args[0][0][0].allowed_hosts)
        self.assertEqual('75M', call_args[0][0][0].client_max_body_size)
        self.assertEqual('pass', call_args[0][0][0].db_password)
        self.assertEqual(5436, call_args[0][0][0].db_port)
        self.assertEqual('tethys_default', call_args[0][0][0].db_username)
        self.assertEqual('/tmp/foo/bar', call_args[0][0][0].directory)
        self.assertFalse(call_args[0][0][0].overwrite)
        self.assertFalse(call_args[0][0][0].production)
        self.assertEqual('settings', call_args[0][0][0].type)
        self.assertEqual(10, call_args[0][0][0].uwsgi_processes)

    @mock.patch('tethys_apps.cli.generate_command')
    def test_generate_subcommand_apache_settings_verbose_options(self, mock_gen_command):
        testargs = ['tethys', 'gen', 'apache', '-d', '/tmp/foo/bar', '--allowed-host', '127.0.0.1',
                    '--allowed-hosts', 'localhost', '--client-max-body-size', '123M', '--uwsgi-processes', '9',
                    '--db-username', 'foo_user', '--db-password', 'foo_pass', '--db-port', '5555',
                    '--production', '--overwrite']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_gen_command.assert_called()
        call_args = mock_gen_command.call_args_list
        self.assertEqual('127.0.0.1', call_args[0][0][0].allowed_host)
        self.assertEqual('localhost', call_args[0][0][0].allowed_hosts)
        self.assertEqual('123M', call_args[0][0][0].client_max_body_size)
        self.assertEqual('foo_pass', call_args[0][0][0].db_password)
        self.assertEqual('5555', call_args[0][0][0].db_port)
        self.assertEqual('foo_user', call_args[0][0][0].db_username)
        self.assertEqual('/tmp/foo/bar', call_args[0][0][0].directory)
        self.assertTrue(call_args[0][0][0].overwrite)
        self.assertTrue(call_args[0][0][0].production)
        self.assertEqual('apache', call_args[0][0][0].type)
        self.assertEqual('9', call_args[0][0][0].uwsgi_processes)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    @mock.patch('tethys_apps.cli.generate_command')
    def test_generate_subcommand_help(self, mock_gen_command, mock_exit, mock_stdout):
        mock_exit.side_effect = SystemExit
        testargs = ['tethys', 'gen', '-h']

        with mock.patch.object(sys, 'argv', testargs):
            self.assertRaises(SystemExit, tethys_command)

        mock_gen_command.assert_not_called()
        mock_exit.assert_called_with(0)

        self.assertIn('--help', mock_stdout.getvalue())
        self.assertIn('--directory', mock_stdout.getvalue())
        self.assertIn('--allowed-host', mock_stdout.getvalue())
        self.assertIn('--client-max-body-size', mock_stdout.getvalue())
        self.assertIn('--uwsgi-processes', mock_stdout.getvalue())
        self.assertIn('--db-username', mock_stdout.getvalue())
        self.assertIn('--db-password', mock_stdout.getvalue())
        self.assertIn('--db-port', mock_stdout.getvalue())
        self.assertIn('--production', mock_stdout.getvalue())
        self.assertIn('--overwrite', mock_stdout.getvalue())

    @mock.patch('tethys_apps.cli.manage_command')
    def test_manage_subcommand_start(self, mock_manage_command):
        testargs = ['tethys', 'manage', 'start']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_manage_command.assert_called()
        call_args = mock_manage_command.call_args_list
        self.assertEqual('start', call_args[0][0][0].command)
        self.assertEqual(False, call_args[0][0][0].force)
        self.assertEqual(None, call_args[0][0][0].manage)
        self.assertEqual(False, call_args[0][0][0].noinput)
        self.assertEqual(None, call_args[0][0][0].port)

    @mock.patch('tethys_apps.cli.manage_command')
    def test_manage_subcommand_start_options(self, mock_manage_command):
        testargs = ['tethys', 'manage', 'start', '-m', '/foo/bar/manage.py', '-p', '5555', '-f']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_manage_command.assert_called()
        call_args = mock_manage_command.call_args_list
        self.assertEqual('start', call_args[0][0][0].command)
        self.assertEqual(True, call_args[0][0][0].force)
        self.assertEqual('/foo/bar/manage.py', call_args[0][0][0].manage)
        self.assertEqual(False, call_args[0][0][0].noinput)
        self.assertEqual('5555', call_args[0][0][0].port)

    @mock.patch('tethys_apps.cli.manage_command')
    def test_manage_subcommand_start_verbose_options(self, mock_manage_command):
        testargs = ['tethys', 'manage', 'start', '--manage', '/foo/bar/manage.py', '--port', '5555', '--force',
                    '--noinput']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_manage_command.assert_called()
        call_args = mock_manage_command.call_args_list
        self.assertEqual('start', call_args[0][0][0].command)
        self.assertEqual(True, call_args[0][0][0].force)
        self.assertEqual('/foo/bar/manage.py', call_args[0][0][0].manage)
        self.assertEqual(True, call_args[0][0][0].noinput)
        self.assertEqual('5555', call_args[0][0][0].port)

    @mock.patch('tethys_apps.cli.manage_command')
    def test_manage_subcommand_syncdb(self, mock_manage_command):
        testargs = ['tethys', 'manage', 'syncdb']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_manage_command.assert_called()
        call_args = mock_manage_command.call_args_list
        self.assertEqual('syncdb', call_args[0][0][0].command)
        self.assertEqual(False, call_args[0][0][0].force)
        self.assertEqual(None, call_args[0][0][0].manage)
        self.assertEqual(False, call_args[0][0][0].noinput)
        self.assertEqual(None, call_args[0][0][0].port)

    @mock.patch('tethys_apps.cli.manage_command')
    def test_manage_subcommand_collectstatic(self, mock_manage_command):
        testargs = ['tethys', 'manage', 'collectstatic']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_manage_command.assert_called()
        call_args = mock_manage_command.call_args_list
        self.assertEqual('collectstatic', call_args[0][0][0].command)
        self.assertEqual(False, call_args[0][0][0].force)
        self.assertEqual(None, call_args[0][0][0].manage)
        self.assertEqual(False, call_args[0][0][0].noinput)
        self.assertEqual(None, call_args[0][0][0].port)

    @mock.patch('tethys_apps.cli.manage_command')
    def test_manage_subcommand_collectworkspaces(self, mock_manage_command):
        testargs = ['tethys', 'manage', 'collectworkspaces']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_manage_command.assert_called()
        call_args = mock_manage_command.call_args_list
        self.assertEqual('collectworkspaces', call_args[0][0][0].command)
        self.assertEqual(False, call_args[0][0][0].force)
        self.assertEqual(None, call_args[0][0][0].manage)
        self.assertEqual(False, call_args[0][0][0].noinput)
        self.assertEqual(None, call_args[0][0][0].port)

    @mock.patch('tethys_apps.cli.manage_command')
    def test_manage_subcommand_collectall(self, mock_manage_command):
        testargs = ['tethys', 'manage', 'collectall']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_manage_command.assert_called()
        call_args = mock_manage_command.call_args_list
        self.assertEqual('collectall', call_args[0][0][0].command)
        self.assertEqual(False, call_args[0][0][0].force)
        self.assertEqual(None, call_args[0][0][0].manage)
        self.assertEqual(False, call_args[0][0][0].noinput)
        self.assertEqual(None, call_args[0][0][0].port)

    @mock.patch('tethys_apps.cli.manage_command')
    def test_manage_subcommand_createsuperuser(self, mock_manage_command):
        testargs = ['tethys', 'manage', 'createsuperuser']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_manage_command.assert_called()
        call_args = mock_manage_command.call_args_list
        self.assertEqual('createsuperuser', call_args[0][0][0].command)
        self.assertEqual(False, call_args[0][0][0].force)
        self.assertEqual(None, call_args[0][0][0].manage)
        self.assertEqual(False, call_args[0][0][0].noinput)
        self.assertEqual(None, call_args[0][0][0].port)

    @mock.patch('tethys_apps.cli.manage_command')
    def test_manage_subcommand_sync(self, mock_manage_command):
        testargs = ['tethys', 'manage', 'sync']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_manage_command.assert_called()
        call_args = mock_manage_command.call_args_list
        self.assertEqual('sync', call_args[0][0][0].command)
        self.assertEqual(False, call_args[0][0][0].force)
        self.assertEqual(None, call_args[0][0][0].manage)
        self.assertEqual(False, call_args[0][0][0].noinput)
        self.assertEqual(None, call_args[0][0][0].port)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    @mock.patch('tethys_apps.cli.manage_command')
    def test_manage_subcommand_help(self, mock_manage_command, mock_exit, mock_stdout):
        mock_exit.side_effect = SystemExit
        testargs = ['tethys', 'manage', '-h']

        with mock.patch.object(sys, 'argv', testargs):
            self.assertRaises(SystemExit, tethys_command)

        mock_manage_command.assert_not_called()
        mock_exit.assert_called_with(0)

        self.assertIn('--help', mock_stdout.getvalue())
        self.assertIn('--manage', mock_stdout.getvalue())
        self.assertIn('--port', mock_stdout.getvalue())
        self.assertIn('--noinput', mock_stdout.getvalue())
        self.assertIn('--force', mock_stdout.getvalue())

    @mock.patch('tethys_apps.cli.scheduler_create_command')
    def test_scheduler_create_command_options(self, mock_scheduler_create_command):
        testargs = ['tethys', 'schedulers', 'create', '-n', 'foo_name', '-e', 'http://foo.foo_endpoint',
                    '-u', 'foo_user', '-p', 'foo_pass', '-k', 'private_foo_pass']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_scheduler_create_command.assert_called()
        call_args = mock_scheduler_create_command.call_args_list
        self.assertEqual('http://foo.foo_endpoint', call_args[0][0][0].endpoint)
        self.assertEqual('foo_name', call_args[0][0][0].name)
        self.assertEqual('foo_pass', call_args[0][0][0].password)
        self.assertEqual('private_foo_pass', call_args[0][0][0].private_key_pass)
        self.assertEqual(None, call_args[0][0][0].private_key_path)
        self.assertEqual('foo_user', call_args[0][0][0].username)

    @mock.patch('tethys_apps.cli.scheduler_create_command')
    def test_scheduler_create_command_verbose_options(self, mock_scheduler_create_command):
        testargs = ['tethys', 'schedulers', 'create', '--name', 'foo_name', '--endpoint', 'http://foo.foo_endpoint',
                    '--username', 'foo_user', '--private-key-path', 'private_foo_path']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_scheduler_create_command.assert_called()
        call_args = mock_scheduler_create_command.call_args_list
        self.assertEqual('http://foo.foo_endpoint', call_args[0][0][0].endpoint)
        self.assertEqual('foo_name', call_args[0][0][0].name)
        self.assertEqual(None, call_args[0][0][0].password)
        self.assertEqual(None, call_args[0][0][0].private_key_pass)
        self.assertEqual('private_foo_path', call_args[0][0][0].private_key_path)
        self.assertEqual('foo_user', call_args[0][0][0].username)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    @mock.patch('tethys_apps.cli.scheduler_create_command')
    def test_scheduler_create_command_help(self, mock_scheduler_create_command, mock_exit, mock_stdout):
        mock_exit.side_effect = SystemExit
        testargs = ['tethys', 'schedulers', 'create', '-h']

        with mock.patch.object(sys, 'argv', testargs):
            self.assertRaises(SystemExit, tethys_command)

        mock_scheduler_create_command.assert_not_called()
        mock_exit.assert_called_with(0)

        self.assertIn('--help', mock_stdout.getvalue())
        self.assertIn('--name', mock_stdout.getvalue())
        self.assertIn('--endpoint', mock_stdout.getvalue())
        self.assertIn('--username', mock_stdout.getvalue())
        self.assertIn('--password', mock_stdout.getvalue())
        self.assertIn('--private-key-path', mock_stdout.getvalue())
        self.assertIn('--private-key-pass', mock_stdout.getvalue())

    @mock.patch('tethys_apps.cli.schedulers_list_command')
    def test_scheduler_list_command(self, mock_scheduler_list_command):
        testargs = ['tethys', 'schedulers', 'list']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_scheduler_list_command.assert_called()

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    @mock.patch('tethys_apps.cli.schedulers_list_command')
    def test_scheduler_list_command_help(self, mock_scheduler_list_command, mock_exit, mock_stdout):
        mock_exit.side_effect = SystemExit
        testargs = ['tethys', 'schedulers', 'list', '-h']

        with mock.patch.object(sys, 'argv', testargs):
            self.assertRaises(SystemExit, tethys_command)

        mock_scheduler_list_command.assert_not_called()
        mock_exit.assert_called_with(0)

        self.assertIn('--help', mock_stdout.getvalue())

    @mock.patch('tethys_apps.cli.schedulers_remove_command')
    def test_scheduler_remove_command(self, mock_scheduler_remove_command):
        testargs = ['tethys', 'schedulers', 'remove', 'foo_name']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_scheduler_remove_command.assert_called()
        call_args = mock_scheduler_remove_command.call_args_list
        self.assertEqual(False, call_args[0][0][0].force)
        self.assertEqual('foo_name', call_args[0][0][0].scheduler_name)

    @mock.patch('tethys_apps.cli.schedulers_remove_command')
    def test_scheduler_remove_command_options(self, mock_scheduler_remove_command):
        testargs = ['tethys', 'schedulers', 'remove', 'foo_name', '-f']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_scheduler_remove_command.assert_called()
        call_args = mock_scheduler_remove_command.call_args_list
        self.assertEqual(True, call_args[0][0][0].force)
        self.assertEqual('foo_name', call_args[0][0][0].scheduler_name)

    @mock.patch('tethys_apps.cli.schedulers_remove_command')
    def test_scheduler_remove_command_verbose_options(self, mock_scheduler_remove_command):
        testargs = ['tethys', 'schedulers', 'remove', 'foo_name', '--force']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_scheduler_remove_command.assert_called()
        call_args = mock_scheduler_remove_command.call_args_list
        self.assertEqual(True, call_args[0][0][0].force)
        self.assertEqual('foo_name', call_args[0][0][0].scheduler_name)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    @mock.patch('tethys_apps.cli.schedulers_remove_command')
    def test_scheduler_list_command_help_2(self, mock_scheduler_remove_command, mock_exit, mock_stdout):
        mock_exit.side_effect = SystemExit
        testargs = ['tethys', 'schedulers', 'remove', '-h']

        with mock.patch.object(sys, 'argv', testargs):
            self.assertRaises(SystemExit, tethys_command)

        mock_scheduler_remove_command.assert_not_called()
        mock_exit.assert_called_with(0)

        self.assertIn('--help', mock_stdout.getvalue())
        self.assertIn('--force', mock_stdout.getvalue())
        self.assertIn('scheduler_name', mock_stdout.getvalue())

    @mock.patch('tethys_apps.cli.services_remove_persistent_command')
    def test_services_remove_persistent_command(self, mock_services_remove_persistent_command):
        testargs = ['tethys', 'services', 'remove', 'persistent', 'foo_service_uid']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_services_remove_persistent_command.assert_called()
        call_args = mock_services_remove_persistent_command.call_args_list
        self.assertEqual(False, call_args[0][0][0].force)
        self.assertEqual('foo_service_uid', call_args[0][0][0].service_uid)

    @mock.patch('tethys_apps.cli.services_remove_persistent_command')
    def test_services_remove_persistent_command_options(self, mock_services_remove_persistent_command):
        testargs = ['tethys', 'services', 'remove', 'persistent', '-f', 'foo_service_uid']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_services_remove_persistent_command.assert_called()
        call_args = mock_services_remove_persistent_command.call_args_list
        self.assertEqual(True, call_args[0][0][0].force)
        self.assertEqual('foo_service_uid', call_args[0][0][0].service_uid)

    @mock.patch('tethys_apps.cli.services_remove_persistent_command')
    def test_services_remove_persistent_command_verbose_options(self, mock_services_remove_persistent_command):
        testargs = ['tethys', 'services', 'remove', 'persistent', '--force', 'foo_service_uid']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_services_remove_persistent_command.assert_called()
        call_args = mock_services_remove_persistent_command.call_args_list
        self.assertEqual(True, call_args[0][0][0].force)
        self.assertEqual('foo_service_uid', call_args[0][0][0].service_uid)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    @mock.patch('tethys_apps.cli.services_remove_persistent_command')
    def test_services_remove_persistent_command_help(self, mock_services_remove_persistent_command, mock_exit,
                                                     mock_stdout):
        mock_exit.side_effect = SystemExit
        testargs = ['tethys', 'services', 'remove', 'persistent', '-h']

        with mock.patch.object(sys, 'argv', testargs):
            self.assertRaises(SystemExit, tethys_command)

        mock_services_remove_persistent_command.assert_not_called()
        mock_exit.assert_called_with(0)

        self.assertIn('--help', mock_stdout.getvalue())
        self.assertIn('--force', mock_stdout.getvalue())
        self.assertIn('service_uid', mock_stdout.getvalue())

    @mock.patch('tethys_apps.cli.services_remove_spatial_command')
    def test_services_remove_spatial_command(self, mock_services_remove_spatial_command):
        testargs = ['tethys', 'services', 'remove', 'spatial', 'foo_service_uid']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_services_remove_spatial_command.assert_called()
        call_args = mock_services_remove_spatial_command.call_args_list
        self.assertEqual(False, call_args[0][0][0].force)
        self.assertEqual('foo_service_uid', call_args[0][0][0].service_uid)

    @mock.patch('tethys_apps.cli.services_remove_spatial_command')
    def test_services_remove_spatial_command_options(self, mock_services_remove_spatial_command):
        testargs = ['tethys', 'services', 'remove', 'spatial', '-f', 'foo_service_uid']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_services_remove_spatial_command.assert_called()
        call_args = mock_services_remove_spatial_command.call_args_list
        self.assertEqual(True, call_args[0][0][0].force)
        self.assertEqual('foo_service_uid', call_args[0][0][0].service_uid)

    @mock.patch('tethys_apps.cli.services_remove_spatial_command')
    def test_services_remove_spatial_command_verbose_options(self, mock_services_remove_spatial_command):
        testargs = ['tethys', 'services', 'remove', 'spatial', '--force', 'foo_service_uid']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_services_remove_spatial_command.assert_called()
        call_args = mock_services_remove_spatial_command.call_args_list
        self.assertEqual(True, call_args[0][0][0].force)
        self.assertEqual('foo_service_uid', call_args[0][0][0].service_uid)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    @mock.patch('tethys_apps.cli.services_remove_spatial_command')
    def test_services_remove_spatial_command_help(self, mock_services_remove_spatial_command, mock_exit, mock_stdout):
        mock_exit.side_effect = SystemExit
        testargs = ['tethys', 'services', 'remove', 'spatial', '-h']

        with mock.patch.object(sys, 'argv', testargs):
            self.assertRaises(SystemExit, tethys_command)

        mock_services_remove_spatial_command.assert_not_called()
        mock_exit.assert_called_with(0)

        self.assertIn('--help', mock_stdout.getvalue())
        self.assertIn('--force', mock_stdout.getvalue())
        self.assertIn('service_uid', mock_stdout.getvalue())

    @mock.patch('tethys_apps.cli.services_create_persistent_command')
    def test_services_create_persistent_command_options(self, mock_services_create_persistent_command):
        testargs = ['tethys', 'services', 'create', 'persistent', '-n', 'foo_name', '-c', 'foo:pass@foo.bar:5555']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_services_create_persistent_command.assert_called()
        call_args = mock_services_create_persistent_command.call_args_list
        self.assertEqual('foo:pass@foo.bar:5555', call_args[0][0][0].connection)
        self.assertEqual('foo_name', call_args[0][0][0].name)

    @mock.patch('tethys_apps.cli.services_create_persistent_command')
    def test_services_create_persistent_command_verbose_options(self, mock_services_create_persistent_command):
        testargs = ['tethys', 'services', 'create', 'persistent', '--name', 'foo_name',
                    '--connection', 'foo:pass@foo.bar:5555']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_services_create_persistent_command.assert_called()
        call_args = mock_services_create_persistent_command.call_args_list
        self.assertEqual('foo:pass@foo.bar:5555', call_args[0][0][0].connection)
        self.assertEqual('foo_name', call_args[0][0][0].name)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    @mock.patch('tethys_apps.cli.services_create_persistent_command')
    def test_services_create_persistent_command_help(self, mock_services_create_persistent_command, mock_exit,
                                                     mock_stdout):
        mock_exit.side_effect = SystemExit
        testargs = ['tethys', 'services', 'create', 'persistent', '-h']

        with mock.patch.object(sys, 'argv', testargs):
            self.assertRaises(SystemExit, tethys_command)

        mock_services_create_persistent_command.assert_not_called()
        mock_exit.assert_called_with(0)

        self.assertIn('--help', mock_stdout.getvalue())
        self.assertIn('--name', mock_stdout.getvalue())
        self.assertIn('--connection', mock_stdout.getvalue())

    @mock.patch('tethys_apps.cli.services_create_spatial_command')
    def test_services_create_spatial_command_options(self, mock_services_create_spatial_command):
        testargs = ['tethys', 'services', 'create', 'spatial', '-n', 'foo_name', '-c', 'foo:pass@http://foo.bar:5555']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_services_create_spatial_command.assert_called()
        call_args = mock_services_create_spatial_command.call_args_list
        self.assertEqual(None, call_args[0][0][0].apikey)
        self.assertEqual('foo:pass@http://foo.bar:5555', call_args[0][0][0].connection)
        self.assertEqual('foo_name', call_args[0][0][0].name)
        self.assertEqual(None, call_args[0][0][0].public_endpoint)

    @mock.patch('tethys_apps.cli.services_create_spatial_command')
    def test_services_create_spatial_command_verbose_options(self, mock_services_create_spatial_command):
        testargs = ['tethys', 'services', 'create', 'spatial', '--name', 'foo_name',
                    '--connection', 'foo:pass@http://foo.bar:5555', '--public-endpoint', 'foo.bar:1234',
                    '--apikey', 'foo_apikey']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_services_create_spatial_command.assert_called()
        call_args = mock_services_create_spatial_command.call_args_list
        self.assertEqual('foo_apikey', call_args[0][0][0].apikey)
        self.assertEqual('foo:pass@http://foo.bar:5555', call_args[0][0][0].connection)
        self.assertEqual('foo_name', call_args[0][0][0].name)
        self.assertEqual('foo.bar:1234', call_args[0][0][0].public_endpoint)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    @mock.patch('tethys_apps.cli.services_create_spatial_command')
    def test_services_create_spatial_command_help(self, mock_services_create_spatial_command, mock_exit,
                                                  mock_stdout):
        mock_exit.side_effect = SystemExit
        testargs = ['tethys', 'services', 'create', 'spatial', '-h']

        with mock.patch.object(sys, 'argv', testargs):
            self.assertRaises(SystemExit, tethys_command)

        mock_services_create_spatial_command.assert_not_called()
        mock_exit.assert_called_with(0)

        self.assertIn('--help', mock_stdout.getvalue())
        self.assertIn('--name', mock_stdout.getvalue())
        self.assertIn('--connection', mock_stdout.getvalue())
        self.assertIn('--public-endpoint', mock_stdout.getvalue())
        self.assertIn('--apikey', mock_stdout.getvalue())

    @mock.patch('tethys_apps.cli.services_list_command')
    def test_services_list_command(self, mock_services_list_command):
        testargs = ['tethys', 'services', 'list']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_services_list_command.assert_called()
        call_args = mock_services_list_command.call_args_list
        self.assertEqual(False, call_args[0][0][0].persistent)
        self.assertEqual(False, call_args[0][0][0].spatial)

    @mock.patch('tethys_apps.cli.services_list_command')
    def test_services_list_command_options(self, mock_services_list_command):
        testargs = ['tethys', 'services', 'list', '-p']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_services_list_command.assert_called()
        call_args = mock_services_list_command.call_args_list
        self.assertEqual(True, call_args[0][0][0].persistent)
        self.assertEqual(False, call_args[0][0][0].spatial)

    @mock.patch('tethys_apps.cli.services_list_command')
    def test_services_list_command_verbose_options(self, mock_services_list_command):
        testargs = ['tethys', 'services', 'list', '--spatial']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_services_list_command.assert_called()
        call_args = mock_services_list_command.call_args_list
        self.assertEqual(False, call_args[0][0][0].persistent)
        self.assertEqual(True, call_args[0][0][0].spatial)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    @mock.patch('tethys_apps.cli.services_list_command')
    def test_services_list_command_help(self, mock_services_list_command, mock_exit, mock_stdout):
        mock_exit.side_effect = SystemExit
        testargs = ['tethys', 'services', 'list', '-h']

        with mock.patch.object(sys, 'argv', testargs):
            self.assertRaises(SystemExit, tethys_command)

        mock_services_list_command.assert_not_called()
        mock_exit.assert_called_with(0)

        self.assertIn('--help', mock_stdout.getvalue())
        self.assertIn('--persistent', mock_stdout.getvalue())
        self.assertIn('--spatial', mock_stdout.getvalue())

    @mock.patch('tethys_apps.cli.app_settings_list_command')
    def test_app_settings_list_command(self, mock_app_settings_list_command):
        testargs = ['tethys', 'app_settings', 'list', 'foo_app']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_app_settings_list_command.assert_called()
        call_args = mock_app_settings_list_command.call_args_list
        self.assertEqual('foo_app', call_args[0][0][0].app)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    @mock.patch('tethys_apps.cli.app_settings_list_command')
    def test_app_settings_list_command_help(self, mock_app_settings_list_command, mock_exit, mock_stdout):
        mock_exit.side_effect = SystemExit
        testargs = ['tethys', 'app_settings', 'list', '-h']

        with mock.patch.object(sys, 'argv', testargs):
            self.assertRaises(SystemExit, tethys_command)

        mock_app_settings_list_command.assert_not_called()
        mock_exit.assert_called_with(0)

        self.assertIn('--help', mock_stdout.getvalue())
        self.assertIn('<app_package>', mock_stdout.getvalue())

    @mock.patch('tethys_apps.cli.app_settings_create_ps_database_command')
    def test_app_settings_create_command_options(self, mock_app_settings_create_command):
        testargs = ['tethys', 'app_settings', 'create', '-a', 'foo_app_package', '-n', 'foo', '-d', 'foo description',
                    'ps_database', '-s', '-y']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_app_settings_create_command.assert_called()
        call_args = mock_app_settings_create_command.call_args_list
        self.assertEqual('foo_app_package', call_args[0][0][0].app)
        self.assertEqual('foo description', call_args[0][0][0].description)
        self.assertEqual(True, call_args[0][0][0].dynamic)
        self.assertEqual(False, call_args[0][0][0].initialized)
        self.assertEqual(None, call_args[0][0][0].initializer)
        self.assertEqual('foo', call_args[0][0][0].name)
        self.assertEqual(False, call_args[0][0][0].required)
        self.assertEqual(True, call_args[0][0][0].spatial)

    @mock.patch('tethys_apps.cli.app_settings_create_ps_database_command')
    def test_app_settings_create_command_verbose_options(self, mock_app_settings_create_command):
        testargs = ['tethys', 'app_settings', 'create', '--app', 'foo_app_package', '--name', 'foo', '--description',
                    'foo description', 'ps_database', '--spatial', '--dynamic']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_app_settings_create_command.assert_called()
        call_args = mock_app_settings_create_command.call_args_list
        self.assertEqual('foo_app_package', call_args[0][0][0].app)
        self.assertEqual('foo description', call_args[0][0][0].description)
        self.assertEqual(True, call_args[0][0][0].dynamic)
        self.assertEqual(False, call_args[0][0][0].initialized)
        self.assertEqual(None, call_args[0][0][0].initializer)
        self.assertEqual('foo', call_args[0][0][0].name)
        self.assertEqual(False, call_args[0][0][0].required)
        self.assertEqual(True, call_args[0][0][0].spatial)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    @mock.patch('tethys_apps.cli.app_settings_create_ps_database_command')
    def test_app_settings_create_command_help(self, mock_app_settings_create_command, mock_exit, mock_stdout):
        mock_exit.side_effect = SystemExit
        testargs = ['tethys', 'app_settings', 'create', '-h']

        with mock.patch.object(sys, 'argv', testargs):
            self.assertRaises(SystemExit, tethys_command)

        mock_app_settings_create_command.assert_not_called()
        mock_exit.assert_called_with(0)

        self.assertIn('--help', mock_stdout.getvalue())
        self.assertIn('--app', mock_stdout.getvalue())
        self.assertIn('--name', mock_stdout.getvalue())
        self.assertIn('--description', mock_stdout.getvalue())
        self.assertIn('--required', mock_stdout.getvalue())
        self.assertIn('--initializer', mock_stdout.getvalue())
        self.assertIn('--initialized', mock_stdout.getvalue())
        self.assertIn('{ps_database}', mock_stdout.getvalue())

    @mock.patch('tethys_apps.cli.app_settings_remove_command')
    def test_app_settings_create_command_options_2(self, mock_app_settings_remove_command):
        testargs = ['tethys', 'app_settings', 'remove', '-n', 'foo', '-f', 'foo_app']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_app_settings_remove_command.assert_called()
        call_args = mock_app_settings_remove_command.call_args_list
        self.assertEqual('foo_app', call_args[0][0][0].app)
        self.assertEqual(True, call_args[0][0][0].force)
        self.assertEqual('foo', call_args[0][0][0].name)

    @mock.patch('tethys_apps.cli.app_settings_remove_command')
    def test_app_settings_create_command_verbose_options_2(self, mock_app_settings_remove_command):
        testargs = ['tethys', 'app_settings', 'remove', '--name', 'foo', '--force', 'foo_app']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_app_settings_remove_command.assert_called()
        call_args = mock_app_settings_remove_command.call_args_list
        self.assertEqual('foo_app', call_args[0][0][0].app)
        self.assertEqual(True, call_args[0][0][0].force)
        self.assertEqual('foo', call_args[0][0][0].name)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    @mock.patch('tethys_apps.cli.app_settings_remove_command')
    def test_app_settings_create_command_help_2(self, mock_app_settings_remove_command, mock_exit, mock_stdout):
        mock_exit.side_effect = SystemExit
        testargs = ['tethys', 'app_settings', 'remove', '-h']

        with mock.patch.object(sys, 'argv', testargs):
            self.assertRaises(SystemExit, tethys_command)

        mock_app_settings_remove_command.assert_not_called()
        mock_exit.assert_called_with(0)

        self.assertIn('--help', mock_stdout.getvalue())
        self.assertIn('<app_package>', mock_stdout.getvalue())
        self.assertIn('--name', mock_stdout.getvalue())
        self.assertIn('--force', mock_stdout.getvalue())

    @mock.patch('tethys_apps.cli.link_command')
    def test_link_command(self, mock_link_command):
        testargs = ['tethys', 'link', 'spatial:foo_service', 'foo_package:database:foo_2']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_link_command.assert_called()
        call_args = mock_link_command.call_args_list
        self.assertEqual('spatial:foo_service', call_args[0][0][0].service)
        self.assertEqual('foo_package:database:foo_2', call_args[0][0][0].setting)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    @mock.patch('tethys_apps.cli.link_command')
    def test_link_command_help(self, mock_link_command, mock_exit, mock_stdout):
        mock_exit.side_effect = SystemExit
        testargs = ['tethys', 'link', '-h']

        with mock.patch.object(sys, 'argv', testargs):
            self.assertRaises(SystemExit, tethys_command)

        mock_link_command.assert_not_called()
        mock_exit.assert_called_with(0)

        self.assertIn('--help', mock_stdout.getvalue())
        self.assertIn('service', mock_stdout.getvalue())
        self.assertIn('setting', mock_stdout.getvalue())

    @mock.patch('tethys_apps.cli.tstc')
    def test_test_command(self, mock_test_command):
        testargs = ['tethys', 'test']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_test_command.assert_called()
        call_args = mock_test_command.call_args_list
        self.assertEqual(False, call_args[0][0][0].coverage)
        self.assertEqual(False, call_args[0][0][0].coverage_html)
        self.assertEqual(None, call_args[0][0][0].file)
        self.assertEqual(False, call_args[0][0][0].gui)
        self.assertEqual(False, call_args[0][0][0].unit)

    @mock.patch('tethys_apps.cli.tstc')
    def test_test_command_options(self, mock_test_command):
        testargs = ['tethys', 'test', '-c', '-C', '-u', '-g', '-f', 'foo.bar']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_test_command.assert_called()
        call_args = mock_test_command.call_args_list
        self.assertEqual(True, call_args[0][0][0].coverage)
        self.assertEqual(True, call_args[0][0][0].coverage_html)
        self.assertEqual('foo.bar', call_args[0][0][0].file)
        self.assertEqual(True, call_args[0][0][0].gui)
        self.assertEqual(True, call_args[0][0][0].unit)

    @mock.patch('tethys_apps.cli.tstc')
    def test_test_command_options_verbose(self, mock_test_command):
        testargs = ['tethys', 'test', '--coverage', '--coverage-html', '--unit', '--gui', '--file', 'foo.bar']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_test_command.assert_called()
        call_args = mock_test_command.call_args_list
        self.assertEqual(True, call_args[0][0][0].coverage)
        self.assertEqual(True, call_args[0][0][0].coverage_html)
        self.assertEqual('foo.bar', call_args[0][0][0].file)
        self.assertEqual(True, call_args[0][0][0].gui)
        self.assertEqual(True, call_args[0][0][0].unit)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    @mock.patch('tethys_apps.cli.tstc')
    def test_test_command_help(self, mock_test_command, mock_exit, mock_stdout):
        mock_exit.side_effect = SystemExit
        testargs = ['tethys', 'test', '-h']

        with mock.patch.object(sys, 'argv', testargs):
            self.assertRaises(SystemExit, tethys_command)

        mock_test_command.assert_not_called()
        mock_exit.assert_called_with(0)

        self.assertIn('--help', mock_stdout.getvalue())
        self.assertIn('--coverage', mock_stdout.getvalue())
        self.assertIn('--coverage-html', mock_stdout.getvalue())
        self.assertIn('--unit', mock_stdout.getvalue())
        self.assertIn('--gui', mock_stdout.getvalue())
        self.assertIn('--file', mock_stdout.getvalue())

    @mock.patch('tethys_apps.cli.uc')
    def test_uninstall_command(self, mock_uninstall_command):
        testargs = ['tethys', 'uninstall', 'foo_app']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_uninstall_command.assert_called()
        call_args = mock_uninstall_command.call_args_list
        self.assertEqual('foo_app', call_args[0][0][0].app_or_extension)
        self.assertEqual(False, call_args[0][0][0].is_extension)

    @mock.patch('tethys_apps.cli.uc')
    def test_uninstall_command_options(self, mock_uninstall_command):
        testargs = ['tethys', 'uninstall', '-e', 'foo_ext']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_uninstall_command.assert_called()
        call_args = mock_uninstall_command.call_args_list
        self.assertEqual('foo_ext', call_args[0][0][0].app_or_extension)
        self.assertEqual(True, call_args[0][0][0].is_extension)

    @mock.patch('tethys_apps.cli.uc')
    def test_uninstall_command_verbose_options(self, mock_uninstall_command):
        testargs = ['tethys', 'uninstall', '--extension', 'foo_ext']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_uninstall_command.assert_called()
        call_args = mock_uninstall_command.call_args_list
        self.assertEqual('foo_ext', call_args[0][0][0].app_or_extension)
        self.assertEqual(True, call_args[0][0][0].is_extension)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    @mock.patch('tethys_apps.cli.uc')
    def test_uninstall_command_help(self, mock_uninstall_command, mock_exit, mock_stdout):
        mock_exit.side_effect = SystemExit
        testargs = ['tethys', 'uninstall', '-h']

        with mock.patch.object(sys, 'argv', testargs):
            self.assertRaises(SystemExit, tethys_command)

        mock_uninstall_command.assert_not_called()
        mock_exit.assert_called_with(0)

        self.assertIn('--help', mock_stdout.getvalue())
        self.assertIn('--extension', mock_stdout.getvalue())
        self.assertIn('app_or_extension', mock_stdout.getvalue())

    @mock.patch('tethys_apps.cli.lc')
    def test_list_command(self, mock_list_command):
        testargs = ['tethys', 'list']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_list_command.assert_called()

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    @mock.patch('tethys_apps.cli.lc')
    def test_list_command_help(self, mock_list_command, mock_exit, mock_stdout):
        mock_exit.side_effect = SystemExit
        testargs = ['tethys', 'list', '-h']

        with mock.patch.object(sys, 'argv', testargs):
            self.assertRaises(SystemExit, tethys_command)

        mock_list_command.assert_not_called()
        mock_exit.assert_called_with(0)

        self.assertIn('--help', mock_stdout.getvalue())

    @mock.patch('tethys_apps.cli.syc')
    def test_syncstores_command_single(self, mock_syncstores_command):
        testargs = ['tethys', 'syncstores', 'foo_app1']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_syncstores_command.assert_called()
        call_args = mock_syncstores_command.call_args_list
        self.assertEqual(['foo_app1'], call_args[0][0][0].app)
        self.assertEqual(None, call_args[0][0][0].database)
        self.assertEqual(False, call_args[0][0][0].firstime)
        self.assertEqual(False, call_args[0][0][0].firsttime)
        self.assertEqual(None, call_args[0][0][0].manage)
        self.assertEqual(False, call_args[0][0][0].refresh)

    @mock.patch('tethys_apps.cli.syc')
    def test_syncstores_command_multiple(self, mock_syncstores_command):
        testargs = ['tethys', 'syncstores', 'foo_app1', 'foo_app2', 'foo_app3']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_syncstores_command.assert_called()
        call_args = mock_syncstores_command.call_args_list
        self.assertEqual(['foo_app1', 'foo_app2', 'foo_app3'], call_args[0][0][0].app)
        self.assertEqual(None, call_args[0][0][0].database)
        self.assertEqual(False, call_args[0][0][0].firstime)
        self.assertEqual(False, call_args[0][0][0].firsttime)
        self.assertEqual(None, call_args[0][0][0].manage)
        self.assertEqual(False, call_args[0][0][0].refresh)

    @mock.patch('tethys_apps.cli.syc')
    def test_syncstores_command_all(self, mock_syncstores_command):
        testargs = ['tethys', 'syncstores', 'all']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_syncstores_command.assert_called()
        call_args = mock_syncstores_command.call_args_list
        self.assertEqual(['all'], call_args[0][0][0].app)
        self.assertEqual(None, call_args[0][0][0].database)
        self.assertEqual(False, call_args[0][0][0].firstime)
        self.assertEqual(False, call_args[0][0][0].firsttime)
        self.assertEqual(None, call_args[0][0][0].manage)
        self.assertEqual(False, call_args[0][0][0].refresh)

    @mock.patch('tethys_apps.cli.syc')
    def test_syncstores_command_options(self, mock_syncstores_command):
        testargs = ['tethys', 'syncstores', '-r', '-f', '-d', 'foo_db', '-m', '/foo/bar/manage.py', 'foo_app1']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_syncstores_command.assert_called()
        call_args = mock_syncstores_command.call_args_list
        self.assertEqual(['foo_app1'], call_args[0][0][0].app)
        self.assertEqual('foo_db', call_args[0][0][0].database)
        self.assertEqual(False, call_args[0][0][0].firstime)
        self.assertEqual(True, call_args[0][0][0].firsttime)
        self.assertEqual('/foo/bar/manage.py', call_args[0][0][0].manage)
        self.assertEqual(True, call_args[0][0][0].refresh)

    @mock.patch('tethys_apps.cli.syc')
    def test_syncstores_command_verbose_options(self, mock_syncstores_command):
        testargs = ['tethys', 'syncstores', '--refresh', '--firsttime', '--database', 'foo_db',
                    '--manage', '/foo/bar/manage.py', 'foo_app1']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_syncstores_command.assert_called()
        call_args = mock_syncstores_command.call_args_list
        self.assertEqual(['foo_app1'], call_args[0][0][0].app)
        self.assertEqual('foo_db', call_args[0][0][0].database)
        self.assertEqual(False, call_args[0][0][0].firstime)
        self.assertEqual(True, call_args[0][0][0].firsttime)
        self.assertEqual('/foo/bar/manage.py', call_args[0][0][0].manage)
        self.assertEqual(True, call_args[0][0][0].refresh)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    @mock.patch('tethys_apps.cli.syc')
    def test_syncstores_command_help(self, mock_syncstores_command, mock_exit, mock_stdout):
        mock_exit.side_effect = SystemExit
        testargs = ['tethys', 'syncstores', '-h']

        with mock.patch.object(sys, 'argv', testargs):
            self.assertRaises(SystemExit, tethys_command)

        mock_syncstores_command.assert_not_called()
        mock_exit.assert_called_with(0)

        self.assertIn('--help', mock_stdout.getvalue())
        self.assertIn('app', mock_stdout.getvalue())
        self.assertIn('--refresh', mock_stdout.getvalue())
        self.assertIn('--firsttime', mock_stdout.getvalue())
        self.assertIn('--database', mock_stdout.getvalue())
        self.assertIn('--manage', mock_stdout.getvalue())

    @mock.patch('tethys_apps.cli.docker_command')
    def test_docker_command(self, mock_docker_command):
        testargs = ['tethys', 'docker', 'init']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_docker_command.assert_called()
        call_args = mock_docker_command.call_args_list
        self.assertEqual(False, call_args[0][0][0].boot2docker)
        self.assertEqual('init', call_args[0][0][0].command)
        self.assertEqual(None, call_args[0][0][0].containers)
        self.assertEqual(False, call_args[0][0][0].defaults)

    @mock.patch('tethys_apps.cli.docker_command')
    def test_docker_command_options(self, mock_docker_command):
        testargs = ['tethys', 'docker', 'start', '-c', 'postgis', 'geoserver']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_docker_command.assert_called()
        call_args = mock_docker_command.call_args_list
        self.assertEqual(False, call_args[0][0][0].boot2docker)
        self.assertEqual('start', call_args[0][0][0].command)
        self.assertEqual(['postgis', 'geoserver'], call_args[0][0][0].containers)
        self.assertEqual(False, call_args[0][0][0].defaults)

    @mock.patch('tethys_apps.cli.docker_command')
    def test_docker_command_verbose_options(self, mock_docker_command):
        testargs = ['tethys', 'docker', 'stop', '--defaults', '--boot2docker']

        with mock.patch.object(sys, 'argv', testargs):
            tethys_command()

        mock_docker_command.assert_called()
        call_args = mock_docker_command.call_args_list
        self.assertEqual(True, call_args[0][0][0].boot2docker)
        self.assertEqual('stop', call_args[0][0][0].command)
        self.assertEqual(None, call_args[0][0][0].containers)
        self.assertEqual(True, call_args[0][0][0].defaults)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.cli.argparse._sys.exit')
    @mock.patch('tethys_apps.cli.docker_command')
    def test_docker_command_help(self, mock_docker_command, mock_exit, mock_stdout):
        mock_exit.side_effect = SystemExit
        testargs = ['tethys', 'docker', '-h']

        with mock.patch.object(sys, 'argv', testargs):
            self.assertRaises(SystemExit, tethys_command)

        mock_docker_command.assert_not_called()
        mock_exit.assert_called_with(0)

        self.assertIn('--help', mock_stdout.getvalue())
        self.assertIn('--defaults', mock_stdout.getvalue())
        self.assertIn('--containers', mock_stdout.getvalue())
        self.assertIn('--boot2docker', mock_stdout.getvalue())
