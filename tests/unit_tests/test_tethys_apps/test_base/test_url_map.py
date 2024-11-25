import unittest
import tethys_apps.base.url_map as base_url_map


class TestUrlMap(unittest.TestCase):
    def setUp(self):
        self.name = "foo_name"
        self.controller = "foo_app.controllers.foo"
        self.root_url = "foo-app"
        self.bound_UrlMap = base_url_map.url_map_maker(self.root_url)

    def tearDown(self):
        pass

    def test_UrlMap(self):
        url = "example/resource/{variable_name}"
        expected_url = r"^example/resource/(?P<variable_name>[0-9A-Za-z-_.]+)/$"
        result = self.bound_UrlMap(name=self.name, url=url, controller=self.controller)
        # Check Result
        self.assertEqual(self.name, result.name)
        self.assertEqual(expected_url, result.url)
        self.assertEqual(self.controller, result.controller)

    def test_UrlMap_ending_slash(self):
        url = "example/resource/{variable_name}/"
        expected_url = r"^example/resource/(?P<variable_name>[0-9A-Za-z-_.]+)/$"
        result = self.bound_UrlMap(name=self.name, url=url, controller=self.controller)
        # Check Result
        self.assertEqual(expected_url, result.url)

    def test_UrlMap_starting_slash(self):
        url = "/example/resource/{variable_name}"
        expected_url = r"^example/resource/(?P<variable_name>[0-9A-Za-z-_.]+)/$"
        result = self.bound_UrlMap(name=self.name, url=url, controller=self.controller)
        # Check Result
        self.assertEqual(expected_url, result.url)

    def test_UrlMap_starting_and_ending_slashes(self):
        url = "/example/resource/{variable_name}/"
        expected_url = r"^example/resource/(?P<variable_name>[0-9A-Za-z-_.]+)/$"
        result = self.bound_UrlMap(name=self.name, url=url, controller=self.controller)
        # Check Result
        self.assertEqual(expected_url, result.url)

    def test_UrlMap_url_with_root(self):
        url = "foo-app/example/resource/{variable_name}"
        expected_url = r"^example/resource/(?P<variable_name>[0-9A-Za-z-_.]+)/$"
        result = self.bound_UrlMap(name=self.name, url=url, controller=self.controller)
        # Check Result
        self.assertEqual(expected_url, result.url)

    def test_UrlMap_url_with_root_and_starting_slash(self):
        url = "/foo-app/example/resource/{variable_name}"
        expected_url = r"^example/resource/(?P<variable_name>[0-9A-Za-z-_.]+)/$"
        result = self.bound_UrlMap(name=self.name, url=url, controller=self.controller)
        # Check Result
        self.assertEqual(expected_url, result.url)

    def test_UrlMap_regex1(self):
        # TEST regex-case1
        regex = "[0-9A-Z]+"
        url = "example/resource/{variable_name}"
        expected_url = "^example/resource/(?P<variable_name>[0-9A-Z]+)/$"
        result = self.bound_UrlMap(
            name=self.name, url=url, controller=self.controller, regex=regex
        )
        self.assertEqual(expected_url, result.url)

    def test_UrlMap_regex2(self):
        # TEST regex-case2
        regex = ["[0-9A-Z]+", "[0-8A-W]+"]
        url = "example/resource/{variable_name}/{variable_name2}"
        expected_url = "^example/resource/(?P<variable_name>[0-9A-Z]+)/(?P<variable_name2>[0-8A-W]+)/$"
        result = self.bound_UrlMap(
            name=self.name, url=url, controller=self.controller, regex=regex
        )
        self.assertEqual(expected_url, result.url)

    def test_UrlMap_regex3(self):
        # TEST regex-case3
        regex = ["[0-9A-Z]+"]
        url = "example/resource/{variable_name}/{variable_name2}"
        expected_url = "^example/resource/(?P<variable_name>[0-9A-Z]+)/(?P<variable_name2>[0-9A-Z]+)/$"
        result = self.bound_UrlMap(
            name=self.name, url=url, controller=self.controller, regex=regex
        )
        self.assertEqual(expected_url, result.url)

    def test_UrlMap_repr(self):
        # TEST __repr__
        url = "example/resource/{variable_name}"
        expected_result = (
            "<UrlMap: name=foo_name,"
            " url=^example/resource/(?P<variable_name>[0-9A-Za-z-_.]+)/$,"
            " controller=foo_app.controllers.foo, protocol=http,"
            " handler=None, handler_type=None, title=None, index=None>"
        )
        result = self.bound_UrlMap(
            name=self.name, url=url, controller=self.controller
        ).__repr__()
        self.assertEqual(expected_result, result)

    def test_UrlMap_empty_url(self):
        # TEST empty url
        regex = ["[0-9A-Z]+"]
        url = ""
        expected_url = "^$"
        result = self.bound_UrlMap(
            name=self.name, url=url, controller=self.controller, regex=regex
        )
        self.assertEqual(expected_url, result.url)

    def test_UrlMap_websocket(self):
        # TEST WebSocket url
        url = "example/resource/{variable_name}"
        expected_url = r"^example/resource/(?P<variable_name>[0-9A-Za-z-_.]+)/ws/$"
        result = self.bound_UrlMap(
            name=self.name, url=url, controller=self.controller, protocol="websocket"
        )
        self.assertEqual(expected_url, result.url)

    def test_UrlMap_websocket_empty(self):
        # TEST empty WebSocket url
        url = ""
        expected_url = "^ws/$"
        result = self.bound_UrlMap(
            name=self.name, url=url, controller=self.controller, protocol="websocket"
        )
        self.assertEqual(expected_url, result.url)

    def test_UrlMap_value_error(self):
        self.assertRaises(
            ValueError,
            self.bound_UrlMap,
            name="1",
            url="2",
            controller="3",
            regex={"1": "2"},
        )
