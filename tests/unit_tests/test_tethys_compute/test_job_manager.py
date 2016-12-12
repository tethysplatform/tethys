from django.test import TestCase
from tethys_apps.base import TethysAppBase
from tethys_compute.job_manager import JobManager, TethysJob, CondorJob
from django.contrib.auth.models import User

def echo(arg):
    return arg

class TestApp(TethysAppBase):
    def job_templates(self):
        return []

class TethysJobTestCase(TestCase):
    def setUp(self):
        self.app = TestApp()
        self.job_manager = JobManager(self.app)
        self.user = User.objects.create_user('user', 'user@example.com', 'pass')

    def test_create_job(self):
        job = self.job_manager.create_empty_job('job', self.user, CondorJob)
        self.assertIsInstance(job, CondorJob, 'Empty job is not an instance of CondorJob')
        self.assertIsInstance(job, TethysJob, 'Empty job is not an instance of TethysJob')

        self.assertIsInstance(job.extended_properties, dict)

        job.extended_properties['property'] = 'value'


        job.save()

        self.assertDictEqual(job.extended_properties, {'property': 'value'})

        job.process_results = echo

        job.save()

        self.assertEqual(job.process_results('test'), 'test')
        self.assertTrue(hasattr(job.process_results, '__call__'))