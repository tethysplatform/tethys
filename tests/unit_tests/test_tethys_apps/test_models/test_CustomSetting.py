import uuid
import json
from tethys_sdk.testing import TethysTestCase
from tethys_apps.models import TethysApp, CustomSettingBase
from django.core.exceptions import ValidationError
from unittest import mock
from tethys_apps.exceptions import TethysAppSettingNotAssigned


class CustomSettingTests(TethysTestCase):
    def set_up(self):
        self.test_app = TethysApp.objects.get(package="test_app")
        pass

    def tear_down(self):
        pass

    def test_clean(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="default_name"
        )
        custom_setting.default = 1
        custom_setting.save()
        # Check ValidationError
        ret = CustomSettingBase.objects.get(name="default_name")
        ret.value = "1"
        ret.clean()
        self.assertEqual("1", ret.value)

    def test_clean_empty_validation_error(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="default_name"
        )
        custom_setting.value = ""
        custom_setting.save()

        # Check ValidationError
        ret = CustomSettingBase.objects.filter(name="default_name").select_subclasses()[
            0
        ]

        self.assertRaises(ValidationError, ret.clean)

    def test_clean_empty_json_validation_error(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="JSON_setting_not_default_value_required"
        )
        custom_setting.value = {}
        custom_setting.save()

        # Check ValidationError
        ret = CustomSettingBase.objects.filter(
            name="JSON_setting_not_default_value_required"
        ).select_subclasses()[0]

        self.assertRaises(ValidationError, ret.clean)

    def test_clean_empty_secret_validation_error(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="Secret_Test_required"
        )
        custom_setting.value = ""
        custom_setting.save()

        # Check ValidationError
        ret = CustomSettingBase.objects.filter(
            name="Secret_Test_required"
        ).select_subclasses()[0]

        self.assertRaises(ValidationError, ret.clean)

    def test_clean_int_validation_error(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="default_name"
        )
        custom_setting.value = "test"
        custom_setting.type = "INTEGER"
        custom_setting.save()

        # Check ValidationError
        ret = CustomSettingBase.objects.filter(name="default_name").select_subclasses()[
            0
        ]
        self.assertRaises(ValidationError, ret.clean)

    def test_clean_float_validation_error(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="default_name"
        )
        custom_setting.value = "test"
        custom_setting.type = "FLOAT"
        custom_setting.save()

        # Check ValidationError
        ret = CustomSettingBase.objects.filter(name="default_name").select_subclasses()[
            0
        ]
        self.assertRaises(ValidationError, ret.clean)

    def test_clean_bool_validation_error(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="default_name"
        )
        custom_setting.value = "test"
        custom_setting.type = "BOOLEAN"
        custom_setting.save()

        # Check ValidationError
        ret = CustomSettingBase.objects.filter(name="default_name").select_subclasses()[
            0
        ]
        self.assertRaises(ValidationError, ret.clean)

    def test_clean_uuid_validation_error(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="default_name"
        )
        custom_setting.value = "test"
        custom_setting.type = "UUID"
        custom_setting.save()

        # Check ValidationError
        ret = CustomSettingBase.objects.filter(name="default_name").select_subclasses()[
            0
        ]
        self.assertRaises(ValidationError, ret.clean)

    def test_clean_json_validation_error(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="JSON_setting_not_default_value"
        )
        custom_setting.value = "test"
        custom_setting.save()

        # Check ValidationError
        ret = CustomSettingBase.objects.filter(
            name="JSON_setting_not_default_value"
        ).select_subclasses()[0]
        self.assertRaises(ValidationError, ret.clean)

    def test_clean_secret_validation_error(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="Secret_Test2_without_required"
        )
        dict_example = {"brand": "Ford", "model": "Mustang", "year": 1964}
        custom_setting.value = json.dumps(dict_example)
        custom_setting.save()

        # Check ValidationError
        ret = CustomSettingBase.objects.filter(
            name="Secret_Test2_without_required"
        ).select_subclasses()[0]
        self.assertEqual(json.dumps(dict_example), ret.value)

    @mock.patch("tethys_apps.utilities.yaml.safe_load")
    @mock.patch("tethys_apps.utilities.Path.exists")
    @mock.patch(
        "tethys_apps.utilities.Path.read_text", return_value='{"secrets": "{}"}'
    )
    def test_clean_secret_validation_with_complete_secrets_yml(
        self, mock_open_file, mock_path_exists, mock_yaml_safe_load
    ):
        app_target_name = "test_app"

        secrets_yml_content = {
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
        mock_path_exists.return_value = True
        mock_yaml_safe_load.return_value = secrets_yml_content

        custom_secret_setting.value = "SECRE:TXX1Y"
        custom_secret_setting.clean()
        custom_secret_setting.save()

        self.assertEqual(custom_secret_setting.get_value(), "SECRE:TXX1Y")

    @mock.patch("tethys_apps.utilities.yaml.safe_load")
    @mock.patch("tethys_apps.utilities.Path.exists")
    @mock.patch(
        "tethys_apps.utilities.Path.read_text", return_value='{"secrets": "{}"}'
    )
    def test_clean_secret_validation_with_incomplete_secrets_yml(
        self, mock_open_file, mock_path_exists, mock_yaml_safe_load
    ):
        secrets_yml_content = {"secrets": {}}

        custom_secret_setting = self.test_app.settings_set.select_subclasses().get(
            name="Secret_Test2_without_required"
        )
        mock_path_exists.return_value = True
        mock_yaml_safe_load.return_value = secrets_yml_content

        custom_secret_setting.value = "SECRE:TXX1Y"
        custom_secret_setting.clean()
        custom_secret_setting.save()

        self.assertEqual(custom_secret_setting.get_value(), "SECRE:TXX1Y")

    def test_get(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="default_name"
        )
        custom_setting.default = 1
        custom_setting.save()

        ret = CustomSettingBase.objects.filter(name="default_name").select_subclasses()[
            0
        ]
        ret.value = ""
        self.assertEqual("1", ret.get_value())

    def test_get_value_empty(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="default_name"
        )
        custom_setting.value = ""
        custom_setting.required = False
        custom_setting.save()

        self.assertIsNone(
            CustomSettingBase.objects.filter(name="default_name")
            .select_subclasses()[0]
            .get_value()
        )

    def test_get_value_secret_required_error(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="Secret_Test_required"
        )
        custom_setting.value = ""
        custom_setting.save()
        with self.assertRaises(TethysAppSettingNotAssigned) as raises_cm:
            custom_setting.get_value()
        exception = raises_cm.exception

        self.assertEqual(
            exception.args,
            (
                'The required setting "Secret_Test_required" for app "test_app":has not been assigned.',
            ),
        )

    def test_get_value_string(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="default_name"
        )
        custom_setting.value = "test_string"
        custom_setting.type = "STRING"
        custom_setting.save()

        ret = (
            CustomSettingBase.objects.filter(name="default_name")
            .select_subclasses()[0]
            .get_value()
        )

        self.assertEqual("test_string", ret)

    def test_get_value_float(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="default_name"
        )
        custom_setting.value = "3.14"
        custom_setting.type = "FLOAT"
        custom_setting.save()

        ret = (
            CustomSettingBase.objects.filter(name="default_name")
            .select_subclasses()[0]
            .get_value()
        )
        self.assertEqual(3.14, ret)

    def test_get_value_integer(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="default_name"
        )
        custom_setting.value = "3"
        custom_setting.type = "INTEGER"
        custom_setting.save()

        ret = (
            CustomSettingBase.objects.filter(name="default_name")
            .select_subclasses()[0]
            .get_value()
        )
        self.assertEqual(3, ret)

    def test_get_value_boolean_true(self):
        test_cases = ["true", "yes", "t", "y", "1"]
        for test in test_cases:
            custom_setting = self.test_app.settings_set.select_subclasses().get(
                name="default_name"
            )
            custom_setting.value = test
            custom_setting.type = "BOOLEAN"
            custom_setting.save()

            ret = (
                CustomSettingBase.objects.filter(name="default_name")
                .select_subclasses()[0]
                .get_value()
            )
            self.assertTrue(ret)

    def test_get_value_boolean_false(self):
        test_cases = ["false", "no", "f", "n", "0"]
        for test in test_cases:
            custom_setting = self.test_app.settings_set.select_subclasses().get(
                name="default_name"
            )
            custom_setting.value = test
            custom_setting.type = "BOOLEAN"
            custom_setting.save()

            ret = (
                CustomSettingBase.objects.filter(name="default_name")
                .select_subclasses()[0]
                .get_value()
            )
            self.assertFalse(ret)

    def test_get_value_uuid(self):
        mock_uuid = uuid.uuid4()
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="default_name"
        )
        custom_setting.value = mock_uuid
        custom_setting.type = "UUID"
        custom_setting.save()

        ret = (
            CustomSettingBase.objects.filter(name="default_name")
            .select_subclasses()[0]
            .get_value()
        )
        self.assertEqual(mock_uuid, ret)

    def test_get_value_json_custom_setting(self):
        ret = (
            CustomSettingBase.objects.filter(name="JSON_setting_default_value")
            .select_subclasses()[0]
            .get_value()
        )
        ret_string = json.dumps(ret)
        self.assertEqual('{"Test": "JSON test String"}', ret_string)

    @mock.patch("tethys_apps.utilities.yaml.safe_load")
    def test_get_value_secret_custom_setting_without_setttings_file(self, _):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="Secret_Test2_without_required"
        )
        custom_setting.value = "Mysecrertxxxx23526236sddgsdgsgsuiLSD"
        custom_setting.clean()
        custom_setting.save()

        ret = (
            CustomSettingBase.objects.filter(name="Secret_Test2_without_required")
            .select_subclasses()[0]
            .get_value()
        )
        self.assertEqual("Mysecrertxxxx23526236sddgsdgsgsuiLSD", ret)

    @mock.patch("tethys_apps.utilities.yaml.safe_load")
    @mock.patch("tethys_apps.utilities.Path.exists")
    @mock.patch(
        "tethys_apps.utilities.Path.read_text", return_value='{"secrets": "{}"}'
    )
    def test_clean_secret_validation_with_complete_secrets_yml_and_error(
        self, mock_open_file, mock_path_exists, mock_yaml_safe_load
    ):
        app_target_name = "test_app"

        fake_salt_string = "my_fake_string"

        secrets_yml_content = {
            "secrets": {
                app_target_name: {
                    "custom_settings_salt_strings": {
                        "Secret_Test2_without_required": fake_salt_string
                    }
                },
                "version": "1.0",
            }
        }

        custom_secret_setting = self.test_app.settings_set.select_subclasses().get(
            name="Secret_Test2_without_required"
        )
        mock_path_exists.return_value = True
        mock_yaml_safe_load.return_value = secrets_yml_content

        custom_secret_setting.value = "SECRE:TXX1Y"
        custom_secret_setting.clean()
        custom_secret_setting.save()

        self.assertEqual(custom_secret_setting.get_value(), "SECRE:TXX1Y")

        # fail if the salt string is changed or lost :)
        fake_salt_string = "change_so_so_it_fails"
        secrets_yml_content = {
            "secrets": {
                app_target_name: {
                    "custom_settings_salt_strings": {
                        "Secret_Test2_without_required": fake_salt_string
                    }
                },
                "version": "1.0",
            }
        }
        mock_yaml_safe_load.return_value = secrets_yml_content

        with self.assertRaises(TethysAppSettingNotAssigned):
            custom_secret_setting.get_value()

    def test_get_secret_value_empty(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="Secret_Test2_without_required"
        )
        custom_setting.value = ""
        custom_setting.save()

        self.assertIsNone(custom_setting.get_value())

    def test_clean_string_validation_with_default(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="default_name"
        )
        custom_setting.value = ""
        custom_setting.default = "default_string"
        custom_setting.clean()
        custom_setting.save()

        # Check value is default value
        self.assertEqual(custom_setting.get_value(), "default_string")

    def test_clean_json_validation_with_default(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="JSON_setting_default_value"
        )
        custom_setting.value = {}
        custom_setting.save()

        # Check value is default value
        self.assertEqual(custom_setting.get_value(), {"Test": "JSON test String"})

    @mock.patch("tethys_apps.models.json.dumps")
    def test_clean_json_validation_with_invalid_json_object(self, mock_json_dumps):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="JSON_setting_not_default_value"
        )
        custom_setting.value = {"secret_key": "secret_value"}
        mock_json_dumps.side_effect = [TypeError]
        with self.assertRaises(ValidationError):
            custom_setting.clean()

    def test_get_value_json_with_default(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="JSON_setting_default_value"
        )
        custom_setting.value = {}
        custom_setting.clean()
        custom_setting.save()

        # Check value is default value
        self.assertEqual(custom_setting.get_value(), {"Test": "JSON test String"})

    def test_get_value_json_with_required(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="JSON_setting_not_default_value_required"
        )
        custom_setting.value = {}
        # custom_setting.clean()
        custom_setting.save()

        # Check value is a required setting
        with self.assertRaises(TethysAppSettingNotAssigned):
            custom_setting.get_value()

    def test_get_value_json_with_no_required_and_empty_value(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="JSON_setting_not_default_value"
        )
        custom_setting.value = {}
        custom_setting.clean()
        custom_setting.save()

        # Check value is a required setting returns None

        self.assertEqual(custom_setting.get_value(), None)

    def test_include_in_api(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="default_name"
        )
        self.assertTrue(custom_setting.include_in_api)

        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="max_count"
        )
        self.assertFalse(custom_setting.include_in_api)

        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="change_factor"
        )
        self.assertFalse(custom_setting.include_in_api)

        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="enable_feature"
        )
        self.assertTrue(custom_setting.include_in_api)

        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="JSON_setting_not_default_value_required"
        )
        self.assertFalse(custom_setting.include_in_api)

        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="JSON_setting_not_default_value"
        )
        self.assertFalse(custom_setting.include_in_api)

        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="JSON_setting_default_value_required"
        )
        self.assertTrue(custom_setting.include_in_api)

        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="JSON_setting_default_value"
        )
        self.assertFalse(custom_setting.include_in_api)

        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="Secret_Test_required"
        )
        self.assertTrue(custom_setting.include_in_api)

        custom_setting = self.test_app.settings_set.select_subclasses().get(
            name="Secret_Test2_without_required"
        )
        self.assertFalse(custom_setting.include_in_api)
