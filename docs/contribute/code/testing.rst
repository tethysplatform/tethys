.. _contribute_testing:

*******
Testing
*******

**Last Updated:** November 2025


.. _contribute_testing_setup_env:

The Tethys Platform test suite consists of unit tests for Python code. The tests are run automatically as part of the Continuous Integration (CI) process using GitHub Actions. This ensures that any new code changes do not introduce regressions or break existing functionality. When contributing to Tethys Platform, it is important to run the test suite locally to verify that your changes do not introduce any issues. This document provides guidance on setting up a testing environment, running the tests, interpreting the results, and writing new tests.

Setup Testing Environment
=========================

The following steps will guide you through setting up a testing environment for Tethys Platform:

1. Setup a development installation of Tethys Platform by following the :ref:`setup_dev_environment` tutorial.
2. Install the test, formatter, and lint, development dependencies by running the following command in the root of the Tethys Platform repository:

    .. code-block:: bash

        pip install -e .[test]

3. [optional] Set up your development environment to :ref:`setup_dev_environment_postgis`. If you do this, also configure Tethys Platform to use the ``tethys_super`` user for the database connection by editing the :file:`portal_config.yml`:

    .. code-block:: yaml

        settings:
          DATABASES:
            default:
                ENGINE: django.db.backends.postgresql
                NAME: tethys_platform
                USER: tethys_super
                PASSWORD: pass
                HOST: localhost
                PORT: <DB_PORT>

Your development environment should be ready for running the test suite.

.. _contribute_testing_running_tests:

Running Tests
=============

When you are developing, you will need to write tests and run them locally to verify that they work. To run the Python unit test suite, use the following command:

.. code-block:: bash

    pytest

The project is configured to automatically run test coverage analysis when the tests are run. The pytest configuration is defined in the ``[tool.pytest.ini_options]`` section of the :file:`pyproject.toml` file at the root of the repository.

To run tests for a specific file, it is necessary to disable the coverage analysis like so:

.. code-block:: bash

    pytest --no-cov path/to/test_file.py

.. _contribute_testing_test_results:

Test Results
------------

As the tests run, output will be displayed in the terminal. Each test file is listed and each dot or character after it represents the outcome of running one test. A "." indicates that the test passed, an "F" indicates that the test failed, and an "x" indicates that the test was expected to fail (xfail). At the end of the test run, a summary of the results will be displayed, including the number of tests that passed, failed, or were xfailed.

.. code-block:: bash

    ============================================================================================== test session starts ==============================================================================================
    platform darwin -- Python 3.10.19, pytest-9.0.1, pluggy-1.6.0
    django: version: 5.2.8, settings: tethys_portal.settings (from ini)
    rootdir: /Users/nswain/Codes/tethys
    configfile: pyproject.toml
    testpaths: tests/unit_tests/
    plugins: anyio-4.11.0, Faker-38.2.0, django-4.11.1, requests-mock-1.12.1, cov-7.0.0
    collected 2235 items                                                                                                                                                                                            

    tests/unit_tests/test_tethys_apps/test_admin.py 
    🚀 Starting global test setup...
    ✅ Global test setup completed!
    ....................................
    tests/unit_tests/test_tethys_apps/test_apps.py ...
    tests/unit_tests/test_tethys_apps/test_decorators.py ............................
    tests/unit_tests/test_tethys_apps/test_harvester.py .
    tests/unit_tests/test_tethys_apps/test_base/test_consumer.py ..xx
    .
    .
    .
    tests/unit_tests/test_tethys_quotas/test_admin.py .....F...
    tests/unit_tests/test_tethys_services/test_utilities.py ...............................
    tests/unit_tests/test_tethys_services/test_views.py ....
    tests/unit_tests/test_tethys_utils/test_deprecation.py .
    🧹 Starting global test teardown...
    Uninstalling Test App...
    Test App uninstalled successfully.
    Uninstalling Test Extension...
    Test Extension uninstalled successfully.
    ✅ Global test teardown completed!


    =================================================================================================== FAILURES ====================================================================================================
    ____________________________________________________________________________________ test_admin_user_quotas_inline_inactive _____________________________________________________________________________________

    admin_client = <django.test.client.Client object at 0x319712020>, admin_user = <User: admin>, load_quotas = None

        @pytest.mark.django_db
        def test_admin_user_quotas_inline_inactive(admin_client, admin_user, load_quotas):
            assert ResourceQuota.objects.count() == 2
            urq = ResourceQuota.objects.get(applies_to="django.contrib.auth.models.User")
            urq.active = False
            urq.save()
            response = admin_client.get(f"/admin/auth/user/{admin_user.id}/change/")
            assert response.status_code == 200
            assert b"User Quotas" in response.content
    >       assert UserQuota.objects.count() == 1
    E       assert 0 == 1
    E        +  where 0 = count()
    E        +    where count = <model_utils.managers.InheritanceManager object at 0x17634e3b0>.count
    E        +      where <model_utils.managers.InheritanceManager object at 0x17634e3b0> = UserQuota.objects

    tests/unit_tests/test_tethys_quotas/test_admin.py:79: AssertionError
    =============================================================================================== warnings summary ================================================================================================

    tests/unit_tests/test_tethys_apps/test_admin.py::TestTethysAppAdmin::test_TethysAppAdmin_manage_app_storage
    /Users/nswain/Codes/tethys/tests/unit_tests/test_tethys_apps/test_admin.py:340: RemovedInDjango60Warning:

    ================================================================================================ tests coverage =================================================================================================
    _______________________________________________________________________________ coverage: platform darwin, python 3.10.19-final-0 _______________________________________________________________________________

    Name                          Stmts   Miss  Cover   Missing
    -----------------------------------------------------------
    tethys_quotas/admin.py          110      6    95%   72, 115, 182-189
    tethys_quotas/decorators.py      34      1    97%   47
    tethys_quotas/utilities.py      140     12    91%   39-44, 69, 94, 97-100, 134, 180, 217, 228
    -----------------------------------------------------------
    TOTAL                         12922     19    99%

    206 files skipped due to complete coverage.
    ============================================================================================ short test summary info ============================================================================================
    FAILED tests/unit_tests/test_tethys_quotas/test_admin.py::test_admin_user_quotas_inline_inactive - assert 0 == 1
    ============================================================================ 1 failed, 2232 passed, 2 xfailed, 19 warnings in 51.52s ============================================================================

