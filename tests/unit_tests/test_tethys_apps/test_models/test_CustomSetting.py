import uuid
from tethys_sdk.testing import TethysTestCase
from tethys_apps.models import TethysApp, CustomSetting
from django.core.exceptions import ValidationError


class CustomSettingTests(TethysTestCase):
    def set_up(self):
        self.test_app = TethysApp.objects.get(package='test_app')
        pass

    def tear_down(self):
        pass

    def test_clean(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(name='default_name')
        custom_setting.default = 1
        custom_setting.save()

        # Check ValidationError
        ret = CustomSetting.objects.get(name='default_name')
        ret.value = ''
        ret.clean()
        self.assertEquals('1', ret.value)

    def test_clean_empty_validation_error(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(name='default_name')
        custom_setting.value = ''
        custom_setting.save()

        # Check ValidationError
        ret = CustomSetting.objects.get(name='default_name')

        self.assertRaises(ValidationError, ret.clean)

    def test_clean_int_validation_error(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(name='default_name')
        custom_setting.value = 'test'
        custom_setting.type = 'INTEGER'
        custom_setting.save()

        # Check ValidationError
        ret = CustomSetting.objects.get(name='default_name')
        self.assertRaises(ValidationError, ret.clean)

    def test_clean_float_validation_error(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(name='default_name')
        custom_setting.value = 'test'
        custom_setting.type = 'FLOAT'
        custom_setting.save()

        # Check ValidationError
        ret = CustomSetting.objects.get(name='default_name')
        self.assertRaises(ValidationError, ret.clean)

    def test_clean_bool_validation_error(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(name='default_name')
        custom_setting.value = 'test'
        custom_setting.type = 'BOOLEAN'
        custom_setting.save()

        # Check ValidationError
        ret = CustomSetting.objects.get(name='default_name')
        self.assertRaises(ValidationError, ret.clean)

    def test_clean_uuid_validation_error(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(name='default_name')
        custom_setting.value = 'test'
        custom_setting.type = 'UUID'
        custom_setting.save()

        # Check ValidationError
        ret = CustomSetting.objects.get(name='default_name')
        self.assertRaises(ValidationError, ret.clean)

    def test_get(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(name='default_name')
        custom_setting.default = 1
        custom_setting.save()

        ret = CustomSetting.objects.get(name='default_name')
        ret.value = ''
        self.assertEquals('1', ret.get_value())

    def test_get_value_empty(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(name='default_name')
        custom_setting.value = ''
        custom_setting.required = False
        custom_setting.save()

        self.assertIsNone(CustomSetting.objects.get(name='default_name').get_value())

    def test_get_value_string(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(name='default_name')
        custom_setting.value = 'test_string'
        custom_setting.type = 'STRING'
        custom_setting.save()

        ret = CustomSetting.objects.get(name='default_name').get_value()

        self.assertEqual('test_string', ret)

    def test_get_value_float(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(name='default_name')
        custom_setting.value = '3.14'
        custom_setting.type = 'FLOAT'
        custom_setting.save()

        ret = CustomSetting.objects.get(name='default_name').get_value()
        self.assertEqual(3.14, ret)

    def test_get_value_integer(self):
        custom_setting = self.test_app.settings_set.select_subclasses().get(name='default_name')
        custom_setting.value = '3'
        custom_setting.type = 'INTEGER'
        custom_setting.save()

        ret = CustomSetting.objects.get(name='default_name').get_value()
        self.assertEqual(3, ret)

    def test_get_value_boolean_true(self):
        test_cases = ['true', 'yes', 't', 'y', '1']
        for test in test_cases:
            custom_setting = self.test_app.settings_set.select_subclasses().get(name='default_name')
            custom_setting.value = test
            custom_setting.type = 'BOOLEAN'
            custom_setting.save()

            ret = CustomSetting.objects.get(name='default_name').get_value()
            self.assertTrue(ret)

    def test_get_value_boolean_false(self):
        test_cases = ['false', 'no', 'f', 'n', '0']
        for test in test_cases:
            custom_setting = self.test_app.settings_set.select_subclasses().get(name='default_name')
            custom_setting.value = test
            custom_setting.type = 'BOOLEAN'
            custom_setting.save()

            ret = CustomSetting.objects.get(name='default_name').get_value()
            self.assertFalse(ret)

    def test_get_value_uuid(self):
        mock_uuid = uuid.uuid4()
        custom_setting = self.test_app.settings_set.select_subclasses().get(name='default_name')
        custom_setting.value = mock_uuid
        custom_setting.type = 'UUID'
        custom_setting.save()

        ret = CustomSetting.objects.get(name='default_name').get_value()
        self.assertEqual(mock_uuid, ret)
