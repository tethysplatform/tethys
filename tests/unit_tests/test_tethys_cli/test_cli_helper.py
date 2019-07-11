import unittest
from unittest import mock
import tethys_cli.cli_helpers as cli_helper


class TestCliHelper(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_add_geoserver_rest_to_endpoint(self):
        endpoint = "http://localhost:8181/geoserver/rest/"
        ret = cli_helper.add_geoserver_rest_to_endpoint(endpoint)
        self.assertEqual(endpoint, ret)

    @mock.patch('tethys_cli.cli_helpers.pretty_output')
    @mock.patch('tethys_cli.cli_helpers.exit')
    def test_get_manage_path_error(self, mock_exit, mock_pretty_output):
        # mock the system exit
        mock_exit.side_effect = SystemExit

        # mock the input args with manage attribute
        args = mock.MagicMock(manage='foo')

        self.assertRaises(SystemExit, cli_helper.get_manage_path, args=args)

        # check the mock exit value
        mock_exit.assert_called_with(1)
        mock_pretty_output.assert_called()

    def test_get_manage_path(self):
        # mock the input args with manage attribute
        args = mock.MagicMock(manage='')

        # call the method
        ret = cli_helper.get_manage_path(args=args)

        # check whether the response has manage
        self.assertIn('manage.py', ret)

    @mock.patch('tethys_cli.cli_helpers.subprocess.call')
    @mock.patch('tethys_cli.cli_helpers.set_testing_environment')
    def test_run_process(self, mock_te_call, mock_subprocess_call):

        # mock the process
        mock_process = ['test']

        cli_helper.run_process(mock_process)

        self.assertEqual(2, len(mock_te_call.call_args_list))

        mock_subprocess_call.assert_called_with(mock_process)

    @mock.patch('tethys_cli.cli_helpers.subprocess.call')
    @mock.patch('tethys_cli.cli_helpers.set_testing_environment')
    def test_run_process_keyboardinterrupt(self, mock_te_call, mock_subprocess_call):

        # mock the process
        mock_process = ['foo']

        mock_subprocess_call.side_effect = KeyboardInterrupt

        cli_helper.run_process(mock_process)
        mock_subprocess_call.assert_called_with(mock_process)
        mock_te_call.assert_called_once()

    @mock.patch('tethys_cli.cli_helpers.django.setup')
    def test_load_apps(self, mock_django_setup):
        cli_helper.load_apps()
        mock_django_setup.assert_called()
