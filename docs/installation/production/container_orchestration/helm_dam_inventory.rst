.. _helm_dam_inventory_example:

*****************************************
Example: Deploy Dam Inventory with Helm
*****************************************

**Last Updated:** October 2026

This example deploys the Dam Inventory app from the :ref:`app development tutorials <tutorials>` to Kubernetes with the ``tethys-app`` Helm chart. It uses the ``advanced-solution`` branch of `tethysapp-dam_inventory <https://github.com/tethysplatform/tethysapp-dam_inventory>`_, which has the two kinds of app settings most apps need:

* a custom setting, ``max_dams``
* a persistent store, ``primary_db``

The app runs in single app mode, so it is served at the root of its own domain (for example ``https://dams.example.org/``) without the app library.

Prerequisites
=============

* A Kubernetes cluster with an Ingress controller, and Helm 3.8 or later.
* A container registry the cluster can pull from.
* A PostgreSQL server the cluster can reach.
* An S3 bucket, or another S3-compatible object store, for static and media files. Its objects must be publicly readable or served through a CDN.

1. Create the Project Files
===========================

Create a directory with these files:

.. code-block:: text

    dam-inventory-deploy/
    ├── Dockerfile
    ├── portal_static.py
    ├── init.d/
    │   └── 50-dam-inventory.sh
    └── values.yaml

Dockerfile
----------

The image builds on ``tethys-uvx``. It installs the app with two packages the app needs that the base image does not include: ``plotly`` for the hydrograph plots, and ``django-storages`` for serving static files from S3.

.. code-block:: dockerfile

    FROM ghcr.io/aquaveo/tethys-uvx:builder-v0.1.0 AS builder

    # Install the app and the extra packages it needs into the Tethys venv
    RUN uv pip install plotly "django-storages[s3]" \
        "tethysapp-dam_inventory @ git+https://github.com/tethysplatform/tethysapp-dam_inventory.git@advanced-solution"

    FROM ghcr.io/aquaveo/tethys-uvx:runtime-base-v0.1.0

    COPY --chown=1000:1000 --from=builder /opt/python /opt/python
    COPY --chown=1000:1000 --from=builder /opt/conda /opt/conda
    # S3 storage class (/opt/portal is on PYTHONPATH) and the provisioning hook
    COPY portal_static.py /opt/portal/
    COPY --chmod=0755 init.d/ /opt/portal/init.d/

S3 Storage Class
----------------

Some Tethys Portal templates refer to static files with a leading slash, such as ``/tethys_portal/images/default_favicon.png``. The stock ``S3Storage`` backend rejects those paths, which makes the login page fail. Save this class as :file:`portal_static.py`:

.. code-block:: python

    from storages.backends.s3 import S3Storage


    class LeadingSlashS3Storage(S3Storage):
        """S3 storage that accepts the leading-slash static paths some Tethys templates use."""

        def _normalize_name(self, name):
            return super()._normalize_name(name.lstrip("/"))

Provisioning Hook
-----------------

The chart runs ``provision.sh`` from the image as a Job before each release. It migrates the database, creates a persistent store service from the ``TETHYS_PS_CONNECTION`` secret, publishes static files, creates the ``admin`` user, and then runs every script in :file:`/opt/portal/init.d/`. Use a hook to configure the app's settings. Save this as :file:`init.d/50-dam-inventory.sh`:

.. code-block:: bash

    #!/usr/bin/env bash
    set -euo pipefail

    # Link the app's persistent store to the service that provision.sh created from
    # TETHYS_PS_CONNECTION. Linking again on later releases is harmless.
    tethys link "persistent:${POSTGIS_SERVICE_NAME}" dam_inventory:ps_database:primary_db \
      || echo "  (primary_db may already be linked)"

    # Create the store's tables. syncstores exits 0 even when an initializer fails,
    # so check its output to fail the release instead.
    out=$(tethys syncstores dam_inventory 2>&1)
    echo "$out"
    if grep -qE '^[A-Za-z_.]+(Error|Exception)\b' <<<"$out"; then
      echo "FATAL: syncstores failed" >&2
      exit 1
    fi

    tethys app_settings set dam_inventory max_dams "${DAM_INVENTORY_MAX_DAMS:-50}"

The hook runs on every release, so each command in it must be safe to repeat.

Values
------

Save this as :file:`values.yaml`, replacing the image, database host, bucket, and domain with your own:

.. code-block:: yaml

    image:
      repository: ghcr.io/my-org/tethysapp-dam-inventory
      tag: "1.0.0"

    tethys:
      mode: single                 # serve one app at the root of the domain
      standaloneApp: dam_inventory
      env:
        POSTGIS_SERVICE_NAME:      # persistent store service created by provision.sh
          value: dam_inventory_db
        DAM_INVENTORY_MAX_DAMS:    # read by the init.d hook
          value: "20"

    externalDatabase:
      host: postgres.example.internal
      name: tethys_platform_dam_inventory
      username: tethys_default

    secrets:
      existingSecretName: dam-inventory-secrets
      secretEnv:
        - name: TETHYS_PS_CONNECTION
          key: TETHYS_PS_CONNECTION
          optional: false
        - name: PORTAL_SUPERUSER_PASSWORD
          key: PORTAL_SUPERUSER_PASSWORD
          optional: false

    s3Static:
      enabled: true
      bucket: dam-inventory-assets
      region: us-east-1

    ingress:
      enabled: true
      className: nginx
      host: dams.example.org

    portalConfig:
      settings:
        STORAGES:
          staticfiles:
            BACKEND: portal_static.LeadingSlashS3Storage

The chart combines ``portalConfig.settings`` with the settings it derives from the other values, so the ``STORAGES`` entry above only replaces the storage class and keeps the bucket options from ``s3Static``.

To access S3 on Amazon EKS, set ``serviceAccount.roleArn`` to an IAM role that can write to the bucket. On other clusters, add ``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY`` to the secret and list them under ``secrets.secretEnv``.

2. Build and Push the Image
===========================

.. code-block:: bash

    docker build -t ghcr.io/my-org/tethysapp-dam-inventory:1.0.0 .
    docker push ghcr.io/my-org/tethysapp-dam-inventory:1.0.0

3. Prepare the Database
=======================

Create the Tethys database and its owner on your PostgreSQL server:

.. code-block:: sql

    CREATE ROLE tethys_default LOGIN PASSWORD '<db-password>';
    CREATE DATABASE tethys_platform_dam_inventory OWNER tethys_default;

Give each standalone app its own database. Apps that share a Tethys database also share its app registry, so a standalone app can break a portal that uses the same database.

The persistent store needs a PostgreSQL user that can create databases, because Tethys creates a ``dam_inventory_primary_db`` database for the store.

4. Create the Secret
====================

.. code-block:: bash

    kubectl create secret generic dam-inventory-secrets \
      --from-literal=TETHYS_SECRET_KEY="$(openssl rand -base64 48)" \
      --from-literal=TETHYS_DB_PASSWORD='<db-password>' \
      --from-literal=TETHYS_PS_CONNECTION='<store-user>:<store-password>@postgres.example.internal:5432' \
      --from-literal=PORTAL_SUPERUSER_PASSWORD='<admin-password>'

``TETHYS_PS_CONNECTION`` uses the ``<username>:<password>@<host>:<port>`` format, not a ``postgresql://`` URL.

5. Install the Chart
====================

.. code-block:: bash

    helm install dam-inventory oci://ghcr.io/aquaveo/charts/tethys-app \
      --version 0.1.5 -f values.yaml

Helm first runs the provisioning Job, then starts the app. Follow the Job with:

.. code-block:: bash

    kubectl logs -f job/dam-inventory-tethys-app-provision

A successful run ends with ``Tethys provision complete``. Point the DNS record for ``dams.example.org`` at your Ingress controller, then open ``https://dams.example.org`` and sign in as ``admin`` with the password from the secret.

6. Release a New Version
========================

Build and push the image with a new tag, set ``image.tag`` in :file:`values.yaml`, and upgrade:

.. code-block:: bash

    helm upgrade dam-inventory oci://ghcr.io/aquaveo/charts/tethys-app \
      --version 0.1.5 -f values.yaml

The provisioning Job runs again before the new pods start, so database migrations and store changes are applied once per release, however many replicas the app has. To scale out, set ``hpa.enabled: true`` and its replica limits in :file:`values.yaml`.
