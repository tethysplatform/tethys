.. _container_orchestration_installation:

*******************************
Container Orchestration Options
*******************************

**Last Updated:** October 2026

The :ref:`Docker deployment <docker_production_installation>` guide runs a Tethys Portal on a single server. Portals that need to scale out, roll out new versions without downtime, or run on a managed container service can use the community projects below. They are maintained by `Aquaveo <https://aquaveo.com>`_, not by the Tethys Platform team.

.. list-table::
    :header-rows: 1
    :widths: 25 35 40

    * - Project
      - Use it to
      - Link
    * - **tethys-uvx**
      - Build a lightweight Tethys image with your apps
      - https://github.com/Aquaveo/tethys-uvx
    * - **tethysapp-helm-library**
      - Deploy that image on Kubernetes with Helm
      - https://github.com/Aquaveo/tethysapp-helm-library
    * - **tethys-ecs-iac**
      - Deploy that image on AWS ECS Fargate with OpenTofu
      - https://github.com/Aquaveo/tethys-ecs-iac

All three work together: build your portal image from ``tethys-uvx``, then run it with either the Helm chart or the ECS module.

The Image: tethys-uvx
=====================

``tethys-uvx`` is an alternative base image to the official ``tethysplatform/tethys-core`` image. It installs Tethys Platform with `uv <https://docs.astral.sh/uv/>`_ instead of conda, and it does not include Salt or NGINX. It contains Tethys and its serving dependencies but no apps. Your portal image builds from it and adds its own apps and :file:`portal_config.yml`.

It differs from the official image in a few ways that matter for scaling:

* **Serving and provisioning are separate.** The container command (``serve.sh``) only renders the configuration and starts the server (uvicorn by default, or gunicorn). Migrations, persistent stores, static files, and the superuser are handled by ``provision.sh``, which your deploy pipeline runs once per release. Adding replicas never re-runs setup.
* **Configuration is declarative.** Hosts, storage backends, and proxy headers are set in your :file:`portal_config.yml`, not discovered at runtime.
* **Small multi-stage images.** Use the ``builder`` image to install your apps and the ``runtime-base`` image to run them:

.. code-block:: dockerfile

    FROM ghcr.io/aquaveo/tethys-uvx:builder-v0.1.0 AS builder
    # Install your apps into ${VIRTUAL_ENV} with `uv pip install`

    FROM ghcr.io/aquaveo/tethys-uvx:runtime-base-v0.1.0
    COPY --from=builder /opt/python /opt/python
    COPY --from=builder /opt/conda /opt/conda
    COPY conf/portal_config.yml /config/portal_config.yml

Pin a versioned tag as shown so that changes to the base image cannot break your portal unexpectedly. See the `tethys-uvx README <https://github.com/Aquaveo/tethys-uvx#readme>`_ for the available tags, database options, and extension hooks.

Serving Static Files with WhiteNoise
------------------------------------

``tethys-uvx`` does not include NGINX, and Django does not serve static files when ``DEBUG`` is off. One option is to upload them to S3 or another object store. A simpler option is `WhiteNoise <https://whitenoise.readthedocs.io/>`_, which serves them from the app server itself. You collect the static files while building the image, so every replica has the same copy and no bucket is needed.

Add ``STATIC_ROOT`` and the WhiteNoise middleware to your :file:`portal_config.yml`:

.. code-block:: yaml

    settings:
      # Static files are collected into the image and served by WhiteNoise
      STATIC_ROOT: /opt/static
      MIDDLEWARE:
        - whitenoise.middleware.WhiteNoiseMiddleware

Then install ``whitenoise`` and collect the static files in the builder stage. This example uses the Dam Inventory app from the tutorials:

.. code-block:: dockerfile

    FROM ghcr.io/aquaveo/tethys-uvx:builder-v0.1.0 AS builder

    RUN uv pip install whitenoise plotly \
        "tethysapp-dam_inventory @ git+https://github.com/tethysplatform/tethysapp-dam_inventory.git@advanced-solution"

    # Collect static files into the image. Tethys needs a database even for
    # collectstatic, so the build uses a throwaway SQLite file.
    COPY portal_config.yml ${TETHYS_HOME}/portal_config.yml
    RUN tethys settings --set DATABASES.default.ENGINE django.db.backends.sqlite3 \
            --set DATABASES.default.NAME /tmp/build.sqlite3 \
        && tethys db migrate \
        && tethys manage collectstatic --noinput \
        && rm /tmp/build.sqlite3

    FROM ghcr.io/aquaveo/tethys-uvx:runtime-base-v0.1.0

    COPY --chown=1000:1000 --from=builder /opt/python /opt/python
    COPY --chown=1000:1000 --from=builder /opt/conda /opt/conda
    COPY --chown=1000:1000 --from=builder /opt/static /opt/static
    COPY --chown=1000:1000 portal_config.yml /config/portal_config.yml

The build-time settings change only affects the builder stage. The runtime image uses your unmodified :file:`portal_config.yml`.

When ``provision.sh`` runs ``collectstatic`` at deploy time, it finds the files already in place and copies nothing. If you deploy with the Helm chart below, which supplies its own :file:`portal_config.yml`, set ``STATIC_ROOT`` and ``MIDDLEWARE`` under ``portalConfig.settings`` and leave ``s3Static`` disabled.

WhiteNoise handles static files only. Files that users upload (media) still need storage that every replica can reach, such as an object store or a shared volume.

Kubernetes: tethysapp-helm-library
==================================

The ``tethys-app`` Helm chart deploys a ``tethys-uvx`` based image on Kubernetes, either as a single app served at the root of a domain or as a full portal with the app library. It provides:

* A Deployment and Service, configured from a mounted :file:`portal_config.yml`.
* A provisioning Job that runs as a Helm hook once per release, so scaling never races migrations.
* Optional Ingress, HorizontalPodAutoscaler, PodDisruptionBudget, IRSA service account, and scale to zero with KEDA.
* Optional bundled PostgreSQL and Valkey for standalone installs.

Install it from the GitHub Container Registry:

.. code-block:: bash

    helm install my-app oci://ghcr.io/aquaveo/charts/tethys-app --version 0.1.5 -f my-values.yaml

For a complete walkthrough that builds an image for an app, configures its settings and persistent store, and installs the chart, see the Dam Inventory example:

.. toctree::
    :maxdepth: 1

    container_orchestration/helm_dam_inventory

See the `chart README <https://github.com/Aquaveo/tethysapp-helm-library/tree/master/charts/tethys-app#readme>`_ for all the chart values.

AWS ECS: tethys-ecs-iac
=======================

``tethys-ecs-iac`` is an `OpenTofu <https://opentofu.org/>`_ module that runs one Tethys Portal on AWS ECS Fargate. It is a reference for running the image in a scalable, stateless setup:

* CloudFront in front of an Application Load Balancer and an ECS service with automatic rollback.
* Static and media files in S3, served through CloudFront.
* An external PostgreSQL database or connection pooler.
* Secrets stored in AWS Systems Manager Parameter Store and injected at runtime, never in the image or the OpenTofu state.
* GitHub Actions templates that run the provisioning task and then roll out the new image.

See the `tethys-ecs-iac README <https://github.com/Aquaveo/tethys-ecs-iac#readme>`_ for the architecture diagram, prerequisites, and per-portal CI templates.
