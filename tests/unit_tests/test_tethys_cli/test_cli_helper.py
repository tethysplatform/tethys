import unittest
from unittest import mock
import tethys_cli.cli_helpers as cli_helper
from tethys_apps.models import TethysApp, CustomSecretSetting


class TestCliHelper(unittest.TestCase):
    def setUp(self):
        self.test_app = TethysApp.objects.get(package="test_app")

    def tearDown(self):
        pass

    def test_add_geoserver_rest_to_endpoint(self):
        endpoint = "http://localhost:8181/geoserver/rest/"
        ret = cli_helper.add_geoserver_rest_to_endpoint(endpoint)
        self.assertEqual(endpoint, ret)

    @mock.patch("tethys_cli.cli_helpers.pretty_output")
    @mock.patch("tethys_cli.cli_helpers.exit")
    def test_get_manage_path_error(self, mock_exit, mock_pretty_output):
        # mock the system exit
        mock_exit.side_effect = SystemExit

        # mock the input args with manage attribute
        args = mock.MagicMock(manage="foo")

        self.assertRaises(SystemExit, cli_helper.get_manage_path, args=args)

        # check the mock exit value
        mock_exit.assert_called_with(1)
        mock_pretty_output.assert_called()

    def test_get_manage_path(self):
        # mock the input args with manage attribute
        args = mock.MagicMock(manage="")

        # call the method
        ret = cli_helper.get_manage_path(args=args)

        # check whether the response has manage
        self.assertIn("manage.py", ret)

    @mock.patch("tethys_cli.cli_helpers.subprocess.call")
    @mock.patch("tethys_cli.cli_helpers.set_testing_environment")
    def test_run_process(self, mock_te_call, mock_subprocess_call):

        # mock the process
        mock_process = ["test"]

        cli_helper.run_process(mock_process)

        self.assertEqual(2, len(mock_te_call.call_args_list))

        mock_subprocess_call.assert_called_with(mock_process)

    @mock.patch("tethys_cli.cli_helpers.subprocess.call")
    @mock.patch("tethys_cli.cli_helpers.set_testing_environment")
    def test_run_process_keyboardinterrupt(self, mock_te_call, mock_subprocess_call):

        # mock the process
        mock_process = ["foo"]

        mock_subprocess_call.side_effect = KeyboardInterrupt

        cli_helper.run_process(mock_process)
        mock_subprocess_call.assert_called_with(mock_process)
        mock_te_call.assert_called_once()

    @mock.patch("tethys_cli.cli_helpers.django.setup")
    def test_load_apps(self, mock_django_setup):
        cli_helper.load_apps()
        mock_django_setup.assert_called()

    @mock.patch("tethys_cli.cli_helpers.bcrypt.gensalt")
    def test_generate_salt_string(self, mock_bcrypt_gensalt):
        fake_salt = "my_random_encrypted_string"
        mock_bcrypt_gensalt.return_value = fake_salt
        my_fake_salt_from_tested_func = cli_helper.generate_salt_string()
        self.assertEqual(my_fake_salt_from_tested_func, fake_salt)

    @mock.patch("tethys_cli.cli_helpers.write_success")
    @mock.patch("tethys_cli.cli_helpers.write_error")
    @mock.patch("tethys_cli.cli_helpers.open", new_callable=mock.mock_open, read_data='{"secrets": "{}"}')
    @mock.patch("tethys_apps.models.os.path.exists")
    @mock.patch("tethys_cli.cli_helpers.yaml.dump")
    @mock.patch("tethys_cli.cli_helpers.yaml.safe_load")
    @mock.patch("tethys_cli.cli_helpers.generate_salt_string")

    def test_gen_salt_string_for_setting_with_no_previous_salt_strings(self,mock_write_success,mock_write_error,mock_open_file,mock_os_path_exists,mock_yaml_dumps,mock_yaml_safe_load,mock_salt_string):

        mock_salt_string.return_value = "my_fake_string"

        app_target_name = 'test_app'
        
        mock_yaml_safe_load.return_value = {
            "secrets":{
                app_target_name: {
                    "custom_settings_salt_strings":{}
                },
                "version": "1.0"
            }
        }
        
        mock_yaml_dumps.return_value = {
            "secrets":{
                app_target_name: {
                    "custom_settings_salt_strings":{
                        "Secret_Test2_without_required" : "my_fake_string"
                    }
                },
                "version": "1.0"
            }
        }

        custom_secret_setting = self.test_app.settings_set.select_subclasses().get(
            name="Secret_Test2_without_required"
        )
        custom_secret_setting.value = "SECRETXX1Y"
        custom_secret_setting.clean()
        custom_secret_setting.save()
        mock_os_path_exists.return_value = False
        # breakpoint()
        ### write only with the 
        cli_helper.gen_salt_string_for_setting("test_app", custom_secret_setting)
        mock_open_file.assert_called_once_with(mock_yaml_dumps, 'w')
        mock_write_error.assert_not_called()
        mock_write_success.assert_called()
        



### generate 5 test:
#with secrets complete
##with no custom_settings
###with no app
