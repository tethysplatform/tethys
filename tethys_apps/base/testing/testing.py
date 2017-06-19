from django.test import TestCase
from django.test import Client
from environment import set_testing_environment
from ..app_base import TethysAppBase


class TethysTestCase(TestCase):
    """
    This class inherits from the Django TestCase class and is itself the class that is should be inherited from when
    creating test case classes within your app. Note that every specific test written within your custom class
    inheriting from this class must begin with the word "test" or it will not be executed during testing.
    """
    def setUp(self):
        # Resets the apps database and app permissions (workaround since Django's testing framework refreshes the
        # core db after each individual test)
        from tethys_apps.utilities import sync_tethys_app_db, register_app_permissions
        sync_tethys_app_db()
        register_app_permissions()
        self.set_up()

    def tearDown(self):
        self.tear_down()

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
        set_testing_environment(True)

        if not issubclass(app_class, TethysAppBase):
            raise TypeError('The app_class argument was not of the correct type. '
                            'It must be a class that inherits from <TethysAppBase>.')

        for store in app_class().persistent_stores():
            if app_class.persistent_store_exists(store.name):
                app_class.destroy_persistent_store(store.name)

            create_store_success = app_class.create_persistent_store(store.name, spatial=store.spatial)

            error = False
            if create_store_success:
                retry_counter = 0
                while True:
                    if retry_counter < 5:
                        try:
                            store.initializer_function(True)
                            break
                        except Exception as e:
                            if 'terminating connection due to administrator command' in str(e):
                                pass
                            else:
                                error = True
                    else:
                        error = True
                        break
            else:
                error = True

            if error:
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
        set_testing_environment(True)

        if not issubclass(app_class, TethysAppBase):
            raise TypeError('The app_class argument was not of the correct type. '
                            'It must be a class that inherits from <TethysAppBase>.')

        for store in app_class().persistent_stores():
            app_class.destroy_persistent_store(store.name)

        # Handle destroying any additional stores created manually during testing
        for store in app_class().list_persistent_stores():
            app_class.destroy_persistent_store(store)

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
