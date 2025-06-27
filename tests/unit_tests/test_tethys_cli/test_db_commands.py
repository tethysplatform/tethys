import sys
import unittest
import warnings
from unittest import mock

from django.test.utils import override_settings

from tethys_cli.db_commands import (
    db_command,
    process_args,
    create_db_user,
    init_db_server,
    start_db_server,
    create_tethys_db,
    purge_db_server,
    _run_process,
    _prompt_if_error,
)


class TestCommandTests(unittest.TestCase):
    def setUp(self):
        run_process_patcher = mock.patch("tethys_cli.db_commands._run_process")
        self.mock_run_process = run_process_patcher.start()
        self.addCleanup(run_process_patcher.stop)

        self.options = {
            "db_engine": "postgresql",
            "db_dir": "foo",
            "db_alias": "test",
            "hostname": "localhost",
            "port": "0000",
            "db_name": "db_name",
            "username": "foo",
            "password": "bar",
            "superuser_name": "Foo",
            "superuser_password": "Bar",
            "portal_superuser_name": "PFoo",
            "portal_superuser_email": "PEmail",
            "portal_superuser_password": "PBar",
            "no_confirmation": True,
        }

        process_args_patcher = mock.patch(
            "tethys_cli.db_commands.process_args", return_value=self.options
        )
        self.mock_process_args = process_args_patcher.start()
        self.addCleanup(process_args_patcher.stop)

        # suppress warning about overriding DATABASES setting.
        warnings.simplefilter("ignore", UserWarning)

    def tearDown(self):
        # revert to normal warnings
        warnings.simplefilter("default", UserWarning)

    def _get_kwargs(self, remove=None):
        remove = remove or list()
        kwargs = self.options.copy()
        for k in remove:
            kwargs.pop(k)
        return kwargs

    @mock.patch("tethys_cli.db_commands.write_error")
    @mock.patch("tethys_cli.db_commands.write_info")
    @mock.patch("tethys_cli.db_commands.run_process")
    def tests_db_command__run_process(
        self, mock_run_process, mock_write_info, mock_write_error
    ):
        mock_args = mock.MagicMock()
        msg = "test msg"
        err_msg = "test err msg"

        self.assertRaises(SystemExit, _run_process, mock_args, msg, err_msg)
        mock_run_process.assert_called_with(mock_args)
        mock_write_info.assert_called_with(msg)
        mock_write_error.assert_called_with(err_msg)

    @mock.patch("tethys_cli.db_commands.write_error")
    @mock.patch("tethys_cli.db_commands.write_info")
    @mock.patch("tethys_cli.db_commands.run_process")
    def tests_db_command__run_process_return_code(
        self, mock_run_process, mock_write_info, mock_write_error
    ):
        mock_args = mock.MagicMock()
        msg = "test msg"
        err_msg = "test err msg"

        _run_process(mock_args, msg, err_msg, exit_on_error=False)
        mock_run_process.assert_called_with(mock_args)
        mock_write_info.assert_called_with(msg)
        mock_write_error.assert_called_with(err_msg)

    @mock.patch("tethys_cli.db_commands.relative_to_tethys_home")
    @mock.patch("tethys_cli.db_commands.vars")
    @override_settings(
        DATABASES={
            "test": {
                "ENGINE": "postgresql",
                "NAME": "db_name",
                "HOST": "localhost",
                "PORT": "0000",
                "DIR": "foo",
            }
        }
    )
    def test_db_command_process_args(self, mock_vars, mock_path):
        path = mock.MagicMock()
        mock_path.return_value = path
        path.is_absolute.return_value = False
        mock_args = mock.MagicMock(command="init", db_alias="test")
        mock_vars.return_value = dict(
            db_engine="postgresql",
            username="foo",
            password="bar",
            superuser_name="Foo",
            superuser_password="Bar",
            portal_superuser_name="PFoo",
            portal_superuser_email="PEmail",
            portal_superuser_password="PBar",
            no_confirmation=True,
        )
        self.mock_run_process.return_value = 0

        options = process_args(mock_args)
        expected = self.options.copy()
        expected.update(db_dir=path)
        self.assertDictEqual(options, expected)

    @mock.patch("tethys_cli.db_commands.Path")
    @mock.patch("tethys_cli.db_commands.vars")
    @override_settings(
        DATABASES={
            "test": {
                "NAME": "db_name",
                "PORT": "0000",
            }
        }
    )
    def test_db_command_process_args_with_error(self, mock_vars, mock_path):
        path = mock.MagicMock()
        mock_path.return_value = path
        path.is_absolute.return_value = False
        mock_args = mock.MagicMock()
        mock_args.command = "init"
        mock_args.db_alias = "test"
        mock_vars.return_value = dict(
            username="foo",
            password="bar",
            superuser_name="Foo",
            superuser_password="Bar",
            portal_superuser_name="PFoo",
            portal_superuser_email="PEmail",
            portal_superuser_password="PBar",
        )
        self.mock_run_process.return_value = 0
        self.assertRaises(RuntimeError, process_args, mock_args)

    @mock.patch("tethys_cli.db_commands.Path")
    @mock.patch("tethys_cli.db_commands.vars")
    @override_settings(
        DATABASES={
            "test": {
                "NAME": "db_name",
                "PORT": "0000",
                "ENGINE": "invalid",
            }
        }
    )
    def test_db_command_process_args_with_engine_error(self, mock_vars, mock_path):
        path = mock.MagicMock()
        mock_path.return_value = path
        path.is_absolute.return_value = False
        mock_args = mock.MagicMock()
        mock_args.command = "create"
        mock_args.db_alias = "test"
        mock_vars.return_value = dict(
            username="foo",
            password="bar",
            superuser_name="Foo",
            superuser_password="Bar",
            portal_superuser_name="PFoo",
            portal_superuser_email="PEmail",
            portal_superuser_password="PBar",
        )
        self.mock_run_process.return_value = 0
        self.assertRaises(RuntimeError, process_args, mock_args)

    def test_db_command_init(self):
        mock_args = mock.MagicMock()
        mock_args.command = "init"
        db_command(mock_args)
        kwargs = self._get_kwargs(remove=["db_dir"])
        self.mock_run_process.assert_called_with(
            ["initdb", "-U", "postgres", "-D", "foo/data"],
            'Initializing Postgresql database server in "foo/data"...',
            "Could not initialize the Postgresql database.",
            **kwargs,
        )

    @mock.patch("tethys_cli.db_commands.write_error")
    @mock.patch("tethys_cli.db_commands.create_db_user")
    def test_db_command_create_error_code_without_exit(
        self, mock_create_db_user, mock_write_error
    ):
        mock_args = mock.MagicMock()
        mock_args.command = "create"
        self.options["exit_creation_on_error"] = False
        mock_create_db_user.return_value = 1
        db_command(mock_args)
        call_args = mock_create_db_user.call_args_list
        kwargs = self._get_kwargs(remove=["superuser_name", "superuser_password"])
        kwargs["exit_on_error"] = False
        kwargs.pop("exit_creation_on_error")
        self.assertEqual(call_args[1], mock.call(**kwargs))
        kwargs.pop("db_name")
        kwargs["username"] = self.options["superuser_name"]
        kwargs["password"] = self.options["superuser_password"]
        self.assertEqual(call_args[0], mock.call(is_superuser=True, **kwargs))
        err_msg = "Failed to setup user/superuser users/tables"
        mock_write_error.assert_called_with(err_msg)

    @mock.patch("tethys_cli.db_commands.write_error")
    @mock.patch("tethys_cli.db_commands.create_db_user")
    def test_db_command_create_error_code_with_exit(
        self, mock_create_db_user, mock_write_error
    ):
        mock_args = mock.MagicMock()
        mock_args.command = "create"
        self.options["exit_creation_on_error"] = True
        mock_create_db_user.return_value = 1
        self.assertRaises(SystemExit, db_command, mock_args)
        call_args = mock_create_db_user.call_args_list
        kwargs = self._get_kwargs(remove=["superuser_name", "superuser_password"])
        kwargs["exit_on_error"] = False
        kwargs.pop("exit_creation_on_error")
        self.assertEqual(call_args[1], mock.call(**kwargs))
        kwargs.pop("db_name")
        kwargs["username"] = self.options["superuser_name"]
        kwargs["password"] = self.options["superuser_password"]
        self.assertEqual(call_args[0], mock.call(is_superuser=True, **kwargs))
        err_msg = "Failed to setup user/superuser users/tables"
        mock_write_error.assert_called_with(err_msg)

    @mock.patch("tethys_cli.db_commands.create_db_user")
    def test_db_command_create_no_error_codes(self, mock_create_db_user):
        mock_args = mock.MagicMock()
        mock_args.command = "create"
        mock_create_db_user.return_value = None
        db_command(mock_args)
        call_args = mock_create_db_user.call_args_list
        kwargs = self._get_kwargs(remove=["superuser_name", "superuser_password"])
        kwargs["exit_on_error"] = False
        self.assertEqual(call_args[1], mock.call(**kwargs))
        kwargs.pop("db_name")
        kwargs["username"] = self.options["superuser_name"]
        kwargs["password"] = self.options["superuser_password"]
        self.assertEqual(call_args[0], mock.call(is_superuser=True, **kwargs))

    def test_db_command_create_db_user(self):
        create_db_user(**self.options)
        call_args = self.mock_run_process.call_args_list
        command = (
            f"CREATE USER {self.options['username']} WITH NOCREATEDB NOCREATEROLE NOSUPERUSER PASSWORD "
            f"'{self.options['password']}';"
        )
        command = (
            f"DO "
            f"$do$ "
            f"BEGIN "
            f"  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{self.options['username']}') THEN "
            f"    {command} "
            f"  END IF; "
            f"END "
            f"$do$;"
        )
        self.assertEqual(
            call_args[0][0][0],
            [
                "psql",
                "-h",
                self.options["hostname"],
                "-U",
                "postgres",
                "-p",
                "0000",
                "--command",
                command,
            ],
        )
        args = [
            "createdb",
            "-h",
            self.options["hostname"],
            "-U",
            "postgres",
            "-E",
            "utf-8",
            "-p",
            self.options["port"],
            "-O",
            self.options["username"],
            self.options["db_name"],
        ]
        kwargs = self._get_kwargs(
            remove=["hostname", "port", "db_name", "username", "password"]
        )
        self.mock_run_process.assert_called_with(
            args,
            'Creating Tethys database table "db_name" for user "foo"...',
            'Failed to create Tethys database table "db_name" for user "foo"',
            **kwargs,
        )

    def test_db_command_create_db_user_with_superuser(self):
        create_db_user(is_superuser=True, **self.options)
        call_args = self.mock_run_process.call_args_list
        command = (
            f"CREATE USER {self.options['username']} WITH CREATEDB NOCREATEROLE SUPERUSER PASSWORD "
            f"'{self.options['password']}';"
        )
        command = (
            f"DO "
            f"$do$ "
            f"BEGIN "
            f"  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{self.options['username']}') THEN "
            f"    {command} "
            f"  END IF; "
            f"END "
            f"$do$;"
        )
        self.assertEqual(
            call_args[0][0][0],
            [
                "psql",
                "-h",
                self.options["hostname"],
                "-U",
                "postgres",
                "-p",
                "0000",
                "--command",
                command,
            ],
        )

    def test_db_command_start(self):
        mock_args = mock.MagicMock()
        mock_args.command = "start"
        db_command(mock_args)
        kwargs = self._get_kwargs(remove=["db_dir", "port"])
        self.mock_run_process.assert_called_with(
            [
                "pg_ctl",
                "-U",
                "postgres",
                "-D",
                "foo/data",
                "-l",
                "foo/logfile",
                "start",
                "-o",
                "-p 0000",
            ],
            'Starting Postgresql database server in "foo/data" on port 0000...',
            "There was an error while starting the Postgresql database.",
            **kwargs,
        )

    def test_db_command_stop(self):
        mock_args = mock.MagicMock()
        mock_args.command = "stop"
        db_command(mock_args)
        kwargs = self._get_kwargs(remove=["db_dir"])
        self.mock_run_process.assert_called_with(
            ["pg_ctl", "-U", "postgres", "-D", "foo/data", "stop"],
            "Stopping Postgresql database server...",
            "There was an error while stopping the Posgresql database.",
            **kwargs,
        )

    def test_db_command_status(self):
        mock_args = mock.MagicMock()
        mock_args.command = "status"
        db_command(mock_args)
        kwargs = self._get_kwargs(remove=["db_dir"])
        self.mock_run_process.assert_called_with(
            ["pg_ctl", "status", "-D", "foo/data"],
            "Checking status of Postgresql database server...",
            "",
            **kwargs,
        )

    @mock.patch("tethys_cli.db_commands.get_manage_path", return_value="foo/manage.py")
    def test_db_command_migrate(self, mock_get_manage_path):
        mock_args = mock.MagicMock()
        mock_args.command = "migrate"
        db_command(mock_args)
        mock_get_manage_path.assert_called()
        kwargs = self._get_kwargs(remove=["db_alias"])
        self.mock_run_process.assert_called_with(
            [sys.executable, "foo/manage.py", "migrate", "--database", "test"],
            "Running migrations for Tethys database...",
            **kwargs,
        )

    @mock.patch("tethys_cli.db_commands.write_info")
    @mock.patch("tethys_cli.db_commands.write_error")
    @mock.patch("django.contrib.auth.models.User.objects.create_superuser")
    @mock.patch("tethys_cli.db_commands.setup_django")
    def test_db_command_createsuperuser(
        self, mock_setup_django, mock_create_superuser, mock_write_error, _
    ):
        from django.db.utils import IntegrityError

        mock_args = mock.MagicMock()
        mock_args.command = "createsuperuser"
        mock_create_superuser.side_effect = IntegrityError
        db_command(mock_args)
        mock_setup_django.assert_called()
        mock_create_superuser.assert_called_with("PFoo", "PEmail", "PBar")
        portal_superuser = self.options["portal_superuser_name"]
        mock_write_error.assert_called_with(
            f'Tethys Portal Superuser "{portal_superuser}" already exists.'
        )

    @mock.patch("tethys_cli.db_commands.create_portal_superuser")
    @mock.patch("tethys_cli.db_commands.migrate_tethys_db")
    @mock.patch("tethys_cli.db_commands.Path")
    def test_db_command_configure_sqlite(
        self, mock_Path, mock_migrate, mock_createsuperuser
    ):
        mock_args = mock.MagicMock()
        mock_args.command = "configure"
        self.mock_process_args.return_value["db_engine"] = "sqlite"
        db_command(mock_args)
        kwargs = self._get_kwargs()
        mock_Path.assert_called_with(kwargs["db_name"])
        mock_migrate.assert_called_with(**self.options)
        mock_createsuperuser.assert_called_with(**self.options)

    @mock.patch("tethys_cli.db_commands.create_portal_superuser")
    @mock.patch("tethys_cli.db_commands.migrate_tethys_db")
    @mock.patch("tethys_cli.db_commands._prompt_if_error")
    def test_db_command_configure_postgres(
        self, mock_prompt_err, mock_migrate, mock_createsuperuser
    ):
        mock_args = mock.MagicMock()
        mock_args.command = "configure"
        db_command(mock_args)
        kwargs = self._get_kwargs()
        creation_kwargs = kwargs | {"exit_creation_on_error": False}
        calls = [
            mock.call(init_db_server, **kwargs),
            mock.call(start_db_server, **kwargs),
            mock.call(create_tethys_db, **creation_kwargs),
        ]
        mock_prompt_err.assert_has_calls(calls)
        mock_migrate.assert_called_with(**self.options)
        mock_createsuperuser.assert_called_with(**self.options)

    @mock.patch("tethys_cli.db_commands.write_info")
    @mock.patch("tethys_apps.harvester.SingletonHarvester")
    def test_db_command_sync(self, MockSingletonHarvester, _):
        # mock the input args
        args = mock.MagicMock(manage="", command="sync", port="8080")

        # call the testing method with the mock args
        db_command(args)

        # mock the singleton harvester
        MockSingletonHarvester.assert_called()
        MockSingletonHarvester().harvest.assert_called()

    def test__prompt_if_error(self):
        mock_fn = mock.MagicMock()
        _prompt_if_error(mock_fn, **self.options)
        mock_fn.assert_called_with(exit_on_error=False, **self.options)

    @mock.patch("tethys_cli.db_commands.input")
    def test__prompt_if_error_continue_yes(self, mock_input):
        mock_fn = mock.MagicMock(__name__="mock_fn")
        mock_input.side_effect = "yes"
        kwargs = self._get_kwargs()
        kwargs.update(no_confirmation=False)
        _prompt_if_error(mock_fn, **kwargs)
        mock_fn.assert_called_with(exit_on_error=False, **kwargs)

    @mock.patch("tethys_cli.db_commands.input")
    def test__prompt_if_error_continue_no(self, mock_input):
        mock_fn = mock.MagicMock(__name__="mock_fn")
        mock_input.side_effect = "no"
        kwargs = self._get_kwargs()
        kwargs.update(no_confirmation=False)
        self.assertRaises(SystemExit, _prompt_if_error, mock_fn, **kwargs)
        mock_fn.assert_called_with(exit_on_error=False, **kwargs)

    @mock.patch("tethys_cli.db_commands.shutil.rmtree")
    @mock.patch("tethys_cli.db_commands.write_error")
    @mock.patch("tethys_cli.db_commands.stop_db_server")
    def test_purge_db_server(self, mock_stop, mock_write_error, mock_rmtree):
        mock_args = mock.MagicMock()
        mock_args.command = "purge"

        kwargs = self._get_kwargs()
        kwargs.update(exit_on_error=False)

        db_command(mock_args)
        mock_stop.assert_called_with(**kwargs)
        mock_write_error.assert_called_once()
        mock_rmtree.assert_called_with(kwargs["db_dir"])

    @mock.patch("tethys_cli.db_commands.Path")
    @mock.patch("tethys_cli.db_commands.write_error")
    def test_purge_db_server_sqlite(self, mock_write_error, mock_path):
        mock_args = mock.MagicMock()
        mock_args.command = "purge"
        self.options["db_dir"] = None
        self.options["db_engine"] = "sqlite3"

        db_command(mock_args)
        mock_write_error.assert_called_once()
        mock_path().unlink.assert_called_once()

    @mock.patch("tethys_cli.db_commands.write_error")
    def test_purge_db_server_invalid(self, mock_write_error):
        mock_args = mock.MagicMock()
        mock_args.command = "purge"
        self.options["db_dir"] = None
        self.options["db_engine"] = ""

        db_command(mock_args)
        mock_write_error.assert_called_once()

    @mock.patch("tethys_cli.db_commands.input")
    @mock.patch("tethys_cli.db_commands.shutil.rmtree")
    @mock.patch("tethys_cli.db_commands.write_error")
    @mock.patch("tethys_cli.db_commands.stop_db_server")
    def test_purge_db_server_continue_yes(
        self, mock_stop, mock_write_error, mock_rmtree, mock_input
    ):
        kwargs = self._get_kwargs()
        kwargs.update(exit_on_error=False, no_confirmation=False)
        mock_input.side_effect = "yes"
        purge_db_server(**kwargs)
        mock_stop.assert_called_with(**kwargs)
        mock_write_error.assert_called_once()
        mock_rmtree.assert_called_with(kwargs["db_dir"])

    @mock.patch("tethys_cli.db_commands.input")
    @mock.patch("tethys_cli.db_commands.shutil.rmtree")
    @mock.patch("tethys_cli.db_commands.write_error")
    @mock.patch("tethys_cli.db_commands.stop_db_server")
    def test_purge_db_server_continue_no(
        self, mock_stop, mock_write_error, mock_rmtree, mock_input
    ):
        kwargs = self._get_kwargs()
        kwargs.update(exit_on_error=False, no_confirmation=False)
        mock_input.side_effect = "no"
        purge_db_server(**kwargs)
        mock_stop.assert_called_with(**kwargs)
        mock_write_error.assert_called_once()
        mock_rmtree.assert_not_called()
