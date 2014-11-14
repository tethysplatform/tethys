********************
Dataset Services API
********************

**Last Updated**: November 7, 2014

:term:`Dataset services` are web services external to Tethys Platform that can be used to store and publish file-based
:term:`datasets` (e.g.: text files, Excel files, zip archives, other model files). Tethys app developers can use the
Dataset Services API to access :term:`datasets` for use in their apps and publish any resulting :term:`datasets` their
apps may produce.

Supported Dataset Services
==========================

* `CKAN <http://ckan.org>`_
* `HydroShare <http://hydroshare.cuahsi.org>`_

Key Concepts
============

The Tethys Dataset Services API provides a standardized interface for interacting with :term:`dataset services`. This
means that you can use datasets from different sources without completely overhauling your code. Each of the supported
:term:`dataset services` provides a ``DatasetEngine`` object with the same methods. For example, all ``DatasetEngine``
object have a method called ``list_datasets()`` and will have the same result, returning a list of the datasets that are
available.

There are two important definitions that are applicable to :term:`dataset services`: :term:`dataset` and :term:`resource`.
A :term:`resource` contains a single file or other object and the metadata associated with it. A :term:`dataset` contains
one or more resources.

Sitewide Configuration
=======================

To use :term:`dataset services`, you must provide an endpoint and credentials for authenticating and authorizing. This
can be done at two levels. As a Tethys Platform administrator, you may wish to provide a set of sitewide
:term:`dataset services` that will be accessible for all app developers. To configure your Tethys Platform with
sitewide :term:`dataset services`, add the ``TETHYS_DATASET_SERVICES`` dictionary to your :file:`settings.py` file::

  TETHYS_DATASET_SERVICES = {
      'default': {
          'ENGINE': 'tethys_datasets.engines.CkanDatasetEngine',
          'ENDPOINT': 'http://www.example.com/api/3/action',
          'APIKEY': 'a-R3llY-n1Ce-@Pi-keY'
      },
      'example': {
          'ENGINE': 'tethys_datasets.engines.HydroServerDatasetEngine',
          'ENDPOINT': 'http://www.demo.com/api',
          'USERNAME': 'user',
          'PASSWORD': 'password'
      }
  }

.. Important::

   Do not use the same credentials in production that you used in development. Doing so could create a serious security
   breach.

Each item of the ``TETHYS_DATASET_SERVICES`` represents the configuration parameters for a single :term:`dataset service`.
The example above provides the credentials for two :term:`dataset services`, one called "default" and another called
"example". The names of the :term:`dataset services` are important, because they are used to retrieve the dataset
engine. The credentials for each :term:`dataset service` are stored in another dictionary with possible keys: ``ENGINE``,
``ENDPOINT``, ``APIKEY, ``USERNAME``, and ``PASSWORD``. The ``ENGINE`` and ``ENDPOINT`` keys are required for all types
of :term:`dataset services`, while the other keys are optional.

**Dataset Service Configuration Dictionary Keys:**

* ENGINE (string): The dot notation path to the DatasetEngine object provided by the Dataset Services API.
* ENDPOINT (string): The URL of the :term:`dataset service` API endpoint.
* APIKEY (string, optional): API key that will be used for authorization.
* USERNAME (string, optional): Username that will be used for authorization.
* PASSWORD (string, optional): Password that will be used for authorization.

.. Note::

   The ``APIKEY``, ``USERNAME``, and ``PASSWORD`` parameters are used to authenticate and authorize certain operations
   on the datasets. The Dataset Services API will only have permissions equivalent to those of the user that the
   credentials belong to. In other words, if the user to which the credentials belong does not have the permissions
   needed to create or edit :term:`datasets`, then apps will not be able to create or edit datasets using that
   :term:`dataset services` configuration.


There are two options for configuring Tethys Platform to for :term:`dataset services`. The first method involves.

App Specific Configuration
==========================

