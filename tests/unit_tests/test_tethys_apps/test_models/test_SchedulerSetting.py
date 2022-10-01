from tethys_sdk.testing import TethysTestCase
from tethys_apps.models import TethysApp
from tethys_apps.exceptions import TethysAppSettingNotAssigned
from django.core.exceptions import ValidationError
from tethys_compute.models.condor.condor_scheduler import CondorScheduler
from tethys_compute.models.dask.dask_scheduler import DaskScheduler


class SchedulerSettingTests(TethysTestCase):
    def set_up(self):
        self.test_app = TethysApp.objects.get(package="test_app")

        # Create condor scheduler and assign to condor setting
        self.condor_scheduler = CondorScheduler(
            name="test_condor_scheduler",
            host="https://example.com",
            port="33",
            username="condor",
            password="password",
            private_key_path="/path/to/some/key",
            private_key_pass="secret",
        )
        self.condor_scheduler.save()

        self.condor_setting = self.test_app.settings_set.select_subclasses().get(
            name="primary_condor"
        )
        self.condor_setting.scheduler_service = self.condor_scheduler
        self.condor_setting.required = True
        self.condor_setting.save()

        # Create dask scheduler and assign to dask setting
        self.dask_scheduler = DaskScheduler(
            name="test_dask_scheduler",
            host="https://example.com",
            timeout=5,
            heartbeat_interval=1,
            dashboard="https://example.com/dashboard",
        )
        self.dask_scheduler.save()

        self.dask_setting = self.test_app.settings_set.select_subclasses().get(
            name="primary_dask"
        )
        self.dask_setting.scheduler_service = self.dask_scheduler
        self.dask_setting.required = False
        self.dask_setting.save()

    def tear_down(self):
        self.condor_setting.scheduler_service = None
        self.condor_setting.required = True
        self.condor_setting.save()
        self.dask_setting.scheduler_service = None
        self.dask_setting.required = False
        self.dask_setting.save()

    def test_clean_empty_when_required(self):
        ss = self.test_app.settings_set.select_subclasses().get(name="primary_condor")
        ss.scheduler_service = None
        ss.required = True
        ss.save()

        with self.assertRaises(ValidationError) as cm:
            ss.clean()

        self.assertEqual("['Required.']", str(cm.exception))

    def test_clean_condor_engine_but_dask_assigned(self):
        ss = self.test_app.settings_set.select_subclasses().get(name="primary_condor")
        ss.scheduler_service = self.dask_scheduler
        ss.save()

        with self.assertRaises(ValidationError) as cm:
            ss.clean()

        self.assertEqual("['Please select a Condor Scheduler.']", str(cm.exception))

    def test_clean_dask_engine_but_condor_assigned(self):
        ss = self.test_app.settings_set.select_subclasses().get(name="primary_dask")
        ss.scheduler_service = self.condor_scheduler
        ss.save()

        with self.assertRaises(ValidationError) as cm:
            ss.clean()

        self.assertEqual("['Please select a Dask Scheduler.']", str(cm.exception))

    def test_get_value_condor_service(self):
        # Get setting through fresh query
        ss = self.test_app.settings_set.select_subclasses().get(name="primary_condor")

        # Execute
        ret = ss.get_value()

        # Check result
        self.assertIsInstance(ret, CondorScheduler)
        self.assertEqual("test_condor_scheduler", ret.name)
        self.assertEqual("https://example.com", ret.host)
        self.assertEqual(33, ret.port)
        self.assertEqual("condor", ret.username)
        self.assertEqual("password", ret.password)
        self.assertEqual("/path/to/some/key", ret.private_key_path)
        self.assertEqual("secret", ret.private_key_pass)

    def test_get_value_dask_service(self):
        # Get setting through fresh query
        ss = self.test_app.settings_set.select_subclasses().get(name="primary_dask")

        # Execute
        ret = ss.get_value()

        # Check result
        self.assertIsInstance(ret, DaskScheduler)
        self.assertEqual("test_dask_scheduler", ret.name)
        self.assertEqual("https://example.com", ret.host)
        self.assertEqual(5, ret.timeout)
        self.assertEqual(1, ret.heartbeat_interval)
        self.assertEqual("https://example.com/dashboard", ret.dashboard)

    def test_get_value_NotAssigned(self):
        # Unset the scheduler service for this test
        ss = self.test_app.settings_set.select_subclasses().get(name="primary_dask")
        ss.scheduler_service = None
        ss.save()

        with self.assertRaises(TethysAppSettingNotAssigned) as cm:
            ss.get_value()

        self.assertEqual(
            "Cannot find Scheduler for SchedulerSetting "
            '"primary_dask" for app "test_app": no '
            "Scheduler assigned.",
            str(cm.exception),
        )
