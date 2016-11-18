from django.test import TestCase
from django.conf import settings
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from app_base import TethysAppBase
from django.contrib.auth.models import User
from django.test import Client
from tethys_apps.utilities import sync_tethys_app_db, register_app_permissions


class TethysTestCase(TestCase):

    def setUp(self):
        # Resets the apps database and app permissions
        sync_tethys_app_db()
        register_app_permissions()
        child_setUp = getattr(self, 'set_up', None)
        if child_setUp:
            if callable(child_setUp):
                self.set_up()

    def tearDown(self):
        child_tearDown = getattr(self, 'tear_down', None)
        if child_tearDown:
            if callable(child_tearDown):
                self.tear_down()

    @staticmethod
    def create_test_persistent_stores_for_app(app_class):
        """
        Creates temporary persistent store databases for this app to be used in testing.

        Args:
          app_class: The app class from the app's app.py module
        """
        if not issubclass(app_class, TethysAppBase):
            raise TypeError('The app_class argument was not of the correct type. '
                            'It must be a class that inherits from <TethysAppBase>.')

        for store in app_class().persistent_stores():
            test_store_name = 'test_{0}'.format(store.name)
            if app_class.persistent_store_exists(test_store_name):
                TethysTestCase.destroy_test_persistent_stores_for_app(app_class, suppress_messages=True)
            # print "Creating test database for alias '{0}'".format(test_store_name)
            create_store_success = app_class.create_persistent_store(test_store_name, spatial=store.spatial)
            if create_store_success:
                while True:
                    try:
                        store.initializer_function(True)
                        break
                    except OperationalError as e:
                        if 'terminating connection due to administrator command' in str(e):
                            pass
                        else:
                            raise e
            else:
                raise SystemError('The test store was not able to be created')

    @staticmethod
    def destroy_test_persistent_stores_for_app(app_class, suppress_messages=False):
        """
            Destroys the temporary persistent store databases for this app that were used in testing.

            Args:
              app_class(TethysAppBase): The app class from the app's app.py module
              suppress_messages(bool): Indicate whether stdout should be supressed

        """
        for store in app_class.list_persistent_stores():
            if store.startswith('test_'):

                super_db = settings.TETHYS_DATABASES['tethys_super']

                super_db_url = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
                    super_db['USER'] if 'USER' in super_db else 'tethys_super',
                    super_db['PASSWORD'] if 'PASSWORD' in super_db else 'pass',
                    super_db['HOST'] if 'HOST' in super_db else '127.0.0.1',
                    super_db['PORT'] if 'PORT' in super_db else '5435',
                    super_db['NAME'] if 'NAME' in super_db else 'tethys_super'
                )

                # Compose db name
                full_db_name = '_'.join((app_class.package, store))

                # Create db engine
                engine = create_engine(super_db_url)

                # Create db
                drop_db_statement = 'DROP DATABASE IF EXISTS {0}'.format(full_db_name)

                if not suppress_messages:
                    # print "Destroying test database for alias '{0}'...".format(store)
                    pass

                try:
                    drop_connection = engine.connect()
                    drop_connection.execute('commit')
                    drop_connection.execute(drop_db_statement)
                except OperationalError as e:
                    if 'being accessed by other users' in str(e):

                        # Force disconnect all other connections to the database
                        disconnect_sessions_statement = '''
                                                        SELECT pg_terminate_backend(pg_stat_activity.pid)
                                                        FROM pg_stat_activity
                                                        WHERE pg_stat_activity.datname = '{0}'
                                                        AND pg_stat_activity.pid <> pg_backend_pid();
                                                        '''.format(full_db_name)
                        drop_connection.execute(disconnect_sessions_statement)

                        # Try again to drop the databse
                        drop_connection.execute('commit')
                        drop_connection.execute(drop_db_statement)
                        drop_connection.close()
                    else:
                        raise e
                finally:
                    drop_connection.close()

    @staticmethod
    def create_test_user(username, password, email=None):
        return User.objects.create_user(username=username, password=password, email=email)

    @staticmethod
    def get_test_client():
        return Client()
