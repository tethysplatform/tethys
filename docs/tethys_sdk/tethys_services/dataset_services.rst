********************
Dataset Services API
********************

**Last Updated**: May 2017

.. important::

    This feature requires the ``tethys_dataset_services`` library to be installed. Starting with Tethys 5.0 or if you are using ``micro-tethys-platform``, you will need to install ```tethys_dataset_services`` using conda or pip as follows:

    .. code-block:: bash

        # conda: conda-forge channel strongly recommended
        conda install -c conda-forge tethys_dataset_services

        # pip
        pip install tethys_dataset_services

:term:`Dataset services` are web services external to Tethys Platform that can be used to store and publish file-based :term:`datasets` (e.g.: text files, Excel files, zip archives, other model files). Tethys app developers can use the Dataset Services API to access :term:`datasets` for use in their apps and publish any resulting :term:`datasets` their apps may produce. Supported options include `CKAN <https://ckan.org/>`_ and `HydroShare <https://hydroshare.org/>`_.

Key Concepts
============

Tethys Dataset Services API provides a standardized interface for interacting with :term:`dataset services`. This means that you can use datasets from different sources without completely overhauling your code. Each of the supported :term:`dataset services` provides a ``DatasetEngine`` object with the same methods. For example, all ``DatasetEngine`` objects have a method called ``list_datasets()`` that will have the same result, returning a list of the datasets that are available.

There are two important definitions that are applicable to :term:`dataset services`: :term:`dataset` and :term:`resource`. A :term:`resource` contains a single file or other object and the metadata associated with it. A :term:`dataset` is a container for one or more resources.

Dataset Service Engine References
=================================

All ``DatasetEngine`` objects implement a minimum set of base methods. However, some ``DatasetEngine`` objects may include additional methods that are unique to that ``DatasetEngine`` and the arguments that each method accepts may vary slightly. Refer to the following references for the methods that are offered by each ``DatasetEngine``.

.. toctree::
    :maxdepth: 1

    dataset_service/base_reference
    dataset_service/ckan_reference
    dataset_service/hydroshare_reference

Dataset Service Settings
========================

Using dataset services in your app is accomplished by adding the ``dataset_service_settings()`` method to your :term:`app class`, which is located in your :term:`app configuration file` (:file:`app.py`). This method should return a list or tuple of ``DatasetServiceSetting``. For example:

::

    from tethys_sdk.app_settings import DatasetServiceSetting

    class App(TethysAppBase):
        """
        Tethys App Class for My First App.
        """
        ...
        def dataset_service_settings(self):
            """
            Example dataset_service_settings method.
            """
            ds_settings = (
                DatasetServiceSetting(
                    name='primary_ckan',
                    description='Primary CKAN service for app to use.',
                    engine=DatasetServiceSetting.CKAN,
                    required=True,
                ),
                DatasetServiceSetting(
                    name='hydroshare',
                    description='HydroShare service for app to use.',
                    engine=DatasetServiceSetting.HYDROSHARE,
                    required=False
                )
            )

            return ds_settings

.. caution::

    The ellipsis in the code block above indicates code that is not shown for brevity. **DO NOT COPY VERBATIM**.

Assign Dataset Service
======================

The ``DatasetServiceSetting`` can be thought of as a socket for a connection to a ``DatasetService``. Before we can do anything with the ``DatasetServiceSetting`` we need to "plug in" or assign a ``DatasetService`` to the setting. The ``DatasetService`` contains the connection information and can be used by multiple apps. Assigning a ``DatasetService`` is done through the Admin Interface of Tethys Portal as follows:

1. Create ``DatasetService`` if one does not already exist

    a. Access the Admin interface of Tethys Portal by clicking on the drop down menu next to your user name and selecting the "Site Admin" option.

    b. Scroll to the **Tethys Service** section of the Admin Interface and select the link titled **Dataset Services**.

    c. Click on the **Add Dataset Service** button.

    d. Fill in the connection information to the database server.

    e. Press the **Save** button to save the new ``DatasetService``.

    .. tip::

        You do not need to create a new ``DatasetService`` for each ``DatasetServiceSetting`` or each app. Apps and ``DatasetServiceSettings`` can share ``DatasetServices``.

