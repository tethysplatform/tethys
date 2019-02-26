import unittest
from unittest import mock
import os
import sys

from tethys_apps.cli.scaffold_commands import proper_name_validator, get_random_color, theme_color_validator, \
    render_path, scaffold_command

if sys.version_info[0] < 3:
    callable_mock_path = '__builtin__.callable'
else:
    callable_mock_path = 'builtins.callable'


class TestScaffoldCommands(unittest.TestCase):

    def setUp(self):
        self.app_prefix = 'tethysapp'
        self.extensions_prefix = 'tethysext'
        self.scaffold_templates_dir = 'scaffold_templates'
        self.extension_template_dir = 'extension_templates'
        self.app_template_dir = 'app_templates'
        self.template_suffix = '_tmpl'
        self.app_path = os.path.join(os.path.dirname(__file__), self.scaffold_templates_dir, self.app_template_dir)
        self.extension_path = os.path.join(os.path.dirname(__file__), self.scaffold_templates_dir,
                                           self.extension_template_dir)

    def tearDown(self):
        pass

    def test_proper_name_validator(self):
        expected_value = 'foo'
        expected_default = 'bar'
        ret = proper_name_validator(expected_value, expected_default)
        self.assertTrue(ret[0])
        self.assertEquals('foo', ret[1])

    def test_proper_name_validator_value_as_default(self):
        expected_value = 'bar'
        expected_default = 'bar'
        ret = proper_name_validator(expected_value, expected_default)
        self.assertTrue(ret[0])
        self.assertEquals('bar', ret[1])

    @mock.patch('tethys_apps.cli.scaffold_commands.pretty_output')
    def test_proper_name_validator_warning(self,  mock_pretty_output):
        expected_value = 'foo_'
        expected_default = 'bar'
        ret = proper_name_validator(expected_value, expected_default)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEquals('Warning: Illegal characters were detected in proper name "foo_". '
                          'They have been replaced or removed with valid characters: "foo "', po_call_args[0][0][0])
        self.assertTrue(ret[0])
        self.assertEquals('foo ', ret[1])

    @mock.patch('tethys_apps.cli.scaffold_commands.pretty_output')
    def test_proper_name_validator_error(self, mock_pretty_output):
        expected_value = '@@'
        expected_default = 'bar'
        ret = proper_name_validator(expected_value, expected_default)
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEquals('Error: Proper name can only contain letters and numbers and spaces.', po_call_args[0][0][0])
        self.assertFalse(ret[0])
        self.assertEquals('@@', ret[1])

    @mock.patch('tethys_apps.cli.scaffold_commands.random.choice')
    def test_get_random_color(self, mock_choice):
        mock_choice.return_value = '#16a085'
        ret = get_random_color()
        self.assertEquals(mock_choice.return_value, ret)

    @mock.patch('tethys_apps.cli.scaffold_commands.get_random_color')
    def test_theme_color_validator_same_default_value(self, mock_random_color):
        expected_value = 'foo'
        expected_default = 'foo'
        mock_random_color.return_value = '#16a085'
        ret = theme_color_validator(expected_value, expected_default)
        self.assertTrue(ret[0])
        self.assertEquals('#16a085', ret[1])

    def test_theme_color_validator(self):
        expected_value = '#8e44ad'
        expected_default = '#16a085'
        ret = theme_color_validator(expected_value, expected_default)
        self.assertTrue(ret[0])
        self.assertEquals('#8e44ad', ret[1])

    @mock.patch('tethys_apps.cli.scaffold_commands.pretty_output')
    def test_theme_color_validator_exception(self, mock_pretty_output):
        expected_value = 'foo'
        expected_default = 'bar'
        ret = theme_color_validator(expected_value, expected_default)
        mock_pretty_output.assert_called()
        self.assertFalse(ret[0])
        self.assertEquals('foo', ret[1])

    def test_render_path_with_plus(self):
        expected_path = '+ite1+'
        expected_context = {'ite1': 'foo'}
        ret = render_path(expected_path, expected_context)
        self.assertEquals('foo', ret)

    def test_render_path(self):
        expected_path = 'variable'
        mock_context = mock.MagicMock()
        ret = render_path(expected_path, mock_context)
        self.assertEquals('variable', ret)

    @mock.patch('tethys_apps.cli.scaffold_commands.logging.getLogger')
    @mock.patch(callable_mock_path)
    @mock.patch('tethys_apps.cli.scaffold_commands.get_random_color')
    @mock.patch('tethys_apps.cli.scaffold_commands.pretty_output')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.path.isdir')
    @mock.patch('tethys_apps.cli.scaffold_commands.shutil.rmtree')
    @mock.patch('tethys_apps.cli.scaffold_commands.Context')
    @mock.patch('tethys_apps.cli.scaffold_commands.render_path')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.walk')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.makedirs')
    @mock.patch('tethys_apps.cli.scaffold_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_apps.cli.scaffold_commands.Template')
    def test_scaffold_command(self, _, __, mock_makedirs, mock_os_walk, mock_render_path, mock_context, mock_rmt,
                              mock_os_path_isdir, mock_pretty_output, mock_random_color, mock_callable, mock_logger):

        # mock the input args
        mock_args = mock.MagicMock()

        mock_args.extension = '.ext'
        mock_args.template = 'template_name'
        mock_args.name = 'project_name'
        mock_args.use_defaults = True
        mock_args.overwrite = True

        # mock the log
        mock_log = mock.MagicMock()

        # mock the getlogger from logging
        mock_logger.return_value = mock_log

        # mocking the validate template call return value
        mock_os_path_isdir.return_value = [True, True]

        mock_callable.return_value = True

        mock_template_context = mock.MagicMock()

        mock_context.return_value = mock_template_context

        mock_render_path.return_value = ''

        mock_os_walk.return_value = [
            ('/foo', ('bar',), ('baz',)),
            ('/foo/bar', (), ('spam', 'eggs')),
        ]

        mock_makedirs.return_value = True

        scaffold_command(args=mock_args)

        mock_pretty_output.assert_called()

        mock_random_color.assert_called()

        # check shutil.rmtree call
        mock_rmt.assert_called()

        mock_render_path.assert_called()

        mock_makedirs.assert_called_with(mock_render_path.return_value)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list

        self.assertEquals('Creating new Tethys project named "tethysext-project_name".', po_call_args[0][0][0])
        self.assertIn('Created:', po_call_args[1][0][0])
        self.assertIn('Created:', po_call_args[2][0][0])
        self.assertIn('Created:', po_call_args[3][0][0])
        self.assertIn('Created:', po_call_args[4][0][0])
        self.assertIn('Created:', po_call_args[5][0][0])
        self.assertEquals('Successfully scaffolded new project "project_name"', po_call_args[6][0][0])

        mock_log_call_args = mock_log.debug.call_args_list
        self.assertIn('Command args', mock_log_call_args[0][0][0])
        self.assertIn('APP_PATH', mock_log_call_args[1][0][0])
        self.assertIn('EXTENSION_PATH', mock_log_call_args[2][0][0])
        self.assertIn('Template root directory', mock_log_call_args[3][0][0])
        self.assertIn('Template context', mock_log_call_args[4][0][0])
        self.assertIn('Project root path', mock_log_call_args[5][0][0])
        self.assertEquals('Loading template: "/foo/baz"', mock_log_call_args[6][0][0])
        self.assertEquals('Rendering template: "/foo/baz"', mock_log_call_args[7][0][0])
        self.assertEquals('Loading template: "/foo/bar/spam"', mock_log_call_args[8][0][0])
        self.assertEquals('Rendering template: "/foo/bar/spam"', mock_log_call_args[9][0][0])
        self.assertEquals('Loading template: "/foo/bar/eggs"', mock_log_call_args[10][0][0])
        self.assertEquals('Rendering template: "/foo/bar/eggs"', mock_log_call_args[11][0][0])

    @mock.patch('tethys_apps.cli.scaffold_commands.exit')
    @mock.patch('tethys_apps.cli.scaffold_commands.logging.getLogger')
    @mock.patch('tethys_apps.cli.scaffold_commands.pretty_output')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.path.isdir')
    def test_scaffold_command_with_not_valid_template(self, mock_os_path_isdir, mock_pretty_output, mock_logger,
                                                      mock_exit):
        # mock the input args
        mock_args = mock.MagicMock()

        mock_args.extension = '.ext'
        mock_args.template = 'template_name'
        mock_args.name = '@@'
        mock_args.use_defaults = True
        mock_args.overwrite = True

        # mock the log
        mock_log = mock.MagicMock()

        # mock the getlogger from logging
        mock_logger.return_value = mock_log

        mock_os_path_isdir.return_value = False

        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, scaffold_command, args=mock_args)

        mock_pretty_output.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list

        self.assertEquals('Error: "template_name" is not a valid template.',
                          po_call_args[0][0][0])

        mock_log_call_args = mock_log.debug.call_args_list
        self.assertIn('Command args', mock_log_call_args[0][0][0])
        self.assertIn('APP_PATH', mock_log_call_args[1][0][0])
        self.assertIn('EXTENSION_PATH', mock_log_call_args[2][0][0])
        self.assertIn('Template root directory', mock_log_call_args[3][0][0])

    @mock.patch('tethys_apps.cli.scaffold_commands.logging.getLogger')
    @mock.patch(callable_mock_path)
    @mock.patch('tethys_apps.cli.scaffold_commands.get_random_color')
    @mock.patch('tethys_apps.cli.scaffold_commands.pretty_output')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.path.isdir')
    @mock.patch('tethys_apps.cli.scaffold_commands.shutil.rmtree')
    @mock.patch('tethys_apps.cli.scaffold_commands.Context')
    @mock.patch('tethys_apps.cli.scaffold_commands.render_path')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.walk')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.makedirs')
    @mock.patch('tethys_apps.cli.scaffold_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_apps.cli.scaffold_commands.Template')
    def test_scaffold_command_with_no_extension(self, _, __, mock_makedirs, mock_os_walk, mock_render_path,
                                                mock_context, mock_rmt,
                                                mock_os_path_isdir, mock_pretty_output, mock_random_color,
                                                mock_callable, mock_logger):
        # mock the input args
        mock_args = mock.MagicMock()

        mock_args.extension = None
        mock_args.template = 'template_name'
        mock_args.name = 'project_name'
        mock_args.use_defaults = True
        mock_args.overwrite = True

        # mock the log
        mock_log = mock.MagicMock()

        # mock the getlogger from logging
        mock_logger.return_value = mock_log

        mock_os_path_isdir.return_value = [True, True]

        mock_callable.return_value = True

        mock_template_context = mock.MagicMock()

        mock_context.return_value = mock_template_context

        mock_render_path.return_value = ''

        mock_os_walk.return_value = [
            ('/foo', ('bar',), ('baz',)),
            ('/foo/bar', (), ('spam', 'eggs')),
        ]

        mock_makedirs.return_value = True

        scaffold_command(args=mock_args)

        mock_pretty_output.assert_called()

        mock_random_color.assert_called()

        # check shutil.rmtree call
        mock_rmt.assert_called()

        mock_render_path.assert_called()

        mock_makedirs.assert_called_with(mock_render_path.return_value)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list

        self.assertEquals('Creating new Tethys project named "tethysapp-project_name".', po_call_args[0][0][0])
        self.assertIn('Created:', po_call_args[1][0][0])
        self.assertIn('Created:', po_call_args[2][0][0])
        self.assertIn('Created:', po_call_args[3][0][0])
        self.assertIn('Created:', po_call_args[4][0][0])
        self.assertIn('Created:', po_call_args[5][0][0])
        self.assertEquals('Successfully scaffolded new project "project_name"', po_call_args[6][0][0])

        mock_log_call_args = mock_log.debug.call_args_list
        self.assertIn('Command args', mock_log_call_args[0][0][0])
        self.assertIn('APP_PATH', mock_log_call_args[1][0][0])
        self.assertIn('EXTENSION_PATH', mock_log_call_args[2][0][0])
        self.assertIn('Template root directory', mock_log_call_args[3][0][0])
        self.assertIn('Template context', mock_log_call_args[4][0][0])
        self.assertIn('Project root path', mock_log_call_args[5][0][0])
        self.assertEquals('Loading template: "/foo/baz"', mock_log_call_args[6][0][0])
        self.assertEquals('Rendering template: "/foo/baz"', mock_log_call_args[7][0][0])
        self.assertEquals('Loading template: "/foo/bar/spam"', mock_log_call_args[8][0][0])
        self.assertEquals('Rendering template: "/foo/bar/spam"', mock_log_call_args[9][0][0])
        self.assertEquals('Loading template: "/foo/bar/eggs"', mock_log_call_args[10][0][0])
        self.assertEquals('Rendering template: "/foo/bar/eggs"', mock_log_call_args[11][0][0])

    @mock.patch('tethys_apps.cli.scaffold_commands.logging.getLogger')
    @mock.patch(callable_mock_path)
    @mock.patch('tethys_apps.cli.scaffold_commands.get_random_color')
    @mock.patch('tethys_apps.cli.scaffold_commands.pretty_output')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.path.isdir')
    @mock.patch('tethys_apps.cli.scaffold_commands.shutil.rmtree')
    @mock.patch('tethys_apps.cli.scaffold_commands.Context')
    @mock.patch('tethys_apps.cli.scaffold_commands.render_path')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.walk')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.makedirs')
    @mock.patch('tethys_apps.cli.scaffold_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_apps.cli.scaffold_commands.Template')
    def test_scaffold_command_with_uppercase_project_name(self, _, __, mock_makedirs, mock_os_walk, mock_render_path,
                                                          mock_context, mock_rmt,
                                                          mock_os_path_isdir, mock_pretty_output, mock_random_color,
                                                          mock_callable, mock_logger):
        # mock the input args
        mock_args = mock.MagicMock()

        mock_args.extension = '.ext'
        mock_args.template = 'template_name'
        mock_args.name = 'PROJECT_NAME'
        mock_args.use_defaults = True
        mock_args.overwrite = True

        # mock the log
        mock_log = mock.MagicMock()

        # mock the getlogger from logging
        mock_logger.return_value = mock_log

        # mocking the validate template call return value
        mock_os_path_isdir.return_value = [True, True]

        mock_callable.return_value = True

        mock_template_context = mock.MagicMock()

        mock_context.return_value = mock_template_context

        mock_render_path.return_value = ''

        mock_os_walk.return_value = [
            ('/foo', ('bar',), ('baz',)),
            ('/foo/bar', (), ('spam', 'eggs')),
        ]

        mock_makedirs.return_value = True

        scaffold_command(args=mock_args)

        mock_pretty_output.assert_called()

        mock_random_color.assert_called()

        # check shutil.rmtree call
        mock_rmt.assert_called()

        mock_render_path.assert_called()

        mock_makedirs.assert_called_with(mock_render_path.return_value)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list

        self.assertEquals('Warning: Uppercase characters in project name "PROJECT_NAME" changed to '
                          'lowercase: "project_name".', po_call_args[0][0][0])
        self.assertEquals('Creating new Tethys project named "tethysext-project_name".', po_call_args[1][0][0])
        self.assertIn('Created:', po_call_args[2][0][0])
        self.assertIn('Created:', po_call_args[3][0][0])
        self.assertIn('Created:', po_call_args[4][0][0])
        self.assertIn('Created:', po_call_args[5][0][0])
        self.assertIn('Created:', po_call_args[6][0][0])
        self.assertEquals('Successfully scaffolded new project "project_name"', po_call_args[7][0][0])

        mock_log_call_args = mock_log.debug.call_args_list
        self.assertIn('Command args', mock_log_call_args[0][0][0])
        self.assertIn('APP_PATH', mock_log_call_args[1][0][0])
        self.assertIn('EXTENSION_PATH', mock_log_call_args[2][0][0])
        self.assertIn('Template root directory', mock_log_call_args[3][0][0])
        self.assertIn('Template context', mock_log_call_args[4][0][0])
        self.assertIn('Project root path', mock_log_call_args[5][0][0])
        self.assertEquals('Loading template: "/foo/baz"', mock_log_call_args[6][0][0])
        self.assertEquals('Rendering template: "/foo/baz"', mock_log_call_args[7][0][0])
        self.assertEquals('Loading template: "/foo/bar/spam"', mock_log_call_args[8][0][0])
        self.assertEquals('Rendering template: "/foo/bar/spam"', mock_log_call_args[9][0][0])
        self.assertEquals('Loading template: "/foo/bar/eggs"', mock_log_call_args[10][0][0])
        self.assertEquals('Rendering template: "/foo/bar/eggs"', mock_log_call_args[11][0][0])

    @mock.patch('tethys_apps.cli.scaffold_commands.exit')
    @mock.patch('tethys_apps.cli.scaffold_commands.logging.getLogger')
    @mock.patch('tethys_apps.cli.scaffold_commands.pretty_output')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.path.isdir')
    def test_scaffold_command_with_wrong_project_name(self, mock_os_path_isdir, mock_pretty_output,  mock_logger,
                                                      mock_exit):
        # mock the input args
        mock_args = mock.MagicMock()

        mock_args.extension = '.ext'
        mock_args.template = 'template_name'
        mock_args.name = '@@'
        mock_args.use_defaults = True
        mock_args.overwrite = True

        # mock the log
        mock_log = mock.MagicMock()

        # mock the getlogger from logging
        mock_logger.return_value = mock_log

        mock_os_path_isdir.return_value = True

        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, scaffold_command, args=mock_args)

        mock_pretty_output.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list

        self.assertEquals('Error: Invalid characters in project name "@@". Only letters, numbers, and underscores.',
                          po_call_args[0][0][0])

        mock_log_call_args = mock_log.debug.call_args_list
        self.assertIn('Command args', mock_log_call_args[0][0][0])
        self.assertIn('APP_PATH', mock_log_call_args[1][0][0])
        self.assertIn('EXTENSION_PATH', mock_log_call_args[2][0][0])

    @mock.patch('tethys_apps.cli.scaffold_commands.logging.getLogger')
    @mock.patch(callable_mock_path)
    @mock.patch('tethys_apps.cli.scaffold_commands.get_random_color')
    @mock.patch('tethys_apps.cli.scaffold_commands.pretty_output')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.path.isdir')
    @mock.patch('tethys_apps.cli.scaffold_commands.shutil.rmtree')
    @mock.patch('tethys_apps.cli.scaffold_commands.Context')
    @mock.patch('tethys_apps.cli.scaffold_commands.render_path')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.walk')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.makedirs')
    @mock.patch('tethys_apps.cli.scaffold_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_apps.cli.scaffold_commands.Template')
    def test_scaffold_command_with_project_warning(self, _, __, mock_makedirs, mock_os_walk, mock_render_path,
                                                   mock_context, mock_rmt,
                                                   mock_os_path_isdir, mock_pretty_output, mock_random_color,
                                                   mock_callable, mock_logger):
        # mock the input args
        mock_args = mock.MagicMock()

        mock_args.extension = '.ext'
        mock_args.template = 'template_name'
        mock_args.name = 'project-name'
        mock_args.use_defaults = True
        mock_args.overwrite = True

        # mock the log
        mock_log = mock.MagicMock()

        # mock the getlogger from logging
        mock_logger.return_value = mock_log

        mock_os_path_isdir.return_value = [True, True]

        mock_callable.return_value = True

        mock_template_context = mock.MagicMock()

        mock_context.return_value = mock_template_context

        mock_render_path.return_value = ''

        mock_os_walk.return_value = [
            ('/foo', ('bar',), ('baz',)),
            ('/foo/bar', (), ('spam', 'eggs')),
        ]

        mock_makedirs.return_value = True

        scaffold_command(args=mock_args)

        mock_pretty_output.assert_called()

        mock_random_color.assert_called()

        # check shutil.rmtree call
        mock_rmt.assert_called()

        mock_render_path.assert_called()

        mock_makedirs.assert_called_with(mock_render_path.return_value)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list

        self.assertEquals('Warning: Dashes in project name "project-name" have been replaced with underscores '
                          '"project_name"', po_call_args[0][0][0])
        self.assertEquals('Creating new Tethys project named "tethysext-project_name".', po_call_args[1][0][0])
        self.assertIn('Created:', po_call_args[2][0][0])
        self.assertIn('Created:', po_call_args[3][0][0])
        self.assertIn('Created:', po_call_args[4][0][0])
        self.assertIn('Created:', po_call_args[5][0][0])
        self.assertIn('Created:', po_call_args[6][0][0])
        self.assertEquals('Successfully scaffolded new project "project_name"', po_call_args[7][0][0])

        mock_log_call_args = mock_log.debug.call_args_list
        self.assertIn('Command args', mock_log_call_args[0][0][0])
        self.assertIn('APP_PATH', mock_log_call_args[1][0][0])
        self.assertIn('EXTENSION_PATH', mock_log_call_args[2][0][0])
        self.assertIn('Template root directory', mock_log_call_args[3][0][0])
        self.assertIn('Template context', mock_log_call_args[4][0][0])
        self.assertIn('Project root path', mock_log_call_args[5][0][0])
        self.assertEquals('Loading template: "/foo/baz"', mock_log_call_args[6][0][0])
        self.assertEquals('Rendering template: "/foo/baz"', mock_log_call_args[7][0][0])
        self.assertEquals('Loading template: "/foo/bar/spam"', mock_log_call_args[8][0][0])
        self.assertEquals('Rendering template: "/foo/bar/spam"', mock_log_call_args[9][0][0])
        self.assertEquals('Loading template: "/foo/bar/eggs"', mock_log_call_args[10][0][0])
        self.assertEquals('Rendering template: "/foo/bar/eggs"', mock_log_call_args[11][0][0])

    @mock.patch('tethys_apps.cli.scaffold_commands.proper_name_validator')
    @mock.patch('tethys_apps.cli.scaffold_commands.input')
    @mock.patch('tethys_apps.cli.scaffold_commands.logging.getLogger')
    @mock.patch(callable_mock_path)
    @mock.patch('tethys_apps.cli.scaffold_commands.get_random_color')
    @mock.patch('tethys_apps.cli.scaffold_commands.pretty_output')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.path.isdir')
    @mock.patch('tethys_apps.cli.scaffold_commands.shutil.rmtree')
    @mock.patch('tethys_apps.cli.scaffold_commands.Context')
    @mock.patch('tethys_apps.cli.scaffold_commands.render_path')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.walk')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.makedirs')
    @mock.patch('tethys_apps.cli.scaffold_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_apps.cli.scaffold_commands.Template')
    def test_scaffold_command_with_no_defaults(self, _, __, mock_makedirs, mock_os_walk, mock_render_path,
                                               mock_context, mock_rmt,
                                               mock_os_path_isdir, mock_pretty_output, mock_random_color,
                                               mock_callable, mock_logger, mock_input, mock_proper_name_validator):
        # mock the input args
        mock_args = mock.MagicMock()

        mock_args.extension = '.ext'
        mock_args.template = 'template_name'
        mock_args.name = 'project-name'
        mock_args.use_defaults = False
        mock_args.overwrite = True

        # mock the log
        mock_log = mock.MagicMock()

        # mock the getlogger from logging
        mock_logger.return_value = mock_log

        mock_os_path_isdir.return_value = [True, True]

        mock_callable.side_effect = [True, False, False, False, False]

        mock_template_context = mock.MagicMock()

        mock_context.return_value = mock_template_context

        mock_render_path.return_value = ''

        mock_os_walk.return_value = [
            ('/foo', ('bar',), ('baz',)),
            ('/foo/bar', (), ('spam', 'eggs')),
        ]

        mock_makedirs.return_value = True

        mock_input.side_effect = ['test1', 'test2', 'test3', 'test4', 'test5']
        mock_proper_name_validator.return_value = True, 'foo'

        scaffold_command(args=mock_args)

        mock_pretty_output.assert_called()

        mock_random_color.assert_called()

        # check shutil.rmtree call
        mock_rmt.assert_called()

        mock_render_path.assert_called()

        # mock the create root directory
        mock_makedirs.assert_called_with(mock_render_path.return_value)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list

        self.assertEquals('Warning: Dashes in project name "project-name" have been replaced with underscores '
                          '"project_name"', po_call_args[0][0][0])
        self.assertEquals('Creating new Tethys project named "tethysext-project_name".', po_call_args[1][0][0])
        self.assertIn('Created:', po_call_args[2][0][0])
        self.assertIn('Created:', po_call_args[3][0][0])
        self.assertIn('Created:', po_call_args[4][0][0])
        self.assertIn('Created:', po_call_args[5][0][0])
        self.assertIn('Created:', po_call_args[6][0][0])
        self.assertEquals('Successfully scaffolded new project "project_name"', po_call_args[7][0][0])

        mock_log_call_args = mock_log.debug.call_args_list
        self.assertIn('Command args', mock_log_call_args[0][0][0])
        self.assertIn('APP_PATH', mock_log_call_args[1][0][0])
        self.assertIn('EXTENSION_PATH', mock_log_call_args[2][0][0])
        self.assertIn('Template root directory', mock_log_call_args[3][0][0])
        self.assertIn('Template context', mock_log_call_args[4][0][0])
        self.assertIn('foo', mock_log_call_args[4][0][0])
        self.assertIn('test2', mock_log_call_args[4][0][0])
        self.assertIn('test3', mock_log_call_args[4][0][0])
        self.assertIn('test4', mock_log_call_args[4][0][0])
        self.assertIn('test5', mock_log_call_args[4][0][0])
        self.assertIn('Project root path', mock_log_call_args[5][0][0])
        self.assertEquals('Loading template: "/foo/baz"', mock_log_call_args[6][0][0])
        self.assertEquals('Rendering template: "/foo/baz"', mock_log_call_args[7][0][0])
        self.assertEquals('Loading template: "/foo/bar/spam"', mock_log_call_args[8][0][0])
        self.assertEquals('Rendering template: "/foo/bar/spam"', mock_log_call_args[9][0][0])
        self.assertEquals('Loading template: "/foo/bar/eggs"', mock_log_call_args[10][0][0])
        self.assertEquals('Rendering template: "/foo/bar/eggs"', mock_log_call_args[11][0][0])

    @mock.patch('tethys_apps.cli.scaffold_commands.proper_name_validator')
    @mock.patch('tethys_apps.cli.scaffold_commands.input')
    @mock.patch('tethys_apps.cli.scaffold_commands.logging.getLogger')
    @mock.patch(callable_mock_path)
    @mock.patch('tethys_apps.cli.scaffold_commands.get_random_color')
    @mock.patch('tethys_apps.cli.scaffold_commands.pretty_output')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.path.isdir')
    @mock.patch('tethys_apps.cli.scaffold_commands.shutil.rmtree')
    @mock.patch('tethys_apps.cli.scaffold_commands.Context')
    @mock.patch('tethys_apps.cli.scaffold_commands.render_path')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.walk')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.makedirs')
    @mock.patch('tethys_apps.cli.scaffold_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_apps.cli.scaffold_commands.Template')
    @mock.patch('tethys_apps.cli.scaffold_commands.exit')
    def test_scaffold_command_with_no_defaults_input_exception(self, mock_exit, _, __, mock_makedirs, mock_os_walk,
                                                               mock_render_path, mock_context, mock_rmt,
                                                               mock_os_path_isdir, mock_pretty_output,
                                                               mock_random_color, mock_callable,
                                                               mock_logger, mock_input, mock_proper_name_validator):
        # mock the input args
        mock_args = mock.MagicMock()

        mock_args.extension = '.ext'
        mock_args.template = 'template_name'
        mock_args.name = 'project-name'
        mock_args.use_defaults = False
        mock_args.overwrite = True

        # mock the log
        mock_log = mock.MagicMock()

        # mock the getlogger from logging
        mock_logger.return_value = mock_log

        # mocking the validate template call return value
        mock_os_path_isdir.return_value = [True, True]

        mock_callable.side_effect = [True, False, False, False, False]

        mock_template_context = mock.MagicMock()

        # testing: walk the template directory, creating the templates and directories in the new project as we go
        mock_context.return_value = mock_template_context

        mock_render_path.return_value = ''

        mock_os_walk.return_value = [
            ('/foo', ('bar',), ('baz',)),
            ('/foo/bar', (), ('spam', 'eggs')),
        ]

        mock_makedirs.return_value = True

        mock_exit.side_effect = SystemExit

        mock_input.side_effect = KeyboardInterrupt

        mock_proper_name_validator.return_value = True, 'foo'

        self.assertRaises(SystemExit, scaffold_command, args=mock_args)

        mock_random_color.assert_called()

        # check shutil.rmtree call
        mock_rmt.assert_not_called()

        mock_render_path.assert_not_called()

        # mock the create root directory
        mock_makedirs.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list

        self.assertEquals('Warning: Dashes in project name "project-name" have been replaced with underscores '
                          '"project_name"', po_call_args[0][0][0])
        self.assertEquals('Creating new Tethys project named "tethysext-project_name".', po_call_args[1][0][0])
        self.assertIn('Scaffolding cancelled.', po_call_args[2][0][0])

        mock_log_call_args = mock_log.debug.call_args_list
        self.assertIn('Command args', mock_log_call_args[0][0][0])
        self.assertIn('APP_PATH', mock_log_call_args[1][0][0])
        self.assertIn('EXTENSION_PATH', mock_log_call_args[2][0][0])
        self.assertIn('Template root directory', mock_log_call_args[3][0][0])

    @mock.patch('tethys_apps.cli.scaffold_commands.proper_name_validator')
    @mock.patch('tethys_apps.cli.scaffold_commands.input')
    @mock.patch('tethys_apps.cli.scaffold_commands.logging.getLogger')
    @mock.patch('tethys_apps.cli.scaffold_commands.callable')
    @mock.patch('tethys_apps.cli.scaffold_commands.get_random_color')
    @mock.patch('tethys_apps.cli.scaffold_commands.pretty_output')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.path.isdir')
    @mock.patch('tethys_apps.cli.scaffold_commands.shutil.rmtree')
    @mock.patch('tethys_apps.cli.scaffold_commands.Context')
    @mock.patch('tethys_apps.cli.scaffold_commands.render_path')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.walk')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.makedirs')
    @mock.patch('tethys_apps.cli.scaffold_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_apps.cli.scaffold_commands.Template')
    def test_scaffold_command_with_no_defaults_invalid_response(self, _, __, mock_makedirs, mock_os_walk,
                                                                mock_render_path,
                                                                mock_context, mock_rmt,
                                                                mock_os_path_isdir, mock_pretty_output,
                                                                mock_random_color,
                                                                mock_callable, mock_logger, mock_input,
                                                                mock_proper_name_validator):
        # mock the input args
        mock_args = mock.MagicMock()

        mock_args.extension = '.ext'
        mock_args.template = 'template_name'
        mock_args.name = 'project-name'
        mock_args.use_defaults = False
        mock_args.overwrite = True

        # mock the log
        mock_log = mock.MagicMock()

        # mock the getlogger from logging
        mock_logger.return_value = mock_log

        # mocking the validate template call return value
        mock_os_path_isdir.return_value = [True, True]

        mock_callable.side_effect = [True, False, False, False, False, False]

        mock_template_context = mock.MagicMock()

        # testing: walk the template directory, creating the templates and directories in the new project as we go
        mock_context.return_value = mock_template_context

        mock_render_path.return_value = ''

        mock_os_walk.return_value = [
            ('/foo', ('bar',), ('baz',)),
            ('/foo/bar', (), ('spam', 'eggs')),
        ]

        mock_makedirs.return_value = True

        mock_input.side_effect = ['test1', 'test1_a', 'test2', 'test3', 'test4', 'test5']
        mock_proper_name_validator.return_value = False, 'foo'

        scaffold_command(args=mock_args)

        mock_pretty_output.assert_called()

        mock_random_color.assert_called()

        # check shutil.rmtree call
        mock_rmt.assert_called()

        mock_render_path.assert_called()

        # mock the create root directory
        mock_makedirs.assert_called_with(mock_render_path.return_value)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list

        self.assertEquals('Warning: Dashes in project name "project-name" have been replaced with underscores '
                          '"project_name"', po_call_args[0][0][0])
        self.assertEquals('Creating new Tethys project named "tethysext-project_name".', po_call_args[1][0][0])
        self.assertIn('Invalid response: foo', po_call_args[2][0][0])
        self.assertIn('Created:', po_call_args[3][0][0])
        self.assertIn('Created:', po_call_args[4][0][0])
        self.assertIn('Created:', po_call_args[5][0][0])
        self.assertIn('Created:', po_call_args[6][0][0])
        self.assertIn('Created:', po_call_args[7][0][0])
        self.assertEquals('Successfully scaffolded new project "project_name"', po_call_args[8][0][0])

        mock_log_call_args = mock_log.debug.call_args_list
        self.assertIn('Command args', mock_log_call_args[0][0][0])
        self.assertIn('APP_PATH', mock_log_call_args[1][0][0])
        self.assertIn('EXTENSION_PATH', mock_log_call_args[2][0][0])
        self.assertIn('Template root directory', mock_log_call_args[3][0][0])
        self.assertIn('Template context', mock_log_call_args[4][0][0])
        self.assertIn('test1_a', mock_log_call_args[4][0][0])
        self.assertIn('test2', mock_log_call_args[4][0][0])
        self.assertIn('test3', mock_log_call_args[4][0][0])
        self.assertIn('test4', mock_log_call_args[4][0][0])
        self.assertIn('test5', mock_log_call_args[4][0][0])
        self.assertIn('Project root path', mock_log_call_args[5][0][0])
        self.assertEquals('Loading template: "/foo/baz"', mock_log_call_args[6][0][0])
        self.assertEquals('Rendering template: "/foo/baz"', mock_log_call_args[7][0][0])
        self.assertEquals('Loading template: "/foo/bar/spam"', mock_log_call_args[8][0][0])
        self.assertEquals('Rendering template: "/foo/bar/spam"', mock_log_call_args[9][0][0])
        self.assertEquals('Loading template: "/foo/bar/eggs"', mock_log_call_args[10][0][0])
        self.assertEquals('Rendering template: "/foo/bar/eggs"', mock_log_call_args[11][0][0])

    @mock.patch('tethys_apps.cli.scaffold_commands.input')
    @mock.patch('tethys_apps.cli.scaffold_commands.logging.getLogger')
    @mock.patch('tethys_apps.cli.scaffold_commands.get_random_color')
    @mock.patch('tethys_apps.cli.scaffold_commands.pretty_output')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.path.isdir')
    @mock.patch('tethys_apps.cli.scaffold_commands.shutil.rmtree')
    @mock.patch('tethys_apps.cli.scaffold_commands.Context')
    @mock.patch('tethys_apps.cli.scaffold_commands.render_path')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.walk')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.makedirs')
    @mock.patch('tethys_apps.cli.scaffold_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_apps.cli.scaffold_commands.Template')
    def test_scaffold_command_with_no_overwrite(self, _, __, mock_makedirs, mock_os_walk, mock_render_path,
                                                mock_context, mock_rmt,
                                                mock_os_path_isdir, mock_pretty_output, mock_random_color,
                                                mock_logger, mock_input):
        # mock the input args
        mock_args = mock.MagicMock()

        mock_args.extension = '.ext'
        mock_args.template = 'template_name'
        mock_args.name = 'project-name'
        mock_args.use_defaults = True
        mock_args.overwrite = False

        # mock the log
        mock_log = mock.MagicMock()

        # mock the getlogger from logging
        mock_logger.return_value = mock_log

        # mocking the validate template call return value
        mock_os_path_isdir.return_value = [True, True]

        mock_template_context = mock.MagicMock()

        # testing: walk the template directory, creating the templates and directories in the new project as we go
        mock_context.return_value = mock_template_context

        mock_render_path.return_value = ''

        mock_os_walk.return_value = [
            ('/foo', ('bar',), ('baz',)),
            ('/foo/bar', (), ('spam', 'eggs')),
        ]

        mock_makedirs.return_value = True

        mock_input.side_effect = ['y']

        scaffold_command(args=mock_args)

        mock_pretty_output.assert_called()

        mock_random_color.assert_called()

        # check shutil.rmtree call
        mock_rmt.assert_called()

        mock_render_path.assert_called()

        # mock the create root directory
        mock_makedirs.assert_called_with(mock_render_path.return_value)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list

        self.assertEquals('Warning: Dashes in project name "project-name" have been replaced with underscores '
                          '"project_name"', po_call_args[0][0][0])
        self.assertEquals('Creating new Tethys project named "tethysext-project_name".', po_call_args[1][0][0])
        self.assertIn('Created:', po_call_args[2][0][0])
        self.assertIn('Created:', po_call_args[3][0][0])
        self.assertIn('Created:', po_call_args[4][0][0])
        self.assertIn('Created:', po_call_args[5][0][0])
        self.assertIn('Created:', po_call_args[6][0][0])
        self.assertEquals('Successfully scaffolded new project "project_name"', po_call_args[7][0][0])

        mock_log_call_args = mock_log.debug.call_args_list
        self.assertIn('Command args', mock_log_call_args[0][0][0])
        self.assertIn('APP_PATH', mock_log_call_args[1][0][0])
        self.assertIn('EXTENSION_PATH', mock_log_call_args[2][0][0])
        self.assertIn('Template root directory', mock_log_call_args[3][0][0])
        self.assertIn('Template context', mock_log_call_args[4][0][0])
        self.assertIn('Project root path', mock_log_call_args[5][0][0])
        self.assertEquals('Loading template: "/foo/baz"', mock_log_call_args[6][0][0])
        self.assertEquals('Rendering template: "/foo/baz"', mock_log_call_args[7][0][0])
        self.assertEquals('Loading template: "/foo/bar/spam"', mock_log_call_args[8][0][0])
        self.assertEquals('Rendering template: "/foo/bar/spam"', mock_log_call_args[9][0][0])
        self.assertEquals('Loading template: "/foo/bar/eggs"', mock_log_call_args[10][0][0])
        self.assertEquals('Rendering template: "/foo/bar/eggs"', mock_log_call_args[11][0][0])

    @mock.patch('tethys_apps.cli.scaffold_commands.exit')
    @mock.patch('tethys_apps.cli.scaffold_commands.input')
    @mock.patch('tethys_apps.cli.scaffold_commands.logging.getLogger')
    @mock.patch('tethys_apps.cli.scaffold_commands.get_random_color')
    @mock.patch('tethys_apps.cli.scaffold_commands.pretty_output')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.path.isdir')
    @mock.patch('tethys_apps.cli.scaffold_commands.shutil.rmtree')
    @mock.patch('tethys_apps.cli.scaffold_commands.Context')
    @mock.patch('tethys_apps.cli.scaffold_commands.render_path')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.walk')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.makedirs')
    @mock.patch('tethys_apps.cli.scaffold_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_apps.cli.scaffold_commands.Template')
    def test_scaffold_command_with_no_overwrite_keyboard_interrupt(self, _, __, mock_makedirs, mock_os_walk,
                                                                   mock_render_path,
                                                                   mock_context, mock_rmt,
                                                                   mock_os_path_isdir, mock_pretty_output,
                                                                   mock_random_color,
                                                                   mock_logger, mock_input, mock_exit):
        # mock the input args
        mock_args = mock.MagicMock()

        mock_args.extension = '.ext'
        mock_args.template = 'template_name'
        mock_args.name = 'project-name'
        mock_args.use_defaults = True
        mock_args.overwrite = False

        # mock the log
        mock_log = mock.MagicMock()

        # mock the getlogger from logging
        mock_logger.return_value = mock_log

        # mocking the validate template call return value
        mock_os_path_isdir.return_value = [True, True]

        mock_template_context = mock.MagicMock()

        # testing: walk the template directory, creating the templates and directories in the new project as we go
        mock_context.return_value = mock_template_context

        mock_render_path.return_value = ''

        mock_os_walk.return_value = [
            ('/foo', ('bar',), ('baz',)),
            ('/foo/bar', (), ('spam', 'eggs')),
        ]

        mock_makedirs.return_value = True

        mock_exit.side_effect = SystemExit

        mock_input.side_effect = KeyboardInterrupt

        self.assertRaises(SystemExit, scaffold_command, args=mock_args)

        mock_pretty_output.assert_called()

        mock_random_color.assert_called()

        # check shutil.rmtree call
        mock_rmt.assert_not_called()

        mock_render_path.assert_not_called()

        # mock the create root directory
        mock_makedirs.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list

        self.assertEquals('Warning: Dashes in project name "project-name" have been replaced with underscores '
                          '"project_name"', po_call_args[0][0][0])
        self.assertEquals('Creating new Tethys project named "tethysext-project_name".', po_call_args[1][0][0])
        self.assertIn('Scaffolding cancelled.', po_call_args[2][0][0])

        mock_log_call_args = mock_log.debug.call_args_list
        self.assertIn('Command args', mock_log_call_args[0][0][0])
        self.assertIn('APP_PATH', mock_log_call_args[1][0][0])
        self.assertIn('EXTENSION_PATH', mock_log_call_args[2][0][0])
        self.assertIn('Template root directory', mock_log_call_args[3][0][0])
        self.assertIn('Template context', mock_log_call_args[4][0][0])
        self.assertIn('Project root path', mock_log_call_args[5][0][0])

    @mock.patch('tethys_apps.cli.scaffold_commands.exit')
    @mock.patch('tethys_apps.cli.scaffold_commands.input')
    @mock.patch('tethys_apps.cli.scaffold_commands.logging.getLogger')
    @mock.patch('tethys_apps.cli.scaffold_commands.get_random_color')
    @mock.patch('tethys_apps.cli.scaffold_commands.pretty_output')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.path.isdir')
    @mock.patch('tethys_apps.cli.scaffold_commands.shutil.rmtree')
    @mock.patch('tethys_apps.cli.scaffold_commands.Context')
    @mock.patch('tethys_apps.cli.scaffold_commands.render_path')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.walk')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.makedirs')
    @mock.patch('tethys_apps.cli.scaffold_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_apps.cli.scaffold_commands.Template')
    def test_scaffold_command_with_no_overwrite_cancel(self, _, __, mock_makedirs, mock_os_walk,
                                                       mock_render_path,
                                                       mock_context, mock_rmt,
                                                       mock_os_path_isdir, mock_pretty_output,
                                                       mock_random_color,
                                                       mock_logger, mock_input, mock_exit):
        # mock the input args
        mock_args = mock.MagicMock()

        mock_args.extension = '.ext'
        mock_args.template = 'template_name'
        mock_args.name = 'project-name'
        mock_args.use_defaults = True
        mock_args.overwrite = False

        # mock the log
        mock_log = mock.MagicMock()

        # mock the getlogger from logging
        mock_logger.return_value = mock_log

        # mocking the validate template call return value
        mock_os_path_isdir.return_value = [True, True]

        mock_template_context = mock.MagicMock()

        # testing: walk the template directory, creating the templates and directories in the new project as we go
        mock_context.return_value = mock_template_context

        mock_render_path.return_value = ''

        mock_os_walk.return_value = [
            ('/foo', ('bar',), ('baz',)),
            ('/foo/bar', (), ('spam', 'eggs')),
        ]

        mock_makedirs.return_value = True

        mock_exit.side_effect = SystemExit

        mock_input.side_effect = ['n']

        self.assertRaises(SystemExit, scaffold_command, args=mock_args)

        mock_pretty_output.assert_called()

        mock_random_color.assert_called()

        # check shutil.rmtree call
        mock_rmt.assert_not_called()

        mock_render_path.assert_not_called()

        # mock the create root directory
        mock_makedirs.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list

        self.assertEquals('Warning: Dashes in project name "project-name" have been replaced with underscores '
                          '"project_name"', po_call_args[0][0][0])
        self.assertEquals('Creating new Tethys project named "tethysext-project_name".', po_call_args[1][0][0])
        self.assertIn('Scaffolding cancelled.', po_call_args[2][0][0])

        mock_log_call_args = mock_log.debug.call_args_list
        self.assertIn('Command args', mock_log_call_args[0][0][0])
        self.assertIn('APP_PATH', mock_log_call_args[1][0][0])
        self.assertIn('EXTENSION_PATH', mock_log_call_args[2][0][0])
        self.assertIn('Template root directory', mock_log_call_args[3][0][0])
        self.assertIn('Template context', mock_log_call_args[4][0][0])
        self.assertIn('Project root path', mock_log_call_args[5][0][0])

    @mock.patch('tethys_apps.cli.scaffold_commands.exit')
    @mock.patch('tethys_apps.cli.scaffold_commands.input')
    @mock.patch('tethys_apps.cli.scaffold_commands.logging.getLogger')
    @mock.patch('tethys_apps.cli.scaffold_commands.get_random_color')
    @mock.patch('tethys_apps.cli.scaffold_commands.pretty_output')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.path.isdir')
    @mock.patch('tethys_apps.cli.scaffold_commands.shutil.rmtree')
    @mock.patch('tethys_apps.cli.scaffold_commands.Context')
    @mock.patch('tethys_apps.cli.scaffold_commands.render_path')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.walk')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.makedirs')
    @mock.patch('tethys_apps.cli.scaffold_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_apps.cli.scaffold_commands.Template')
    def test_scaffold_command_with_no_overwrite_os_error(self, _, __, mock_makedirs, mock_os_walk,
                                                         mock_render_path,
                                                         mock_context, mock_rmt,
                                                         mock_os_path_isdir, mock_pretty_output,
                                                         mock_random_color,
                                                         mock_logger, mock_input, mock_exit):
        # mock the input args
        mock_args = mock.MagicMock()

        mock_args.extension = '.ext'
        mock_args.template = 'template_name'
        mock_args.name = 'project-name'
        mock_args.use_defaults = True
        mock_args.overwrite = False

        # mock the log
        mock_log = mock.MagicMock()

        # mock the getlogger from logging
        mock_logger.return_value = mock_log

        # mocking the validate template call return value
        mock_os_path_isdir.return_value = [True, True]

        mock_template_context = mock.MagicMock()

        # testing: walk the template directory, creating the templates and directories in the new project as we go
        mock_context.return_value = mock_template_context

        mock_render_path.return_value = ''

        mock_os_walk.return_value = [
            ('/foo', ('bar',), ('baz',)),
            ('/foo/bar', (), ('spam', 'eggs')),
        ]

        mock_makedirs.return_value = True

        mock_exit.side_effect = SystemExit

        mock_input.side_effect = ['y']

        mock_rmt.side_effect = OSError

        self.assertRaises(SystemExit, scaffold_command, args=mock_args)

        mock_pretty_output.assert_called()

        mock_random_color.assert_called()

        # check shutil.rmtree call
        mock_rmt.assert_called_once()

        mock_render_path.assert_not_called()

        # mock the create root directory
        mock_makedirs.assert_not_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list

        self.assertEquals('Warning: Dashes in project name "project-name" have been replaced with underscores '
                          '"project_name"', po_call_args[0][0][0])
        self.assertEquals('Creating new Tethys project named "tethysext-project_name".', po_call_args[1][0][0])
        self.assertIn('Error: Unable to overwrite', po_call_args[2][0][0])

        mock_log_call_args = mock_log.debug.call_args_list
        self.assertIn('Command args', mock_log_call_args[0][0][0])
        self.assertIn('APP_PATH', mock_log_call_args[1][0][0])
        self.assertIn('EXTENSION_PATH', mock_log_call_args[2][0][0])
        self.assertIn('Template root directory', mock_log_call_args[3][0][0])
        self.assertIn('Template context', mock_log_call_args[4][0][0])
        self.assertIn('Project root path', mock_log_call_args[5][0][0])

    @mock.patch('tethys_apps.cli.scaffold_commands.logging.getLogger')
    @mock.patch('tethys_apps.cli.scaffold_commands.get_random_color')
    @mock.patch('tethys_apps.cli.scaffold_commands.pretty_output')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.path.isdir')
    @mock.patch('tethys_apps.cli.scaffold_commands.shutil.rmtree')
    @mock.patch('tethys_apps.cli.scaffold_commands.Context')
    @mock.patch('tethys_apps.cli.scaffold_commands.render_path')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.walk')
    @mock.patch('tethys_apps.cli.scaffold_commands.os.makedirs')
    @mock.patch('tethys_apps.cli.scaffold_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_apps.cli.scaffold_commands.Template')
    def test_scaffold_command_with_unicode_decode_error(self, mock_template, _, mock_makedirs, mock_os_walk,
                                                        mock_render_path,
                                                        mock_context, mock_rmt,
                                                        mock_os_path_isdir, mock_pretty_output,
                                                        mock_random_color,
                                                        mock_logger):
        # mock the input args
        mock_args = mock.MagicMock()

        mock_args.extension = '.ext'
        mock_args.template = 'template_name'
        mock_args.name = 'project-name'
        mock_args.use_defaults = True
        mock_args.overwrite = True

        # mock the log
        mock_log = mock.MagicMock()

        # mock the getlogger from logging
        mock_logger.return_value = mock_log

        # mocking the validate template call return value
        mock_os_path_isdir.return_value = [True, True]
        mock_template.side_effect = UnicodeDecodeError('foo', 'bar'.encode(), 1, 2, 'baz')

        mock_template_context = mock.MagicMock()

        # testing: walk the template directory, creating the templates and directories in the new project as we go
        mock_context.return_value = mock_template_context

        mock_render_path.return_value = ''

        mock_os_walk.return_value = [
            ('/foo', ('bar',), ('baz',)),
            ('/foo/bar', (), ('spam', 'eggs')),
        ]

        mock_makedirs.return_value = True

        scaffold_command(args=mock_args)

        mock_pretty_output.assert_called()

        mock_random_color.assert_called()

        # check shutil.rmtree call
        mock_rmt.assert_called_once()

        mock_render_path.assert_called()

        # mock the create root directory
        mock_makedirs.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list

        self.assertEquals('Warning: Dashes in project name "project-name" have been replaced with underscores '
                          '"project_name"', po_call_args[0][0][0])
        self.assertEquals('Creating new Tethys project named "tethysext-project_name".', po_call_args[1][0][0])
        self.assertIn('Created', po_call_args[2][0][0])
        self.assertIn('Created', po_call_args[3][0][0])
        self.assertIn('Successfully scaffolded new project "project_name"', po_call_args[4][0][0])

        mock_log_call_args = mock_log.debug.call_args_list
        self.assertIn('Command args', mock_log_call_args[0][0][0])
        self.assertIn('APP_PATH', mock_log_call_args[1][0][0])
        self.assertIn('EXTENSION_PATH', mock_log_call_args[2][0][0])
        self.assertIn('Template root directory', mock_log_call_args[3][0][0])
        self.assertIn('Template context', mock_log_call_args[4][0][0])
        self.assertIn('Project root path', mock_log_call_args[5][0][0])
