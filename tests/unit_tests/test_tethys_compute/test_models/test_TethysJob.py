from tethys_sdk.testing import TethysTestCase
from tethys_compute.models import TethysJob
from django.contrib.auth.models import User
import datetime


class TethysJobTest(TethysTestCase):
    def set_up(self):
        self.user = User.objects.create_user('tethys_super', 'user@example.com', 'pass')
        self.tethysjob = TethysJob(
            name='test_tethysjob',
            description='test_description',
            user=self.user,
            label='test_label',
        )
        self.tethysjob.save()

    def tear_down(self):
        self.tethysjob.delete()

    def test_update_status_interval_prop(self):
        ret = TethysJob.objects.get(name='test_tethysjob').update_status_interval

        # Check result
        self.assertIsInstance(ret, datetime.timedelta)
        self.assertEqual(datetime.timedelta(0, 10), ret)

    def test_last_status_update_prop(self):
        pass
        # ret = TethysJob.objects.get(name='test_tethysjob').last_status_update

        # # Check result
        # import pdb
        # pdb.set_trace()
