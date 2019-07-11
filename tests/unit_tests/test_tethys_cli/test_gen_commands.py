import unittest
from unittest import mock

from tethys_cli.gen_commands import (
    get_environment_value,
    get_settings_value,
    generate_command,
    GEN_SETTINGS_OPTION,
    GEN_NGINX_OPTION,
    GEN_NGINX_SERVICE_OPTION,
    GEN_ASGI_SERVICE_OPTION,
    GEN_SERVICES_OPTION,
    GEN_INSTALL_OPTION,
    GEN_PORTAL_OPTION,
)


class CLIGenCommandsTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_environment_value(self):
        result = get_environment_value(value_name='DJANGO_SETTINGS_MODULE')

        self.assertEqual('tethys_portal.settings', result)

    def test_get_environment_value_bad(self):
        self.assertRaises(EnvironmentError, get_environment_value,
                          value_name='foo_bar_baz_bad_environment_value_foo_bar_baz')

    def test_get_settings_value(self):
        result = get_settings_value(value_name='INSTALLED_APPS')

        self.assertIn('tethys_apps', result)

    def test_get_settings_value_bad(self):
        self.assertRaises(ValueError, get_settings_value, value_name='foo_bar_baz_bad_setting_foo_bar_baz')

    @mock.patch('tethys_cli.gen_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_cli.gen_commands.os.path.isfile')
    def test_generate_command_settings_option(self, mock_os_path_isfile, mock_file):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_SETTINGS_OPTION
        mock_args.directory = None
        mock_os_path_isfile.return_value = False

        generate_command(args=mock_args)

        mock_os_path_isfile.assert_called_once()
        mock_file.assert_called()

    @mock.patch('tethys_cli.gen_commands.get_settings_value')
    @mock.patch('tethys_cli.gen_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_cli.gen_commands.os.path.isfile')
    def test_generate_command_nginx_option(self, mock_os_path_isfile, mock_file, mock_settings):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_NGINX_OPTION
        mock_args.directory = None
        mock_os_path_isfile.return_value = False
        mock_settings.side_effect = ['/foo/workspace', '/foo/static']

        generate_command(args=mock_args)

        mock_os_path_isfile.assert_called_once()
        mock_file.assert_called()
        mock_settings.assert_any_call('TETHYS_WORKSPACES_ROOT')
        mock_settings.assert_called_with('STATIC_ROOT')

    @mock.patch('tethys_cli.gen_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_cli.gen_commands.os.path.isfile')
    def test_generate_command_nginx_service(self, mock_os_path_isfile, mock_file):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_NGINX_SERVICE_OPTION
        mock_args.directory = None
        mock_os_path_isfile.return_value = False

        generate_command(args=mock_args)

        mock_os_path_isfile.assert_called_once()
        mock_file.assert_called()

    @mock.patch('tethys_cli.gen_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_cli.gen_commands.os.path.isfile')
    def test_generate_command_portal_yaml(self, mock_os_path_isfile, mock_file):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_PORTAL_OPTION
        mock_args.directory = None
        mock_os_path_isfile.return_value = False

        generate_command(args=mock_args)

        mock_os_path_isfile.assert_called_once()
        mock_file.assert_called()

    @mock.patch('tethys_cli.gen_commands.render_template')
    @mock.patch('tethys_cli.gen_commands.linux_distribution')
    @mock.patch('tethys_cli.gen_commands.os.path.exists')
    @mock.patch('tethys_cli.gen_commands.get_environment_value')
    @mock.patch('tethys_cli.gen_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_cli.gen_commands.os.path.isfile')
    def test_generate_command_asgi_service_option_nginx_conf_redhat(self, mock_os_path_isfile, mock_file, mock_env,
                                                                    mock_os_path_exists, mock_linux_distribution,
                                                                    mock_render_template):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_ASGI_SERVICE_OPTION
        mock_args.directory = None
        mock_os_path_isfile.return_value = False
        mock_env.side_effect = ['/foo/conda', 'conda_env']
        mock_os_path_exists.return_value = True
        mock_linux_distribution.return_value = ['redhat']
        mock_file.return_value = mock.mock_open(read_data='user foo_user').return_value

        generate_command(args=mock_args)

        mock_os_path_isfile.assert_called_once()
        mock_file.assert_called()
        mock_env.assert_any_call('CONDA_HOME')
        mock_env.assert_called_with('CONDA_ENV_NAME')
        mock_os_path_exists.assert_called_once_with('/etc/nginx/nginx.conf')
        context = mock_render_template.call_args_list[0][0][1]
        self.assertEqual('http-', context['user_option_prefix'])
        self.assertEqual('foo_user', context['nginx_user'])

    @mock.patch('tethys_cli.gen_commands.render_template')
    @mock.patch('tethys_cli.gen_commands.linux_distribution')
    @mock.patch('tethys_cli.gen_commands.os.path.exists')
    @mock.patch('tethys_cli.gen_commands.get_environment_value')
    @mock.patch('tethys_cli.gen_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_cli.gen_commands.os.path.isfile')
    def test_generate_command_asgi_service_option_nginx_conf_ubuntu(self, mock_os_path_isfile, mock_file, mock_env,
                                                                    mock_os_path_exists, mock_linux_distribution,
                                                                    mock_render_template):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_ASGI_SERVICE_OPTION
        mock_args.directory = None
        mock_os_path_isfile.return_value = False
        mock_env.side_effect = ['/foo/conda', 'conda_env']
        mock_os_path_exists.return_value = True
        mock_linux_distribution.return_value = 'ubuntu'
        mock_file.return_value = mock.mock_open(read_data='user foo_user').return_value

        generate_command(args=mock_args)

        mock_os_path_isfile.assert_called_once()
        mock_file.assert_called()
        mock_env.assert_any_call('CONDA_HOME')
        mock_env.assert_called_with('CONDA_ENV_NAME')
        mock_os_path_exists.assert_called_once_with('/etc/nginx/nginx.conf')
        context = mock_render_template.call_args_list[0][0][1]
        self.assertEqual('', context['user_option_prefix'])
        self.assertEqual('foo_user', context['nginx_user'])

    @mock.patch('tethys_cli.gen_commands.render_template')
    @mock.patch('tethys_cli.gen_commands.linux_distribution')
    @mock.patch('tethys_cli.gen_commands.os.path.exists')
    @mock.patch('tethys_cli.gen_commands.get_environment_value')
    @mock.patch('tethys_cli.gen_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_cli.gen_commands.os.path.isfile')
    def test_generate_command_asgi_service_option_nginx_conf_not_linux(self, mock_os_path_isfile, mock_file, mock_env,
                                                                       mock_os_path_exists, mock_linux_distribution,
                                                                       mock_render_template):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_ASGI_SERVICE_OPTION
        mock_args.directory = None
        mock_os_path_isfile.return_value = False
        mock_env.side_effect = ['/foo/conda', 'conda_env']
        mock_os_path_exists.return_value = True
        mock_linux_distribution.side_effect = Exception
        mock_file.return_value = mock.mock_open(read_data='user foo_user').return_value

        generate_command(args=mock_args)

        mock_os_path_isfile.assert_called_once()
        mock_file.assert_called()
        mock_env.assert_any_call('CONDA_HOME')
        mock_env.assert_called_with('CONDA_ENV_NAME')
        mock_os_path_exists.assert_called_once_with('/etc/nginx/nginx.conf')
        context = mock_render_template.call_args_list[0][0][1]
        self.assertEqual('', context['user_option_prefix'])
        self.assertEqual('foo_user', context['nginx_user'])

    @mock.patch('tethys_cli.gen_commands.get_environment_value')
    @mock.patch('tethys_cli.gen_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_cli.gen_commands.os.path.isfile')
    def test_generate_command_asgi_service_option(self, mock_os_path_isfile, mock_file, mock_env):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_ASGI_SERVICE_OPTION
        mock_args.directory = None
        mock_os_path_isfile.return_value = False
        mock_env.side_effect = ['/foo/conda', 'conda_env']

        generate_command(args=mock_args)

        mock_os_path_isfile.assert_called()
        mock_file.assert_called()
        mock_env.assert_any_call('CONDA_HOME')
        mock_env.assert_called_with('CONDA_ENV_NAME')

    @mock.patch('tethys_cli.gen_commands.linux_distribution')
    @mock.patch('tethys_cli.gen_commands.get_environment_value')
    @mock.patch('tethys_cli.gen_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_cli.gen_commands.os.path.isfile')
    def test_generate_command_asgi_service_option_distro(self, mock_os_path_isfile, mock_file, mock_env,
                                                         mock_distribution):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_ASGI_SERVICE_OPTION
        mock_args.directory = None
        mock_os_path_isfile.return_value = False
        mock_env.side_effect = ['/foo/conda', 'conda_env']
        mock_distribution.return_value = ('redhat', 'linux', '')

        generate_command(args=mock_args)

        mock_os_path_isfile.assert_called_once()
        mock_file.assert_called()
        mock_env.assert_any_call('CONDA_HOME')
        mock_env.assert_called_with('CONDA_ENV_NAME')

    @mock.patch('tethys_cli.gen_commands.os.path.isdir')
    @mock.patch('tethys_cli.gen_commands.get_environment_value')
    @mock.patch('tethys_cli.gen_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_cli.gen_commands.os.path.isfile')
    def test_generate_command_asgi_settings_option_directory(self, mock_os_path_isfile, mock_file, mock_env,
                                                             mock_os_path_isdir):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_ASGI_SERVICE_OPTION
        mock_args.directory = '/foo/temp'
        mock_os_path_isfile.return_value = False
        mock_env.side_effect = ['/foo/conda', 'conda_env']
        mock_os_path_isdir.return_value = True

        generate_command(args=mock_args)

        mock_os_path_isfile.assert_called_once()
        mock_file.assert_called()
        mock_os_path_isdir.assert_called_with(mock_args.directory)
        mock_env.assert_any_call('CONDA_HOME')
        mock_env.assert_called_with('CONDA_ENV_NAME')

    @mock.patch('tethys_cli.gen_commands.print')
    @mock.patch('tethys_cli.gen_commands.exit')
    @mock.patch('tethys_cli.gen_commands.os.path.isdir')
    @mock.patch('tethys_cli.gen_commands.get_environment_value')
    @mock.patch('tethys_cli.gen_commands.os.path.isfile')
    def test_generate_command_asgi_settings_option_bad_directory(self, mock_os_path_isfile, mock_env,
                                                                 mock_os_path_isdir, mock_exit, mock_print):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_ASGI_SERVICE_OPTION
        mock_args.directory = '/foo/temp'
        mock_os_path_isfile.return_value = False
        mock_env.side_effect = ['/foo/conda', 'conda_env']
        mock_os_path_isdir.return_value = False
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, generate_command, args=mock_args)

        mock_os_path_isfile.assert_not_called()
        mock_os_path_isdir.assert_called_once_with(mock_args.directory)

        # Check if print is called correctly
        rts_call_args = mock_print.call_args_list
        self.assertIn('ERROR: ', rts_call_args[0][0][0])
        self.assertIn('is not a valid directory', rts_call_args[0][0][0])

        mock_env.assert_any_call('CONDA_HOME')
        mock_env.assert_called_with('CONDA_ENV_NAME')

    @mock.patch('tethys_cli.gen_commands.print')
    @mock.patch('tethys_cli.gen_commands.exit')
    @mock.patch('tethys_cli.gen_commands.input')
    @mock.patch('tethys_cli.gen_commands.get_environment_value')
    @mock.patch('tethys_cli.gen_commands.os.path.isfile')
    def test_generate_command_asgi_settings_pre_existing_input_exit(self, mock_os_path_isfile, mock_env,
                                                                    mock_input, mock_exit, mock_print):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_ASGI_SERVICE_OPTION
        mock_args.directory = None
        mock_args.overwrite = False
        mock_os_path_isfile.return_value = True
        mock_env.side_effect = ['/foo/conda', 'conda_env']
        mock_input.side_effect = ['foo', 'no']
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, generate_command, args=mock_args)

        mock_os_path_isfile.assert_called_once()

        # Check if print is called correctly
        rts_call_args = mock_print.call_args_list
        self.assertIn('Generation of', rts_call_args[0][0][0])
        self.assertIn('cancelled', rts_call_args[0][0][0])

        mock_env.assert_any_call('CONDA_HOME')
        mock_env.assert_called_with('CONDA_ENV_NAME')

    @mock.patch('tethys_cli.gen_commands.get_environment_value')
    @mock.patch('tethys_cli.gen_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_cli.gen_commands.os.path.isfile')
    def test_generate_command_asgi_settings_pre_existing_overwrite(self, mock_os_path_isfile, mock_file, mock_env):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_ASGI_SERVICE_OPTION
        mock_args.directory = None
        mock_args.overwrite = True
        mock_os_path_isfile.return_value = True
        mock_env.side_effect = ['/foo/conda', 'conda_env']

        generate_command(args=mock_args)

        mock_os_path_isfile.assert_called_once()
        mock_file.assert_called()
        mock_env.assert_any_call('CONDA_HOME')
        mock_env.assert_called_with('CONDA_ENV_NAME')

    @mock.patch('tethys_cli.gen_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_cli.gen_commands.os.path.isfile')
    def test_generate_command_services_option(self, mock_os_path_isfile, mock_file):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_SERVICES_OPTION
        mock_args.directory = None
        mock_os_path_isfile.return_value = False

        generate_command(args=mock_args)

        mock_os_path_isfile.assert_called_once()
        mock_file.assert_called()

    @mock.patch('tethys_cli.gen_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_cli.gen_commands.os.path.isfile')
    @mock.patch('tethys_cli.gen_commands.print')
    def test_generate_command_install_option(self, mock_print, mock_os_path_isfile, mock_file):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_INSTALL_OPTION
        mock_args.directory = None
        mock_os_path_isfile.return_value = False

        generate_command(args=mock_args)

        rts_call_args = mock_print.call_args_list
        self.assertIn('Please review the generated install.yml', rts_call_args[0][0][0])

        mock_os_path_isfile.assert_called_once()
        mock_file.assert_called()
