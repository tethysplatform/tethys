import pytest
from unittest import mock
import tethys_cli.cli_helpers as cli_helper
from django.core.signing import Signer, BadSignature


@pytest.mark.django_db
def test_add_geoserver_rest_to_endpoint():
    endpoint = "http://localhost:8181/geoserver/rest/"
    ret = cli_helper.add_geoserver_rest_to_endpoint(endpoint)
    assert endpoint == ret


@mock.patch("tethys_cli.cli_helpers.pretty_output")
@mock.patch("tethys_cli.cli_helpers.exit")
@pytest.mark.django_db
def test_get_manage_path_error(mock_exit, mock_pretty_output):
    mock_exit.side_effect = SystemExit
    args = mock.MagicMock(manage="foo")
    with pytest.raises(SystemExit):
        cli_helper.get_manage_path(args=args)
    mock_exit.assert_called_with(1)
    mock_pretty_output.assert_called()


@pytest.mark.django_db
def test_get_manage_path():
    args = mock.MagicMock(manage="")
    ret = cli_helper.get_manage_path(args=args)
    assert "manage.py" in ret


@mock.patch("tethys_cli.cli_helpers.subprocess.call")
@mock.patch("tethys_cli.cli_helpers.set_testing_environment")
@pytest.mark.django_db
def test_run_process(mock_te_call, mock_subprocess_call):
    mock_process = ["test"]
    cli_helper.run_process(mock_process)
    assert len(mock_te_call.call_args_list) == 2
    mock_subprocess_call.assert_called_with(mock_process)


@mock.patch("tethys_cli.cli_helpers.subprocess.call")
@mock.patch("tethys_cli.cli_helpers.set_testing_environment")
@pytest.mark.django_db
def test_run_process_keyboardinterrupt(mock_te_call, mock_subprocess_call):
    mock_process = ["foo"]
    mock_subprocess_call.side_effect = KeyboardInterrupt
    cli_helper.run_process(mock_process)
    mock_subprocess_call.assert_called_with(mock_process)
    mock_te_call.assert_called_once()


@mock.patch("tethys_cli.cli_helpers.django.setup")
@pytest.mark.django_db
def test_setup_django(mock_django_setup):
    cli_helper.setup_django()
    mock_django_setup.assert_called()


@mock.patch("tethys_cli.cli_helpers.django.setup")
@pytest.mark.django_db
def test_setup_django_supress_output(mock_django_setup):
    cli_helper.setup_django(supress_output=True)
    mock_django_setup.assert_called()


@mock.patch("tethys_cli.cli_helpers.bcrypt.gensalt")
@pytest.mark.django_db
def test_generate_salt_string(mock_bcrypt_gensalt):
    fake_salt = "my_random_encrypted_string"
    mock_bcrypt_gensalt.return_value = fake_salt
    my_fake_salt_from_tested_func = cli_helper.generate_salt_string()
    assert my_fake_salt_from_tested_func == fake_salt


@mock.patch("tethys_cli.cli_helpers.write_success")
@mock.patch("tethys_cli.cli_helpers.yaml.dump")
@mock.patch("tethys_cli.cli_helpers.yaml.safe_load")
@mock.patch("tethys_cli.cli_helpers.generate_salt_string")
@mock.patch(
    "tethys_cli.cli_helpers.Path.open",
    new_callable=lambda: mock.mock_open(read_data='{"secrets": "{}"}'),
)
@pytest.mark.django_db
def test_gen_salt_string_for_setting_with_no_previous_salt_strings(
    mock_open_file,
    mock_salt_string,
    mock_yaml_safe_load,
    mock_yaml_dumps,
    mock_write_success,
    test_app,
):
    mock_salt_string.return_value.decode.return_value = "my_fake_string"
    app_target_name = "test_app"
    before_content = {
        "secrets": {
            app_target_name: {"custom_settings_salt_strings": {}},
            "version": "1.0",
        }
    }
    after_content = {
        "secrets": {
            app_target_name: {
                "custom_settings_salt_strings": {
                    "Secret_Test2_without_required": "my_fake_string"
                }
            },
            "version": "1.0",
        }
    }
    custom_secret_setting = test_app.settings_set.select_subclasses().get(
        name="Secret_Test2_without_required"
    )
    custom_secret_setting.value = "SECRETXX1Y"
    custom_secret_setting.clean()
    custom_secret_setting.save()
    mock_yaml_safe_load.return_value = before_content
    cli_helper.gen_salt_string_for_setting("test_app", custom_secret_setting)
    mock_yaml_dumps.assert_called_once_with(after_content, mock_open_file.return_value)
    mock_write_success.assert_called()
    assert custom_secret_setting.get_value() == "SECRETXX1Y"


