import unittest
from unittest import mock

from tethys_layouts.views.tethys_layout import TethysLayout


class TestTethysLayout(unittest.TestCase):
    def setUp(self):
        self.inst = TethysLayout()

    def tearDown(self):
        pass

    def test_default_props(self):
        ret = TethysLayout()
        
        self.assertEqual('', ret.template_name)
        self.assertIsNone(ret.app)
        self.assertIsNone(ret.back_url)
        self.assertEqual('tethys_layouts/tethys_layout.html', ret.base_template)
        self.assertEqual('', ret.layout_title)
        self.assertEqual('', ret.layout_subtitle)

    def test_get(self):
        pass

    def test_get_http_response(self):
        pass

    def test_get_method(self):
        pass

    def test_post(self):
        pass

    def test_post_method(self):
        pass

    def test_request_to_method_get_with_dashes(self):
        class CustomLayout(TethysLayout):
            def some_method(self):
                pass
        mock_request = mock.MagicMock(method='GET', GET=dict(method='some-method'))
        inst = CustomLayout()
        ret = inst.request_to_method(mock_request)
        self.assertEqual(inst.some_method, ret)

    def test_request_to_method_post_with_underscores(self):
        class CustomLayout(TethysLayout):
            def some_method(self):
                pass
        mock_request = mock.MagicMock(method='POST', POST=dict(method='some_method'))
        inst = CustomLayout()
        ret = inst.request_to_method(mock_request)
        self.assertEqual(inst.some_method, ret)

    def test_request_to_method_no_request_method(self):
        class CustomLayout(TethysLayout):
            def some_method(self):
                pass
        mock_request = mock.MagicMock(method='GET', GET=dict(method='not-a-method'))
        inst = CustomLayout()
        ret = inst.request_to_method(mock_request)
        self.assertIsNone(ret)

    def test_on_get(self):
        mock_request = mock.MagicMock()
        ret = self.inst.on_get(mock_request)
        self.assertIsNone(ret)

    def test_get_permissions(self):
        test_perms = dict(foo=True)
        mock_request = mock.MagicMock()
        ret = self.inst.get_permissions(mock_request, test_perms)
        self.assertIs(test_perms, ret)

    def test_get_context(self):
        test_context = dict(foo='bar')
        mock_request = mock.MagicMock()
        ret = self.inst.get_context(mock_request, test_context)
        self.assertIs(test_context, ret)
