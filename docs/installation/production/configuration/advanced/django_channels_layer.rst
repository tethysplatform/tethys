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
Development installations make use of the default ``InMemoryChannelLayer``, however this layer is not meant for production (See `Django Channels documentation <https://channels.readthedocs.io/en/latest/topics/channel_layers.html#in-memory-channel-layer>`_). For production purposes, ``Django Channels`` suppports a ``REDIS CHANNEL LAYER``, however other ``CHANNEL_LAYERS`` can be configured. The following documentation demonstrates how to configure a ``REDIS CHANNEL LAYER``.

First, install the ``channels_redis`` Python package in your Tethys conda environment.

..

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

..

    docker run -p 6379:6379 -d redis:5

Once the ``CHANNEL_LAYER`` has been configured, the number of ``ASGI_PROCESSES`` can be increased as in the example below:

..

    tethys gen asgi_service --asgi-processes <desired_number_of_instances> --conda-prefix <path_to_tethys_conda_environment>

.. note::

    If using a Docker image, the ``CHANNEL_LAYER`` and ``ASGI_PROCESSES`` parameters can be set on the ``Dockerfile``.
