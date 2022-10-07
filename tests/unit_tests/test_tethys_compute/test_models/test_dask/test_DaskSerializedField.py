from unittest import mock
from distributed.protocol.serialize import serialize
from django.core.exceptions import ValidationError
from tethys_sdk.testing import TethysTestCase
from tethys_compute.models.dask.dask_field import DaskSerializedField


class DaskSerializedFieldTests(TethysTestCase):
    def set_up(self):
        self.field = DaskSerializedField(blank=True, null=True)
        self.value = "foo"
        self.s_value = str(serialize(self.value))

    def tear_down(self):
        pass

    def test_get_internal_type(self):
        ret = self.field.get_internal_type()
        self.assertEqual("TextField", ret)

    def test_from_db_value(self):
        ret = self.field.from_db_value(value=self.s_value)
        self.assertEqual(self.value, ret)

    def test_from_db_value_none(self):
        ret = self.field.from_db_value(value=None)
        self.assertIsNone(ret)

    @mock.patch("tethys_compute.models.dask.dask_field.deserialize")
    def test_from_db_value_deserialize_exception(self, mock_deserialize):
        mock_deserialize.side_effect = Exception
        self.assertRaises(ValidationError, self.field.from_db_value, value=self.s_value)

    def test_to_python(self):
        ret = self.field.to_python(value=self.s_value)
        self.assertEqual(self.value, ret)

    def test_to_python_none(self):
        ret = self.field.to_python(value=None)
        self.assertIsNone(ret)

    def test_to_python_not_str(self):
        ret = self.field.to_python(value=1)
        self.assertEqual(1, ret)

    @mock.patch("tethys_compute.models.dask.dask_field.deserialize")
    def test_to_python_deserialize_exception(self, mock_deserialize):
        mock_deserialize.side_effect = Exception
        self.assertRaises(ValidationError, self.field.to_python, value=self.s_value)

    def test_get_prep_value(self):
        ret = self.field.get_prep_value(value=self.value)
        self.assertEqual(self.s_value, ret)

    @mock.patch("tethys_compute.models.dask.dask_field.serialize")
    def test_get_prep_value_serialize_exception(self, mock_serialize):
        mock_serialize.side_effect = Exception
        self.assertRaises(ValidationError, self.field.get_prep_value, value=self.value)

    def test_value_to_string(self):
        obj = mock.MagicMock(bar="foo")
        self.field.attname = "bar"
        ret = self.field.value_to_string(obj)
        self.assertEqual(self.s_value, ret)
