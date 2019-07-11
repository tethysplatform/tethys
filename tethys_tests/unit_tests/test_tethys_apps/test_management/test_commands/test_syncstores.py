try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import unittest
from unittest import mock

from argparse import ArgumentParser
from tethys_apps.management.commands import syncstores


class ManagementCommandsSyncstoresTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_syncstores_add_arguments(self):
        parser = ArgumentParser()
        cmd = syncstores.Command()
        cmd.add_arguments(parser)
        self.assertIn('app_name', parser.format_usage())
        self.assertIn('[-r]', parser.format_usage())
        self.assertIn('[-f]', parser.format_usage())
        self.assertIn('[-d DATABASE]', parser.format_usage())
        self.assertIn('--refresh', parser.format_help())
        self.assertIn('--firsttime', parser.format_help())
        self.assertIn('--database DATABASE', parser.format_help())

    @mock.patch('tethys_apps.management.commands.syncstores.Command.provision_persistent_stores')
    def test_handle(self, mock_provision_persistent_stores):
        # Mock the function, it will be tested elsewhere
        mock_provision_persistent_stores.return_value = True

        cmd = syncstores.Command()
        cmd.handle(app_name='foo')

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.models.TethysApp.persistent_store_database_settings')
    @mock.patch('tethys_apps.models.TethysApp.persistent_store_database_settings')
    @mock.patch('tethys_apps.models.TethysApp.persistent_store_database_settings')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_provision_persistent_stores_all_apps_no_database(self, mock_app, mock_setting1, mock_setting2,
                                                              mock_setting3, mock_stdout):
        # Mock arguments
        mock_app_names = syncstores.ALL_APPS
        mock_options = {'database': '', 'refresh': True, 'first_time': True}

        # Mock for ps db settings
        mock_setting1.name = 'setting1_name'
        mock_setting1.create_persistent_store_database.return_value = True
        mock_setting2.name = 'setting2_name'
        mock_setting2.create_persistent_store_database.return_value = True
        mock_setting3.name = 'setting3_name'
        mock_setting3.create_persistent_store_database.return_value = True

        # Mock for TethysApp (2 apps, 2 settings for first app, 1 setting for second app)
        mock_app1 = mock.MagicMock()
        mock_app1.persistent_store_database_settings = [mock_setting1, mock_setting2]
        mock_app2 = mock.MagicMock()
        mock_app2.persistent_store_database_settings = [mock_setting3]
        mock_app.objects.all.return_value = [mock_app1, mock_app2]

        cmd = syncstores.Command()
        cmd.provision_persistent_stores(app_names=mock_app_names, options=mock_options)

        mock_app.objects.all.assert_called_once()
        mock_setting1.create_persistent_store_database.assert_called_once_with(refresh=True, force_first_time=True)
        mock_setting2.create_persistent_store_database.assert_called_once_with(refresh=True, force_first_time=True)
        mock_setting3.create_persistent_store_database.assert_called_once_with(refresh=True, force_first_time=True)
        self.assertIn('Provisioning Persistent Stores...', mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.models.TethysApp.persistent_store_database_settings')
    @mock.patch('tethys_apps.models.TethysApp.persistent_store_database_settings')
    @mock.patch('tethys_apps.models.TethysApp.persistent_store_database_settings')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_provision_persistent_stores_all_apps_database_no_match(self, mock_app, mock_setting1, mock_setting2,
                                                                    mock_setting3, mock_stdout):
        # Mock arguments
        mock_app_names = syncstores.ALL_APPS
        mock_options = {'database': '/foo/no_match', 'refresh': True, 'first_time': True}

        # Mock for ps db settings
        mock_setting1.name = 'setting1_name'
        mock_setting1.create_persistent_store_database.return_value = True
        mock_setting2.name = 'setting2_name'
        mock_setting2.create_persistent_store_database.return_value = True
        mock_setting3.name = 'setting3_name'
        mock_setting3.create_persistent_store_database.return_value = True

        # Mock for TethysApp (2 apps, 2 settings for first app, 1 setting for second app)
        mock_app1 = mock.MagicMock()
        mock_app1.persistent_store_database_settings = [mock_setting1, mock_setting2]
        mock_app2 = mock.MagicMock()
        mock_app2.persistent_store_database_settings = [mock_setting3]
        mock_app.objects.all.return_value = [mock_app1, mock_app2]

        cmd = syncstores.Command()
        cmd.provision_persistent_stores(app_names=mock_app_names, options=mock_options)

        mock_app.objects.all.assert_called_once()
        mock_setting1.create_persistent_store_database.assert_not_called()
        mock_setting2.create_persistent_store_database.assert_not_called()
        mock_setting3.create_persistent_store_database.assert_not_called()
        self.assertIn('Provisioning Persistent Stores...', mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.models.TethysApp.persistent_store_database_settings')
    @mock.patch('tethys_apps.models.TethysApp.persistent_store_database_settings')
    @mock.patch('tethys_apps.models.TethysApp.persistent_store_database_settings')
    @mock.patch('tethys_apps.models.TethysApp')
    def test_provision_persistent_stores_all_apps_database_single_match(self, mock_app, mock_setting1, mock_setting2,
                                                                        mock_setting3, mock_stdout):
        # Mock arguments
        mock_app_names = syncstores.ALL_APPS
        mock_options = {'database': '/foo/match', 'refresh': False, 'first_time': False}

        # Mock for ps db settings
        mock_setting1.name = 'setting1_name'
        mock_setting1.create_persistent_store_database.return_value = True
        mock_setting2.name = '/foo/match'
        mock_setting2.create_persistent_store_database.return_value = True
        mock_setting3.name = 'setting3_name'
        mock_setting3.create_persistent_store_database.return_value = True

        # Mock for TethysApp (2 apps, 2 settings for first app, 1 setting for second app)
        mock_app1 = mock.MagicMock()
        mock_app1.persistent_store_database_settings = [mock_setting1, mock_setting2]
        mock_app2 = mock.MagicMock()
        mock_app2.persistent_store_database_settings = [mock_setting3]
        mock_app.objects.all.return_value = [mock_app1, mock_app2]

        cmd = syncstores.Command()
        cmd.provision_persistent_stores(app_names=mock_app_names, options=mock_options)

        mock_app.objects.all.assert_called_once()
        mock_setting1.create_persistent_store_database.assert_not_called()
        mock_setting2.create_persistent_store_database.assert_called_once_with(refresh=False, force_first_time=False)
        mock_setting3.create_persistent_store_database.assert_not_called()
        self.assertIn('Provisioning Persistent Stores...', mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('tethys_apps.models.TethysApp')
    def test_provision_persistent_stores_given_apps_not_found(self, mock_app, mock_stdout):
        # Mock arguments
        mock_app_names = ['foo_missing']
        mock_options = {'database': '', 'refresh': True, 'first_time': True}

        # Mock for TethysApp (return no apps found)
        mock_app.objects.filter.return_value = []

        cmd = syncstores.Command()
        cmd.provision_persistent_stores(app_names=mock_app_names, options=mock_options)

        mock_app.objects.filter.assert_called_once()
        self.assertIn('The app named "foo_missing" cannot be found.', mock_stdout.getvalue())
        self.assertIn('Please make sure it is installed and try again.', mock_stdout.getvalue())
        self.assertIn('Provisioning Persistent Stores...', mock_stdout.getvalue())
