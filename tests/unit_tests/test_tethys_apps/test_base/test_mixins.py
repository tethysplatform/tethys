import unittest
import tethys_apps.base.mixins as tethys_mixins


class TestTethysBaseMixin(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_TethysBaseMixin(self):
        result = tethys_mixins.TethysBaseMixin()
        result.root_url = 'test-url'
        self.assertEqual('test_url', result.namespace)