2. Navigate to App Settings Page

    a. Return to the Home page of the Admin Interface using the **Home** link in the breadcrumbs or as you did in step 1a.

    b. Scroll to the **Tethys Apps** section of the Admin Interface and select the **Installed Apps** linke.

    c. Select the link for your app from the list of installed apps.



3. Assign ``DatasetService`` to the appropriate ``DatasetServiceSetting``

    a. Scroll to the **Dataset Service Settings** section and locate the ``DatasetServiceSetting``.

    .. note::

        If you don't see the ``DatasetServiceSetting`` in the list, uninstall the app and reinstall it again.

    b. Assign the appropriate ``DatasetService`` to your ``DatasetServiceSetting`` using the drop down menu in the **Dataset Service** column.

    c. Press the **Save** button at the bottom of the page to save your changes.

.. note::

    During development you will assign the ``DatasetService`` setting yourself. However, when the app is installed in production, this steps is performed by the portal administrator upon installing your app, which may or may not be yourself.

Working with Dataset Services
=============================

After dataset services have been properly configured, you can use the services to store and retrieve data for your apps. The process involves the following steps:

1. Get a Dataset Service Engine
-------------------------------

Call the ``get_dataset_service()`` method of the app class to get a ``DatasetEngine``:

.. code-block:: python

    from .app import App

    ckan_engine = App.get_dataset_service('primary_ckan', as_engine=True)

You can also create a ``DatasetEngine`` object directly. This can be useful if you want to vary the credentials for dataset access frequently (e.g.: using user specific credentials):

.. code-block:: python

  from tethys_dataset_services.engines import CkanDatasetEngine

  dataset_engine = CkanDatasetEngine(endpoint='http://www.example.com/api/3/action', apikey='a-R3llY-n1Ce-@Pi-keY')

.. caution::

  Take care not to store API keys, usernames, or passwords in the source files of your app--especially if the source is made public. This could compromise the security of the dataset service.


2. Use the Dataset Service Engine
---------------------------------

After you have a ``DatasetEngine``, simply call the desired method on it. All ``DatasetEngine`` methods return a dictionary with an item named ``'success'`` that contains a boolean. If the operation was successful, the value of ``'success'`` will be ``True``, otherwise it will be ``False``. If the value of ``'success'`` is ``True``, the dictionary will also contain an item named ``'result'`` that will contain the results. If it is ``False``, the dictionary will contain an item named ``'error'`` that will contain information about the error that occurred. This can be used for debugging purposes as illustrated in the following example:

.. code-block:: python

    from .app import MyFirstApp as App

    dataset_engine = App.get_dataset_service('primary_ckan', as_engine=True)

    result = dataset_engine.list_datasets()

    if result['success']:
        dataset_list = result['result']

        for dataset in dataset_list:
            print(dataset)
    else:
        print(result['error'])

Use the dataset service engines references above for descriptions of the methods available and examples.


.. note::

    The HydroShare dataset engine uses OAuth 2.0 to authenticate and authorize interactions with the HydroShare via the REST API. This requires passing the ``request`` object as one of the arguments in ``get_dataset_engine()`` method call. Also, to ensure the user is connected to HydroShare, app developers must use the ``ensure_oauth2()`` decorator on any controllers that use the HydroShare dataset engine. For example:

    .. code-block:: python

        from tethys_sdk.services import get_dataset_engine, ensure_oauth2
        from .app import App

        @ensure_oauth2('hydroshare')
        def my_controller(request):
            """
            This is an example controller that uses the HydroShare API.
            """
            engine = App.get_dataset_service('hydroshare', request=request)

            response = engine.list_datasets()

            context = {}

            return App.render(request, 'home.html', context)