Failing Tests
+++++++++++++

If any tests fail, the output will indicate which tests failed and why. You should use this information to debug the issue and fix the tests or the bug in the code the test is revealing:

.. code-block:: bash

    .
    .
    .
    tests/unit_tests/test_tethys_quotas/test_admin.py .....F...
    .
    .
    .
    =================================================================================================== FAILURES ====================================================================================================
    ____________________________________________________________________________________ test_admin_user_quotas_inline_inactive _____________________________________________________________________________________

    admin_client = <django.test.client.Client object at 0x319712020>, admin_user = <User: admin>, load_quotas = None

        @pytest.mark.django_db
        def test_admin_user_quotas_inline_inactive(admin_client, admin_user, load_quotas):
            assert ResourceQuota.objects.count() == 2
            urq = ResourceQuota.objects.get(applies_to="django.contrib.auth.models.User")
            urq.active = False
            urq.save()
            response = admin_client.get(f"/admin/auth/user/{admin_user.id}/change/")
            assert response.status_code == 200
            assert b"User Quotas" in response.content
    >       assert UserQuota.objects.count() == 1
    E       assert 0 == 1
    E        +  where 0 = count()
    E        +    where count = <model_utils.managers.InheritanceManager object at 0x17634e3b0>.count
    E        +      where <model_utils.managers.InheritanceManager object at 0x17634e3b0> = UserQuota.objects

    tests/unit_tests/test_tethys_quotas/test_admin.py:79: AssertionError
    .
    .
    .
    ============================================================================================ short test summary info ============================================================================================
    FAILED tests/unit_tests/test_tethys_quotas/test_admin.py::test_admin_user_quotas_inline_inactive - assert 0 == 1
    ============================================================================ 1 failed, 2232 passed, 2 xfailed, 19 warnings in 51.52s ============================================================================

Warnings
++++++++

The warning summary section will list any deprecation warnings or other warnings that were raised during the test run. You should review these warnings and address them as necessary to ensure that the code is up to date and follows best practices.

.. code-block:: bash

    =============================================================================================== warnings summary ================================================================================================

    tests/unit_tests/test_tethys_apps/test_admin.py::TestTethysAppAdmin::test_TethysAppAdmin_manage_app_storage
    /Users/nswain/Codes/tethys/tests/unit_tests/test_tethys_apps/test_admin.py:340: RemovedInDjango60Warning:


.. _contribute_testing_coverage:

Code Coverage
-------------

Tethys Platform requires 100% test coverage for all new code. This means that every line of code is run at least once during the running of the tests suite. The project is configured to automatically run coverage analsis when you run the ``pytest`` command. The test output includes a coverage report near the end. The coverage report indicated which files and which lines in the files are missing coverage. Write additional tests as necessary to increase the coverage to 100%. Here is an example of the coverage report:

