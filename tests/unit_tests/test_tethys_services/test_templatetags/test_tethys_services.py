import unittest
from unittest import mock

from owslib.wps import ComplexData
from tethys_services.templatetags.tethys_services import is_complex_data


class TethysServicesIsComplexDataTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_complex_data_false(self):
        mock_args = mock.MagicMock()

        self.assertFalse(is_complex_data(mock_args))

    def test_is_compex_data_true(self):
        mock_args = mock.MagicMock()
        mock_args = ComplexData()

        self.assertTrue(is_complex_data(mock_args))
