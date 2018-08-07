import unittest
import mock
from tethys_apps.cli.cli_colors import pretty_output, FG_RED, FG_BLUE, BOLD, FG_GREEN, BG_GREEN, END, ALL_OFF
from StringIO import StringIO


class TestCliColors(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_pretty_output_fg_red(self, mock_print):
        act_msg = 'This is a test in RED'
        expected_string = '\x1b[31mThis is a test in RED\x1b[0m\n'
        with pretty_output(FG_RED) as p:
            p.write(act_msg)
        print_value = mock_print.getvalue()
        self.assertEqual(expected_string, print_value)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_pretty_output_fg_blue(self, mock_print):
        act_msg = 'This is a test in BLUE'
        expected_string = '\x1b[34mThis is a test in BLUE\x1b[0m\n'
        with pretty_output(FG_BLUE) as p:
            p.write(act_msg)
        print_value = mock_print.getvalue()
        self.assertEqual(expected_string, print_value)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_pretty_output_bold_fg_green(self, mock_print):
        act_msg = 'This is a bold text in green'
        expected_string = '\x1b[1m\x1b[32mThis is a bold text in green\x1b[0m\n'
        with pretty_output(BOLD, FG_GREEN) as p:
            p.write(act_msg)
        print_value = mock_print.getvalue()
        self.assertEqual(expected_string, print_value)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_pretty_output_bold_bg_green(self, mock_print):
        act_msg = 'This is a text with green background'
        expected_string = '\x1b[1m\x1b[42mThis is a text with green background\x1b[0m\n'
        with pretty_output(BOLD, BG_GREEN) as p:
            p.write(act_msg)
        print_value = mock_print.getvalue()
        self.assertEqual(expected_string, print_value)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_pretty_output_fg_green(self, mock_print):
        act_msg = 'This is a green text with ' + BOLD + 'bold' + END + ' text included'
        expected_string = '\x1b[32mThis is a green text with \x1b[1mbold\x1b[0m\x1b[32m text included\x1b[0m\n'
        with pretty_output(FG_GREEN) as p:
            p.write(act_msg)
        print_value = mock_print.getvalue()
        self.assertEqual(expected_string, print_value)

    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_pretty_output_empty_msg(self, mock_print):
        in_msg = BOLD + 'Use this' + END + ' even with ' + BOLD + FG_RED + 'no parameters' + \
                 END + ' in the with statement'
        exp_str = '\x1b[1mUse this\x1b[0m even with \x1b[1m\x1b[31mno parameters\x1b[0m in the with statement\x1b[0m\n'
        with pretty_output() as p:
            p.write(in_msg)
        print_value = mock_print.getvalue()
        self.assertIn(ALL_OFF, print_value)
        self.assertEqual(exp_str, print_value)