Alternatively, if you do not wish to rely on the sitewide :term:`dataset services` configuration, you may also configure
app specific :term:`dataset services` that will only be available to your app. This is done by adding another method to
the :file:`app.py` file for your app. Import ``DatasetService`` from ``tethys_apps.base`` and the create a method called
``dataset_services`` to your app class. This method must return a ``list`` or ``tuple`` of ``DatasetService`` objects.
For example::

  from tethys_apps.base import TethysAppBase, DatasetService

  class ExampleApp(TethysAppBase):
      """
      Tethys App Class
      """
      ...

      def dataset_services(self):
          """
          Add one or more dataset services
          """
          dataset_services = (DatasetService(name='example',
                                             type='ckan',
                                             endpoint='http://www.example.com/api/3/action',
                                             apikey='a-R3llY-n1Ce-@Pi-keY'
                                             ),
          )

          return dataset_services

The ``DatasetService`` object can be initialized with the following options: ``name``, ``type``, ``endpoint``, ``apikey``,
``username``, and ``password``. The ``name``, ``type``, and ``endpoint`` parameters are required. A summary of the
parameters is provided:

**DatasetService(name, type, endpoint, apikey, username, password)**

* name (string): Name of the :term:`dataset service`.
* type (string): Type of the :term:`dataset service`, either 'ckan' or 'hydroshare'.
* endpoint (string): The URL of the :term:`dataset services` API endpoint.
* apikey (string, optional): API key that will be used for authorization.
* username (string, optional): Username that will be used for authorization.
* password (string, optional): Password that will be used for authorization.

Get a Dataset Engine
====================

The Dataset Services API provides a convenience function for working with :term:`dataset services` called
``get_dataset_engine``. To retrieve and engine for a sitewide configuration, call ``get_dataset_engine`` with the name
of the configuration::

  from tethys_apps.utilities import get_dataset_engine

  dataset_engine = get_dataset_engine(name='example')

To use a app specific :term:`dataset services`, call the ``get_dataset_engine`` function with the name of the
configuration and your app class as follows::

  from tethys_apps.utilities import get_dataset_engine
  from ..app import ExampleApp

  dataset_engine = get_dataset_engine(name='example', app_class=ExampleApp)

When used with the ``app_class`` parameter, the ``get_dataset_engine`` function will search first through any app specific
:term:`dataset services` and then it will search for sitewide :term:`dataset services`. It will return the first service
with a matching name or raise an exception if the service cannot be found with the given name.

Alternatively, you can create a ``DatasetEngine`` object directly without using the convenience function. This can be useful
if you want to vary the credentials for dataset access frequently (e.g.: using user specific credentials). Simply import
it and instantiate it with valid credentials::

  from tethys_datasets.engines import CkanDatasetEngine

  dataset_engine = CkanDatasetEngine(endpoint='http://www.example.com/api/3/action', apikey='a-R3llY-n1Ce-@Pi-keY')


Using the Dataset Engine
========================

After you have a ``DatasetEngine``, simply call the desired method on it. All ``DatasetEngine`` methods return a dictionary
with an item named 'success' that contains a boolean. If the operation was successful, 'success' will be true, otherwise
it will be false. If 'success' is true, the dictionary will have an item named 'result' that will contain the results.
If it is false, the dictionary will have an item named 'error' that will contain information about the error that
occurred. This can be very useful for debugging purposes as illustrated in the following example::

  from tethys_apps.utilities import get_dataset_engine
  from ..app import ExampleApp

  dataset_engine = get_dataset_engine(name='example', app_class=ExampleApp)

  result = dataset_engine.list_datasets()

  if result['success']:
      dataset_list = result['result']

      for each dataset in dataset_list:
          print dataset
  else:
      print(result['error'])

Dataset Engine References
=========================

All ``DatasetEngine`` objects implement a minimum set of base methods. However, some ``DatasetEngine`` objects may
include additional methods that are unique to that ``DatasetEngine`` and the arguments that each method accepts may vary
slightly. Refer to the following references for the methods that are offered by each ``DatasetEngine``.

.. toctree::
    :maxdepth: 1

    dataset_service/base_reference
    dataset_service/ckan_reference
    dataset_service/hydroshare_reference
