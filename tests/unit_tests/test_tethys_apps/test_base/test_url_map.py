import unittest
import tethys_apps.base.url_map as base_url_map


class TestUrlMap(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_UrlMapBase(self):
        name = 'test_name'
        url = '/example/resource/{variable_name}/'
        expected_url = r'^example/resource/(?P<variable_name>[0-9A-Za-z-_.]+)/$'
        controller = 'test_controller'

        result = base_url_map.UrlMapBase(name=name, url=url, controller=controller)

        # Check Result
        self.assertEqual(name, result.name)
        self.assertEqual(expected_url, result.url)
        self.assertEqual(controller, result.controller)

        # TEST regex-case1
        regex = '[0-9A-Z]+'
        expected_url = '^example/resource/(?P<variable_name>[0-9A-Z]+)/$'

        result = base_url_map.UrlMapBase(name=name, url=url, controller=controller, regex=regex)
        self.assertEqual(expected_url, result.url)

        # TEST regex-case2
        regex = ['[0-9A-Z]+', '[0-8A-W]+']
        url = '/example/resource/{variable_name}/{variable_name2}/'
        expected_url = '^example/resource/(?P<variable_name>[0-9A-Z]+)/(?P<variable_name2>[0-8A-W]+)/$'

        result = base_url_map.UrlMapBase(name=name, url=url, controller=controller, regex=regex)
        self.assertEqual(expected_url, result.url)

        # TEST regex-case3
        regex = ['[0-9A-Z]+']
        url = '/example/resource/{variable_name}/{variable_name2}/'
        expected_url = '^example/resource/(?P<variable_name>[0-9A-Z]+)/(?P<variable_name2>[0-9A-Z]+)/$'

        result = base_url_map.UrlMapBase(name=name, url=url, controller=controller, regex=regex)
        self.assertEqual(expected_url, result.url)

        # TEST __repre__
        expected_result = '<UrlMap: name=test_name, url=^example/resource/(?P<variable_name>[0-9A-Za-z-_.]+)/' \
                          '(?P<variable_name2>[0-9A-Za-z-_.]+)/$, controller=test_controller, protocol=http, ' \
                          'handler=None, handler_type=None>'
        result = base_url_map.UrlMapBase(name=name, url=url, controller=controller).__repr__()
        self.assertEqual(expected_result, result)

        # TEST empty url
        regex = ['[0-9A-Z]+']
        url = ''
        expected_url = '^$'

        result = base_url_map.UrlMapBase(name=name, url=url, controller=controller, regex=regex)
        self.assertEqual(expected_url, result.url)

        # TEST WebSocket url
        url = 'example/resource/{variable_name}/'
        expected_url = r'^test-app/example/resource/(?P<variable_name>[0-9A-Za-z-_.]+)/ws/$'

        test_UrlMap = base_url_map.url_map_maker('test-app')
        result = test_UrlMap(name=name, url=url, controller=controller, protocol='websocket')
        self.assertEqual(expected_url, result.url)

        # TEST empty WebSocket url
        url = ''
        expected_url = '^test-app/ws/$'

        result = test_UrlMap(name=name, url=url, controller=controller,  protocol='websocket')
        self.assertEqual(expected_url, result.url)

    def test_UrlMapBase_value_error(self):
        self.assertRaises(ValueError, base_url_map.UrlMapBase, name='1', url='2',
                          controller='3', regex={'1': '2'})
