import unittest
from unittest import mock

from tethys_cli.version_command import version_command


class VersionCommandTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_cli.version_command.print')
    @mock.patch('tethys_cli.version_command.__version__')
    def test_version_command(self, mock_version, mock_print):
        mock_args = mock.MagicMock()

        version_command(mock_args)

        mock_print.assert_called_with(mock_version)
