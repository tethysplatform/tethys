import unittest
from tethys_apps.templatetags import humanize


class TestHumanize(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_human_duration_minutes(self):
        ret = humanize.human_duration("PT30M")
        self.assertIn(ret, ["in 30 minutes", "in 29 minutes"])

    def test_human_duration_a_day(self):
        ret = humanize.human_duration("P1DT12H")
        self.assertIn(ret, ["in a day"])

    def test_human_duration_hour(self):
        ret = humanize.human_duration("PT1H")
        self.assertIn(ret, ["in an hour"])
