***********
Testing API
***********

**Last Updated:** November 18, 2016

Manually testing your app can be very time consuming, especially when modifying a simple line of code usually warrants retesting everything. To help automate and streamline the testing of your app, Tethys Platform provides you with a great starting point by providing the following:

1. A ``tests`` directory with a ``tests.py`` script within your app's default scaffold that contains well-commented sample testing code.
2. The Testing API which provides a helpful test class for setting up your app's testing environment.


Writing Tests
-------------
Tests should be written in a separate python script that is contained somewhere within your app's scaffold. By default, a ``tests`` directory already exists in the app-level directory and contains a ``tests.py`` script. Unless you have a good reason not to, it would be best to start writing your test code here.

As an example, if wanting to automate the testing of a the map controller in the "My First App" from the tutorials, the ``tests.py`` script might be modified to look like the following:

::

    from tethys_sdk.testing import TethysTestCase
    from ..app import MyFirstApp

    class MapControllerTestCase(TethysTestCase):
        def set_up(self):
            self.create_test_persistent_stores_for_app(MyFirstApp)
            self.create_test_user(username="joe", email="joe@some_site.com", password="secret")
            self.c = self.get_test_client()

        def tear_down(self):
            self.destroy_test_persistent_stores_for_app(MyFirstApp)

        def test_success_and_context(self):
            self.c.force_login(self.user)
            response = self.c.get('/apps/my-first-app/map/')

            # Check that the response returned successfully
            self.assertEqual(response.status_code, 200)

            # Check that the response returned the context variable
            self.assertIsNotNone(response.context['map_options'])

Tethys Platform leverages the native Django testing framework (which leverages the unittests Python module) to make writing tests for your app much simpler. While Tethys Platform encapsulates most of what is needed in its Testing API, it may still be necessary to refer to the Django and Python documentation for additional help while writing tests. Refer to their documentation here:

https://docs.djangoproject.com/en/1.9/topics/testing/overview/#writing-tests

https://docs.python.org/2.7/library/unittest.html#module-unittest

Running Tests
-------------
To run any tests at an app level:

1. Open a terminal
2. Enter the Tethys Platform python environment:
    ``$ . /usr/lib/tethys/bin/activate``
3. In settings.py make sure that the tethys_default database user is set to tethys_super:
::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'tethys_default',
            'USER': 'tethys_super',
            'PASSWORD': 'pass',
            'HOST': '127.0.0.1',
            'PORT': '5435'
        }
    }

4. Enter app-level ``tethys test`` command.
    ``(tethys)$ tethys test -f tethys_apps.tethysapp.<app_name(required)>.<folder_name>.<file_name>.<class_name>.<function_name> [-c/C]``
    Where ``-c`` tracks code coverage and prints out a report in the terminal, and ``-C`` does opens the report as an interactive HTML page in your browser

More specifically:

To run all tests across an app:
    Test command: ``(tethys)$ tethys test -f tethys_apps.tethysapp.<app_name>``
To run all tests within specific directory of an app:
    Test command: ``(tethys)$ tethys test -f tethys_apps.tethysapp.<app_name>.<folder_name>``

And so forth... Thus, you can hone in on the exact tests that you want to run.

  .. note::
    Remember to append either ``-c`` or ``-C`` if you would like a coverage report at the end of the testing printed in your terminal, or opened in your browser as an interactive HTML page, respectively.

API Documentation
-----------------
.. autoclass:: tethys_apps.base.testing.TethysTestCase
    :members: set_up, tear_down, create_test_user, create_test_superuser, get_test_client, create_test_persistent_stores_for_app, destroy_test_persistent_stores_for_app
