import logging

from django.test import Client
from django.test import TestCase

from tethys_apps.base.app_base import TethysAppBase
from tethys_apps.base.testing.environment import is_testing_environment, get_test_db_name


class TethysTestCase(TestCase):
    """
    This class inherits from the Django TestCase class and is itself the class that is should be inherited from when
    creating test case classes within your app. Note that every specific test written within your custom class
    inheriting from this class must begin with the word "test" or it will not be executed during testing.
    """
    def setUp(self):
        # Resets the apps database and app permissions (workaround since Django's testing framework refreshes the
        # core db after each individual test)
        from tethys_apps.harvester import SingletonHarvester
        harvester = SingletonHarvester()
        harvester.harvest()
        logging.disable(logging.CRITICAL)
        self.set_up()

    def tearDown(self):
        self.tear_down()
        logging.disable(logging.NOTSET)

    def set_up(self):
        """
        This method is to be overridden by the custom test case classes that inherit from the TethysTestCase class and
        is used to perform any set up that is applicable to every test function that is defined within the custom test
        class

        Return:
            None
        """
        pass

    def tear_down(self):
        """
        This method is to be overridden by the custom test case classes that inherit from the TethysTestCase class and
        is used to perform any tear down that is applicable to every test function that is defined within the custom
        test class. It is often used in conjunction with the "set_up" function to tear down what was setup therein.

        Return:
            None
        """
        pass

    @staticmethod
    def create_test_persistent_stores_for_app(app_class):
        """
        Creates temporary persistent store databases for this app to be used in testing.

        Args:
            app_class: The app class from the app's app.py module
        Return:
            None
        """
        from tethys_apps.models import TethysApp

        if not is_testing_environment():
            raise EnvironmentError('This function will only execute properly if executed in the testing environment.')

        if not issubclass(app_class, TethysAppBase):
            raise TypeError('The app_class argument was not of the correct type. '
                            'It must be a class that inherits from <TethysAppBase>.')

        db_app = TethysApp.objects.get(package=app_class.package)

        ps_database_settings = db_app.persistent_store_database_settings
        for db_setting in ps_database_settings:
            create_store_success = app_class.create_persistent_store(db_name=db_setting.name,
                                                                     connection_name=None,
                                                                     spatial=db_setting.spatial,
                                                                     initializer=db_setting.initializer,
                                                                     refresh=True,
                                                                     force_first_time=True)

            if not create_store_success:
                raise SystemError('The test store was not able to be created')

    @staticmethod
    def destroy_test_persistent_stores_for_app(app_class):
        """
        Destroys the temporary persistent store databases for this app that were used in testing.

        Args:
            app_class: The app class from the app's app.py module
        Return:
            None
        """
        if not is_testing_environment():
            raise EnvironmentError('This function will only execute properly if executed in the testing environment.')

        if not issubclass(app_class, TethysAppBase):
            raise TypeError('The app_class argument was not of the correct type. '
                            'It must be a class that inherits from <TethysAppBase>.')

        for db_name in app_class.list_persistent_store_databases(static_only=True):
            test_db_name = get_test_db_name(db_name)
            app_class.drop_persistent_store(test_db_name)

    @staticmethod
    def create_test_user(username, password, email=None):
        """
        Creates and returns temporary user to be used in testing

        Args:
            username(string): The username for the temporary test user
            password(string): The password for the temporary test user
            email(string): The email address for the temporary test user
        Return:
            User object
        """
        from django.contrib.auth.models import User
        return User.objects.create_user(username=username, password=password, email=email)

    @staticmethod
    def create_test_superuser(username, password, email=None):
        """
        Creates and returns a temporary superuser to be used in testing

        Args:
            username(string): The username for the temporary test user
            password(string): The password for the temporary test user
            email(string): The email address for the temporary test user
        Return:
            User object
        """
        from django.contrib.auth.models import User
        return User.objects.create_superuser(username=username, password=password, email=email)

    @staticmethod
    def get_test_client():
        """
        Returns a Client object to be used to mimic a browser in testing

        Return:
            Client object
        """
        return Client()
