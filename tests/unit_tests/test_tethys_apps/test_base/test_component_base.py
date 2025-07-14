import unittest
from unittest import mock
from django.test import RequestFactory

import tethys_apps.base.component_base as component_app_base
from tethys_apps.base.url_map import UrlMapBase
from ... import UserFactory


class TestTethysAppBase(unittest.TestCase):
    def setUp(self):
        self.app = component_app_base.ComponentBase()
        self.user = UserFactory()
        self.request_factory = RequestFactory()
        self.fake_name = "fake_name"

    def tearDown(self):
        pass

    def test_navigation_links_not_auto(self):
        self.app.nav_links = ["test", "1", "2", "3"]
        self.assertListEqual(self.app.navigation_links, self.app.nav_links)

    def test_navigation_links_auto_excluded_page(self):
        app = component_app_base.ComponentBase()
        app.nav_links = "auto"
        app.index = "home"
        app.root_url = "test-app"

        app._registered_url_maps = [
            UrlMapBase(
                name="exclude_page",
                url="",
                controller=None,
                title="Exclude Page",
                index=-1,
            ),
            UrlMapBase(
                name="last_page", url="", controller=None, title="Last Page", index=3
            ),
            UrlMapBase(
                name="third_page", url="", controller=None, title="Third Page", index=2
            ),
            UrlMapBase(
                name="second_page",
                url="",
                controller=None,
                title="Second Page",
                index=1,
            ),
            UrlMapBase(name="home", url="", controller=None, title="Home", index=0),
        ]

        links = app.navigation_links

        self.assertListEqual(
            links,
            [
                {"title": "Home", "href": "/apps/test-app/"},
                {"title": "Second Page", "href": "/apps/test-app/second-page/"},
                {"title": "Third Page", "href": "/apps/test-app/third-page/"},
                {"title": "Last Page", "href": "/apps/test-app/last-page/"},
            ],
        )
        self.assertEqual(links, app.nav_links)

    @mock.patch("tethys_apps.base.component_base.page_controller")
    def test_page_decorator(self, mock_pc):
        app = component_app_base.ComponentBase()

        def test_page(lib):
            return lib.html.div("Test 123")

        self.assertEqual(app.page(test_page), mock_pc.return_value)
        mock_pc.assert_called_once_with(test_page, app=component_app_base.ComponentBase)
