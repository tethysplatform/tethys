from tethys_sdk.testing import TethysTestCase
from tethys_compute.models import Scheduler


class SchedulerTest(TethysTestCase):
    def set_up(self):
        self.scheduler = Scheduler(
            name='test_scheduler',
            host='localhost',
            username='tethys_super',
            password='pass',
            private_key_path='test_path',
            private_key_pass='test_pass'
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
        self.assertEqual('tethys_super', ret.username)
        self.assertEqual('pass', ret.password)
        self.assertEqual('test_path', ret.private_key_path)
        self.assertEqual('test_pass', ret.private_key_pass)
