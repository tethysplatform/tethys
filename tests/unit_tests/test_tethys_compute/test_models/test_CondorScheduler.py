"""
********************************************************************************
* Name: test_CondorScheduler
* Author: nswain
* Created On: October 02, 2018
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""

from tethys_apps.base.testing.testing import TethysTestCase
from tethys_compute.models import Scheduler, CondorScheduler


class CondorSchedulerTest(TethysTestCase):
    def set_up(self):
        self.scheduler = CondorScheduler(
            name="test_scheduler",
            host="localhost",
            username="tethys_super",
            password="pass",
            private_key_path="test_path",
            private_key_pass="test_pass",
        )
        self.scheduler.save()

    def tear_down(self):
        self.scheduler.delete()

    def test_CondorScheduler(self):
        ret = CondorScheduler.objects.get(name="test_scheduler")

        # Check result
        self.assertIsInstance(ret, CondorScheduler)
        self.assertEqual("test_scheduler", ret.name)
        self.assertEqual("localhost", ret.host)
        self.assertEqual("tethys_super", ret.username)
        self.assertEqual("pass", ret.password)
        self.assertEqual("test_path", ret.private_key_path)
        self.assertEqual("test_pass", ret.private_key_pass)
        self.assertEqual("HTCondor Scheduler", ret._meta.verbose_name)
        self.assertEqual("HTCondor Schedulers", ret._meta.verbose_name_plural)

    def test_CondorScheduler_inheritance(self):
        ret = Scheduler.objects.get_subclass(name="test_scheduler")

        # Check result
        self.assertIsInstance(ret, CondorScheduler)
        self.assertEqual("test_scheduler", ret.name)
        self.assertEqual("localhost", ret.host)
        self.assertEqual("tethys_super", ret.username)
        self.assertEqual("pass", ret.password)
        self.assertEqual("test_path", ret.private_key_path)
        self.assertEqual("test_pass", ret.private_key_pass)
