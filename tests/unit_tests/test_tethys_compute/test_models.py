from django.test import TestCase
from tethys_compute.models import TethysJob

class TethysJobTestCase(TestCase):
    def setUp(self):
        job = TethysJob()

    def test_job(self):
        pass