@mock.patch("tethys_cli.cli_helpers.write_success")
@mock.patch("tethys_cli.cli_helpers.yaml.dump")
@mock.patch("tethys_cli.cli_helpers.yaml.safe_load")
@mock.patch("tethys_cli.cli_helpers.secrets_signed_unsigned_value")
@mock.patch("tethys_cli.cli_helpers.generate_salt_string")
@mock.patch(
    "tethys_cli.cli_helpers.Path.open",
    new_callable=lambda: mock.mock_open(read_data='{"secrets": "{}"}'),
)
@pytest.mark.django_db
def test_gen_salt_string_for_setting_with_previous_salt_strings(
    mock_open_file,
    mock_salt_string,
    mock_secrets_signed_unsigned_value,
    mock_yaml_safe_load,
    mock_yaml_dumps,
    mock_write_success,
    test_app,
):
    mock_salt_string.return_value.decode.return_value = "my_last_fake_string"
    app_target_name = "test_app"
    before_content = {
        "secrets": {
            app_target_name: {
                "custom_settings_salt_strings": {
                    "Secret_Test2_without_required": "my_first_fake_string"
                }
            },
            "version": "1.0",
        }
    }
    after_content = {
        "secrets": {
            app_target_name: {
                "custom_settings_salt_strings": {
                    "Secret_Test2_without_required": "my_last_fake_string"
                }
            },
            "version": "1.0",
        }
    }
    custom_secret_setting = test_app.settings_set.select_subclasses().get(
        name="Secret_Test2_without_required"
    )
    signer = Signer(salt="my_first_fake_string")
    new_val = signer.sign_object("SECRETXX1Y")
    custom_secret_setting.value = new_val
    custom_secret_setting.save()
    mock_secrets_signed_unsigned_value.return_value = "SECRETXX1Y"
    mock_yaml_safe_load.return_value = before_content
    cli_helper.gen_salt_string_for_setting("test_app", custom_secret_setting)
    mock_yaml_dumps.assert_called_once_with(after_content, mock_open_file.return_value)
    mock_write_success.assert_called()
    custom_secret_setting.get_value()
    assert custom_secret_setting.get_value() == "SECRETXX1Y"


@mock.patch("tethys_cli.cli_helpers.write_warning")
@mock.patch("tethys_cli.cli_helpers.write_success")
@mock.patch("tethys_cli.cli_helpers.yaml.dump")
@mock.patch("tethys_cli.cli_helpers.yaml.safe_load")
@mock.patch("tethys_cli.cli_helpers.generate_salt_string")
@mock.patch(
    "tethys_cli.cli_helpers.Path.open",
    new_callable=lambda: mock.mock_open(read_data='{"secrets": "{}"}'),
)
@pytest.mark.django_db
def test_gen_salt_string_for_setting_with_empty_secrets(
    mock_open_file,
    mock_salt_string,
    mock_yaml_safe_load,
    mock_yaml_dumps,
    mock_write_success,
    mock_write_warning,
    test_app,
):
    mock_salt_string.return_value.decode.return_value = "my_fake_string"
    app_target_name = "test_app"
    before_content = {"secrets": {"version": "1.0"}}
    after_content = {
        "secrets": {
            app_target_name: {
                "custom_settings_salt_strings": {
                    "Secret_Test2_without_required": "my_fake_string"
                }
            },
            "version": "1.0",
        }
    }
    custom_secret_setting = test_app.settings_set.select_subclasses().get(
        name="Secret_Test2_without_required"
    )
    custom_secret_setting.value = "SECRETXX1Y"
    custom_secret_setting.clean()
    custom_secret_setting.save()
    mock_yaml_safe_load.return_value = before_content
    cli_helper.gen_salt_string_for_setting("test_app", custom_secret_setting)
    mock_yaml_dumps.assert_called_once_with(after_content, mock_open_file.return_value)
    mock_write_success.assert_called()
    assert mock_write_warning.call_count == 2
    assert custom_secret_setting.get_value() == "SECRETXX1Y"


