from django.test import TestCase
from captcha.models import CaptchaStore
from django.contrib.auth.models import User
from unittest import mock
from tethys_compute.utilities import ListField, DictionaryField, Creator


def test_fun():
    return 'test'


class TestObject:
    test_name = 'test'


class TethysComputeUtilitiesTests(TestCase):

    def setUp(self):
        CaptchaStore.generate_key()
        self.hashkey = CaptchaStore.objects.all()[0].hashkey
        self.response = CaptchaStore.objects.all()[0].response
        self.user = User.objects.create_user(username='user_exist',
                                             email='foo_exist@aquaveo.com',
                                             password='glass_onion')

    def tearDown(self):
        pass

    def test_Creator_init(self):
        mock_obj = mock.MagicMock()
        ret = Creator(mock_obj)
        self.assertEqual(mock_obj, ret.field)

    def test_Creator_get_set(self):
        mock_field = mock.MagicMock()
        mock_field.name = 'test_name'

        mock_field.to_python.return_value = 'test_name_value'

        # Set Object Value
        TestObject.test_name = 'test2'

        ret = Creator(mock_field)

        ret_value = ret.__get__(TestObject)

        self.assertEqual('test2', ret_value)

        # Object is None
        ret_value = ret.__get__(None)

        # Check result
        self.assertEqual(ret_value, ret)

    # ListField

    def test_ListField(self):
        ret = ListField()
        self.assertEqual('List object', ret.description)

    def test_list_field_get_internal_type(self):
        ret = ListField()
        self.assertEqual('TextField', ret.get_internal_type())

    def test_list_field_to_python_none(self):
        ret = ListField()
        self.assertIsNone(ret.to_python(value=None))

    def test_list_field_to_python_empty_str(self):
        ret = ListField()
        self.assertListEqual([], ret.to_python(value=""))

    @mock.patch('tethys_compute.utilities.json.loads')
    def test_list_field_to_python_str(self, mock_jl):
        ret = ListField()
        ret.to_python(value='foo')
        mock_jl.assert_called_with('foo')

    @mock.patch('tethys_compute.utilities.json.loads')
    def test_list_field_to_python_str_ValueError(self, mock_jl):
        ret = ListField()
        mock_jl.side_effect = ValueError
        self.assertRaises(ValueError, ret.to_python, value='foo')

    def test_list_field_to_python_list(self):
        ret = ListField()
        input_value = ['foo', 'bar']
        output = ret.to_python(value=input_value)
        self.assertListEqual(input_value, output)

    def test_list_field_to_python_dict(self):
        ret = ListField()
        input_value = {'name': 'bar'}
        output = ret.to_python(value=input_value)
        self.assertListEqual([], output)

    @mock.patch('tethys_compute.utilities.ListField.to_python')
    def test_list_field_from_db_value(self, mock_tp):
        ret = ListField()
        ret.from_db_value(value='foo', expression='exp', connection='con', context='ctx')
        mock_tp.assert_called_with('foo')

    def test_list_field_get_prep_value(self):
        ret = ListField()
        self.assertEqual('', ret.get_prep_value(value=''))

    def test_list_field_get_prep_value_str(self):
        ret = ListField()
        self.assertEqual('foo', ret.get_prep_value(value='foo'))

    @mock.patch('tethys_compute.utilities.json.dumps')
    def test_list_field_get_prep_value_list(self, mock_jd):
        ret = ListField()
        input_value = ['foo', 'bar']
        ret.get_prep_value(value=input_value)
        mock_jd.assert_called_with(input_value)

    @mock.patch('tethys_compute.utilities.ListField.get_prep_value')
    @mock.patch('tethys_compute.utilities.ListField.value_from_object')
    def test_list_field_value_to_string(self, mock_gpvo, mock_gpv):
        ret = ListField()

        output = mock_gpvo.return_value

        mock_obj = mock.MagicMock()

        ret.value_to_string(obj=mock_obj)

        mock_gpvo.assert_called_with(mock_obj)

        mock_gpv.assert_called_with(output)

    @mock.patch('tethys_compute.utilities.ListField.get_prep_value')
    @mock.patch('django.db.models.fields.Field.clean')
    def test_list_field_clean(self, mock_sc, mock_gpv):
        ret = ListField()
        input_value = 'foo'
        input_model_instance = mock.MagicMock()

        output = mock_sc.return_value

        ret.clean(value=input_value, model_instance=input_model_instance)

        mock_sc.assert_called_with(input_value, input_model_instance)

        mock_gpv.assert_called_with(output)

    @mock.patch('django.db.models.fields.Field.formfield')
    def test_list_field_formfield(self, mock_ff):
        ret = ListField()
        ret.formfield(additional='test2')
        mock_ff.assert_called_once()

    # DictionaryField

    def test_DictionaryField(self):
        ret = DictionaryField()
        self.assertEqual('Dictionary object', ret.description)

    def test_dictionary_field_get_internal_type(self):
        ret = DictionaryField()
        self.assertEqual('TextField', ret.get_internal_type())

    def test_dictionary_field_to_python_none(self):
        ret = DictionaryField()
        self.assertIsNone(ret.to_python(value=None))

    def test_dictionary_field_to_python_empty_str(self):
        ret = DictionaryField()
        self.assertDictEqual({}, ret.to_python(value=""))

    @mock.patch('tethys_compute.utilities.json.loads')
    def test_dictionary_field_to_python_str(self, mock_jl):
        ret = DictionaryField()
        ret.to_python(value='foo')
        mock_jl.assert_called_with('foo')

    @mock.patch('tethys_compute.utilities.json.loads')
    def test_dictionary_field_to_python_str_value_error(self, mock_jl):
        ret = DictionaryField()
        mock_jl.side_effect = ValueError
        self.assertRaises(ValueError, ret.to_python, value='foo')

    def test_dictionary_field_to_python_dict(self):
        ret = DictionaryField()
        input_dict = {'name': 'foo', 'extra': 'bar'}
        res = ret.to_python(value=input_dict)
        self.assertDictEqual(input_dict, res)

    def test_dictionary_field_to_python_empty_dict(self):
        ret = DictionaryField()
        input_value = ['test1', 'test2']
        res = ret.to_python(value=input_value)
        self.assertDictEqual({}, res)

    @mock.patch('tethys_compute.utilities.DictionaryField.to_python')
    def test_dictionary_field_from_db_value(self, mock_tp):
        ret = DictionaryField()
        ret.from_db_value(value='foo', expression='exp', connection='con', context='ctx')
        mock_tp.assert_called_with('foo')

    def test_dictionary_field_get_prep_value(self):
        ret = DictionaryField()
        self.assertEqual('', ret.get_prep_value(value=''))

    def test_dictionary_field_get_prep_value_str(self):
        ret = DictionaryField()
        self.assertEqual('foo', ret.get_prep_value(value='foo'))

    @mock.patch('tethys_compute.utilities.json.dumps')
    def test_dictionary_field_get_prep_value_list(self, mock_jd):
        ret = DictionaryField()
        input_value = ['foo', 'bar']
        ret.get_prep_value(value=input_value)
        mock_jd.assert_called_with(input_value)

    @mock.patch('tethys_compute.utilities.DictionaryField.get_prep_value')
    @mock.patch('tethys_compute.utilities.DictionaryField.value_from_object')
    def test_dictionary_field_value_to_string(self, mock_gpvo, mock_gpv):
        ret = DictionaryField()

        output = mock_gpvo.return_value

        mock_obj = mock.MagicMock()

        ret.value_to_string(obj=mock_obj)

        mock_gpvo.assert_called_with(mock_obj)

        mock_gpv.assert_called_with(output)

    @mock.patch('tethys_compute.utilities.DictionaryField.get_prep_value')
    @mock.patch('django.db.models.fields.Field.clean')
    def test_dictionary_field_clean(self, mock_sc, mock_gpv):
        ret = DictionaryField()
        input_value = 'foo'
        input_model_instance = mock.MagicMock()

        output = mock_sc.return_value

        ret.clean(value=input_value, model_instance=input_model_instance)

        mock_sc.assert_called_with(input_value, input_model_instance)

        mock_gpv.assert_called_with(output)

    @mock.patch('django.db.models.fields.Field.formfield')
    def test_dictionary_field_formfield(self, mock_ff):
        ret = DictionaryField()
        ret.formfield(additional='test2')
        mock_ff.assert_called_once()