.. code-block:: bash

    ================================================================================================ tests coverage =================================================================================================
    _______________________________________________________________________________ coverage: platform darwin, python 3.10.19-final-0 _______________________________________________________________________________

    Name                          Stmts   Miss  Cover   Missing
    -----------------------------------------------------------
    tethys_quotas/admin.py          110      6    95%   72, 115, 182-189
    tethys_quotas/decorators.py      34      1    97%   47
    tethys_quotas/utilities.py      140     12    91%   39-44, 69, 94, 97-100, 134, 180, 217, 228
    -----------------------------------------------------------
    TOTAL                         12922     19    99%

    206 files skipped due to complete coverage.

.. _contribute_testing_linting:

Code Style
==========

The Python code in Tethys Platform is developed following the `PEP8 style guide <https://peps.python.org/pep-0008/>`_. The code is linted using flake8 and formatted using the Black code formatter.

Install the codes style dependencies by running the following command in the root of the Tethys Platform repository:

.. code-block:: bash

    pip install -e .[lint]

flake8
------

Tethys Platform uses the flake8 linter to check for conformance to the PEP8 style guide and other Python codestyle best practices. To run the linter, run the following command in the root of the Tethys Platform repository:

.. code-block:: bash

    flake8

This is an example of the output you might see when running flake8:

.. code-block:: bash

    ./tests/unit_tests/test_tethys_layouts/test_mixins/test_map_layout.py:1373:17: B041 Repeated key-value pair in dictionary literal.
    ./tethys_apps/models.py:1263:2: E999 TabError: inconsistent use of tabs and spaces in indentation

**If no output is displayed, the check passed and there are no issues.** No news is good news. If any issues are found, they will be listed in the output. Most are self explanatory, but a quick web search referencing the issue code will usually provide more information on the issue and how to resolve it. For more information on flake8, see the `flake8 documentation <https://flake8.pycqa.org/en/latest/>`_.

Black
-----

Within the PEP8 style guide, there is a lot of room for interpretation for how code can be formatted. This can lead to inconsistencies in code style across a large codebase. To help maintain a consistent code style, Tethys Platform uses the Black code formatter. Using a formatter like Black can help reduce the time spent on code reviews by minimizing the diffs and preventing tiffs over how a block of code should be styled.

You will most frequently encounter the need to run the Black formatter after the Black check fails on a Pull Request you have opened. Fixing the failure is simple: run Black on the codebase, then commit and push the changes. To format the code using Black, run the following command in the root of the Tethys Platform repository:

.. code-block:: bash

    black .

This is an example of the output you might see when running Black:

.. code-block:: bash

    All done! ✨ 🍰 ✨
    483 files left unchanged.

To learn more about the Black code formatter, see the `Black documentation <https://black.readthedocs.io/en/stable/>`_.

.. _contribute_testing_writing_tests:

Writing Tests
=============

Whether you are adding a new feature or fixing a bug, you should write tests to verify that the code works as expected. This may involve updating existing tests or writing new ones. The following sections provide guidance on writing tests for Python and JavaScript code.

Python Unit Tests
-----------------

The Python tests were originally written using the `unittest <https://docs.python.org/3/library/unittest.html>`_ framework. However, the project is transisitioning to using `pytest <https://docs.pytest.org/en/stable/>`_ as the primary testing framework. New tests should be written using pytest, and existing tests should be converted to pytest over time. The following sections provide guidance on writing Python unit tests using pytest.

Unittest to Pytest Conversion Script
++++++++++++++++++++++++++++++++++++++

An experimental script has been written to help convert existing unittest files to pytest. It is not perfect and does not cover all cases, but it can help speed up the conversion process. The script is located at :file:`scripts/convert_unittest_to_pytest.py`. To use the script, run the following command in the root of the Tethys Platform repository:

.. code-block:: bash

    python scripts/convert_unittest_to_pytest.py path/to/unittest_file.py


Organization
++++++++++++

The Python tests are located in the :file:`tests` directory at the root of the repository. The tests are organized into subdirectories based on the module they are testing. For example, tests for the ``tethys_apps.harvester`` module are located in the :file:`tests/unit_tests/test_tethys_apps/test_harvester.py` file. This pattern is used to make finding tests easier and should be followed when adding new test files. All functions that are intended to be run as tests should be prefixed with ``test_``. Test classes should also be prefixed with ``Test``. This is necessary for pytest to automatically discover and run the tests.

.. warning::

    Take care when naming non-test functions and classes to avoid using the ``test_`` and ``Test`` prefixes, as this will cause pytest to attempt to run them as tests, which may lead to unexpected errors.

.. _contribute_testing_mocking:

Mocking
+++++++

