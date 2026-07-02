.. _multi_tenancy_config:

************************
Multi Tenancy (Optional)
************************

**Last Updated:** December 2025

.. important::

   This capability requires the ``django-tenants`` third-party library to be installed. Starting with Tethys 5.0 or if you are using ``micro-tethys-platform``, you will need to install ``django-tenants`` using conda or pip as follows:

   .. code-block:: bash

      # conda: conda-forge channel strongly recommended
      conda install -c conda-forge django-tenants

      # pip
      pip install django-tenants

.. important::

    Multi-tenancy requires PostgreSQL as the database backend. SQLite is not supported.

Tethys Portal supports only one tenant per portal by default. Multi-tenancy allows you to run multiple tenants (isolated instances of Tethys Portal) within a single deployment. This is useful for organizations or providers that want to provide separate environments for different groups or customers. In addition, multi-tenancy enables the ability to separate and customize the look and resources of the Tethys Portal based on each tenant. This functionality extends to the app level.


Enable Multi-Tenancy
====================

Use the following instructions to setup multi-tenancy for your Tethys Portal deployment. See the `Django-tenants Documentation <https://django-tenants.readthedocs.io/en/latest/use.html>`_ for more information.

Configuration
-------------

Enable multi-tenancy by making the following changes to your settings:

Begin by enabling Tethys Tenants:

.. code-block:: yaml
   :emphasize-lines: 3-4

   settings:
     ...
     TENANTS_CONFIG:
       ENABLED: true

Next, override the database engine to use the ``django-tenants`` backend:

.. code-block:: yaml
    :emphasize-lines: 4

    settings:
      DATABASES:
        default:
          ENGINE: django_tenants.postgresql_backend

You can customize the multi-tenancy behavior with the following settings:

.. code-block:: yaml
    :emphasize-lines: 4-9

    settings:
      TENANTS_CONFIG:
        ENABLED: true
        TENANT_APPS:
          - "tethys_apps"
          - "tethys_config"
        TENANT_LIMIT_SET_CALLS: false
        TENANT_COLOR_ADMIN_APPS: true
        SHOW_PUBLIC_IF_NO_TENANT_FOUND: false

Configuration Options
=====================

**TENANT_APPS**
    List of Django apps that should be isolated per tenant. These apps will have their database tables created in each tenant's schema.

**TENANT_LIMIT_SET_CALLS**
    Boolean (default: ``false``). When ``true``, limits database SET calls for performance optimization.

**TENANT_COLOR_ADMIN_APPS**
    Boolean (default: ``true``). When ``true``, colors tenant-enabled sections dark green in the site admin.

**SHOW_PUBLIC_IF_NO_TENANT_FOUND**
    Boolean (default: ``false``). When ``true``, shows the public schema when no tenant is found instead of returning a 404 error.

Working with Tenants
====================

**Run migrations**:

If the Tethys database is being created for the first time, new tenant tables are created as part of it by detecting and applying migrations in the following way.

   .. code-block:: bash

       tethys manage makemigrations <app_label>
       tethys manage migrate_schemas

If existing django-apps become tenant aware (are moved to the `TENANT_APPS` list) later on, django will not recognize that new migrations need to be applied by default. Use the ``migrate`` command to first unapply the migrations at the tenant level and then reapply them properly using the ``zero`` parameter and the ``--tenant``` flag in the following way.

   .. code-block:: bash

       tethys manage migrate <app_label> zero --fake --tenant
       tethys manage migrate <app_label> --tenant

After updating your :file:`portal_config.yml` file:

**Create tenant**:

   .. code-block:: bash

       tethys manage create_tenant

See the `Django-tenants Documentation <https://django-tenants.readthedocs.io/en/latest/use.html#create-tenant>`_ for more details on using the `create_tenant` command or run ``tethys manage create_tenant --django-help`` on the active tethys environment terminal.

Even though it already exists, the default public schema must be added to the Tenants table using the `create_tenant` command. See the example below:

   .. code-block:: bash

       tethys manage create_tenant --schema_name public --name Public --domain-domain localhost

**Create tenant superuser**:

Each tenant requires its own portal admin account. Create a superuser for a specific tenant by running the following command:

   .. code-block:: bash

       tethys manage create_tenant_superuser

New tenants and tenant domains can be added via the Tethys Portal Admin interface once multi-tenancy is enabled. The Tethys Tenants admin block is only visible to superusers of the public schema.

.. figure:: ./images/tethys_tenants_admin.png
    :width: 800px

Management
----------

Django-tenants includes two very useful commands to help manage database schemas.

- `tenant_command <https://django-tenants.readthedocs.io/en/latest/use.html#tenant-command>`_: Runs any django manage command on an individual schema
- `all_tenants_command <https://django-tenants.readthedocs.io/en/latest/use.html#all-tenants-command>`_: Runs any django manage command on all schemas

For example, to show the applied migrations for a specific tenant schema or for all tenant schemas, use the following commands:

   .. code-block:: bash

       tethys manage tenant_command showmigrations <app_label> --schema <schema_name>
       tethys manage all_tenants_command showmigrations <app_label>
