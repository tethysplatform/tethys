import unittest
from unittest import mock

import tethys_cli.version_command as vc


class VersionCommandTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_add_version_parser(self):
        mock_subparsers = mock.MagicMock()

        vc.add_version_parser(mock_subparsers)

        mock_subparsers.add_parser.assert_called_with(
            "version", help="Print the version of tethys_platform"
        )
        mock_subparsers.add_parser().set_defaults.assert_called_with(
            func=vc.version_command
        )

    @mock.patch("tethys_cli.version_command.print")
    def test_version_command(self, mock_print):
        from tethys_portal import __version__

        mock_args = mock.MagicMock()
        vc.version_command(mock_args)
        mock_print.assert_called_with(__version__)
