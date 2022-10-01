import unittest
import tethys_gizmos.gizmo_options.message_box as gizmo_message_box


class TestMessageBox(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_MessageBox(self):
        name = "MB Name"
        title = "MB Title"

        result = gizmo_message_box.MessageBox(name=name, title=title)

        # Check Result
        self.assertEqual(name, result["name"])
        self.assertEqual(title, result["title"])
