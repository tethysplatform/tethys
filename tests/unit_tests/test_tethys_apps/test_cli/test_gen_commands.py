import unittest
from unittest import mock
import tethys_apps.cli.gen_commands
from tethys_apps.cli.gen_commands import get_environment_value, get_settings_value, generate_command
from tethys_apps.cli.gen_commands import GEN_SETTINGS_OPTION, GEN_NGINX_OPTION, GEN_ASGI_SERVICE_OPTION

try:
    reload
except NameError:   # Python 3
    from imp import reload


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

    @mock.patch('tethys_apps.cli.gen_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_apps.cli.gen_commands.os.path.isfile')
    def test_generate_command_settings_option(self, mock_os_path_isfile, mock_file):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_SETTINGS_OPTION
        mock_args.directory = None
        mock_os_path_isfile.return_value = False

        generate_command(args=mock_args)

        mock_os_path_isfile.assert_called_once()
        mock_file.assert_called()

    @mock.patch('tethys_apps.cli.gen_commands.get_settings_value')
    @mock.patch('tethys_apps.cli.gen_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_apps.cli.gen_commands.os.path.isfile')
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

    @mock.patch('tethys_apps.cli.gen_commands.Context')
    @mock.patch('tethys_apps.cli.gen_commands.linux_distribution')
    @mock.patch('tethys_apps.cli.gen_commands.os.path.exists')
    @mock.patch('tethys_apps.cli.gen_commands.get_environment_value')
    @mock.patch('tethys_apps.cli.gen_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_apps.cli.gen_commands.os.path.isfile')
    def test_generate_command_asgi_service_nginx_conf_redhat(self, mock_os_path_isfile, mock_file, mock_env,
                                                             mock_os_path_exists, mock_linux_distribution,
                                                             mock_context):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_ASGI_SERVICE_OPTION
        mock_args.directory = None
        mock_os_path_isfile.return_value = False
        mock_env.side_effect = [8000, '/foo/conda', 'conda_env']
        mock_os_path_exists.return_value = True
        mock_linux_distribution.return_value = ['redhat']
        # First open is for the Template, next two are for /etc/nginx/nginx.conf and /etc/passwd, and the final
        # open is to "write" out the resulting file.  The middle two opens return information about a user, while
        # the first and last use MagicMock.
        handlers = (mock_file.return_value,
                    mock.mock_open(read_data='user foo_user').return_value,
                    mock.mock_open(read_data='foo_user:x:1000:1000:Foo User,,,:/foo/nginx:/bin/bash').return_value,
                    mock_file.return_value)
        mock_file.side_effect = handlers

        generate_command(args=mock_args)

        mock_os_path_isfile.assert_called_once()
        mock_file.assert_called()
        mock_env.assert_any_call('TETHYS_PORT')
        mock_env.assert_any_call('CONDA_HOME')
        mock_env.assert_called_with('CONDA_ENV_NAME')
        mock_os_path_exists.assert_called_once_with('/etc/nginx/nginx.conf')
        context = mock_context().update.call_args_list[0][0][0]
        self.assertEqual('http-', context['user_option_prefix'])

    @mock.patch('tethys_apps.cli.gen_commands.Context')
    @mock.patch('tethys_apps.cli.gen_commands.linux_distribution')
    @mock.patch('tethys_apps.cli.gen_commands.os.path.exists')
    @mock.patch('tethys_apps.cli.gen_commands.get_environment_value')
    @mock.patch('tethys_apps.cli.gen_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_apps.cli.gen_commands.os.path.isfile')
    def test_generate_command_asgi_service_option_nginx_conf_ubuntu(self, mock_os_path_isfile, mock_file, mock_env,
                                                                    mock_os_path_exists, mock_linux_distribution,
                                                                    mock_context):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_ASGI_SERVICE_OPTION
        mock_args.directory = None
        mock_os_path_isfile.return_value = False
        mock_env.side_effect = [8000, '/foo/conda', 'conda_env']
        mock_os_path_exists.return_value = True
        mock_linux_distribution.return_value = 'ubuntu'
        # First open is for the Template, next two are for /etc/nginx/nginx.conf and /etc/passwd, and the final
        # open is to "write" out the resulting file.  The middle two opens return information about a user, while
        # the first and last use MagicMock.
        handlers = (mock_file.return_value,
                    mock.mock_open(read_data='user foo_user').return_value,
                    mock.mock_open(read_data='foo_user:x:1000:1000:Foo User,,,:/foo/nginx:/bin/bash').return_value,
                    mock_file.return_value)
        mock_file.side_effect = handlers

        generate_command(args=mock_args)

        mock_os_path_isfile.assert_called_once()
        mock_file.assert_called()
        mock_env.assert_any_call('TETHYS_PORT')
        mock_env.assert_any_call('CONDA_HOME')
        mock_env.assert_called_with('CONDA_ENV_NAME')
        mock_os_path_exists.assert_called_once_with('/etc/nginx/nginx.conf')
        context = mock_context().update.call_args_list[0][0][0]
        self.assertEqual('', context['user_option_prefix'])

    @mock.patch('tethys_apps.cli.gen_commands.Context')
    @mock.patch('tethys_apps.cli.gen_commands.linux_distribution')
    @mock.patch('tethys_apps.cli.gen_commands.os.path.exists')
    @mock.patch('tethys_apps.cli.gen_commands.get_environment_value')
    @mock.patch('tethys_apps.cli.gen_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_apps.cli.gen_commands.os.path.isfile')
    def test_generate_command_asgi_service_option_nginx_conf_not_linux(self, mock_os_path_isfile, mock_file, mock_env,
                                                                       mock_os_path_exists, mock_linux_distribution,
                                                                       mock_context):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_ASGI_SERVICE_OPTION
        mock_args.directory = None
        mock_os_path_isfile.return_value = False
        mock_env.side_effect = [8000, '/foo/conda', 'conda_env']
        mock_os_path_exists.return_value = True
        mock_linux_distribution.side_effect = Exception
        # First open is for the Template, next two are for /etc/nginx/nginx.conf and /etc/passwd, and the final
        # open is to "write" out the resulting file.  The middle two opens return information about a user, while
        # the first and last use MagicMock.
        handlers = (mock_file.return_value,
                    mock.mock_open(read_data='user foo_user').return_value,
                    mock.mock_open(read_data='foo_user:x:1000:1000:Foo User,,,:/foo/nginx:/bin/bash').return_value,
                    mock_file.return_value)
        mock_file.side_effect = handlers

        generate_command(args=mock_args)

        mock_os_path_isfile.assert_called_once()
        mock_file.assert_called()
        mock_env.assert_any_call('TETHYS_PORT')
        mock_env.assert_any_call('CONDA_HOME')
        mock_env.assert_called_with('CONDA_ENV_NAME')
        mock_os_path_exists.assert_called_once_with('/etc/nginx/nginx.conf')
        context = mock_context().update.call_args_list[0][0][0]
        self.assertEqual('', context['user_option_prefix'])

    @mock.patch('tethys_apps.cli.gen_commands.get_environment_value')
    @mock.patch('tethys_apps.cli.gen_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_apps.cli.gen_commands.os.path.isfile')
    def test_generate_command_asgi_service_option(self, mock_os_path_isfile, mock_file, mock_env):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_ASGI_SERVICE_OPTION
        mock_args.directory = None
        mock_os_path_isfile.return_value = False
        mock_env.side_effect = [8000, '/foo/conda', 'conda_env']

        generate_command(args=mock_args)

        mock_os_path_isfile.assert_called_once()
        mock_file.assert_called()
        mock_env.assert_any_call('TETHYS_PORT')
        mock_env.assert_any_call('CONDA_HOME')
        mock_env.assert_called_with('CONDA_ENV_NAME')

    @mock.patch('tethys_apps.cli.gen_commands.linux_distribution')
    @mock.patch('tethys_apps.cli.gen_commands.get_environment_value')
    @mock.patch('tethys_apps.cli.gen_commands.open', new_callable=mock.mock_open)
    @mock.patch('tethys_apps.cli.gen_commands.os.path.isfile')
    def test_generate_command_asgi_service_option_distro(self, mock_os_path_isfile, mock_file, mock_env,
                                                         mock_distribution):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_ASGI_SERVICE_OPTION
        mock_args.directory = None
        mock_os_path_isfile.return_value = False
        mock_env.side_effect = [8000, '/foo/conda', 'conda_env']
        mock_distribution.return_value = ('redhat', 'linux', '')

        generate_command(args=mock_args)

        mock_os_path_isfile.assert_called_once()
        mock_file.assert_called()
        mock_env.assert_any_call('TETHYS_PORT')
        mock_env.assert_any_call('CONDA_HOME')
        mock_env.assert_called_with('CONDA_ENV_NAME')

    @mock.patch('tethys_apps.cli.gen_commands.os.environ')
    def test_django_settings_module_error(self, mock_environ):
        mock_environ.side_effect = Exception
        try:
            reload(tethys_apps.cli.gen_commands)
        except Exception:
            pass

        self.assertTrue(tethys_apps.cli.gen_commands.settings.configured)
