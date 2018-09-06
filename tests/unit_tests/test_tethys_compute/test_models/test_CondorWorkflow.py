from tethys_sdk.testing import TethysTestCase
from tethys_compute.models import TethysJob, CondorPyWorkflow, CondorWorkflow
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone
import mock
import os
import shutil
import os.path


class CondorWorkflowTest(TethysTestCase):
    def set_up(self):
        path = os.path.dirname(__file__)
        self.workspace_dir = os.path.join(path, 'workspace')
        self.user = User.objects.create_user('tethys_super', 'user@example.com', 'pass')

        self.condorworkflow = CondorWorkflow(
            _max_jobs={'foo': 'bar'},
            _config='test_config',
            workspace=self.workspace_dir,
            user=self.user,
            name='test name'
        )
        self.condorworkflow.save()

    def tear_down(self):
        self.condorworkflow.delete()

    def test_condor_object_prop(self):
        ret = self.condorworkflow._condor_object

        # Check workflow return
        self.assertEqual({'foo': 'bar'}, ret.max_jobs)
        self.assertEqual('test_config', ret.config)
        self.assertEqual('<DAG: test_name>', repr(ret))

    @mock.patch('tethys_compute.models.CondorBase.condor_object')
    def test_execute(self, mock_co):
        # Mock submit to return a 111 cluster id
        mock_co.submit.return_value = 111

        self.condorworkflow._execute(options=['foo'])

