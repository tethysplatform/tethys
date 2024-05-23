from tethys_utils import deprecation_warning

import unittest
from unittest import mock


class TestDeprecation(unittest.TestCase):
    @mock.patch("tethys_utils.deprecation.print")
    def test_deprecation_warning(self, mock_print):
        deprecation_warning("version", "feature", "message")
        mock_print.assert_called_once()
