from tethys_sdk.testing import TethysTestCase
from tethys_compute.models.condor.condor_scheduler import CondorScheduler
from tethys_compute.models.condor.condor_py_job import CondorPyJob
from tethys_compute.models.condor.condor_job import CondorJob
from condorpy import Templates
from django.contrib.auth.models import User
from condorpy import Job
from unittest import mock


class CondorPyJobTest(TethysTestCase):
    def set_up(self):
        self.condor_py = CondorPyJob(
            condorpyjob_id='99',
            _attributes={'foo': 'bar'},
            _remote_input_files=['test_file1.txt', 'test_file2.txt'],
        )

        self.condor_py.save()

        user = User.objects.create_user('tethys_super', 'user@example.com', 'pass')

        scheduler = CondorScheduler(
            name='test_scheduler',
            host='localhost',
            username='tethys_super',
            password='pass',
        )

        self.condorjob = CondorJob(
            name='test condorbase',
            description='test_description',
            user=user,
            label='test_label',
            workspace='test_workspace',
            scheduler=scheduler,
            condorpyjob_id='98',
        )

    def tear_down(self):
        self.condor_py.delete()

    def test_init(self):
        ret = CondorPyJob(_attributes={'foo': 'bar'},
                          condorpy_template_name='vanilla_base',
                          )
        # Check result
        # Instance of CondorPyJob
        self.assertIsInstance(ret, CondorPyJob)
        # Check return vanilla Django base
        self.assertEqual('vanilla', ret.attributes['universe'])

    def test_get_condorpy_template(self):
        ret = CondorPyJob.get_condorpy_template('vanilla_base')

        # Check result
        self.assertEqual(ret, Templates.vanilla_base)

    def test_get_condorpy_template_default(self):
        ret = CondorPyJob.get_condorpy_template(None)

        # Check result
        self.assertEqual(ret, Templates.base)

    def test_get_condorpy_template_no_template(self):
        ret = CondorPyJob.get_condorpy_template('test')

        # Check result
        self.assertEqual(ret, Templates.base)

    def test_condorpy_job(self):
        ret = self.condorjob.condorpy_job

        # Check result for Django Job
        self.assertIsInstance(ret, Job)
        self.assertEqual('test_condorbase', ret.name)
        self.assertEqual('test_workspace', ret._cwd)
        self.assertEqual('test_condorbase', ret.attributes['job_name'])
        self.assertEqual(1, ret.num_jobs)

    def test_attributes(self):
        ret = CondorPyJob.objects.get(condorpyjob_id='99').attributes

        self.assertEqual({'foo': 'bar'}, ret)

    @mock.patch('tethys_compute.models.condor.condor_py_job.CondorPyJob.condorpy_job')
    def test_set_attributes(self, mock_ca):
        set_attributes = {'baz': 'qux'}
        ret = CondorPyJob.objects.get(condorpyjob_id='99')

        ret.attributes = set_attributes

        # Mock setter
        mock_ca._attributes = set_attributes

        self.assertEqual({'baz': 'qux'}, ret.attributes)

    @mock.patch('tethys_compute.models.condor.condor_py_job.CondorPyJob.condorpy_job')
    def test_numjobs(self, mock_cj):
        num_job = 5
        ret = CondorPyJob.objects.get(condorpyjob_id='99')
        ret.num_jobs = num_job

        # Mock setter
        mock_cj.numb_jobs = num_job

        # self.assertEqual(5, ret)
        self.assertEqual(num_job, ret.num_jobs)

    @mock.patch('tethys_compute.models.condor.condor_py_job.CondorPyJob.condorpy_job')
    def test_remote_input_files(self, mock_cj):
        ret = CondorPyJob.objects.get(condorpyjob_id='99')
        ret.remote_input_files = ['test_newfile1.txt']

        # Mock setter
        mock_cj.remote_input_files = ['test_newfile1.txt']

        # Check result
        self.assertEqual(['test_newfile1.txt'], ret.remote_input_files)

    def test_initial_dir(self):
        ret = self.condorjob.initial_dir

        # Check result
        self.assertEqual('test_workspace/.', ret)

    def test_set_and_get_attribute(self):
        self.condorjob.set_attribute('test', 'value')

        ret = self.condorjob.get_attribute('test')

        # Check Result
        self.assertEqual('value', ret)

    def test_update_database_fields(self):
        ret = self.condorjob

        # Before Update
        self.assertFalse(ret.attributes)

        # Execute
        ret.update_database_fields()

        # Check after update
        self.assertEqual('test_condorbase', ret.attributes['job_name'])
