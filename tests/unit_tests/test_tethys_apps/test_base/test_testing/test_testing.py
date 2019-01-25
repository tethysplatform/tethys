import unittest
import tethys_apps.base.testing.testing as base_testing
from unittest import mock
from tethys_apps.base.app_base import TethysAppBase


class TestClass():
    pass


def bypass_init(self):
    pass


class TestTethysTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_apps.harvester.SingletonHarvester')
    def test_setup(self, mock_harvest):
        base_testing.TethysTestCase.__init__ = bypass_init
        t = base_testing.TethysTestCase()
        t.set_up = mock.MagicMock()
        t.setUp()

        t.set_up.assert_called()
        mock_harvest().harvest.assert_called()

    def test_set_up(self):
        base_testing.TethysTestCase.__init__ = bypass_init
        t = base_testing.TethysTestCase()
        t.set_up()

    def test_teardown(self):
        base_testing.TethysTestCase.__init__ = bypass_init
        t = base_testing.TethysTestCase()
        t.tear_down = mock.MagicMock()
        t.tearDown()

        t.tear_down.assert_called()

    def test_tear_down(self):
        base_testing.TethysTestCase.__init__ = bypass_init
        t = base_testing.TethysTestCase()
        t.tear_down()

    @mock.patch('tethys_apps.base.testing.testing.TethysAppBase.create_persistent_store')
    @mock.patch('tethys_apps.models.TethysApp')
    @mock.patch('tethys_apps.base.testing.testing.is_testing_environment')
    def test_create_test_persistent_stores_for_app(self, mock_ite, mock_ta, mock_cps):
        mock_ite.return_value = True
        app_class = TethysAppBase

        # mock_db_setting
        db_setting = mock.MagicMock(spatial='test_spatial', initializer='test_init')
        db_setting.name = 'test_name'
        db_app = mock.MagicMock(persistent_store_database_settings=[db_setting])
        mock_ta.objects.get.return_value = db_app

        # Execute
        base_testing.TethysTestCase.create_test_persistent_stores_for_app(app_class)

        # Check Result
        mock_ta.objects.get.assert_called_with(package='')
        mock_cps.assert_called_with(connection_name=None, db_name='test_name', force_first_time=True,
                                    initializer='test_init', refresh=True, spatial='test_spatial')

    @mock.patch('tethys_apps.base.testing.testing.is_testing_environment')
    def test_create_test_persistent_stores_for_app_not_testing_env(self, mock_ite):
        mock_ite.return_value = False
        app_class = TethysAppBase
        self.assertRaises(EnvironmentError, base_testing.TethysTestCase.create_test_persistent_stores_for_app,
                          app_class)

    @mock.patch('tethys_apps.base.testing.testing.is_testing_environment')
    def test_create_test_persistent_stores_for_app_not_subclass(self, mock_ite):
        mock_ite.return_value = True
        app_class = TestClass
        self.assertRaises(TypeError, base_testing.TethysTestCase.create_test_persistent_stores_for_app, app_class)

    @mock.patch('tethys_apps.base.testing.testing.TethysAppBase.create_persistent_store')
    @mock.patch('tethys_apps.models.TethysApp')
    @mock.patch('tethys_apps.base.testing.testing.is_testing_environment')
    def test_create_test_persistent_stores_for_app_not_success(self, mock_ite, mock_ta, mock_cps):
        mock_ite.return_value = True
        app_class = TethysAppBase

        # mock_db_setting
        db_setting = mock.MagicMock()
        db_app = mock.MagicMock(persistent_store_database_settings=[db_setting])
        mock_ta.objects.get.return_value = db_app

        # mock create_peristent_store
        mock_cps.return_value = False

        # Execute
        self.assertRaises(SystemError, base_testing.TethysTestCase.create_test_persistent_stores_for_app, app_class)

    @mock.patch('tethys_apps.base.testing.testing.TethysAppBase.drop_persistent_store')
    @mock.patch('tethys_apps.base.testing.testing.get_test_db_name')
    @mock.patch('tethys_apps.base.testing.testing.TethysAppBase.list_persistent_store_databases')
    @mock.patch('tethys_apps.base.testing.testing.is_testing_environment')
    def test_destroy_test_persistent_stores_for_app(self, mock_ite, mock_lps, mock_get, mock_dps):
        mock_ite.return_value = True
        app_class = TethysAppBase

        mock_lps.return_value = ['db_name']
        mock_get.return_value = 'test_db_name'
        # Execute
        base_testing.TethysTestCase.destroy_test_persistent_stores_for_app(app_class)

        # Check mock called
        mock_get.assert_called_with('db_name')
        mock_dps.assert_called_with('test_db_name')

    @mock.patch('tethys_apps.base.testing.testing.is_testing_environment')
    def test_destroy_test_persistent_stores_for_app_not_testing_env(self, mock_ite):
        mock_ite.return_value = False
        app_class = TethysAppBase
        self.assertRaises(EnvironmentError, base_testing.TethysTestCase.destroy_test_persistent_stores_for_app,
                          app_class)

    @mock.patch('tethys_apps.base.testing.testing.is_testing_environment')
    def test_destroy_test_persistent_stores_for_app_not_subclass(self, mock_ite):
        mock_ite.return_value = True
        app_class = TestClass
        # Execute
        self.assertRaises(TypeError, base_testing.TethysTestCase.destroy_test_persistent_stores_for_app, app_class)

    @mock.patch('django.contrib.auth.models.User')
    def test_create_test_user(self, mock_user):
        mock_user.objects.create_user = mock.MagicMock(return_value='test_create_user')

        result = base_testing.TethysTestCase.create_test_user(username='test_user', password='test_pass',
                                                              email='test_e')

        # Check result
        self.assertEqual('test_create_user', result)
        mock_user.objects.create_user.assert_called_with(username='test_user', password='test_pass', email='test_e')

    @mock.patch('django.contrib.auth.models.User')
    def test_create_test_super_user(self, mock_user):
        mock_user.objects.create_superuser = mock.MagicMock(return_value='test_create_super_user')

        result = base_testing.TethysTestCase.create_test_superuser(username='test_user', password='test_pass',
                                                                   email='test_e')

        # Check result
        self.assertEqual('test_create_super_user', result)
        mock_user.objects.create_superuser.assert_called_with(username='test_user', password='test_pass',
                                                              email='test_e')

    @mock.patch('tethys_apps.base.testing.testing.Client')
    def test_get_test_client(self, mock_client):
        mock_client.return_value = 'test_get_client'

        result = base_testing.TethysTestCase.get_test_client()

        # Check result
        self.assertEqual('test_get_client', result)
