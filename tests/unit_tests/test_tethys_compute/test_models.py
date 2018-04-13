from django.test import TestCase
from tethys_compute.models import TethysJob


class TethysJobTestCase(TestCase):
    def setUp(self):
        job = TethysJob()  # noqa  # TODO remove noqa flag when tests are added

    def test_job(self):
        pass
