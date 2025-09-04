import pytest
import unittest
from unittest import mock
import tethys_cli.cli_helpers as cli_helper
from tethys_apps.models import TethysApp
from django.core.signing import Signer, BadSignature


class TestCliHelper(unittest.TestCase):
    def setUp(self):
        self.test_app = TethysApp.objects.get(package="test_app")

    def tearDown(self):
        pass

    @pytest.mark.django_db
    def test_add_geoserver_rest_to_endpoint(self):
        endpoint = "http://localhost:8181/geoserver/rest/"
        ret = cli_helper.add_geoserver_rest_to_endpoint(endpoint)
        self.assertEqual(endpoint, ret)

    @mock.patch("tethys_cli.cli_helpers.pretty_output")
    @mock.patch("tethys_cli.cli_helpers.exit")
    @pytest.mark.django_db
    def test_get_manage_path_error(self, mock_exit, mock_pretty_output):
        # mock the system exit
        mock_exit.side_effect = SystemExit

        # mock the input args with manage attribute
        args = mock.MagicMock(manage="foo")

        self.assertRaises(SystemExit, cli_helper.get_manage_path, args=args)

        # check the mock exit value
        mock_exit.assert_called_with(1)
        mock_pretty_output.assert_called()

    @pytest.mark.django_db
    def test_get_manage_path(self):
        # mock the input args with manage attribute
        args = mock.MagicMock(manage="")

        # call the method
        ret = cli_helper.get_manage_path(args=args)

        # check whether the response has manage
        self.assertIn("manage.py", ret)

    @mock.patch("tethys_cli.cli_helpers.subprocess.call")
    @mock.patch("tethys_cli.cli_helpers.set_testing_environment")
    @pytest.mark.django_db
    def test_run_process(self, mock_te_call, mock_subprocess_call):
        # mock the process
        mock_process = ["test"]

        cli_helper.run_process(mock_process)

        self.assertEqual(2, len(mock_te_call.call_args_list))

        mock_subprocess_call.assert_called_with(mock_process)

    @mock.patch("tethys_cli.cli_helpers.subprocess.call")
    @mock.patch("tethys_cli.cli_helpers.set_testing_environment")
    @pytest.mark.django_db
    def test_run_process_keyboardinterrupt(self, mock_te_call, mock_subprocess_call):
        # mock the process
        mock_process = ["foo"]

        mock_subprocess_call.side_effect = KeyboardInterrupt

        cli_helper.run_process(mock_process)
        mock_subprocess_call.assert_called_with(mock_process)
        mock_te_call.assert_called_once()

    @mock.patch("tethys_cli.cli_helpers.django.setup")
    @pytest.mark.django_db
    def test_setup_django(self, mock_django_setup):
        cli_helper.setup_django()
        mock_django_setup.assert_called()

    @mock.patch("tethys_cli.cli_helpers.django.setup")
    @pytest.mark.django_db
    def test_setup_django_supress_output(self, mock_django_setup):
        cli_helper.setup_django(supress_output=True)
        mock_django_setup.assert_called()

    @mock.patch("tethys_cli.cli_helpers.bcrypt.gensalt")
    @pytest.mark.django_db
    def test_generate_salt_string(self, mock_bcrypt_gensalt):
        fake_salt = "my_random_encrypted_string"
        mock_bcrypt_gensalt.return_value = fake_salt
        my_fake_salt_from_tested_func = cli_helper.generate_salt_string()
        self.assertEqual(my_fake_salt_from_tested_func, fake_salt)

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
        self,
        mock_open_file,
        mock_salt_string,
        mock_yaml_safe_load,
        mock_yaml_dumps,
        mock_write_success,
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
        custom_secret_setting = self.test_app.settings_set.select_subclasses().get(
            name="Secret_Test2_without_required"
        )
        custom_secret_setting.value = "SECRETXX1Y"
        custom_secret_setting.clean()
        custom_secret_setting.save()

        mock_yaml_safe_load.return_value = before_content

        cli_helper.gen_salt_string_for_setting("test_app", custom_secret_setting)

        mock_yaml_dumps.assert_called_once_with(
            after_content, mock_open_file.return_value
        )
        mock_write_success.assert_called()
        self.assertEqual(custom_secret_setting.get_value(), "SECRETXX1Y")

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
        self,
        mock_open_file,
        mock_salt_string,
        mock_secrets_signed_unsigned_value,
        mock_yaml_safe_load,
        mock_yaml_dumps,
        mock_write_success,
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
        custom_secret_setting = self.test_app.settings_set.select_subclasses().get(
            name="Secret_Test2_without_required"
        )
        signer = Signer(salt="my_first_fake_string")

        new_val = signer.sign_object("SECRETXX1Y")

        custom_secret_setting.value = new_val
        custom_secret_setting.save()

        mock_secrets_signed_unsigned_value.return_value = "SECRETXX1Y"

        mock_yaml_safe_load.return_value = before_content

        cli_helper.gen_salt_string_for_setting("test_app", custom_secret_setting)

        mock_yaml_dumps.assert_called_once_with(
            after_content, mock_open_file.return_value
        )
        mock_write_success.assert_called()
        custom_secret_setting.get_value()
        self.assertEqual(custom_secret_setting.get_value(), "SECRETXX1Y")

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
        self,
        mock_open_file,
        mock_salt_string,
        mock_yaml_safe_load,
        mock_yaml_dumps,
        mock_write_success,
        mock_write_warning,
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
        custom_secret_setting = self.test_app.settings_set.select_subclasses().get(
            name="Secret_Test2_without_required"
        )
        custom_secret_setting.value = "SECRETXX1Y"
        custom_secret_setting.clean()
        custom_secret_setting.save()

        mock_yaml_safe_load.return_value = before_content

        cli_helper.gen_salt_string_for_setting("test_app", custom_secret_setting)

        mock_yaml_dumps.assert_called_once_with(
            after_content, mock_open_file.return_value
        )
        mock_write_success.assert_called()
        self.assertEqual(mock_write_warning.call_count, 2)
        self.assertEqual(custom_secret_setting.get_value(), "SECRETXX1Y")

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
        self,
        mock_open_file,
        mock_salt_string,
        mock_secrets_signed_unsigned_value,
        mock_yaml_safe_load,
        mock_write_warning,
    ):
        mock_salt_string.return_value.decode.return_value = "my_fake_string"

        before_content = {"secrets": {"version": "1.0"}}

        custom_secret_setting = self.test_app.settings_set.select_subclasses().get(
            name="Secret_Test2_without_required"
        )

        custom_secret_setting.value = "SECRETXX1Y"
        custom_secret_setting.clean()
        custom_secret_setting.save()

        mock_secrets_signed_unsigned_value.side_effect = BadSignature
        mock_yaml_safe_load.return_value = before_content
        with self.assertRaises(BadSignature):
            cli_helper.gen_salt_string_for_setting("test_app", custom_secret_setting)

        self.assertEqual(mock_write_warning.call_count, 0)
