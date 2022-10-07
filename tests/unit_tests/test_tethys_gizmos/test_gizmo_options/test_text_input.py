import unittest
import tethys_gizmos.gizmo_options.text_input as gizmo_text_input


class TestTextInput(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_TextInput(self):
        display_text = "Text Error"
        name = "inputEmail"
        initial = "bob@example.com"
        icon_append = "glyphicon glyphicon-envelope"
        error = "Here is my error text"

        result = gizmo_text_input.TextInput(
            name=name,
            display_text=display_text,
            initial=initial,
            icon_append=icon_append,
            error=error,
        )
        # Check Result
        self.assertEqual(display_text, result["display_text"])
        self.assertEqual(name, result["name"])
        self.assertEqual(initial, result["initial"])
        self.assertEqual(icon_append, result["icon_append"])
        self.assertEqual(error, result["error"])
