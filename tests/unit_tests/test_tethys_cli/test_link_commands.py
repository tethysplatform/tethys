import unittest
from unittest import mock
import tethys_cli.link_commands as link_commands


class TestLinkCommands(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch("tethys_cli.link_commands.exit")
    @mock.patch("tethys_cli.link_commands.link_service_to_app_setting")
    @mock.patch("tethys_cli.link_commands.pretty_output")
    def test_link_commands(self, _, mock_link_app_setting, mock_exit):
        args = mock.MagicMock(
            service="persistent_connection:super_conn",
            setting="epanet:database:epanet_2",
        )
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, link_commands.link_command, args)

        mock_link_app_setting.assert_called_with(
            "persistent_connection", "super_conn", "epanet", "database", "epanet_2"
        )
        mock_exit.assert_called_with(0)

    @mock.patch("tethys_cli.link_commands.exit")
    @mock.patch("tethys_cli.link_commands.link_service_to_app_setting")
    @mock.patch("tethys_cli.link_commands.pretty_output")
    def test_link_commands_index_error(
        self, mock_pretty_output, mock_link_app_setting, mock_exit
    ):
        args = mock.MagicMock(service="con1", setting="db:database")
        # NOTE: We have the mocked exit function raise a SystemExit exception to break the code
        # execution like the original exit function would have done.
        mock_exit.side_effect = SystemExit

        try:
            self.assertRaises(IndexError, link_commands.link_command, args)
        except SystemExit:
            pass

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn("Incorrect argument format", po_call_args[0][0][0])
        mock_link_app_setting.assert_not_called()
        mock_exit.assert_called_with(1)

    @mock.patch("tethys_cli.link_commands.exit")
    @mock.patch("tethys_cli.link_commands.link_service_to_app_setting")
    @mock.patch("tethys_cli.link_commands.pretty_output")
    def test_link_commands_with_exception(
        self, mock_pretty_output, mock_link_app_setting, mock_exit
    ):
        # NOTE: We have the mocked exit function raise a SystemExit exception to break the code
        # execution like the original exit function would have done.
        mock_link_app_setting = mock.MagicMock()
        mock_link_app_setting.return_value = None
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, link_commands.link_command, None)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertIn(
            "An unexpected error occurred. Please try again.", po_call_args[1][0][0]
        )
        mock_exit.assert_called_with(1)

    @mock.patch("tethys_cli.link_commands.exit")
    @mock.patch(
        "tethys_cli.link_commands.link_service_to_app_setting", return_value=False
    )
    @mock.patch("tethys_cli.link_commands.pretty_output")
    def test_link_commands_with_no_success(self, _, mock_link_app_setting, mock_exit):
        # NOTE: We have the mocked exit function raise a SystemExit exception to break the code
        # execution like the original exit function would have done.
        args = mock.MagicMock(
            service="persistent_connection:super_conn",
            setting="epanet:database:epanet_2",
        )
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, link_commands.link_command, args)

        mock_link_app_setting.assert_called_with(
            "persistent_connection", "super_conn", "epanet", "database", "epanet_2"
        )
        mock_exit.assert_called_with(1)
