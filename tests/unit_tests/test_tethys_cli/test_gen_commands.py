import unittest
from unittest import mock
from pathlib import Path
import tempfile


from tethys_cli.gen_commands import (
    get_environment_value,
    get_settings_value,
    derive_version_from_conda_environment,
    gen_meta_yaml,
    generate_command,
    gen_vendor_static_files,
    download_vendor_static_files,
    parse_setup_py,
    gen_pyproject,
    pyproject_post_process,
    get_destination_path,
    GEN_APACHE_OPTION,
    GEN_APACHE_SERVICE_OPTION,
    GEN_NGINX_OPTION,
    GEN_NGINX_SERVICE_OPTION,
    GEN_ASGI_SERVICE_OPTION,
    GEN_SERVICES_OPTION,
    GEN_INSTALL_OPTION,
    GEN_PORTAL_OPTION,
    GEN_SECRETS_OPTION,
    GEN_META_YAML_OPTION,
    GEN_PACKAGE_JSON_OPTION,
    GEN_PYPROJECT_OPTION,
    GEN_REQUIREMENTS_OPTION,
    VALID_GEN_OBJECTS,
)

from tethys_apps.utilities import get_tethys_src_dir

TETHYS_SRC = get_tethys_src_dir()


class CLIGenCommandsTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_environment_value(self):
        result = get_environment_value(value_name="DJANGO_SETTINGS_MODULE")

        self.assertEqual("tethys_portal.settings", result)

    def test_get_environment_value_bad(self):
        self.assertRaises(
            EnvironmentError,
            get_environment_value,
            value_name="foo_bar_baz_bad_environment_value_foo_bar_baz",
        )

    def test_get_settings_value(self):
        result = get_settings_value(value_name="INSTALLED_APPS")

        self.assertIn("tethys_apps", result)

    def test_get_settings_value_bad(self):
        self.assertRaises(
            ValueError,
            get_settings_value,
            value_name="foo_bar_baz_bad_setting_foo_bar_baz",
        )

    @mock.patch("tethys_cli.gen_commands.write_info")
    @mock.patch("tethys_cli.gen_commands.get_settings_value")
    @mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
    @mock.patch("tethys_cli.gen_commands.Path.is_file")
    def test_generate_command_apache_option(
        self, mock_is_file, mock_file, mock_settings, mock_write_info
    ):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_APACHE_OPTION
        mock_args.directory = None
        mock_is_file.return_value = False
        mock_settings.side_effect = [
            "/foo/workspace",
            "/foo/static",
            "/foo/media",
            "/foo/prefix",
        ]

        generate_command(args=mock_args)

        mock_is_file.assert_called_once()
        mock_file.assert_called()
        mock_settings.assert_any_call("MEDIA_ROOT")
        mock_settings.assert_any_call("STATIC_ROOT")
        mock_settings.assert_called_with("PREFIX_URL")

        mock_write_info.assert_called_once()

    @mock.patch("tethys_cli.gen_commands.write_info")
    @mock.patch("tethys_cli.gen_commands.get_settings_value")
    @mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
    @mock.patch("tethys_cli.gen_commands.Path.is_file")
    def test_generate_command_nginx_option(
        self, mock_is_file, mock_file, mock_settings, mock_write_info
    ):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_NGINX_OPTION
        mock_args.directory = None
        mock_is_file.return_value = False
        mock_settings.side_effect = [
            "/foo/workspace",
            "/foo/static",
            "/foo/media",
            "/foo/prefix",
        ]

        generate_command(args=mock_args)

        mock_is_file.assert_called_once()
        mock_file.assert_called()
        mock_settings.assert_any_call("TETHYS_WORKSPACES_ROOT")
        mock_settings.assert_any_call("MEDIA_ROOT")
        mock_settings.assert_called_with("PREFIX_URL")

        mock_write_info.assert_called_once()

    @mock.patch("tethys_cli.gen_commands.write_info")
    @mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
    @mock.patch("tethys_cli.gen_commands.Path.is_file")
    def test_generate_command_nginx_service(
        self, mock_is_file, mock_file, mock_write_info
    ):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_NGINX_SERVICE_OPTION
        mock_args.directory = None
        mock_is_file.return_value = False

        generate_command(args=mock_args)

        mock_is_file.assert_called_once()
        mock_file.assert_called()

        mock_write_info.assert_called_once()

    @mock.patch("tethys_cli.gen_commands.write_info")
    @mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
    @mock.patch("tethys_cli.gen_commands.Path.is_file")
    def test_generate_command_apache_service(
        self, mock_is_file, mock_file, mock_write_info
    ):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_APACHE_SERVICE_OPTION
        mock_args.directory = None
        mock_is_file.return_value = False

        generate_command(args=mock_args)

        mock_is_file.assert_called_once()
        mock_file.assert_called()

        mock_write_info.assert_called_once()

    @mock.patch("tethys_cli.gen_commands.Path.is_dir")
    @mock.patch("tethys_cli.gen_commands.write_info")
    @mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
    @mock.patch("tethys_cli.gen_commands.Path.is_file")
    @mock.patch("tethys_cli.gen_commands.Path.mkdir")
    def test_generate_command_portal_yaml__tethys_home_not_exists(
        self, mock_mkdir, mock_is_file, mock_file, mock_write_info, mock_isdir
    ):
        mock_args = mock.MagicMock(
            type=GEN_PORTAL_OPTION, directory=None, spec=["overwrite", "server_port"]
        )
        mock_is_file.return_value = False
        mock_isdir.side_effect = [
            False,
            True,
        ]  # TETHYS_HOME dir exists, computed dir exists

        generate_command(args=mock_args)

        mock_is_file.assert_called_once()
        mock_file.assert_called()

        # Verify it makes the Tethys Home directory
        mock_mkdir.assert_called()
        rts_call_args = mock_write_info.call_args_list[0]
        self.assertIn("A Tethys Portal configuration file", rts_call_args.args[0])

    @mock.patch("tethys_cli.gen_commands.write_info")
    @mock.patch("tethys_cli.gen_commands.render_template")
    @mock.patch("tethys_cli.gen_commands.Path.exists")
    @mock.patch("tethys_cli.gen_commands.get_environment_value")
    @mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
    @mock.patch("tethys_cli.gen_commands.Path.is_file")
    def test_generate_command_asgi_service_option_nginx_conf(
        self,
        mock_is_file,
        mock_file,
        mock_env,
        mock_path_exists,
        mock_render_template,
        mock_write_info,
    ):
        mock_args = mock.MagicMock(conda_prefix=False)
        mock_args.type = GEN_ASGI_SERVICE_OPTION
        mock_args.directory = None
        mock_is_file.return_value = False
        mock_env.side_effect = ["/foo/conda", "conda_env"]
        mock_path_exists.return_value = True
        mock_file.return_value = mock.mock_open(read_data="user foo_user").return_value

        generate_command(args=mock_args)

        mock_is_file.assert_called_once()
        mock_file.assert_called()
        mock_env.assert_called_with("CONDA_PREFIX")
        mock_path_exists.assert_called_once()
        context = mock_render_template.call_args.args[1]
        self.assertEqual("foo_user", context["nginx_user"])

        mock_write_info.assert_called()

    @mock.patch("tethys_cli.gen_commands.write_info")
    @mock.patch("tethys_cli.gen_commands.get_environment_value")
    @mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
    @mock.patch("tethys_cli.gen_commands.Path.is_file")
    def test_generate_command_asgi_service_option(
        self, mock_is_file, mock_file, mock_env, mock_write_info
    ):
        mock_args = mock.MagicMock(conda_prefix=False)
        mock_args.type = GEN_ASGI_SERVICE_OPTION
        mock_args.directory = None
        mock_is_file.return_value = False
        mock_env.side_effect = ["/foo/conda", "conda_env"]

        generate_command(args=mock_args)

        mock_is_file.assert_called()
        mock_file.assert_called()
        mock_env.assert_called_with("CONDA_PREFIX")

        mock_write_info.assert_called()

    @mock.patch("tethys_cli.gen_commands.write_info")
    @mock.patch("tethys_cli.gen_commands.get_environment_value")
    @mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
    @mock.patch("tethys_cli.gen_commands.Path.is_file")
    def test_generate_command_asgi_service_option_distro(
        self,
        mock_is_file,
        mock_file,
        mock_env,
        mock_write_info,
    ):
        mock_args = mock.MagicMock(conda_prefix=False)
        mock_args.type = GEN_ASGI_SERVICE_OPTION
        mock_args.directory = None
        mock_is_file.return_value = False
        mock_env.side_effect = ["/foo/conda", "conda_env"]

        generate_command(args=mock_args)

        mock_is_file.assert_called_once()
        mock_file.assert_called()
        mock_env.assert_called_with("CONDA_PREFIX")

        mock_write_info.assert_called()

    @mock.patch("tethys_cli.gen_commands.write_info")
    @mock.patch("tethys_cli.gen_commands.Path.is_dir")
    @mock.patch("tethys_cli.gen_commands.get_environment_value")
    @mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
    @mock.patch("tethys_cli.gen_commands.Path.is_file")
    def test_generate_command_asgi_settings_option_directory(
        self,
        mock_is_file,
        mock_file,
        mock_env,
        mock_is_dir,
        mock_write_info,
    ):
        mock_args = mock.MagicMock(conda_prefix=False)
        mock_args.type = GEN_ASGI_SERVICE_OPTION
        mock_args.directory = str(Path("/").absolute() / "foo" / "temp")
        mock_is_file.return_value = False
        mock_env.side_effect = ["/foo/conda", "conda_env"]
        mock_is_dir.side_effect = [
            True,
            True,
        ]  # TETHYS_HOME exists, computed directory exists

        generate_command(args=mock_args)

        mock_is_file.assert_called_once()
        mock_file.assert_called()
        self.assertEqual(mock_is_dir.call_count, 2)
        mock_env.assert_called_with("CONDA_PREFIX")

        mock_write_info.assert_called()

    @mock.patch("tethys_cli.gen_commands.write_error")
    @mock.patch("tethys_cli.gen_commands.exit")
    @mock.patch("tethys_cli.gen_commands.Path.is_dir")
    @mock.patch("tethys_cli.gen_commands.get_environment_value")
    @mock.patch("tethys_cli.gen_commands.Path.is_file")
    def test_generate_command_asgi_settings_option_bad_directory(
        self,
        mock_is_file,
        mock_env,
        mock_is_dir,
        mock_exit,
        mock_write_error,
    ):
        mock_args = mock.MagicMock(conda_prefix=False)
        mock_args.type = GEN_ASGI_SERVICE_OPTION
        mock_args.directory = str(Path("/").absolute() / "foo" / "temp")
        mock_is_file.return_value = False
        mock_env.side_effect = ["/foo/conda", "conda_env"]
        mock_is_dir.side_effect = [
            True,
            False,
        ]  # TETHYS_HOME exists, computed directory exists
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, generate_command, args=mock_args)

        mock_is_file.assert_not_called()
        self.assertEqual(mock_is_dir.call_count, 2)

        # Check if print is called correctly
        rts_call_args = mock_write_error.call_args
        self.assertIn("ERROR: ", rts_call_args.args[0])
        self.assertIn("is not a valid directory", rts_call_args.args[0])

        mock_env.assert_called_with("CONDA_PREFIX")

    @mock.patch("tethys_cli.gen_commands.write_info")
    @mock.patch("tethys_cli.gen_commands.write_warning")
    @mock.patch("tethys_cli.gen_commands.exit")
    @mock.patch("tethys_cli.gen_commands.input")
    @mock.patch("tethys_cli.gen_commands.get_environment_value")
    @mock.patch("tethys_cli.gen_commands.Path.is_file")
    def test_generate_command_asgi_settings_pre_existing_input_exit(
        self,
        mock_is_file,
        mock_env,
        mock_input,
        mock_exit,
        mock_write_warning,
        mock_write_info,
    ):
        mock_args = mock.MagicMock(conda_prefix=False)
        mock_args.type = GEN_ASGI_SERVICE_OPTION
        mock_args.directory = None
        mock_args.overwrite = False
        mock_is_file.return_value = True
        mock_env.side_effect = ["/foo/conda", "conda_env"]
        mock_input.side_effect = ["foo", "no"]
        # NOTE: to prevent our tests from exiting prematurely, we change the behavior of exit to raise an exception
        # to break the code execution, which we catch below.
        mock_exit.side_effect = SystemExit

        self.assertRaises(SystemExit, generate_command, args=mock_args)

        mock_is_file.assert_called_once()

        # Check if print is called correctly
        rts_call_args = mock_write_warning.call_args
        self.assertIn("Generation of", rts_call_args.args[0])
        self.assertIn("cancelled", rts_call_args.args[0])

        mock_env.assert_called_with("CONDA_PREFIX")

    @mock.patch("tethys_cli.gen_commands.write_info")
    @mock.patch("tethys_cli.gen_commands.get_environment_value")
    @mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
    @mock.patch("tethys_cli.gen_commands.Path.is_file")
    def test_generate_command_asgi_settings_pre_existing_overwrite(
        self, mock_is_file, mock_file, mock_env, mock_write_info
    ):
        mock_args = mock.MagicMock(conda_prefix=False)
        mock_args.type = GEN_ASGI_SERVICE_OPTION
        mock_args.directory = None
        mock_args.overwrite = True
        mock_is_file.return_value = True
        mock_env.side_effect = ["/foo/conda", "conda_env"]

        generate_command(args=mock_args)

        mock_is_file.assert_called_once()
        mock_file.assert_called()
        mock_env.assert_called_with("CONDA_PREFIX")

        mock_write_info.assert_called()

    @mock.patch("tethys_cli.gen_commands.write_info")
    @mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
    @mock.patch("tethys_cli.gen_commands.Path.is_file")
    def test_generate_command_services_option(
        self, mock_is_file, mock_file, mock_write_info
    ):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_SERVICES_OPTION
        mock_args.directory = None
        mock_is_file.return_value = False

        generate_command(args=mock_args)

        mock_is_file.assert_called_once()
        mock_file.assert_called()

    @mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
    @mock.patch("tethys_cli.gen_commands.Path.is_file")
    @mock.patch("tethys_cli.gen_commands.write_info")
    def test_generate_command_install_option(
        self, mock_write_info, mock_is_file, mock_file
    ):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_INSTALL_OPTION
        mock_args.directory = None
        mock_is_file.return_value = False

        generate_command(args=mock_args)

        rts_call_args = mock_write_info.call_args_list[0]
        self.assertIn("Please review the generated install.yml", rts_call_args.args[0])

        mock_is_file.assert_called_once()
        mock_file.assert_called()

    @mock.patch("tethys_cli.gen_commands.run")
    @mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
    @mock.patch("tethys_cli.gen_commands.Path.is_file")
    @mock.patch("tethys_cli.gen_commands.write_warning")
    @mock.patch("tethys_cli.gen_commands.write_info")
    def test_generate_requirements_option(
        self, mock_write_info, mock_write_warn, mock_is_file, mock_file, mock_run
    ):
        mock_args = mock.MagicMock()
        mock_args.type = GEN_REQUIREMENTS_OPTION
        mock_args.directory = None
        mock_is_file.return_value = False

        generate_command(args=mock_args)

        mock_write_warn.assert_called_once()
        mock_write_info.assert_called_once()
        mock_is_file.assert_called_once()
        mock_file.assert_called()
        mock_run.assert_called_once()

    @mock.patch("tethys_cli.gen_commands.write_info")
    @mock.patch("tethys_cli.gen_commands.Template")
    @mock.patch("tethys_cli.gen_commands.yaml.safe_load")
    @mock.patch("tethys_cli.gen_commands.run_command")
    @mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
    @mock.patch("tethys_cli.gen_commands.Path.is_file")
    @mock.patch("tethys_cli.gen_commands.print")
    def test_generate_command_metayaml(
        self,
        mock_print,
        mock_is_file,
        mock_file,
        mock_run_command,
        mock_load,
        mock_Template,
        _,
    ):
        mock_args = mock.MagicMock(micro=False)
        mock_args.type = GEN_META_YAML_OPTION
        mock_args.directory = None
        mock_args.pin_level = "minor"
        mock_is_file.return_value = False
        stdout = (
            "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
            "#\n"
            "# Name                    Version                   Build  Channel\n"
            "foo                       1.2.3                     py37_0    conda-forge\n"
            "bar                       4.5.6                     py37h516909a_0    conda-forge\n"
            "goo                       7.8                       py37h516909a_0    conda-forge\n"
        )
        mock_run_command.return_value = (stdout, "", 0)
        mock_load.return_value = {"dependencies": ["foo", "bar=4.5", "goo"]}
        mock_Template().render.return_value = "out"
        generate_command(args=mock_args)

        mock_run_command.assert_any_call("list", "foo")
        mock_run_command.assert_any_call("list", "goo")

        mock_print.assert_not_called()

        render_context = mock_Template().render.call_args.args[0]
        expected_context = {
            "package_name": "tethys-platform",
            "run_requirements": ["foo=1.2.*", "bar=4.5", "goo=7.8"],
            "tethys_version": mock.ANY,
        }
        self.assertDictEqual(expected_context, render_context)
        mock_file.assert_called()

    @mock.patch("tethys_cli.gen_commands.write_info")
    @mock.patch("tethys_cli.gen_commands.derive_version_from_conda_environment")
    @mock.patch("tethys_cli.gen_commands.yaml.safe_load")
    @mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
    def test_gen_meta_yaml_overriding_dependencies(
        self, _, mock_load, mock_dvfce, mock_write_info
    ):
        mock_args = mock.MagicMock(micro=False)
        mock_args.type = GEN_META_YAML_OPTION
        mock_args.directory = None
        mock_args.pin_level = "minor"

        mock_load.return_value = {
            "dependencies": [
                "foo",
                "foo=1.2.3",
                "foo>=1.2.3",
                "foo<=1.2.3",
                "foo>1.2.3",
                "foo<1.2.3",
            ]
        }

        ret = gen_meta_yaml(mock_args)

        self.assertEqual(1, mock_dvfce.call_count)
        mock_dvfce.assert_called_with("foo", level="minor")

        expected_context = {
            "package_name": "tethys-platform",
            "run_requirements": [
                mock_dvfce(),
                "foo=1.2.3",
                "foo>=1.2.3",
                "foo<=1.2.3",
                "foo>1.2.3",
                "foo<1.2.3",
            ],
            "tethys_version": mock.ANY,
        }
        self.assertDictEqual(expected_context, ret)

    @mock.patch("tethys_cli.gen_commands.run_command")
    def test_derive_version_from_conda_environment_minor(self, mock_run_command):
        stdout = (
            "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
            "#\n"
            "# Name                    Version                   Build  Channel\n"
            "foo                       1.2.3.4.5                 py37_0    conda-forge"
        )
        mock_run_command.return_value = (stdout, "", 0)
        ret = derive_version_from_conda_environment("foo", "minor")
        self.assertEqual("foo=1.2.*", ret)

        stdout = (
            "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
            "#\n"
            "# Name                    Version                   Build  Channel\n"
            "foo                       1.2.3                     py37_0    conda-forge"
        )
        mock_run_command.return_value = (stdout, "", 0)
        ret = derive_version_from_conda_environment("foo", "minor")
        self.assertEqual("foo=1.2.*", ret)

        stdout = (
            "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
            "#\n"
            "# Name                    Version                   Build  Channel\n"
            "foo                       1.2                       py37_0    conda-forge"
        )
        mock_run_command.return_value = (stdout, "", 0)
        ret = derive_version_from_conda_environment("foo", "minor")
        self.assertEqual("foo=1.2", ret)

        stdout = (
            "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
            "#\n"
            "# Name                    Version                   Build  Channel\n"
            "foo                       1                         py37_0    conda-forge"
        )
        mock_run_command.return_value = (stdout, "", 0)
        ret = derive_version_from_conda_environment("foo", "minor")
        self.assertEqual("foo", ret)

    @mock.patch("tethys_cli.gen_commands.run_command")
    def test_derive_version_from_conda_environment_major(self, mock_run_command):
        # More than three version numbers
        stdout = (
            "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
            "#\n"
            "# Name                    Version                   Build  Channel\n"
            "foo                       1.2.3.4.5                 py37_0    conda-forge"
        )
        mock_run_command.return_value = (stdout, "", 0)

        ret = derive_version_from_conda_environment("foo", "major")
        self.assertEqual("foo=1.*", ret)

        # Three version numbers
        stdout = (
            "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
            "#\n"
            "# Name                    Version                   Build  Channel\n"
            "foo                       1.2.3                     py37_0    conda-forge"
        )
        mock_run_command.return_value = (stdout, "", 0)
        ret = derive_version_from_conda_environment("foo", "major")
        self.assertEqual("foo=1.*", ret)

        # Two version numbers
        stdout = (
            "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
            "#\n"
            "# Name                    Version                   Build  Channel\n"
            "foo                       1.2                       py37_0    conda-forge"
        )
        mock_run_command.return_value = (stdout, "", 0)
        ret = derive_version_from_conda_environment("foo", "major")
        self.assertEqual("foo=1.*", ret)

        # Less than two version numbers
        stdout = (
            "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
            "#\n"
            "# Name                    Version                   Build  Channel\n"
            "foo                       1                         py37_0    conda-forge"
        )
        mock_run_command.return_value = (stdout, "", 0)
        ret = derive_version_from_conda_environment("foo", "major")
        self.assertEqual("foo=1", ret)

    @mock.patch("tethys_cli.gen_commands.run_command")
    def test_derive_version_from_conda_environment_patch(self, mock_run_command):
        stdout = (
            "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
            "#\n"
            "# Name                    Version                   Build  Channel\n"
            "foo                       1.2.3.4.5                 py37_0    conda-forge"
        )
        mock_run_command.return_value = (stdout, "", 0)
        ret = derive_version_from_conda_environment("foo", "patch")
        self.assertEqual("foo=1.2.3.*", ret)

        stdout = (
            "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
            "#\n"
            "# Name                    Version                   Build  Channel\n"
            "foo                       1.2.3                     py37_0    conda-forge"
        )
        mock_run_command.return_value = (stdout, "", 0)
        ret = derive_version_from_conda_environment("foo", "patch")
        self.assertEqual("foo=1.2.3", ret)

        stdout = (
            "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
            "#\n"
            "# Name                    Version                   Build  Channel\n"
            "foo                       1.2                       py37_0    conda-forge"
        )
        mock_run_command.return_value = (stdout, "", 0)
        ret = derive_version_from_conda_environment("foo", "patch")
        self.assertEqual("foo=1.2", ret)

        stdout = (
            "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
            "#\n"
            "# Name                    Version                   Build  Channel\n"
            "foo                       1                         py37_0    conda-forge"
        )
        mock_run_command.return_value = (stdout, "", 0)
        ret = derive_version_from_conda_environment("foo", "patch")
        self.assertEqual("foo=1", ret)

    @mock.patch("tethys_cli.gen_commands.run_command")
    def test_derive_version_from_conda_environment_none(self, mock_run_command):
        stdout = (
            "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
            "#\n"
            "# Name                    Version                   Build  Channel\n"
            "foo                       1.2.3.4.5                 py37_0    conda-forge"
        )
        mock_run_command.return_value = (stdout, "", 0)
        ret = derive_version_from_conda_environment("foo", "none")
        self.assertEqual("foo", ret)

        stdout = (
            "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
            "#\n"
            "# Name                    Version                   Build  Channel\n"
            "foo                       1.2.3                     py37_0    conda-forge"
        )
        mock_run_command.return_value = (stdout, "", 0)
        ret = derive_version_from_conda_environment("foo", "none")
        self.assertEqual("foo", ret)

        stdout = (
            "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
            "#\n"
            "# Name                    Version                   Build  Channel\n"
            "foo                       1.2                       py37_0    conda-forge"
        )
        mock_run_command.return_value = (stdout, "", 0)
        ret = derive_version_from_conda_environment("foo", "none")
        self.assertEqual("foo", ret)

        stdout = (
            "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
            "#\n"
            "# Name                    Version                   Build  Channel\n"
            "foo                       1                         py37_0    conda-forge"
        )
        mock_run_command.return_value = (stdout, "", 0)
        ret = derive_version_from_conda_environment("foo", "none")
        self.assertEqual("foo", ret)

    @mock.patch("tethys_cli.gen_commands.print")
    @mock.patch("tethys_cli.gen_commands.run_command")
    def test_derive_version_from_conda_environment_conda_list_error(
        self, mock_run_command, mock_print
    ):
        mock_run_command.return_value = ("", "Some error", 1)

        ret = derive_version_from_conda_environment("foo", "minor")

        self.assertEqual("foo", ret)

        rts_call_args_list = mock_print.call_args_list
        self.assertEqual(
            'ERROR: Something went wrong looking up dependency "foo" in environment',
            rts_call_args_list[0].args[0],
        )
        self.assertEqual("Some error", rts_call_args_list[1].args[0])

    def test_gen_vendor_static_files(self):
        context = gen_vendor_static_files(mock.MagicMock())
        for _, v in context.items():
            self.assertIsNotNone(v)

    @mock.patch("tethys_cli.gen_commands.call")
    def test_download_vendor_static_files(self, mock_call):
        download_vendor_static_files(mock.MagicMock())
        mock_call.assert_called_once()

    @mock.patch("tethys_cli.gen_commands.write_error")
    @mock.patch("tethys_cli.gen_commands.call")
    def test_download_vendor_static_files_no_npm(self, mock_call, mock_error):
        mock_call.side_effect = FileNotFoundError
        download_vendor_static_files(mock.MagicMock())
        mock_call.assert_called_once()
        mock_error.assert_called_once()

    @mock.patch("tethys_cli.gen_commands.has_module")
    @mock.patch("tethys_cli.gen_commands.write_error")
    @mock.patch("tethys_cli.gen_commands.call")
    def test_download_vendor_static_files_no_npm_no_conda(
        self, mock_call, mock_error, mock_has_module
    ):
        mock_call.side_effect = FileNotFoundError
        mock_has_module.return_value = False
        download_vendor_static_files(mock.MagicMock())
        mock_call.assert_called_once()
        mock_error.assert_called_once()

    @mock.patch("tethys_cli.gen_commands.check_for_existing_file")
    @mock.patch("tethys_cli.gen_commands.Path.is_dir", return_value=True)
    def test_get_destination_path_vendor(self, mock_isdir, mock_check_file):
        mock_args = mock.MagicMock(
            type=GEN_PACKAGE_JSON_OPTION,
            directory=False,
        )
        result = get_destination_path(mock_args)
        mock_isdir.assert_called()
        mock_check_file.assert_called_once()
        self.assertEqual(
            result, str(Path(TETHYS_SRC) / "tethys_portal" / "static" / "package.json")
        )

    @mock.patch("tethys_cli.gen_commands.GEN_COMMANDS")
    @mock.patch("tethys_cli.gen_commands.write_path_to_console")
    @mock.patch("tethys_cli.gen_commands.render_template")
    @mock.patch("tethys_cli.gen_commands.get_destination_path")
    def test_generate_commmand_post_process_func(
        self, mock_gdp, mock_render, mock_write_path, mock_commands
    ):
        mock_commands.__getitem__.return_value = (mock.MagicMock(), mock.MagicMock())
        mock_args = mock.MagicMock(
            type="test",
        )
        generate_command(mock_args)
        mock_gdp.assert_called_once_with(mock_args)
        mock_render.assert_called_once()
        mock_write_path.assert_called_once()
        mock_commands.__getitem__.assert_called_once()

    def test_templates_exist(self):
        template_dir = Path(TETHYS_SRC) / "tethys_cli" / "gen_templates"
        for file_name in VALID_GEN_OBJECTS:
            template_path = template_dir / file_name
            self.assertTrue(template_path.exists())

    @mock.patch("tethys_cli.gen_commands.Path.is_dir")
    @mock.patch("tethys_cli.gen_commands.write_info")
    @mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
    @mock.patch("tethys_cli.gen_commands.Path.is_file")
    @mock.patch("tethys_cli.gen_commands.Path.mkdir")
    def test_generate_command_secrets_yaml_tethys_home_not_exists(
        self, mock_mkdir, mock_is_file, mock_file, mock_write_info, mock_isdir
    ):
        mock_args = mock.MagicMock(
            type=GEN_SECRETS_OPTION, directory=None, spec=["overwrite"]
        )
        mock_is_file.return_value = False
        mock_isdir.side_effect = [
            False,
            True,
        ]  # TETHYS_HOME dir exists, computed dir exists

        generate_command(args=mock_args)

        mock_is_file.assert_called_once()
        mock_file.assert_called()

        # Verify it makes the Tethys Home directory
        mock_mkdir.assert_called()
        rts_call_args = mock_write_info.call_args_list[0]
        self.assertIn("A Tethys Secrets file", rts_call_args.args[0])

    @mock.patch("tethys_cli.gen_commands.exit", side_effect=SystemExit)
    @mock.patch("tethys_cli.gen_commands.get_target_tethys_app_dir")
    @mock.patch("tethys_cli.gen_commands.write_error")
    def test_generate_command_pyproject_no_setup_py(
        self, mock_write_error, mock_gttad, mock_exit
    ):
        mock_args = mock.MagicMock(
            type=GEN_PYPROJECT_OPTION,
            directory=None,
            spec=["overwrite"],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            app_dir = Path(temp_dir)
            mock_gttad.return_value = app_dir

            with self.assertRaises(SystemExit):
                gen_pyproject(mock_args)

            error_msg = mock_write_error.call_args.args[0]

            expected = f'The specified Tethys app directory "{app_dir}" does not contain a setup.py file.'
            self.assertIn(expected, error_msg)

            # exit should be called once
            mock_exit.assert_called_once()

    def test_parse_setup_py(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            setup_path = temp_dir / "setup.py"

            import textwrap

            # Write a fake setup.py into the temp folder
            setup_path.write_text(
                textwrap.dedent(
                    """
                    app_package = 'test_app'

                    from setuptools import setup

                    setup(
                        description='A test description',
                        author='Test Author',
                        author_email='test@example.com',
                        keywords=['alpha', 'beta'],
                        license='MIT',
                    )
                    """
                )
            )

            metadata = parse_setup_py(setup_path)

            assert metadata["app_package"] == "test_app"
            assert metadata["description"] == "A test description"
            assert metadata["author"] == "Test Author"
            assert metadata["author_email"] == "test@example.com"
            assert metadata["keywords"] == "alpha, beta"
            assert metadata["license"] == "MIT"

    @mock.patch("tethys_cli.gen_commands.write_error")
    def test_parse_setup_py_no_setup(self, mock_write_error):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            setup_path = temp_dir / "setup.py"

            metadata = parse_setup_py(setup_path)

            self.assertIsNone(metadata)

            error_msg = mock_write_error.call_args.args[0]

            expected = f"Failed to parse setup.py: [Errno 2] No such file or directory: '{setup_path}'"
            self.assertIn(expected, error_msg)

    @mock.patch("tethys_cli.gen_commands.write_warning")
    @mock.patch("tethys_cli.gen_commands.exit", side_effect=SystemExit)
    def test_parse_setup_py_invalid_package_name(self, mock_exit, mock_write_warning):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            setup_path = temp_dir / "setup.py"

            import textwrap

            # Write a fake setup.py into the temp folder
            setup_path.write_text(
                textwrap.dedent(
                    """
                    app_package = fake_function()

                    from setuptools import setup

                    setup(
                        description='A test description',
                        author='Test Author',
                        author_email='test@example.com',
                        keywords=['alpha', 'beta'],
                        license='MIT',
                    )
                    """
                )
            )
            with self.assertRaises(SystemExit):
                parse_setup_py(setup_path)

            warning_msg = mock_write_warning.call_args.args[0]

            expected = "Found invalid 'app_package' in setup.py: 'fake_function()'"

            self.assertIn(expected, warning_msg)

            mock_exit.assert_called_once()

    @mock.patch("tethys_cli.gen_commands.write_warning")
    @mock.patch("tethys_cli.gen_commands.exit", side_effect=SystemExit)
    def test_parse_setup_py_no_app_package(self, mock_exit, mock_write_warning):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            setup_path = temp_dir / "setup.py"

            import textwrap

            # Write a fake setup.py into the temp folder
            setup_path.write_text(
                textwrap.dedent(
                    """
                    from setuptools import setup

                    setup(
                        description='A test description',
                        author='Test Author',
                        author_email='test@example.com',
                        keywords=['alpha', 'beta'],
                        license='MIT',
                    )
                    """
                )
            )
            with self.assertRaises(SystemExit):
                parse_setup_py(setup_path)

            warning_msg = mock_write_warning.call_args.args[0]
            expected = "Could not find 'app_package' in setup.py."
            self.assertIn(expected, warning_msg)

            mock_exit.assert_called_once()

    @mock.patch("tethys_cli.gen_commands.write_warning")
    @mock.patch("tethys_cli.gen_commands.exit", side_effect=SystemExit)
    def test_parse_setup_py_invalid_setup_attr(self, mock_exit, mock_write_warning):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            setup_path = temp_dir / "setup.py"

            import textwrap

            # Write a fake setup.py into the temp folder
            setup_path.write_text(
                textwrap.dedent(
                    """
                    from setuptools import setup

                    app_package = 'test_app'

                    setup(
                        description='A test description',
                        author=fake_function(),
                        author_email='test@example.com',
                        keywords=['alpha', 'beta'],
                        license='MIT',
                    )
                    """
                )
            )
            with self.assertRaises(SystemExit):
                parse_setup_py(setup_path)

            warning_msg = mock_write_warning.call_args.args[0]
            expected = "Found invalid 'author' in setup.py: 'fake_function()'"
            self.assertIn(expected, warning_msg)

            mock_exit.assert_called_once()

    @mock.patch("tethys_cli.gen_commands.input", return_value="yes")
    @mock.patch("tethys_cli.gen_commands.write_info")
    @mock.patch("tethys_cli.gen_commands.get_destination_path")
    def test_pyproject_post_process_remove_setup_yes(
        self, mock_gdp, mock_write_info, _
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            setup_path = temp_dir / "setup.py"

            setup_path.write_text("fake content")

            mock_gdp.return_value = temp_dir / "pyproject.toml"

            mock_args = mock.MagicMock(type=GEN_PYPROJECT_OPTION)
            pyproject_post_process(mock_args)

            # Verify setup.py was removed
            self.assertFalse(setup_path.exists())

            mock_write_info.assert_called_once()
            info_msg = mock_write_info.call_args.args[0]
            self.assertIn(f'Removed setup.py file at "{setup_path}".', info_msg)

    @mock.patch("tethys_cli.gen_commands.input", return_value="no")
    @mock.patch("tethys_cli.gen_commands.get_destination_path")
    def test_pyproject_post_process_remove_setup_no(self, mock_gdp, _):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            setup_path = temp_dir / "setup.py"

            setup_path.write_text("fake content")

            mock_gdp.return_value = temp_dir / "pyproject.toml"

            mock_args = mock.MagicMock(type=GEN_PYPROJECT_OPTION)

            pyproject_post_process(mock_args)

            # Verify setup.py still exists
            self.assertTrue(setup_path.exists())

    @mock.patch("tethys_cli.gen_commands.input", return_value="yes")
    @mock.patch("tethys_cli.gen_commands.write_error")
    @mock.patch("tethys_cli.gen_commands.get_destination_path")
    def test_pyproject_post_process_setup_not_found(
        self, mock_gdp, mock_write_error, _
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)

            mock_gdp.return_value = temp_dir / "pyproject.toml"

            mock_args = mock.MagicMock(type=GEN_PYPROJECT_OPTION)

            pyproject_post_process(mock_args)

            mock_write_error.assert_called_once()
            error_msg = mock_write_error.call_args.args[0]
            self.assertIn(
                f'The specified Tethys app directory "{temp_dir}" does not contain a setup.py file',
                error_msg,
            )

    @mock.patch("tethys_cli.gen_commands.write_info")
    @mock.patch("tethys_cli.gen_commands.get_destination_path")
    @mock.patch("tethys_cli.gen_commands.input", side_effect=["invalid", "maybe", "y"])
    def test_pyproject_post_process_invalid_input_retry(self, mock_input, mock_gdp, _):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            setup_path = temp_dir / "setup.py"

            setup_path.write_text("fake content")

            mock_gdp.return_value = temp_dir / "pyproject.toml"

            mock_args = mock.MagicMock(type=GEN_PYPROJECT_OPTION)

            pyproject_post_process(mock_args)

            # Verify setup.py was removed
            self.assertFalse(setup_path.exists())

            # Verify input was called 3 times
            self.assertEqual(mock_input.call_count, 3)
