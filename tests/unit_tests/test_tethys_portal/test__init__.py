from importlib import reload
import unittest

import tethys_portal


class TethysPortalInitTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__version__(self):
        reload(tethys_portal)
        self.assertTrue(getattr(tethys_portal, "__version__", False))
        self.assertIsNotNone(tethys_portal.__version__)
