from ast import literal_eval as make_tuple
from django.db import models
from django.core.exceptions import ValidationError
from distributed.protocol.serialize import serialize, deserialize


class DaskSerializedField(models.Field):

    description = 'A field the automatically serializes and deserializes using Dask serialization.'

    def get_internal_type(self):
        return 'TextField'

    def from_db_value(self, value, *args, **kwargs):
        """
        Called in all circumstances when data is loaded from the database, including in aggregates and values() calls.
        """
        if value is None:
            return value

        try:
            return deserialize(*make_tuple(value))
        except Exception:
            raise ValidationError('Unable to deserialize value: {}'.format(str(value)))

    def to_python(self, value):
        """
        Called by deserialization and during the clean() method used on forms.
        """
        if value is None or not isinstance(value, str):
            return value

        try:
            return deserialize(*make_tuple(value))
        except Exception:
            raise ValidationError('Unable to deserialize value: {}'.format(value))

    def get_prep_value(self, value):
        """
        Called to convert Python objects back to query values.
        """
        try:
            serialize_tuple = serialize(value)
            return str(serialize_tuple)
        except Exception:
            raise ValidationError('Unable to serialize value: {}'.format(value))

    def value_to_string(self, obj):
        """
        Called by serialization.
        """
        value = self.value_from_object(obj)
        return self.get_prep_value(value)
