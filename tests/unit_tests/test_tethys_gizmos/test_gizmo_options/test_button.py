import unittest
import tethys_gizmos.gizmo_options.button as gizmo_button


class TestButton(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_ButtonGroup(self):
        buttons = [{'display_text': 'Add', 'style': 'success'},
                   {'display_text': 'Delete', 'style': 'danger'}]
        result = gizmo_button.ButtonGroup(buttons)

        self.assertIn(buttons[0], result['buttons'])
        self.assertIn(buttons[1], result['buttons'])

    def test_Button(self):
        display_text = 'Add'
        name = 'Aquaveo'
        style = 'success'
        icon = 'glyphicon glyphicon-globe'
        href = 'linktest'
        attr = {'title': 'test title', 'description': 'test attributes'}
        test_class = 'Test Class'
        result = gizmo_button.Button(display_text=display_text, name=name, style=style,
                                     icon=icon, href=href, submit=True, disabled=False,
                                     attributes=attr, classes=test_class)

        self.assertEqual(display_text, result['display_text'])
        self.assertEqual(name, result['name'])
        self.assertEqual(style, result['style'])
        self.assertEqual(icon, result['icon'])
        self.assertEqual(href, result['href'])
        self.assertEqual(attr, result['attributes'])
        self.assertEqual(test_class, result['classes'])
