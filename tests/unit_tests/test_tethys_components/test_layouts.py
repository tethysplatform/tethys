from tethys_components import layouts
from unittest import TestCase, mock
from reactpy.core.component import Component


class TestComponentLayouts(TestCase):

    @mock.patch("tethys_components.layouts.HeaderWithNavBar", return_value={})
    def test_NavHeader(self, _):
        test_layout = layouts.NavHeader({
            'app': mock.MagicMock(),
            'user': mock.MagicMock(),
            'nav-links': mock.MagicMock()
        })
        self.assertIsInstance(test_layout, Component)
        self.assertIsInstance(test_layout.render(), dict)
