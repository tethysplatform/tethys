from tethys_sdk.testing import TethysTestCase
from tethys_compute.models import BasicJob
from django.contrib.auth.models import User


class CondorBaseTest(TethysTestCase):
    def set_up(self):
        self.user = User.objects.create_user("tethys_super", "user@example.com", "pass")
        self.basic_job = BasicJob(
            name="test_basicjob",
            description="test_description",
            user=self.user,
            label="test_label",
        )
        self.basic_job.save()

    def tear_down(self):
        self.basic_job.delete()

    def test_type(self):
        ret = self.basic_job.type
        self.assertEqual("BasicJob", ret)

    def test_execute(self):
        ret = BasicJob.objects.get(name="test_basicjob")._execute()
        self.assertIsNone(ret)

    def test__update_status(self):
        ret = BasicJob.objects.get(name="test_basicjob")._update_status()
        self.assertIsNone(ret)

    def test_process_results(self):
        ret = BasicJob.objects.get(name="test_basicjob")._process_results()
        self.assertIsNone(ret)

    def test_stop(self):
        ret = BasicJob.objects.get(name="test_basicjob").stop()
        self.assertIsNone(ret)

    def test_pause(self):
        ret = BasicJob.objects.get(name="test_basicjob").pause()
        self.assertIsNone(ret)

    def test_resume(self):
        ret = BasicJob.objects.get(name="test_basicjob").resume()
        self.assertIsNone(ret)

    def test_resubmit(self):
        job = BasicJob.objects.get(name="test_basicjob")
        job._resubmit()
        self.assertEqual(job.status, "Running")
