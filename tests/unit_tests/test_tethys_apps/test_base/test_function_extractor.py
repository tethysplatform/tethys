import unittest
import tethys_apps.base.function_extractor as tethys_function_extractor
import mock


class PathObject(object):
    def __init__(self, name):
        self.name = name

    def callable(self):
        return self.name


class TestTethysFunctionExtractor(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        path = 'tethysapp-test_app.tethysapp.test_app.controller.home'
        result = tethys_function_extractor.TethysFunctionExtractor(path=path)
        # Check Result
        self.assertEqual(path, result.path)
        self.assertEqual('tethys_apps.tethysapp', result.prefix)

    def test_init_not_str(self):
        path = PathObject(name='test')
        # TODO: ask Nathan on why self.valid or self.function isn't valid.
        # result = tethys_function_extractor.TethysFunctionExtractor(path=path)
