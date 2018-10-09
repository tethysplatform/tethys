import unittest
import tethys_apps.cli.cli_helpers as cli_helper


class TestCliHelper(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_add_geoserver_rest_to_endpoint(self):
        endpoint = "http://localhost:8181/geoserver/rest/"
        ret = cli_helper.add_geoserver_rest_to_endpoint(endpoint)
        self.assertEqual(endpoint, ret)
