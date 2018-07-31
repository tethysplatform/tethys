import unittest
import tethys_apps.base.mixins as tethys_mixins
import mock


class TestTethysBaseMixin(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_TethysBaseMixin(self):
        result = tethys_mixins.TethysBaseMixin()
        result.root_url = 'test-url'
        self.assertEqual(result.namespace, 'test_url')
