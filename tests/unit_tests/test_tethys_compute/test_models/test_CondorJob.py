from tethys_sdk.testing import TethysTestCase
from tethys_compute.models.tethys_job import TethysJob
from tethys_compute.models.condor.condor_job import CondorJob
from tethys_compute.models.condor.condor_scheduler import CondorScheduler
from tethys_compute.models.condor.condor_base import CondorBase
from tethys_compute.models.condor.condor_py_job import CondorPyJob
from django.contrib.auth.models import User
from unittest import mock
import os
import shutil
import os.path


class CondorJobTest(TethysTestCase):
    def set_up(self):
        self.user = User.objects.create_user('tethys_super', 'user@example.com', 'pass')

        self.scheduler = CondorScheduler(
            name='test_scheduler',
            host='localhost',
            username='tethys_super',
            password='pass',
        )
        self.scheduler.save()

        path = os.path.dirname(__file__)
        self.workspace_dir = os.path.join(path, 'workspace')

        self.condorjob = CondorJob(
            name='test condorbase',
            description='test_description',
            user=self.user,
            label='test_label',
            cluster_id='1',
            remote_id='test_machine',
            workspace=self.workspace_dir,
            scheduler=self.scheduler,
            condorpyjob_id='99',
            _attributes={'foo': 'bar'},
            _remote_input_files=['test_file1.txt', 'test_file2.txt'],
        )
        self.condorjob.save()

        self.id_val = TethysJob.objects.get(name='test condorbase').id

    def tear_down(self):
        self.scheduler.delete()
        if self.condorjob.condorpyjob_ptr_id == 99:
            self.condorjob.delete()

        if os.path.exists(self.workspace_dir):
            shutil.rmtree(self.workspace_dir)

    def test_type(self):
        ret = self.condorjob.type
        self.assertEqual('CondorJob', ret)

    def test_condor_object_prop(self):
        condorpy_job = self.condorjob._condor_object

        # Check result
        self.assertEqual('test_condorbase', condorpy_job.name)
        self.assertEqual('test_condorbase', condorpy_job.attributes['job_name'])
        self.assertEqual('bar', condorpy_job.attributes['foo'])
        self.assertIn('test_file1.txt', condorpy_job.remote_input_files)
        self.assertIn('test_file2.txt', condorpy_job.remote_input_files)

    @mock.patch('tethys_compute.models.condor.condor_job.CondorBase.condor_object')
    def test_execute(self, mock_cos):
        # TODO: Check if we can mock this or we can provide an executable.
        # Mock condor_object.submit()
        mock_cos.submit.return_value = 111
        self.condorjob._execute(queue=2)

        # Check result
        self.assertEqual(111, self.condorjob.cluster_id)
        self.assertEqual(2, self.condorjob.num_jobs)

    @mock.patch('tethys_compute.models.condor.condor_job.CondorPyJob.update_database_fields')
    @mock.patch('tethys_compute.models.condor.condor_job.CondorBase.update_database_fields')
    def test_update_database_fields(self, mock_cb_update, mock_cj_update):
        # Mock condor_object.submit()
        self.condorjob.update_database_fields()

        # Check result
        mock_cb_update.assert_called()
        mock_cj_update.assert_called()

    def test_condor_job_pre_save(self):
        # Check if CondorBase is updated
        self.assertIsInstance(CondorBase.objects.get(tethysjob_ptr_id=self.id_val), CondorBase)

        # Check if CondorPyJob is updated
        self.assertIsInstance(CondorPyJob.objects.get(condorpyjob_id=99), CondorPyJob)

    @mock.patch('tethys_compute.models.condor.condor_job.CondorBase.condor_object')
    def test_condor_job_pre_delete(self, mock_co):
        if not os.path.exists(self.workspace_dir):
            os.makedirs(self.workspace_dir)
            file_path = os.path.join(self.workspace_dir, 'test_file.txt')
            open(file_path, 'a').close()

        self.condorjob.delete()

        # Check if close_remote is called
        mock_co.close_remote.assert_called()

        # Check if file has been removed
        self.assertFalse(os.path.isfile(file_path))

    @mock.patch('tethys_compute.models.condor.condor_job.log')
    @mock.patch('tethys_compute.models.condor.condor_job.CondorBase.condor_object')
    def test_condor_job_pre_delete_exception(self, mock_co, mock_log):
        mock_co.close_remote.side_effect = Exception('test error')
        self.condorjob.delete()

        # Check if close_remote is called
        mock_log.exception.assert_called_with('test error')
