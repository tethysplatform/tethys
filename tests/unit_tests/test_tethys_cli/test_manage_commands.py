import sys
import unittest
from unittest import mock

from django.test.utils import override_settings

from tethys_utils import DOCS_BASE_URL

import pytest

import tethys_cli.manage_commands as manage_commands
from tethys_cli.manage_commands import (
    MANAGE_START,
    MANAGE_COLLECTSTATIC,
    MANAGE_COLLECTWORKSPACES,
    MANAGE_COLLECT,
    MANAGE_GET_PATH,
)


class TestManageCommands(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch("tethys_cli.manage_commands.run_process")
    def test_manage_command_manage_start(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage="", command=MANAGE_START, port="8080")

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # check the values from the argument list
        self.assertEqual(sys.executable, process_call_args[0][0][0][0])
        self.assertIn("manage.py", process_call_args[0][0][0][1])
        self.assertEqual("runserver", process_call_args[0][0][0][2])
        self.assertEqual("8080", process_call_args[0][0][0][3])

    @mock.patch("tethys_cli.manage_commands.run_process")
    def test_manage_command_manage_start_with_no_port(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage="", command=MANAGE_START, port="")

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # check the values from the argument list
        self.assertEqual(sys.executable, process_call_args[0][0][0][0])
        self.assertIn("manage.py", process_call_args[0][0][0][1])
        self.assertEqual("runserver", process_call_args[0][0][0][2])

    @mock.patch("tethys_cli.manage_commands.run_process")
    def test_manage_command_manage_manage_collectstatic(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(
            manage="", command=MANAGE_COLLECTSTATIC, port="8080", noinput=False
        )

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # intermediate process
        self.assertEqual(sys.executable, process_call_args[0][0][0][0])
        self.assertIn("manage.py", process_call_args[0][0][0][1])
        self.assertEqual("pre_collectstatic", process_call_args[0][0][0][2])

        # primary process
        self.assertEqual(sys.executable, process_call_args[1][0][0][0])
        self.assertIn("manage.py", process_call_args[1][0][0][1])
        self.assertEqual("collectstatic", process_call_args[1][0][0][2])
        self.assertIn("--noinput", process_call_args[1][0][0])

    @mock.patch("tethys_cli.manage_commands.run_process")
    def test_manage_command_manage_manage_collectstatic_with_no_input(
        self, mock_run_process
    ):
        # mock the input args
        args = mock.MagicMock(
            manage="", command=MANAGE_COLLECTSTATIC, port="8080", noinput=True
        )

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # intermediate process
        self.assertEqual(sys.executable, process_call_args[0][0][0][0])
        self.assertIn("manage.py", process_call_args[0][0][0][1])
        self.assertEqual("pre_collectstatic", process_call_args[0][0][0][2])

        # primary process
        self.assertEqual(sys.executable, process_call_args[1][0][0][0])
        self.assertIn("manage.py", process_call_args[1][0][0][1])
        self.assertEqual("collectstatic", process_call_args[1][0][0][2])
        self.assertEqual("--noinput", process_call_args[1][0][0][3])

    @mock.patch("tethys_cli.manage_commands.run_process")
    def test_manage_command_manage_manage_collectstatic_with_clear(
        self, mock_run_process
    ):
        # mock the input args
        args = mock.MagicMock(
            manage="", command=MANAGE_COLLECTSTATIC, port="8080", clear=True, link=False
        )

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # intermediate process
        self.assertEqual(sys.executable, process_call_args[0][0][0][0])
        self.assertIn("manage.py", process_call_args[0][0][0][1])
        self.assertEqual("pre_collectstatic", process_call_args[0][0][0][2])
        self.assertEqual("--clear", process_call_args[0][0][0][3])

        # primary process
        self.assertEqual(sys.executable, process_call_args[1][0][0][0])
        self.assertIn("manage.py", process_call_args[1][0][0][1])
        self.assertEqual("collectstatic", process_call_args[1][0][0][2])
        self.assertEqual("--noinput", process_call_args[1][0][0][3])

    @mock.patch("tethys_cli.manage_commands.deprecation_warning")
    @mock.patch("tethys_cli.manage_commands.run_process")
    def test_manage_command_manage_manage_collect_workspace(self, mock_run_process, _):
        # mock the input args
        args = mock.MagicMock(
            manage="", command=MANAGE_COLLECTWORKSPACES, port="8080", force=True
        )

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # check the values from the argument list
        self.assertEqual(sys.executable, process_call_args[0][0][0][0])
        self.assertIn("manage.py", process_call_args[0][0][0][1])
        self.assertEqual("collectworkspaces", process_call_args[0][0][0][2])
        self.assertEqual("--force", process_call_args[0][0][0][3])

    @mock.patch("tethys_cli.manage_commands.deprecation_warning")
    @mock.patch("tethys_cli.manage_commands.run_process")
    def test_manage_command_manage_manage_collect_workspace_with_no_force(
        self, mock_run_process, _
    ):
        # mock the input args
        args = mock.MagicMock(manage="", command=MANAGE_COLLECTWORKSPACES, force=False)

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # check the values from the argument list
        self.assertEqual(sys.executable, process_call_args[0][0][0][0])
        self.assertIn("manage.py", process_call_args[0][0][0][1])
        self.assertEqual("collectworkspaces", process_call_args[0][0][0][2])
        self.assertNotIn("--force", process_call_args[0][0][0])

    @mock.patch("tethys_cli.manage_commands.deprecation_warning")
    @mock.patch("tethys_cli.manage_commands.run_process")
    def test_manage_command_manage_manage_collect(self, mock_run_process, _):
        # mock the input args
        args = mock.MagicMock(
            manage="", command=MANAGE_COLLECT, port="8080", noinput=False
        )

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # pre_collectstatic
        self.assertEqual(sys.executable, process_call_args[0][0][0][0])
        self.assertIn("manage.py", process_call_args[0][0][0][1])
        self.assertEqual("pre_collectstatic", process_call_args[0][0][0][2])

        # collectstatic
        self.assertEqual(sys.executable, process_call_args[1][0][0][0])
        self.assertIn("manage.py", process_call_args[1][0][0][1])
        self.assertEqual("collectstatic", process_call_args[1][0][0][2])
        self.assertIn("--noinput", process_call_args[1][0][0])

        # collectworkspaces
        self.assertEqual(sys.executable, process_call_args[2][0][0][0])
        self.assertIn("manage.py", process_call_args[2][0][0][1])
        self.assertEqual("collectworkspaces", process_call_args[2][0][0][2])

    @mock.patch("tethys_cli.manage_commands.deprecation_warning")
    @mock.patch("tethys_cli.manage_commands.run_process")
    def test_manage_command_manage_manage_collect_no_input(self, mock_run_process, _):
        # mock the input args
        args = mock.MagicMock(
            manage="", command=MANAGE_COLLECT, port="8080", noinput=True
        )

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # pre_collectstatic
        self.assertEqual(sys.executable, process_call_args[0][0][0][0])
        self.assertIn("manage.py", process_call_args[0][0][0][1])
        self.assertEqual("pre_collectstatic", process_call_args[0][0][0][2])

        # collectstatic
        self.assertEqual(sys.executable, process_call_args[1][0][0][0])
        self.assertIn("manage.py", process_call_args[1][0][0][1])
        self.assertEqual("collectstatic", process_call_args[1][0][0][2])
        self.assertEqual("--noinput", process_call_args[1][0][0][3])

        # collectworkspaces
        self.assertEqual(sys.executable, process_call_args[2][0][0][0])
        self.assertIn("manage.py", process_call_args[2][0][0][1])
        self.assertEqual("collectworkspaces", process_call_args[2][0][0][2])

    @mock.patch("tethys_cli.manage_commands.deprecation_warning")
    @mock.patch("tethys_cli.manage_commands.run_process")
    def test_manage_command_manage_manage_collect_clear(self, mock_run_process, _):
        # mock the input args
        args = mock.MagicMock(
            manage="", command=MANAGE_COLLECT, port="8080", clear=True
        )

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # pre_collectstatic
        self.assertEqual(sys.executable, process_call_args[0][0][0][0])
        self.assertIn("manage.py", process_call_args[0][0][0][1])
        self.assertEqual("pre_collectstatic", process_call_args[0][0][0][2])
        self.assertEqual("--clear", process_call_args[0][0][0][3])

        # collectstatic
        self.assertEqual(sys.executable, process_call_args[1][0][0][0])
        self.assertIn("manage.py", process_call_args[1][0][0][1])
        self.assertEqual("collectstatic", process_call_args[1][0][0][2])
        self.assertEqual("--noinput", process_call_args[1][0][0][3])

        # collectworkspaces
        self.assertEqual(sys.executable, process_call_args[2][0][0][0])
        self.assertIn("manage.py", process_call_args[2][0][0][1])
        self.assertEqual("collectworkspaces", process_call_args[2][0][0][2])

    @mock.patch(
        "tethys_cli.manage_commands.get_manage_path", return_value="foo/manage.py"
    )
    @mock.patch("builtins.print")
    def test_manage_command_manage_path(self, mock_print, _):
        # mock the input args
        args = mock.MagicMock(manage="", command=MANAGE_GET_PATH)

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # check print called
        mock_print.assert_called_with("foo/manage.py")

    @mock.patch("tethys_cli.manage_commands.run_process")
    def test_manage_django_commands_help(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage="", command="shell", django_help=True)

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # check the values from the argument list
        self.assertEqual(sys.executable, process_call_args[0][0][0][0])
        self.assertIn("manage.py", process_call_args[0][0][0][1])
        self.assertEqual("shell", process_call_args[0][0][0][2])
        self.assertEqual("--help", process_call_args[0][0][0][3])

    @mock.patch("tethys_cli.manage_commands.run_process")
    def test_manage_django_commands(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage="", command="shell", django_help=False)

        # call the testing method with the mock args
        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # check the values from the argument list
        self.assertEqual(sys.executable, process_call_args[0][0][0][0])
        self.assertIn("manage.py", process_call_args[0][0][0][1])
        self.assertIn("shell", process_call_args[0][0][0][2])

    @mock.patch("tethys_cli.manage_commands.run_process")
    def test_manage_django_commands_with_options(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage="", command="check", django_help=False)
        unknown_args = ["--version"]

        # call the testing method with the mock args
        manage_commands.manage_command(args, unknown_args=unknown_args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # check the values from the argument list
        self.assertEqual(sys.executable, process_call_args[0][0][0][0])
        self.assertIn("manage.py", process_call_args[0][0][0][1])
        self.assertEqual("check", process_call_args[0][0][0][2])
        self.assertEqual(unknown_args[0], process_call_args[0][0][0][3])

    @mock.patch("tethys_cli.manage_commands.write_warning")
    @mock.patch("tethys_cli.manage_commands.sys.exit", side_effect=SystemExit)
    @override_settings(TENANTS_ENABLED=False)
    def test_manage_command_with_tenants_disabled_warning(
        self, mock_exit, mock_write_warning
    ):
        # mock the input arg
        args = mock.MagicMock(manage="", command="create_tenant", django_help=False)

        with pytest.raises(SystemExit):
            manage_commands.manage_command(args)

        mock_write_warning.assert_called_with(
            "Multi-tenancy features are not enabled. To enable multi-tenancy, set 'TENANTS_CONFIG.ENABLED "
            "to true in your portal_config.yml file. "
            "You can use the following command to do so:\n\n"
            "tethys settings --set TENANTS_CONFIG.ENABLED true\n\n"
            "For more information, see the documentation at "
            f"{DOCS_BASE_URL}tethys_portal/multi_tenancy.html"
        )

        mock_exit.assert_called_with(1)

    @mock.patch("tethys_cli.manage_commands.write_warning")
    @mock.patch("tethys_cli.manage_commands.sys.exit", side_effect=SystemExit)
    @override_settings(
        TENANTS_ENABLED=True,
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3"}},
    )
    def test_manage_command_with_incorrect_db_engine_warning(
        self, mock_exit, mock_write_warning
    ):
        # mock the input args
        args = mock.MagicMock(manage="", command="create_tenant", django_help=False)

        with pytest.raises(SystemExit):
            manage_commands.manage_command(args)

        mock_write_warning.assert_called_with(
            "The database engine for the default database must be set to "
            "'django_tenants.postgresql_backend' to use multi-tenancy features.\n"
            "Please update your portal_config.yml file accordingly."
            "You can use the following command to do so:\n\n"
            "tethys settings --set DATABASES.default.ENGINE django_tenants.postgresql_backend\n\n"
            "For more information, see the documentation at "
            f"{DOCS_BASE_URL}tethys_portal/multi_tenancy.html"
        )

        mock_exit.assert_called_with(1)

    @mock.patch("tethys_cli.manage_commands.run_process")
    @override_settings(
        TENANTS_ENABLED=True,
        DATABASES={"default": {"ENGINE": "django_tenants.postgresql_backend"}},
    )
    def test_manage_command_with_tenants(self, mock_run_process):
        # mock the input args
        args = mock.MagicMock(manage="", command="create_tenant", django_help=False)

        manage_commands.manage_command(args)

        # get the call arguments for the run process mock method
        process_call_args = mock_run_process.call_args_list

        # check the values from the argument list
        assert sys.executable == process_call_args[0][0][0][0]
        assert "manage.py" in process_call_args[0][0][0][1]
        assert "create_tenant" == process_call_args[0][0][0][2]
