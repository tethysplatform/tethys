import unittest

from tethys_layouts.views.tethys_layout import TethysLayout
from tethys_layouts.exceptions import TethysLayoutPropertyException


class TestTethysLayoutExceptions(unittest.TestCase):
    def test_TethysLayoutPropertyException(self):
        with self.assertRaises(TethysLayoutPropertyException) as cm:
            raise TethysLayoutPropertyException("foo", TethysLayout)

        self.assertEqual(
            str(cm.exception),
            'You must define the "foo" property '
            "on your TethysLayout class to use this feature.",
        )
