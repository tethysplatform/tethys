********************
Dataset Services API
********************

**Last Updated**: August 5, 2015

.. warning::

   UNDER CONSTRUCTION

:term:`Dataset services` are web services external to Tethys Platform that can be used to store and publish file-based
:term:`datasets` (e.g.: text files, Excel files, zip archives, other model files). Tethys app developers can use the
Dataset Services API to access :term:`datasets` for use in their apps and publish any resulting :term:`datasets` their
apps may produce. `CKAN <http://ckan.org>`_ is currently they only supported dataset service.

Key Concepts
============

Tethys Dataset Services API provides a standardized interface for interacting with :term:`dataset services`. This
means that you can use datasets from different sources without completely overhauling your code. Each of the supported
:term:`dataset services` provides a ``DatasetEngine`` object with the same methods. For example, all ``DatasetEngine``
objects have a method called ``list_datasets()`` that will have the same result, returning a list of the datasets that are
available.

There are two important definitions that are applicable to :term:`dataset services`: :term:`dataset` and :term:`resource`.
A :term:`resource` contains a single file or other object and the metadata associated with it. A :term:`dataset` is a container for
one or more resources.

Dataset Service Engine References
=================================

All ``DatasetEngine`` objects implement a minimum set of base methods. However, some ``DatasetEngine`` objects may include additional methods that are unique to that ``DatasetEngine`` and the arguments that each method accepts may vary slightly. Refer to the following references for the methods that are offered by each ``DatasetEngine``.

.. toctree::
    :maxdepth: 1

    dataset_service/base_reference
    dataset_service/ckan_reference
    dataset_service/hydroshare_reference

Register New Dataset Service
============================

Registering new dataset services is performed through the System Admin Settings.

1. Login to your Tethys Platform instance as an administrator.
2. Select "Site Admin" from the user drop down menu.

  .. figure:: ../../images/site_admin/select_site_admin.png
      :width: 600px
      :align: center


3. Select "Dataset Services" from the "Tethys Services" section.

  .. figure:: ../../images/site_admin/home.png
      :width: 600px
      :align: center


4. Select an existing Dataset Service configuration from the list to edit it OR click on the "Add Dataset Service" button to create a new one.

  .. figure:: ../../images/site_admin/dataset_services.png
      :width: 600px
      :align: center

5. Give the Dataset Service configuration a name, select an appropriate engine, and specify the endpoint. The name must be unique, because it is used to retrieve the Dataset Service connection object. The endpoint is a URL pointing to the Dataset Service API. Example endpoints for several different types of Dataset Services are shown below:

  ::

    # CKAN Endpoint URL
    http://www.example.com/api/3/action

  If authentication is required, specify either the API key or the username and password.

  .. note::

      When linking Tethys to a CKAN dataset service, an API Key is required. All user accounts are issued an API key. To access the API Key log into the CKAN on which you have an account and browse to your user profile page. The API key will be listed there. Depending on the CKAN instance and the dataset, you may have full read-write access or you may have read-only access.

  When you are done, the form should look similar to this:

  .. figure:: ../../images/site_admin/dataset_service_edit.png
      :width: 600px
      :align: center

6. Press "Save" to save the Dataset Service configuration.

.. note::

  Prior to version Tethys Platform 1.1.0, it was possible to register dataset services using a mechanism in the :term:`app configuration file`. This mechanism has been deprecated due to security concerns.

Working with Dataset Services
=============================

After dataset services have been properly configured, you can use the services to store and retrieve data for your apps. The process involves the following steps:

1. Get a Dataset Service Engine
-------------------------------

The Dataset Services API provides a convenience function for working with :term:`dataset services` called ``get_dataset_engine``. To retrieve and engine for a sitewide configuration, call ``get_dataset_engine`` with the name of the configuration::

  from tethys_sdk.services import get_dataset_engine

  dataset_engine = get_dataset_engine(name='example')

It will return the first service with a matching name or raise an exception if the service cannot be found with the given name. Alternatively, you may retrieve a list of all the dataset engine objects that are registered using the ``list_dataset_engines`` function:

::

  from tethys_sdk.services import list_dataset_engines

  dataset_engines = list_dataset_engines()

You can also create a ``DatasetEngine`` object directly without using the convenience function. This can be useful if you want to vary the credentials for dataset access frequently (e.g.: using user specific credentials). Simply import it and instantiate it with valid credentials::

  from tethys_dataset_services.engines import CkanDatasetEngine

  dataset_engine = CkanDatasetEngine(endpoint='http://www.example.com/api/3/action', apikey='a-R3llY-n1Ce-@Pi-keY')

.. caution::

  Take care not to store API keys, usernames, or passwords in the source files of your app--especially if the source is made public. This could compromise the security of the dataset service.


2. Use the Dataset Service Engine
---------------------------------

After you have a ``DatasetEngine``, simply call the desired method on it. All ``DatasetEngine`` methods return a dictionary with an item named ``'success'`` that contains a boolean. If the operation was successful, the value of ``'success'`` will be ``True``, otherwise it will be ``False``. If the value of ``'success'`` is ``True``, the dictionary will also contain an item named ``'result'`` that will contain the results. If it is ``False``, the dictionary will contain an item named ``'error'`` that will contain information about the error that occurred. This can be used for debugging purposes as illustrated in the following example::

  from tethys_sdk.services import get_dataset_engine

  dataset_engine = get_dataset_engine(name='example')

  result = dataset_engine.list_datasets()

  if result['success']:
      dataset_list = result['result']

      for each dataset in dataset_list:
          print dataset
  else:
      print(result['error'])

Use the dataset service engines references above for descriptions of the methods available and examples.


.. note::

    The HydroShare dataset engine uses OAuth 2.0 to authenticate and authorize interactions with the HydroShare via the REST API. This requires passing the ``request`` object as one of the arguments in ``get_dataset_engine()`` method call. Also, to ensure the user is connected to HydroShare, app developers must use the ``ensure_oauth2()`` decorator on any controllers that use the HydroShare dataset engine. For example:

    ::

        from tethys_sdk.services import get_dataset_engine, ensure_oauth2

        @ensure_oauth2('hydroshare')
        def my_controller(request):
            """
            This is an example controller that uses the HydroShare API.
            """
            engine = get_dataset_engine('hydroshare', request=request)

            response = engine.list_datasets()

            context = {}

            return render(request, 'red_one/home.html', context)

