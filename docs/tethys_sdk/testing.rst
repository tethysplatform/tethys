***********
Testing API
***********

**Last Updated:** December 2022

Manually testing your app can be very time consuming, especially when modifying a simple line of code usually warrants retesting everything. To help automate and streamline the testing of your app, Tethys Platform provides you with a great starting point by providing the following:

1. A ``tests`` directory with a ``tests.py`` script within your app's default scaffold that contains well-commented sample testing code.
2. The Testing API which provides a helpful test class for setting up your app's testing environment.


Writing Tests
-------------
Tests should be written in a separate python script that is contained somewhere within your app's scaffold. By default, a ``tests`` directory already exists in the app-level directory and contains a ``tests.py`` script. Unless you have a good reason not to, it would be best to start writing your test code here.

As an example, if wanting to automate the testing of a the map controller in the "My First App" from the tutorials, the ``tests.py`` script might be modified to look like the following:

.. code-block:: python

    from tethys_sdk.testing import TethysTestCase
    from ..app import MyFirstApp

    class MapControllerTestCase(TethysTestCase):
        def set_up(self):
            self.create_test_persistent_stores_for_app(MyFirstApp)
            self.create_test_user(username="joe", email="joe@some_site.com", password="secret")
            self.client = self.get_test_client()

        def tear_down(self):
            self.destroy_test_persistent_stores_for_app(MyFirstApp)

        def test_success_and_context(self):
            self.client.force_login(self.user)
            response = self.client.get('/apps/my-first-app/map/')

            # Check that the response returned successfully
            self.assertEqual(response.status_code, 200)

            # Check that the response returned the context variable
            self.assertIsNotNone(response.context['map_options'])

Tethys Platform leverages the native Django testing framework (which leverages the unittests Python module) to make writing tests for your app much simpler. While Tethys Platform encapsulates most of what is needed in its Testing API, it may still be necessary to refer to the Django and Python documentation for additional help while writing tests. Refer to their documentation here:

https://docs.djangoproject.com/en/5.1/topics/testing/

https://docs.python.org/2.7/library/unittest.html#module-unittest

Testing Controllers that Use OAuth2 Authentication
++++++++++++++++++++++++++++++++++++++++++++++++++

.. important::

   This feature requires the ``social-auth-app-django`` library to be installed. Starting with Tethys 5.0 or if you are using ``micro-tethys-platform``, you will need to install ``social-auth-app-django`` using conda or pip as follows:

   .. code-block:: bash

      # conda: conda-forge channel strongly recommended
      conda install -c conda-forge social-auth-app-django

      # pip
      pip install social-auth-app-django

Using the ``force_login`` method above works great for testing controllers where login is required. However, additional steps are required to test controllers that must be authenticated with a specific OAuth2 provider (i.e. specify the ``ensure_oauth_provider`` argument to the ``controller`` decorator). For example, if you have a controller like this:

.. code-block:: python

    @controller(
      ensure_oauth2_provider="google-oauth2"
    )
    def home(request):
      ...

Then your test will need to define the ``UserSocialAuth`` database object to register the test user with the oauth provider. This can be done in the ``setUpClass`` method of your test class:

.. code-block:: python

    from unittest import mock
    from social_django.models import UserSocialAuth
    from tethys_sdk.testing import TethysTestCase


    class MapControllerTestCase(TethysTestCase):

        @classmethod
        def setUpClass(cls):
            super().setUpClass()
            cls.client = cls.get_test_client()
            cls.user = cls.create_test_user(username="joe", password="secret", email="joe@some_site.com")
            UserSocialAuth(user=cls.user, provider="google-oauth2").save()


Once the ``UserSocialAuth`` object is defined you can then use the ``force_login`` method as before:

.. code-block:: python

        def test_success_and_context(self):
            self.client.force_login(self.user)
            response = self.client.get('/apps/my-first-app/map/')

            # Check that the response returned successfully
            self.assertEqual(response.status_code, 200)

            # Check that the response returned the context variable
            self.assertIsNotNone(response.context['map_options'])

Running Tests
-------------
To run tests for an app:

1. :ref:`activate_environment`

2. In portal_config.yml make sure that the default database user is set to ``tethys_super`` or is a super user of the database:

  .. code-block:: yaml

      DATABASES:
          default:
              ENGINE: django.db.backends.postgresql_psycopg2
              NAME: tethys_platform
              USER: tethys_super
              PASSWORD: pass
              HOST: 127.0.0.1
              PORT: 5435

3. From the root directory of your app, run the ``tethys manage test`` command:

  .. code-block:: shell

      tethys manage test tethysapp/<app_name>/tests

  This will run all tests defined in the ``tests`` directory of your app. If you would like to run just a subset of tests then you can specify which tests to run with the following:

  To run all tests in a specific module within the ``tests`` directory:

  .. code-block:: shell

      tethys manage test tethysapp/<app_name>/tests/<module_name>

      # or

      tethys manage test tethysapp.<app_name>.tests.<module_name>

  To run all tests within specific class of a test module:

  .. code-block:: shell

    tethys manage test tethysapp.<app_name>.tests.<module_name>.<class_name>

  And to run a single test method within a test class:

  .. code-block:: shell

      tethys manage test tethysapp.<app_name>.tests.<module_name>.<class_name>.<method_name>

  For example, to run just the ``test_success_and_context`` test method defined above you would use the following command:

  .. code-block:: shell

      tethys manage tests tethysapp.my_first_app.tests.tests.MapControllerTestCase.test_success_and_context


.. important::

  When specifying the tests to run using a system path (e.g. ``tethysapp/<app_name>/tests/``) you must provide either an absolute path or the path relative to your current working directory.
  When specifying the tests to run using a Python module (e.g. ``tethysapp.<app_name>.tests.<module_name>``) then your current working directory is irrelevant, but note that this format will only work for modules under the ``tests`` directory. You cannot specify the whole ``tests`` directory as a Python module.

API Documentation
-----------------
.. autoclass:: tethys_apps.base.testing.testing.TethysTestCase
    :members: set_up, tear_down, create_test_user, create_test_superuser, get_test_client, create_test_persistent_stores_for_app, destroy_test_persistent_stores_for_app
