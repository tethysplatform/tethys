********************************
Django Channels Layer (Optional)
********************************

**Last Updated:** Sep 2020

Production installations that use the ``WebSockets`` and/or ``Bokeh Server`` functionality that comes with Tethys, require the a ``CHANNEL_LAYER``.

Key Concepts
============
A ``CHANNEL_LAYER`` provides a backend where ``WebSocket`` messages can be stored and then accessed by  different app instances (ASGI processes).

Adding a REDIS CHANNEL_LAYER
============================
Development installations make use of the default ``InMemoryChannelLayer``, however this layer has some limitations in production (See `Django Channels documentation <https://channels.readthedocs.io/en/latest/topics/channel_layers.html#in-memory-channel-layer>`_). To address these limitations, ``Django Channels`` suppports a ``REDIS CHANNEL LAYER``, however other ``CHANNEL_LAYERS`` can be configured. The following documentation demonstrates how to configure a ``REDIS CHANNEL LAYER``.

First, install the ``channels_redis`` Python package in your Tethys conda environment.

::

    pip install channels_redis

Second, add or modify the ``CHANNEL_LAYERS`` parameter in the ``portal_config.yml`` as follows:

.. code-block:: yaml

    CHANNEL_LAYERS:
      default:
        BACKEND: channels_redis.core.RedisChannelLayer
        CONFIG:
          hosts:
          - [127.0.0.1, 6379]

Finally, start a redis instance. This can easily be done with docker as shown below.

::

    docker run -p 6379:6379 -d redis:5

Once a production ``CHANNEL_LAYER`` has been configured, the number of ``ASGI_PROCESSES`` can be increased as in the example below:

::

    tethys gen asgi_service --asgi-processes <desired_number_of_instances> --conda-prefix <path_to_tethys_conda_environment>

.. warning::

    ``Bokeh Server`` does not currently support the use of multi intance processes. Therefore, it does not work with more than one ASGI process (``ASGI_PROCESSES`` must be equal to 1) (See `Bokeh Server documentation <https://docs.bokeh.org/en/latest/docs/reference/server/server.html#bokeh.server.server.Server>`_).


With Tethys Docker
------------------

If using Tethys Docker, the ``CHANNEL_LAYER`` and ``ASGI_PROCESSES`` parameters can be set on the ``Dockerfile`` or ``docker-compose``. Below is an example of how to set these variables in a ``Dockerfile``.

::

    ENV ASGI_PROCESSES 1
    ENV CHANNEL_LAYER "channels_redis.core.RedisChannelLayer"

To configure redis this way, add the following to docker-compose at the same level as the other containters (db, geoserver, etc.):

.. code-block:: yaml

    redis:
      image: redis:5
      restart: always
      networks:
        - "internal"
      ports:
        - "6379:6379"

Finally, add the following code at the beginning of ``tethys_app.sls``

.. code-block:: yaml

    {% set CHANNEL_LAYER = salt['environ.get']('CHANNEL_LAYER') %}
    {% set ASGI_PROCESSES = salt['environ.get']('ASGI_PROCESSES') %}


    Insert_Redis_Channel_Layer:
      cmd.run:
        - name: >
            {{TETHYS_BIN_DIR }}/tethys settings
            --set CHANNEL_LAYERS.default.BACKEND {{ CHANNEL_LAYER }}
            --set CHANNEL_LAYERS.default.CONFIG.hosts "[[docker_redis_1,6379],]"
        - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/portal_config.yml" ];"

    Regenerate_ASGI_Service_TethysCore:
      cmd.run:
        - name: >
            {{TETHYS_BIN_DIR }}/tethys gen asgi_service
            --asgi-processes {{ ASGI_PROCESSES }}
            --conda-prefix {{ CONDA_HOME }}/envs/{{ CONDA_ENV_NAME }}
            --overwrite
        - unless: /bin/bash -c "[ -f "{{ TETHYS_PERSIST }}/portal_config.yml" ];"