As unit tests, the Python tests should be focused on testing the smallest units of code possible. This means that you should often mock any external service dependencies that are not the focus of the test such as GeoServer or HTCondor. When the tests are run during the GitHub action checks, these services won't be available. The exception to this is the primary Tethys Platform database, which may be used in tests and will be available for checks (see below).

The `unittest.mock <https://docs.python.org/3/library/unittest.mock.html>`_ module is used to create mock objects in place of services or third-party library objects. The mock objects can be used to simulate the behavior of the real objects and control the return values of methods. For example, to mock the ``requests.get`` function, you could use the following code:

.. code-block:: python

    from unittest.mock import patch

    @patch('some_module.that_uses.requests.get')
    def test_my_function(mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'key': 'value'}

        result = my_function()

        assert result == 'value'

You must provide an argument to the function to receive the mock object, in this case ``mock_get``. If you use multiple ``@patch`` decorators, the mock objects will be passed to the test function in the reverse order that the decorators are applied:

.. code-block:: python

    @patch('module.ClassA')
    @patch('module.ClassB')
    def test_something(mock_class_b, mock_class_a):
        ...


There are many tutorials and guides available online that can help you learn how to use the ``unittest.mock`` module effectively, so it won't be covered in detail here. There are also many examples in the 2000+ existing tests in the Tethys Platform codebase that you can use as a reference.

.. tip::

    When using a combination of the ``mock.patch`` decorators and ``pytest`` fixtures, be sure that the fixtures are listed after the mock decorator parameters:. For example the ``test_app`` fixture is listed after the ``mock_input`` mocked parameter in the following example:

    .. code-block:: python

        @mock.patch("tethys_cli.cli_helpers.input")
        def test_prompt_yes_or_no__invalid_first(mock_input, test_app):
            question = "How are you?"
            mock_input.side_effect = ["invalid", "y"]
            test_val = cli_helper.prompt_yes_or_no(question, default="n")
            assert test_val
            assert mock_input.call_count == 2


Django Testing Tools
++++++++++++++++++++

There are a number of tools provided by Django to help with testing Django applications. The older, unittest-style tests in Tethys Platform sometimes make use of the Django ``TestCase`` class, which provides a number of useful methods for testing Django applications (see: `Django testing documentation <https://docs.djangoproject.com/en/5.2/topics/testing/advanced/>`). However, when writing new tests or converting old tests to pytest you should use the ``pytest_django`` fixtures and markers (see: `pytest-django documentation <https://pytest-django.readthedocs.io/en/latest/>`_).

Database
++++++++

Some tests need to interact with the database to verify that the code is working as expected. Most often this is the case when the code makes uses of one of the many Django ORM models (e.g. tethys_apps.models). Tests that interact with the database must be explicity marked with the ``pytest.mark.django_db`` decorators (both old unittest style and new pytest style tests):

.. code-block:: python

    import pytest

    @pytest.mark.django_db
    def test_admin_resource_quotas_change(admin_client, load_quotas):
        assert ResourceQuota.objects.count() == 2
        user_quota = ResourceQuota.objects.get(applies_to="django.contrib.auth.models.User")
        response = admin_client.get(
            f"/admin/tethys_quotas/resourcequota/{user_quota.id}/change/"
        )
        assert response.status_code == 200



The older, unittest-style tests that need to interact with the database often use the ``TethysTestCase``, which inherits from the Django ``TestCase`` class. This class is able to use the test database that is created for tests. It also provides special setup and tear down functionality that ensures that the tests are isolated from each other and that the database is in a known state when the test starts. These should be migrated to use ``pytest_django`` fixtures and markers over time.

Custom Fixtures
+++++++++++++++

Tethys Platform provides a number of custom pytest fixtures to help with testing. These fixtures are located in the :file:`conftest.py` files throughout the test suite. Some of the most commonly used fixtures include:

- ``test_app``: required when you want to test functionality that depends on a Tethys App being installed. The fixture installs the test app located at :file:`tests/apps/tethysapp-test_app` before the test runs. It returns the ``TethysApp`` instance for the test app.
- ``reload_urls``: returns a function that can be called to reload the Django URL configuration after some test setup such as changing the ``PREFIX_URL`` setting.
- ``test_dir``: returns the ``Path`` to the :file:`tests` directory. This can be useful when you need to get the path to a test file or resource.
- ``load_quotas``: initializes the ``tethys_quotas`` module and loads the test quotas defined in the test app. Tests with this fixture also have the ``test_app`` fixture applied automatically.

.. important::

    Fixtures can only be used in pytest-style tests. They cannot be used in unittest-style tests.


JavaScript Unit Tests
---------------------

Coming Soon
