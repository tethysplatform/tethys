from tethys_sdk.testing import TethysTestCase
from tethys_compute.models import Scheduler


class SchedulerTest(TethysTestCase):
    def set_up(self):
        self.scheduler = Scheduler(
            name='test_scheduler',
            host='localhost',
        )
        self.scheduler.save()

    def tear_down(self):
        self.scheduler.delete()

    def test_Scheduler(self):
        ret = Scheduler.objects.get(name='test_scheduler')

        # Check result
        self.assertIsInstance(ret, Scheduler)
        self.assertEqual('test_scheduler', ret.name)
        self.assertEqual('localhost', ret.host)
