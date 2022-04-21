from importlib import reload
from importlib.metadata import PackageNotFoundError
import unittest
from unittest import mock

import tethys_portal


class VersionCommandTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__version__(self):
        reload(tethys_portal)
        self.assertTrue(getattr(tethys_portal, '__version__', False))
        self.assertIsNotNone(tethys_portal.__version__)
