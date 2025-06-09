.. _tethys_components_custom:

Custom Tethys Components
************************

Custom Python components provided by Tethys.

.. important::

    This module should *not* be used directly (e.g. via ``from tethys_components import custom``) but is made accessible on the :ref:`tethys_components_library` ``lib`` object via the ``tethys`` namespace (i.e. ``lib.tethys``).

    When the API is access this way, the first ``lib`` argument for each component function below behaves much like ``self`` does for classes, meaning it *should not* be explicitly passed.

.. automodule:: tethys_components.custom
    :members: