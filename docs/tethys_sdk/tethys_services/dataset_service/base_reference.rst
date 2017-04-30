*****************************
Base Dataset Engine Reference
*****************************

**Last Updated**: January 19, 2015

All ``DatasetEngine`` object provide a minimum set of methods for interacting with :term:`datasets` and :term:`resources`.
Specifically, the methods allow the standard CRUD operations (Create, Read, Update, Delete) for both :term:`datasets` and
:term:`resources`.

All ``DatasetEngine`` methods return a dictionary, often called the Response dictionary. The Response dictionary contains
an item named 'success' that contains a boolean indicating whether the operation was successful or not. If 'success' is
``True``, then the the dictionary will also have an item named 'result' that contains the result of the operation. If
'success' is ``False``, then the Response dictionary will contain an item called 'error' with information about what went
wrong.

The following reference provides a summary of the base methods and properties provided by all ``DatasetEngine`` objects.

Properties
==========

:class:`DatasetEngine.` **endpoint** (string): URL for the :term:`dataset service` API endpoint.

:class:`DatasetEngine.` **apikey** (string, optional): API key may be used for authorization.

:class:`DatasetEngine.` **username** (string, optional): Username key may be used for authorization.

:class:`DatasetEngine.` **password** (string, optional): Password key may be used for authorization.

:class:`DatasetEngine.` **type** (string, readonly): Identifies the type of ``DatasetEngine`` object.


Create Methods
==============

.. automethod:: tethys_dataset_services.base.DatasetEngine.create_dataset

.. automethod:: tethys_dataset_services.base.DatasetEngine.create_resource

Read Methods
============

.. automethod:: tethys_dataset_services.base.DatasetEngine.get_dataset

.. automethod:: tethys_dataset_services.base.DatasetEngine.get_resource

.. automethod:: tethys_dataset_services.base.DatasetEngine.search_datasets

.. automethod:: tethys_dataset_services.base.DatasetEngine.search_resources

.. automethod:: tethys_dataset_services.base.DatasetEngine.list_datasets


Update Methods
==============

.. automethod:: tethys_dataset_services.base.DatasetEngine.update_dataset

.. automethod:: tethys_dataset_services.base.DatasetEngine.update_resource


Delete Methods
==============

.. automethod:: tethys_dataset_services.base.DatasetEngine.delete_dataset

.. automethod:: tethys_dataset_services.base.DatasetEngine.delete_resource