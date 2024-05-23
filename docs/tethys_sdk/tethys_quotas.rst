.. _sdk_quotas_api:

*****************
Tethys Quotas API
*****************

**Last Updated:** March 2019

Tethys Quotas allows portal admins to set-up, manage and enforce storage, compute-time and other resource quotas on users, apps and other entities. The portal admins can declare a quota's defaults and state (i.e. active/inactive) and change it at anytime to meet the needs of the portal. They can also set entity specific quotas if the need arises (an entity can be a Tethys App or a User). For example, if there is a portal default quota on user workspace storage of 5 GB but there is a specific user who needs double that to complete their workflows, an admin can go into that user's settings and change their user-specific quota to 10 GB.

Built-in Quotas
===============

Custom quotas can be created, but by default Tethys includes two built-in quotas: :ref:`tethys_quotas_user_admin` and :ref:`tethys_quotas_app_admin`.

.. tip::

    See :ref:`tethys_quotas_custom_quota` for information on how to remove quotas and/or add custom quotas.


Admin Pages
===========

For information on how to manage the built-in quotas see :ref:`tethys_quotas_app_manage_storage` and :ref:`tethys_quotas_user_manage`

.. _tethys_quotas_rqh:

ResourceQuotaHandler
====================

.. autoclass:: tethys_quotas.handlers.base.ResourceQuotaHandler
   :members:

.. _tethys_quotas_custom_quota:

Creating Custom Quotas
======================

To create a custom quota you will have to create a new quota handler class. Your new handler class will have to inherit from the :ref:`tethys_quotas_rqh` class. Follow the pattern in the built-in handler class, ``WorkspaceQuotaHandler`` (located at ``src/tethys_quotas/handlers/workspace.py``).

.. important::

    The abstract method, ``get_current_use``, which needs to be overridden in any custom quota handler class, is essential as it holds the logic for what the quota is measuring (time, storage, etc.).

To load a custom quota, append the classpath to the ``RESOURCE_QUOTA_HANDLERS`` section of the :file:`portal_config.yml` file (see snippet of :file:`portal_config.yml` below).

::

    # RESOURCE QUOTAS TO INSTALL
    RESOURCE_QUOTA_HANDLERS:
      - tethys_quotas.handlers.workspace.WorkspaceQuotaHandler

**Figure 1.** :file:`portal_config.yml` file showing the ``RESOURCE_QUOTA_HANDLERS`` section.

.. note::

    Delete or comment out classpath strings in the :file:`portal_config.yml` file to remove certain quota types from the portal.

Enforcing Quotas
================

Using the :ref:`tethys_paths_api` to access workspaces and media directories will automatically enforce the built in workspace quotas. To enforce a custom quota, the ``@enforce_quota`` decorator must be used. Within the decorator initialization, pass in the respective ``codename`` of the quota you wish to enforce.

::

    # Import the enforce_quota decorator
    from tethys_sdk.quotas import enforce_quota
    ...

    # Enforce the desired quota (taken from the Dam Inventory Tutorial)
    @enforce_quota('user_dam_quota')
    @permission_required('add_dams')
    def add_dam(request):
        """
        Controller for the Add Dam page.
        """
        ...

**Figure 2.** Example usage of ``@enforce_quota``, taken from the Dam Inventory Tutorial.

The ``@enforce_quota`` decorator will check to make sure the desired quota hasn't been met. If the quota has been met the user will be rerouted to an error page displaying the quota's help text.

Quotas API
==========

A few helper functions have been added with Tethys Quotas to help developers integrate quotas within their apps.

get_quota
---------

.. autofunction:: tethys_quotas.utilities.get_quota

get_resource_available
----------------------

.. autofunction:: tethys_quotas.utilities.get_resource_available

passes_quota
------------

.. autofunction:: tethys_quotas.utilities.passes_quota

Additional Resources
====================

For more information and examples on how to use the Tethys Quotas API (including creating and enforcing custom quotas) see the :doc:`../tutorials/quotas` tutorial.
