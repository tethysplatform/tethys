******************************
SpatialDatasetEngine Interface
******************************

**Last Updated**: December 2019

All objects that implement the ``SpatialDatasetEngine`` interface provide a minimum set of methods for interacting with layers and resources. Specifically, the methods allow the standard CRUD operations (Create, Read, Update, Delete) for both layers and resources.

All ``SpatialDatasetEngine`` methods return a dictionary called the response dictionary. The Response dictionary contains an item named ``'success'`` whose value is a boolean indicating whether the operation was successful or not. If ``'success'`` is ``True``, then the the dictionary will also have a ``'result'`` key that contains the result of the operation. If ``'success'`` is ``False``, then the Response dictionary will contain an ``'error'`` key with information about what went wrong.

The following reference provides a summary of the base methods and properties provided by all ``SpatialDatasetEngine`` objects.

Properties
==========

:class:`SpatialDatasetEngine.` **endpoint** (string): URL for the spatial dataset service API endpoint.

:class:`SpatialDatasetEngine.` **apikey** (string, optional): API key may be used for authorization.

:class:`SpatialDatasetEngine.` **username** (string, optional): Username key may be used for authorization.

:class:`SpatialDatasetEngine.` **password** (string, optional): Password key may be used for authorization.

:class:`SpatialDatasetEngine.` **type** (string, readonly): Identifies the type of ``SpatialDatasetEngine`` object.


Create Methods
==============

.. automethod:: tethys_dataset_services.base.SpatialDatasetEngine.create_resource

.. automethod:: tethys_dataset_services.base.SpatialDatasetEngine.create_layer

Read Methods
============

.. automethod:: tethys_dataset_services.base.SpatialDatasetEngine.get_resource

.. automethod:: tethys_dataset_services.base.SpatialDatasetEngine.get_layer

.. automethod:: tethys_dataset_services.base.SpatialDatasetEngine.list_resources

.. automethod:: tethys_dataset_services.base.SpatialDatasetEngine.list_layers


Update Methods
==============

.. automethod:: tethys_dataset_services.base.SpatialDatasetEngine.update_resource

.. automethod:: tethys_dataset_services.base.SpatialDatasetEngine.update_layer


Delete Methods
==============

.. automethod:: tethys_dataset_services.base.SpatialDatasetEngine.delete_resource

.. automethod:: tethys_dataset_services.base.SpatialDatasetEngine.delete_layer