@mock.patch("tethys_cli.cli_helpers.write_warning")
@mock.patch("tethys_cli.cli_helpers.yaml.safe_load")
@mock.patch("tethys_cli.cli_helpers.secrets_signed_unsigned_value")
@mock.patch("tethys_cli.cli_helpers.generate_salt_string")
@mock.patch(
    "tethys_cli.cli_helpers.Path.open",
    new_callable=lambda: mock.mock_open(read_data='{"secrets": "{}"}'),
)
@pytest.mark.django_db
def test_gen_salt_string_for_setting_with_secrets_deleted_or_changed(
    mock_open_file,
    mock_salt_string,
    mock_secrets_signed_unsigned_value,
    mock_yaml_safe_load,
    mock_write_warning,
    test_app,
):
    mock_salt_string.return_value.decode.return_value = "my_fake_string"
    before_content = {"secrets": {"version": "1.0"}}
    custom_secret_setting = test_app.settings_set.select_subclasses().get(
        name="Secret_Test2_without_required"
    )
    custom_secret_setting.value = "SECRETXX1Y"
    custom_secret_setting.clean()
    custom_secret_setting.save()
    mock_secrets_signed_unsigned_value.side_effect = BadSignature
    mock_yaml_safe_load.return_value = before_content
    with pytest.raises(BadSignature):
        cli_helper.gen_salt_string_for_setting("test_app", custom_secret_setting)
    assert mock_write_warning.call_count == 0

    @mock.patch("tethys_cli.cli_helpers.subprocess.Popen")
    @mock.patch("tethys_cli.cli_helpers.os.environ.get")
    @mock.patch("tethys_cli.cli_helpers.shutil.which")
    @mock.patch("tethys_cli.cli_helpers.import_module")
    def test_new_conda_run_command(
        self,
        mock_import_module,
        mock_shutil_which,
        mock_os_environ_get,
        mock_popen,
    ):
        # Force fallback to shell implementation (import fails)
        mock_import_module.side_effect = ImportError

        mock_shutil_which.side_effect = ["/usr/bin/conda", None, None]
        mock_os_environ_get.side_effect = [None, None]

        # Proc mock: communicate() tuple + returncode
        proc = mock.MagicMock()
        proc.communicate.return_value = ("conda list output", "")
        proc.returncode = 0
        mock_popen.return_value = proc

        conda_run_func = cli_helper.conda_run_command()
        stdout, stderr, returncode = conda_run_func("list", "")

        self.assertEqual(stdout, "conda list output")
        self.assertEqual(stderr, "")
        self.assertEqual(returncode, 0)

        # Ensure Popen was called with the resolved exe and command
        called_cmd = mock_popen.call_args[0][0]
        self.assertEqual(called_cmd[:2], ["/usr/bin/conda", "list"])
        # stdout/stderr default to PIPE when not provided
        self.assertEqual(
            mock_popen.call_args.kwargs.get("stdout"), -1
        )  # passed positionally
        self.assertEqual(
            mock_popen.call_args.kwargs.get("stderr"), -1
        )  # passed positionally

    @mock.patch("tethys_cli.cli_helpers.subprocess.Popen")
    @mock.patch("tethys_cli.cli_helpers.os.environ.get")
    @mock.patch("tethys_cli.cli_helpers.shutil.which")
    @mock.patch("tethys_cli.cli_helpers.import_module")
    def test_new_conda_run_command_with_error(
        self,
        mock_import_module,
        mock_shutil_which,
        mock_os_environ_get,
        mock_popen,
    ):
        mock_import_module.side_effect = ImportError
        # No executables discovered
        mock_shutil_which.side_effect = [None, None, None]
        mock_os_environ_get.side_effect = [None, None]

        conda_run_func = cli_helper.conda_run_command()
        stdout, stderr, returncode = conda_run_func("list", "")

        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "conda executable not found on PATH")
        self.assertEqual(returncode, 1)
        mock_popen.assert_not_called()

    @mock.patch("tethys_cli.cli_helpers.subprocess.Popen")
    @mock.patch("tethys_cli.cli_helpers.os.environ.get")
    @mock.patch("tethys_cli.cli_helpers.shutil.which")
    @mock.patch("tethys_cli.cli_helpers.import_module")
    def test_new_conda_run_command_keyboard_interrupt(
        self, mock_import_module, mock_which, mock_env_get, mock_popen
    ):
        # Force fallback to _shell_run_command
        mock_import_module.side_effect = ImportError

        # Make exe discovery succeed
        mock_which.side_effect = ["/usr/bin/conda", None, None]
        mock_env_get.side_effect = [None, None]

        # Configure the Popen instance
        proc = mock.MagicMock()
        # First communicate raises KeyboardInterrupt; second returns empty output
        proc.communicate.side_effect = [KeyboardInterrupt, ("", "")]
        proc.returncode = 0
        mock_popen.return_value = proc

        conda_run_func = cli_helper.conda_run_command()
        stdout, stderr, rc = conda_run_func("list", "")

        self.assertEqual((stdout, stderr, rc), ("", "", 0))
        proc.terminate.assert_called_once()

        # sanity: check command used
        called_cmd = mock_popen.call_args[0][0]
        self.assertEqual(called_cmd[:2], ["/usr/bin/conda", "list"])

    @mock.patch("tethys_cli.cli_helpers.optional_import")  # CHANGED
    def test_legacy_conda_run_command(self, mock_optional_import):
        mock_optional_import.return_value = lambda command, *args, **kwargs: (
            "stdout",
            "stderr",
            0,
        )
        conda_run_func = cli_helper.conda_run_command()
        stdout, stderr, returncode = conda_run_func("list", "")
        self.assertEqual(stdout, "stdout")
        self.assertEqual(stderr, "stderr")
        self.assertEqual(returncode, 0)

    @mock.patch("tethys_cli.cli_helpers.subprocess.Popen")
    @mock.patch("tethys_cli.cli_helpers.os.environ.get")
    @mock.patch("tethys_cli.cli_helpers.shutil.which")
    @mock.patch("tethys_cli.cli_helpers.import_module")
    def test_shell_run_command_auto_yes_for_install(
        self,
        mock_import_module,
        mock_shutil_which,
        mock_os_environ_get,
        mock_popen,
    ):
        mock_import_module.side_effect = ImportError
        mock_shutil_which.side_effect = ["/usr/bin/conda", None, None]
        mock_os_environ_get.side_effect = [None, None]

        proc = mock.MagicMock()
        proc.communicate.return_value = ("", "")
        proc.returncode = 0
        mock_popen.return_value = proc

        conda_run_func = cli_helper.conda_run_command()
        conda_run_func("install", "numpy")

        called_cmd = mock_popen.call_args[0][0]
        self.assertEqual(called_cmd[0:2], ["/usr/bin/conda", "install"])
        self.assertIn("--yes", called_cmd)

    @mock.patch("tethys_cli.cli_helpers.import_module")
    def test_load_conda_commands_first_module_success(self, mock_import_module):
        """Test load_conda_commands when first module (conda.cli.python_api) is available"""
        mock_commands = mock.MagicMock()
        mock_module = mock.MagicMock()
        mock_module.Commands = mock_commands
        mock_import_module.return_value = mock_module

        result = cli_helper.load_conda_commands()

        mock_import_module.assert_called_once_with("conda.cli.python_api")
        self.assertEqual(result, mock_commands)

    @mock.patch("tethys_cli.cli_helpers.import_module")
    def test_load_conda_commands_second_module_success(self, mock_import_module):
        """Test load_conda_commands when second module (conda.testing.integration) is available"""
        mock_commands = mock.MagicMock()
        mock_module = mock.MagicMock()
        mock_module.Commands = mock_commands

        # First call raises ImportError, second call succeeds
        mock_import_module.side_effect = [ImportError("Module not found"), mock_module]

        result = cli_helper.load_conda_commands()

        # Should have tried both modules
        expected_calls = [
            mock.call("conda.cli.python_api"),
            mock.call("conda.testing.integration"),
        ]
        mock_import_module.assert_has_calls(expected_calls)
        self.assertEqual(result, mock_commands)

    @mock.patch("tethys_cli.cli_helpers.import_module")
    def test_load_conda_commands_attribute_error(self, mock_import_module):
        """Test load_conda_commands when modules exist but don't have Commands attribute"""
        mock_module = mock.MagicMock()
        del mock_module.Commands  # Remove Commands attribute to trigger AttributeError

        # First call raises AttributeError, second call raises ImportError
        mock_import_module.side_effect = [mock_module, ImportError("Module not found")]

        result = cli_helper.load_conda_commands()

        # Should have tried both modules and fallen back to local commands
        expected_calls = [
            mock.call("conda.cli.python_api"),
            mock.call("conda.testing.integration"),
        ]
        mock_import_module.assert_has_calls(expected_calls)
        self.assertEqual(result, cli_helper._LocalCondaCommands)

    @mock.patch("tethys_cli.cli_helpers.import_module")
    def test_load_conda_commands_fallback_to_local(self, mock_import_module):
        """Test load_conda_commands falls back to _LocalCondaCommands when all modules fail"""
        # Both import attempts fail
        mock_import_module.side_effect = [
            ImportError("conda.cli.python_api not found"),
            ImportError("conda.testing.integration not found"),
        ]

        result = cli_helper.load_conda_commands()

        # Should have tried both modules
        expected_calls = [
            mock.call("conda.cli.python_api"),
            mock.call("conda.testing.integration"),
        ]
        mock_import_module.assert_has_calls(expected_calls)
        self.assertEqual(result, cli_helper._LocalCondaCommands)

    def test_local_conda_commands_attributes(self):
        """Test that _LocalCondaCommands has expected attributes"""
        commands = cli_helper._LocalCondaCommands

        # Test that all expected command attributes exist
        expected_commands = [
            "COMPARE",
            "CONFIG",
            "CLEAN",
            "CREATE",
            "INFO",
            "INSTALL",
            "LIST",
            "REMOVE",
            "SEARCH",
            "UPDATE",
            "RUN",
        ]

        for command in expected_commands:
            self.assertTrue(hasattr(commands, command))
            self.assertEqual(getattr(commands, command), command.lower())
