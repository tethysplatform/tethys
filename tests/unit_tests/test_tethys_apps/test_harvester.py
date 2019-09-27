import io
import unittest
from unittest import mock

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import ProgrammingError
from tethys_apps.harvester import SingletonHarvester
from tethys_apps.base.testing.environment import set_testing_environment


class HarvesterTest(unittest.TestCase):

    def setUp(self):
        set_testing_environment(False)

    def tearDown(self):
        set_testing_environment(True)

    @mock.patch('tethys_apps.harvester.tethys_log')
    @mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_harvest_extensions_apps(self, mock_stdout, _):
        """
        Test for SingletonHarvester.harvest.
        Checks for expected text output
        :param mock_stdout:  mock for text output
        :return:
        """
        shv = SingletonHarvester()
        shv.harvest()

        self.assertIn('Loading Tethys Extensions...', mock_stdout.getvalue())
        self.assertIn('Tethys Extensions Loaded:', mock_stdout.getvalue())
        self.assertIn('test_extension', mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=io.StringIO)
    @mock.patch('pkgutil.iter_modules')
    def test_harvest_extensions_exception(self, mock_pkgutil, mock_stdout):
        """
        Test for SingletonHarvester.harvest.
        With an exception thrown, when harvesting the extensions
        :param mock_pkgutil:  mock for the exception
        :param mock_stdout:  mock for the text output
        :return:
        """
        mock_pkgutil.side_effect = Exception

        shv = SingletonHarvester()
        shv.harvest_extensions()

        self.assertIn('Loading Tethys Extensions...', mock_stdout.getvalue())
        self.assertNotIn('Tethys Extensions Loaded:', mock_stdout.getvalue())
        self.assertNotIn('test_extension', mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=io.StringIO)
    @mock.patch('pkgutil.iter_modules')
    def test_harvest_apps_exception(self, mock_pkgutil, mock_stdout):
        """
        Test for SingletonHarvester.harvest.
        With an exception thrown, when harvesting the extensions
        :param mock_pkgutil:  mock for the exception
        :param mock_stdout:  mock for the text output
        :return:
        """
        mock_pkgutil.side_effect = Exception

        shv = SingletonHarvester()
        shv.harvest_apps()

        self.assertIn('Loading Tethys Apps...', mock_stdout.getvalue())
        self.assertNotIn('Tethys Apps Loaded:', mock_stdout.getvalue())
        self.assertNotIn('test_app', mock_stdout.getvalue())

    def test_harvest_get_url_patterns(self):
        """
        Test for SingletonHarvester.get_url_patterns
        :return:
        """
        shv = SingletonHarvester()
        app_url_patterns = shv.get_url_patterns()['app_url_patterns']
        ext_url_patterns = shv.get_url_patterns()['ext_url_patterns']
        app_ws_patterns = shv.get_url_patterns()['ws_url_patterns']

        self.assertGreaterEqual(len(app_url_patterns), 1)
        self.assertIn('test_app', app_url_patterns)
        self.assertGreaterEqual(len(ext_url_patterns), 1)
        self.assertIn('test_extension', ext_url_patterns)
        self.assertGreaterEqual(len(app_ws_patterns), 1)
        self.assertIn('test_app', app_ws_patterns)

    def test_harvest_validate_extension(self):
        """
        Test for SingletonHarvester._validate_extension
        :return:
        """
        mock_args = mock.MagicMock()

        shv = SingletonHarvester()
        extension = shv._validate_extension(mock_args)
        self.assertEqual(mock_args, extension)

    def test_harvest_validate_app(self):
        """
        Test for SingletonHarvester._validate_app
        Gives invalid icon and color information which is altered by the function
        :return:
        """
        mock_args = mock.MagicMock()
        mock_args.icon = '/foo_icon'  # prepended slash
        mock_args.color = 'foo_color'  # missing prepended #, not 6 or 3 digit hex color

        shv = SingletonHarvester()
        validate = shv._validate_app(mock_args)

        self.assertEqual('foo_icon', validate.icon)
        self.assertEqual('', validate.color)

    @mock.patch('sys.stdout', new_callable=io.StringIO)
    @mock.patch('tethys_apps.harvester.tethys_log.exception')
    def test_harvest_extension_instances_ImportError(self, mock_logexception, mock_stdout):
        """
        Test for SingletonHarvester._harvest_extension_instances
        With an ImportError exception thrown due to invalid argument information passed
        :param mock_logexception:  mock for the tethys_log exception
        :param mock_stdout:  mock for the text output
        :return:
        """
        mock_args = mock.MagicMock()
        dict_ext = {'foo': 'foo_ext'}
        mock_args = dict_ext

        shv = SingletonHarvester()
        shv._harvest_extension_instances(mock_args)

        valid_ext_instances = []
        valid_extension_modules = {}

        self.assertEqual(valid_ext_instances, shv.extensions)
        self.assertEqual(valid_extension_modules, shv.extension_modules)
        mock_logexception.assert_called_once()
        self.assertIn('Tethys Extensions Loaded:', mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=io.StringIO)
    @mock.patch('tethys_apps.harvester.tethys_log.exception')
    @mock.patch('tethys_apps.harvester.issubclass')
    def test_harvest_extension_instances_TypeError(self, mock_subclass, mock_logexception, mock_stdout):
        """
        Test for SingletonHarvester._harvest_extension_instances
        With a TypeError exception mocked up
        :param mock_subclass:  mock for the TypeError exception
        :param mock_logexception:  mock for the tethys_log exception
        :param mock_stdout:  mock for the text output
        :return:
        """
        mock_args = mock.MagicMock()
        dict_ext = {'test_extension': 'tethysext.test_extension'}
        mock_args = dict_ext
        mock_subclass.side_effect = TypeError

        shv = SingletonHarvester()
        shv._harvest_extension_instances(mock_args)

        valid_ext_instances = []
        valid_extension_modules = {}

        self.assertEqual(valid_ext_instances, shv.extensions)
        self.assertEqual(valid_extension_modules, shv.extension_modules)
        mock_logexception.assert_not_called()
        mock_subclass.assert_called()
        self.assertIn('Tethys Extensions Loaded:', mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=io.StringIO)
    @mock.patch('tethys_apps.harvester.tethys_log.exception')
    def test_harvest_app_instances_ImportError(self, mock_logexception, mock_stdout):
        """
        Test for SingletonHarvester._harvest_app_instances
        With an ImportError exception thrown due to invalid argument information passed
        :param mock_logexception:  mock for the tethys_log exception
        :param mock_stdout:  mock for the text output
        :return:
        """
        mock_args = mock.MagicMock()
        list_apps = {'__init__.py': '__init__.py', 'foo': 'foo'}
        mock_args = list_apps

        shv = SingletonHarvester()
        shv._harvest_app_instances(mock_args)

        valid_app_instance_list = []

        self.assertEqual(valid_app_instance_list, shv.apps)
        mock_logexception.assert_called_once()
        self.assertIn('Tethys Apps Loaded:', mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=io.StringIO)
    @mock.patch('tethys_apps.harvester.tethys_log.exception')
    @mock.patch('tethys_apps.harvester.issubclass')
    def test_harvest_app_instances_TypeError(self, mock_subclass, mock_logexception, mock_stdout):
        """
        Test for SingletonHarvester._harvest_app_instances
        :param mock_subclass:  mock for the TypeError exception
        :param mock_logexception:  mock for the tethys_log exception
        :param mock_stdout:  mock for the text output
        :return:
        """
        mock_args = mock.MagicMock()
        list_apps = {'test_app': 'tethysapp.test_app'}

        mock_args = list_apps
        mock_subclass.side_effect = TypeError

        shv = SingletonHarvester()
        shv._harvest_app_instances(mock_args)

        valid_app_instance_list = []

        self.assertEqual(valid_app_instance_list, shv.apps)
        mock_logexception.assert_not_called()
        mock_subclass.assert_called()
        self.assertIn('Tethys Apps Loaded:', mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=io.StringIO)
    @mock.patch('tethys_apps.harvester.tethys_log.exception')
    @mock.patch('tethysapp.test_app.app.TestApp.url_maps')
    def test_harvest_app_instances_load_url_patterns_exception(self, mock_url_maps, mock_logexception, mock_stdout):
        """
        Test for SingletonHarvester._harvest_app_instances
        For the app url patterns exception
        With an exception mocked up for the url_patterns
        :param mock_url_maps:  mock for url_patterns to throw an Exception
        :param mock_logexception:  mock for the tethys_log exception
        :param mock_stdout:  mock for the text output
        :return:
        """
        list_apps = {'test_app': 'tethysapp.test_app'}
        mock_args = list_apps
        mock_url_maps.side_effect = ImportError

        shv = SingletonHarvester()
        shv._harvest_app_instances(mock_args)

        mock_logexception.assert_called()
        mock_url_maps.assert_called()
        self.assertIn('Tethys Apps Loaded:', mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=io.StringIO)
    @mock.patch('tethys_apps.harvester.tethys_log.exception')
    @mock.patch('tethysapp.test_app.app.TestApp.url_maps')
    def test_harvest_app_instances_load_handler_patterns_exception(self, mock_url_maps, mock_logexception, mock_stdout):
        """
        Test for SingletonHarvester._harvest_app_instances
        For the app url patterns exception
        With an exception mocked up for the url_patterns
        :param mock_url_maps:  mock for url_patterns to throw an Exception
        :param mock_logexception:  mock for the tethys_log exception
        :param mock_stdout:  mock for the text output
        :return:
        """
        list_apps = {'test_app': 'tethysapp.test_app'}
        mock_args = list_apps
        mock_url_maps.side_effect = ['', ImportError]

        shv = SingletonHarvester()
        shv._harvest_app_instances(mock_args)

        mock_logexception.assert_called()
        mock_url_maps.assert_called()
        self.assertIn('Tethys Apps Loaded:', mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=io.StringIO)
    @mock.patch('tethys_apps.harvester.tethys_log.warning')
    @mock.patch('tethysapp.test_app.app.TestApp.register_app_permissions')
    def test_harvest_app_instances_programming_error(self, mock_permissions, mock_logwarning, mock_stdout):
        """
        Test for SingletonHarvester._harvest_app_instances
        For the app permissions exception (ProgrammingError)
        With an exception mocked up for register_app_permissions
        :param mock_permissions:  mock for throwing a ProgrammingError exception
        :param mock_logerror:  mock for the tethys_log error
        :param mock_stdout:  mock for the text output
        :return:
        """
        list_apps = {'test_app': 'tethysapp.test_app'}

        mock_permissions.side_effect = ProgrammingError

        shv = SingletonHarvester()
        shv._harvest_app_instances(list_apps)

        mock_logwarning.assert_called()
        mock_permissions.assert_called()
        self.assertIn('Tethys Apps Loaded:', mock_stdout.getvalue())
        self.assertIn('test_app', mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=io.StringIO)
    @mock.patch('tethys_apps.harvester.tethys_log.warning')
    @mock.patch('tethysapp.test_app.app.TestApp.register_app_permissions')
    def test_harvest_app_instances_object_does_not_exist(self, mock_permissions, mock_logwarning, mock_stdout):
        """
        Test for SingletonHarvester._harvest_app_instances
        For the app permissions exception (ObjectDoesNotExist)
        With an exception mocked up for register_app_permissions
        :param mock_permissions:  mock for throwing a ObjectDoesNotExist exception
        :param mock_logerror:  mock for the tethys_log error
        :param mock_stdout:  mock for the text output
        :return:
        """
        list_apps = {'test_app': 'tethysapp.test_app'}

        mock_permissions.side_effect = ObjectDoesNotExist

        shv = SingletonHarvester()
        shv._harvest_app_instances(list_apps)

        mock_logwarning.assert_called()
        mock_permissions.assert_called()
        self.assertIn('Tethys Apps Loaded:', mock_stdout.getvalue())
        self.assertIn('test_app', mock_stdout.getvalue())
