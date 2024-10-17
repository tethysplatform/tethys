from tethys_components import custom
from tethys_components.library import Library as lib
from unittest import mock, IsolatedAsyncioTestCase
from importlib import reload


class TestCustomComponents(IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        mock.patch("reactpy.component", new_callable=lambda: lambda x: x).start()
        reload(custom)

    @classmethod
    def tearDownClass(cls):
        mock.patch.stopall()
        reload(custom)
        lib.refresh()

    def test_Panel_defaults(self):
        test_component = custom.Panel({})
        self.assertIsInstance(test_component, dict)
        self.assertIn("tagName", test_component)
        self.assertIn("attributes", test_component)
        self.assertIn("children", test_component)

    async def test_Panel_all_props_provided(self):
        test_set_show = mock.MagicMock()
        props = {
            "show": True,
            "set-show": test_set_show,
            "position": "right",
            "extent": "30vw",
            "name": "Test Panel 123",
        }
        test_component = custom.Panel(props)
        self.assertIsInstance(test_component, dict)
        self.assertIn("tagName", test_component)
        self.assertIn("attributes", test_component)
        self.assertIn("children", test_component)
        test_set_show.assert_not_called()
        event_handler = test_component["children"][0]["children"][1]["eventHandlers"][
            "on_click"
        ]
        self.assertTrue(callable(event_handler.function))
        await event_handler.function([None])
        test_set_show.assert_called_once_with(False)

    def test_HeaderButton(self):
        test_component = custom.HeaderButton({})
        self.assertIsInstance(test_component, dict)
        self.assertIn("tagName", test_component)
        self.assertIn("attributes", test_component)

    def test_NavIcon(self):
        test_component = custom.NavIcon("test_src", "test_color")
        self.assertIsInstance(test_component, dict)
        self.assertIn("tagName", test_component)
        self.assertIn("attributes", test_component)

    def test_NavMenu(self):
        test_component = custom.NavMenu({})
        self.assertIsInstance(test_component, dict)
        self.assertIn("tagName", test_component)
        self.assertIn("children", test_component)

    def test_HeaderWithNavBar(self):
        custom.lib.hooks = mock.MagicMock()
        custom.lib.hooks.use_query().data.id = 10
        test_app = mock.MagicMock(icon="icon.png", color="test_color")
        test_user = mock.MagicMock()
        test_nav_links = [mock.MagicMock(), mock.MagicMock(), mock.MagicMock()]
        test_component = custom.HeaderWithNavBar(test_app, test_user, test_nav_links)
        self.assertIsInstance(test_component, dict)
        self.assertIn("tagName", test_component)
        self.assertIn("attributes", test_component)
        self.assertIn("children", test_component)
        del custom.lib.hooks

    def test_get_db_object(self):
        test_app = mock.MagicMock()
        return_val = custom.get_db_object(test_app)
        self.assertEqual(return_val, test_app.db_object)

    def test_hooks(self):
        custom.lib.hooks  # should not fail
