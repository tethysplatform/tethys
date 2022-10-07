import unittest
import tethys_gizmos.context_processors as gizmos_context_processor


class TestContextProcessor(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_tethys_gizmos_context(self):
        result = gizmos_context_processor.tethys_gizmos_context("request")

        # Check Result
        self.assertEqual({"gizmos_rendered": []}, result)
