import pytest
from unittest import mock
from pathlib import Path

from tethys_cli.gen_commands import (
    get_environment_value,
    get_settings_value,
    derive_version_from_conda_environment,
    gen_meta_yaml,
    generate_command,
    gen_vendor_static_files,
    download_vendor_static_files,
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
    GEN_REQUIREMENTS_OPTION,
    VALID_GEN_OBJECTS,
)

from tethys_apps.utilities import get_tethys_src_dir

TETHYS_SRC = get_tethys_src_dir()


def test_get_environment_value():
    result = get_environment_value(value_name="DJANGO_SETTINGS_MODULE")

    assert result == "tethys_portal.settings"


def test_get_environment_value_bad():
    with pytest.raises(EnvironmentError):
        get_environment_value(
            value_name="foo_bar_baz_bad_environment_value_foo_bar_baz"
        )


def test_get_settings_value():
    result = get_settings_value(value_name="INSTALLED_APPS")

    assert "tethys_apps" in result


def test_get_settings_value_bad():
    with pytest.raises(ValueError):
        get_settings_value(value_name="foo_bar_baz_bad_setting_foo_bar_baz")


@mock.patch("tethys_cli.gen_commands.write_info")
@mock.patch("tethys_cli.gen_commands.get_settings_value")
@mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
@mock.patch("tethys_cli.gen_commands.Path.is_file")
def test_generate_command_apache_option(
    mock_is_file, mock_file, mock_settings, mock_write_info
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
    mock_is_file, mock_file, mock_settings, mock_write_info
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
def test_generate_command_nginx_service(mock_is_file, mock_file, mock_write_info):
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
def test_generate_command_apache_service(mock_is_file, mock_file, mock_write_info):
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
    mock_mkdir, mock_is_file, mock_file, mock_write_info, mock_isdir
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
    assert "A Tethys Portal configuration file" in rts_call_args.args[0]


@mock.patch("tethys_cli.gen_commands.write_info")
@mock.patch("tethys_cli.gen_commands.render_template")
@mock.patch("tethys_cli.gen_commands.Path.exists")
@mock.patch("tethys_cli.gen_commands.get_environment_value")
@mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
@mock.patch("tethys_cli.gen_commands.Path.is_file")
def test_generate_command_asgi_service_option_nginx_conf(
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
    assert context["nginx_user"] == "foo_user"

    mock_write_info.assert_called()


@mock.patch("tethys_cli.gen_commands.write_info")
@mock.patch("tethys_cli.gen_commands.get_environment_value")
@mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
@mock.patch("tethys_cli.gen_commands.Path.is_file")
def test_generate_command_asgi_service_option(
    mock_is_file, mock_file, mock_env, mock_write_info
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
    mock_is_file, mock_file, mock_env, mock_write_info
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
    mock_is_file, mock_file, mock_env, mock_is_dir, mock_write_info
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
    assert mock_is_dir.call_count == 2
    mock_env.assert_called_with("CONDA_PREFIX")

    mock_write_info.assert_called()


@mock.patch("tethys_cli.gen_commands.write_error")
@mock.patch("tethys_cli.gen_commands.exit")
@mock.patch("tethys_cli.gen_commands.Path.is_dir")
@mock.patch("tethys_cli.gen_commands.get_environment_value")
@mock.patch("tethys_cli.gen_commands.Path.is_file")
def test_generate_command_asgi_settings_option_bad_directory(
    mock_is_file, mock_env, mock_is_dir, mock_exit, mock_write_error
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

    with pytest.raises(SystemExit):
        generate_command(args=mock_args)

    mock_is_file.assert_not_called()
    assert mock_is_dir.call_count == 2

    # Check if print is called correctly
    rts_call_args = mock_write_error.call_args
    assert "ERROR: " in rts_call_args.args[0]
    assert "is not a valid directory" in rts_call_args.args[0]

    mock_env.assert_called_with("CONDA_PREFIX")


@mock.patch("tethys_cli.gen_commands.write_info")
@mock.patch("tethys_cli.gen_commands.write_warning")
@mock.patch("tethys_cli.gen_commands.exit")
@mock.patch("tethys_cli.gen_commands.input")
@mock.patch("tethys_cli.gen_commands.get_environment_value")
@mock.patch("tethys_cli.gen_commands.Path.is_file")
def test_generate_command_asgi_settings_pre_existing_input_exit(
    mock_is_file, mock_env, mock_input, mock_exit, mock_write_warning, mock_write_info
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

    with pytest.raises(SystemExit):
        generate_command(args=mock_args)

    mock_is_file.assert_called_once()

    # Check if print is called correctly
    rts_call_args = mock_write_warning.call_args
    assert "Generation of" in rts_call_args.args[0]
    assert "cancelled" in rts_call_args.args[0]

    mock_env.assert_called_with("CONDA_PREFIX")


@mock.patch("tethys_cli.gen_commands.write_info")
@mock.patch("tethys_cli.gen_commands.get_environment_value")
@mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
@mock.patch("tethys_cli.gen_commands.Path.is_file")
def test_generate_command_asgi_settings_pre_existing_overwrite(
    mock_is_file, mock_file, mock_env, mock_write_info
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
def test_generate_command_services_option(mock_is_file, mock_file, mock_write_info):
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
def test_generate_command_install_option(mock_write_info, mock_is_file, mock_file):
    mock_args = mock.MagicMock()
    mock_args.type = GEN_INSTALL_OPTION
    mock_args.directory = None
    mock_is_file.return_value = False

    generate_command(args=mock_args)

    rts_call_args = mock_write_info.call_args_list[0]
    assert "Please review the generated install.yml" in rts_call_args.args[0]

    mock_is_file.assert_called_once()
    mock_file.assert_called()


@mock.patch("tethys_cli.gen_commands.run")
@mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
@mock.patch("tethys_cli.gen_commands.Path.is_file")
@mock.patch("tethys_cli.gen_commands.write_warning")
@mock.patch("tethys_cli.gen_commands.write_info")
def test_generate_requirements_option(
    mock_write_info, mock_write_warn, mock_is_file, mock_file, mock_run
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
    mock_print, mock_is_file, mock_file, mock_run_command, mock_load, mock_Template, _
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
    assert expected_context == render_context
    mock_file.assert_called()


@mock.patch("tethys_cli.gen_commands.write_info")
@mock.patch("tethys_cli.gen_commands.derive_version_from_conda_environment")
@mock.patch("tethys_cli.gen_commands.yaml.safe_load")
@mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
def test_gen_meta_yaml_overriding_dependencies(
    _mock_open, mock_load, mock_dvfce, _mock_write_info
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

    assert mock_dvfce.call_count == 1
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
    assert expected_context == ret


@mock.patch("tethys_cli.gen_commands.run_command")
def test_derive_version_from_conda_environment_minor(mock_run_command):
    # More than three version numbers
    stdout = (
        "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
        "#\n"
        "# Name                    Version                   Build  Channel\n"
        "foo                       1.2.3.4.5                 py37_0    conda-forge"
    )
    mock_run_command.return_value = (stdout, "", 0)

    ret = derive_version_from_conda_environment("foo", "minor")

    assert ret == "foo=1.2.*"

    # Three version numbers
    stdout = (
        "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
        "#\n"
        "# Name                    Version                   Build  Channel\n"
        "foo                       1.2.3                     py37_0    conda-forge"
    )
    mock_run_command.return_value = (stdout, "", 0)

    ret = derive_version_from_conda_environment("foo", "minor")

    assert ret == "foo=1.2.*"

    # Two version numbers
    stdout = (
        "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
        "#\n"
        "# Name                    Version                   Build  Channel\n"
        "foo                       1.2                       py37_0    conda-forge"
    )
    mock_run_command.return_value = (stdout, "", 0)

    ret = derive_version_from_conda_environment("foo", "minor")

    assert ret == "foo=1.2"

    # Less than two version numbers
    stdout = (
        "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
        "#\n"
        "# Name                    Version                   Build  Channel\n"
        "foo                       1                         py37_0    conda-forge"
    )
    mock_run_command.return_value = (stdout, "", 0)

    ret = derive_version_from_conda_environment("foo", "minor")

    assert ret == "foo"


@mock.patch("tethys_cli.gen_commands.run_command")
def test_derive_version_from_conda_environment_major(mock_run_command):
    # More than three version numbers
    stdout = (
        "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
        "#\n"
        "# Name                    Version                   Build  Channel\n"
        "foo                       1.2.3.4.5                 py37_0    conda-forge"
    )
    mock_run_command.return_value = (stdout, "", 0)

    ret = derive_version_from_conda_environment("foo", "major")

    assert ret == "foo=1.*"

    # Three version numbers
    stdout = (
        "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
        "#\n"
        "# Name                    Version                   Build  Channel\n"
        "foo                       1.2.3                     py37_0    conda-forge"
    )
    mock_run_command.return_value = (stdout, "", 0)

    ret = derive_version_from_conda_environment("foo", "major")

    assert ret == "foo=1.*"

    # Two version numbers
    stdout = (
        "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
        "#\n"
        "# Name                    Version                   Build  Channel\n"
        "foo                       1.2                       py37_0    conda-forge"
    )
    mock_run_command.return_value = (stdout, "", 0)

    ret = derive_version_from_conda_environment("foo", "major")

    assert ret == "foo=1.*"

    # Less than two version numbers
    stdout = (
        "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
        "#\n"
        "# Name                    Version                   Build  Channel\n"
        "foo                       1                         py37_0    conda-forge"
    )
    mock_run_command.return_value = (stdout, "", 0)

    ret = derive_version_from_conda_environment("foo", "major")

    assert ret == "foo=1"


@mock.patch("tethys_cli.gen_commands.run_command")
def test_derive_version_from_conda_environment_patch(mock_run_command):
    # More than three version numbers
    stdout = (
        "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
        "#\n"
        "# Name                    Version                   Build  Channel\n"
        "foo                       1.2.3.4.5                 py37_0    conda-forge"
    )
    mock_run_command.return_value = (stdout, "", 0)

    ret = derive_version_from_conda_environment("foo", "patch")

    assert ret == "foo=1.2.3.*"

    # Three version numbers
    stdout = (
        "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
        "#\n"
        "# Name                    Version                   Build  Channel\n"
        "foo                       1.2.3                     py37_0    conda-forge"
    )
    mock_run_command.return_value = (stdout, "", 0)

    ret = derive_version_from_conda_environment("foo", "patch")

    assert ret == "foo=1.2.3"

    # Two version numbers
    stdout = (
        "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
        "#\n"
        "# Name                    Version                   Build  Channel\n"
        "foo                       1.2                       py37_0    conda-forge"
    )
    mock_run_command.return_value = (stdout, "", 0)

    ret = derive_version_from_conda_environment("foo", "patch")

    assert ret == "foo=1.2"

    # Less than two version numbers
    stdout = (
        "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
        "#\n"
        "# Name                    Version                   Build  Channel\n"
        "foo                       1                         py37_0    conda-forge"
    )
    mock_run_command.return_value = (stdout, "", 0)

    ret = derive_version_from_conda_environment("foo", "patch")

    assert ret == "foo=1"


@mock.patch("tethys_cli.gen_commands.run_command")
def test_derive_version_from_conda_environment_none(mock_run_command):
    # More than three version numbers
    stdout = (
        "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
        "#\n"
        "# Name                    Version                   Build  Channel\n"
        "foo                       1.2.3.4.5                 py37_0    conda-forge"
    )
    mock_run_command.return_value = (stdout, "", 0)

    ret = derive_version_from_conda_environment("foo", "none")

    assert ret == "foo"

    # Three version numbers
    stdout = (
        "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
        "#\n"
        "# Name                    Version                   Build  Channel\n"
        "foo                       1.2.3                     py37_0    conda-forge"
    )
    mock_run_command.return_value = (stdout, "", 0)

    ret = derive_version_from_conda_environment("foo", "none")

    assert ret == "foo"

    # Two version numbers
    stdout = (
        "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
        "#\n"
        "# Name                    Version                   Build  Channel\n"
        "foo                       1.2                       py37_0    conda-forge"
    )
    mock_run_command.return_value = (stdout, "", 0)

    ret = derive_version_from_conda_environment("foo", "none")

    assert ret == "foo"

    # Less than two version numbers
    stdout = (
        "# packages in environment at /home/nswain/miniconda/envs/tethys:\n"
        "#\n"
        "# Name                    Version                   Build  Channel\n"
        "foo                       1                         py37_0    conda-forge"
    )
    mock_run_command.return_value = (stdout, "", 0)

    ret = derive_version_from_conda_environment("foo", "none")

    assert ret == "foo"


@mock.patch("tethys_cli.gen_commands.print")
@mock.patch("tethys_cli.gen_commands.run_command")
def test_derive_version_from_conda_environment_conda_list_error(
    mock_run_command, mock_print
):
    # More than three version numbers
    mock_run_command.return_value = ("", "Some error", 1)

    ret = derive_version_from_conda_environment("foo", "minor")

    assert ret == "foo"

    rts_call_args_list = mock_print.call_args_list
    assert (
        rts_call_args_list[0].args[0]
        == 'ERROR: Something went wrong looking up dependency "foo" in environment'
    )
    assert rts_call_args_list[1].args[0] == "Some error"


def test_gen_vendor_static_files():
    context = gen_vendor_static_files(mock.MagicMock())
    for _, v in context.items():
        assert v is not None


@mock.patch("tethys_cli.gen_commands.call")
def test_download_vendor_static_files(mock_call):
    download_vendor_static_files(mock.MagicMock())
    mock_call.assert_called_once()


@mock.patch("tethys_cli.gen_commands.write_error")
@mock.patch("tethys_cli.gen_commands.call")
def test_download_vendor_static_files_no_npm(mock_call, mock_error):
    mock_call.side_effect = FileNotFoundError
    download_vendor_static_files(mock.MagicMock())
    mock_call.assert_called_once()
    mock_error.assert_called_once()


@mock.patch("tethys_cli.gen_commands.has_module")
@mock.patch("tethys_cli.gen_commands.write_error")
@mock.patch("tethys_cli.gen_commands.call")
def test_download_vendor_static_files_no_npm_no_conda(
    mock_call, mock_error, mock_has_module
):
    mock_call.side_effect = FileNotFoundError
    mock_has_module.return_value = False
    download_vendor_static_files(mock.MagicMock())
    mock_call.assert_called_once()
    mock_error.assert_called_once()


@mock.patch("tethys_cli.gen_commands.check_for_existing_file")
@mock.patch("tethys_cli.gen_commands.Path.is_dir", return_value=True)
def test_get_destination_path_vendor(mock_isdir, mock_check_file):
    mock_args = mock.MagicMock(
        type=GEN_PACKAGE_JSON_OPTION,
        directory=False,
    )
    result = get_destination_path(mock_args)
    mock_isdir.assert_called()
    mock_check_file.assert_called_once()
    assert result == str(Path(TETHYS_SRC) / "tethys_portal" / "static" / "package.json")


@mock.patch("tethys_cli.gen_commands.GEN_COMMANDS")
@mock.patch("tethys_cli.gen_commands.write_path_to_console")
@mock.patch("tethys_cli.gen_commands.render_template")
@mock.patch("tethys_cli.gen_commands.get_destination_path")
def test_generate_commmand_post_process_func(
    mock_get_path, mock_render, mock_write_path, mock_commands
):
    mock_commands.__getitem__.return_value = (mock.MagicMock(), mock.MagicMock())
    mock_args = mock.MagicMock(
        type="test",
    )
    generate_command(mock_args)
    mock_get_path.assert_called_once_with(mock_args)
    mock_render.assert_called_once()
    mock_write_path.assert_called_once()
    mock_commands.__getitem__.assert_called_once()


def test_templates_exist():
    template_dir = Path(TETHYS_SRC) / "tethys_cli" / "gen_templates"
    for file_name in VALID_GEN_OBJECTS:
        template_path = template_dir / file_name
        assert template_path.exists()


@mock.patch("tethys_cli.gen_commands.Path.is_dir")
@mock.patch("tethys_cli.gen_commands.write_info")
@mock.patch("tethys_cli.gen_commands.Path.open", new_callable=mock.mock_open)
@mock.patch("tethys_cli.gen_commands.Path.is_file")
@mock.patch("tethys_cli.gen_commands.Path.mkdir")
@pytest.mark.django_db
def test_generate_command_secrets_yaml_tethys_home_not_exists(
    mock_mkdir, mock_is_file, mock_file, mock_write_info, mock_isdir, test_app
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
    assert "A Tethys Secrets file" in rts_call_args.args[0]
