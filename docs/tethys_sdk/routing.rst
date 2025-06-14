.. _routing_api:

***********
Routing API
***********

**Last Updated:** December 2022

Routing is the way a request to a URL is connected (or routed) to a function or class that is responsible for handling that request. When a request is submitted to Tethys, it matches the URL of that request against a list of registered URLs and calls the function or class that is registered with that URL. This connection between the URL and the function or class that handles it is also called a URL mapping. A function or class that is mapped to a URL endpoint is known as either a controller or a consumer (depending on the protocol used in the URL).

Beginning in Tethys 4.0, registering a URL is done by decorating its function or class with one of the Tethys routing decorators (``controller`` or ``consumer``). The ``controller`` decorator is used to register a URL using the HTTP protocol, while the ``consumer`` decorator is used to register a URL using the :ref:`websocket <websockets>` protocol.

.. warning::

  The ``url_maps`` method in the ``app.py`` is deprecated in favor of the new ``controller`` decorator approach (described below) and **WILL BE REMOVED in Tethys 4.1.0**. The ``url_maps`` method is temporarily available in Tethys 4.0 to allow for easier migration of apps to using the new ``controller`` decorator method. If you still wish to declare ``UrlMaps`` in the :file:`app.py`, use the new ``register_url_maps()`` method and then remove the ``url_maps()`` method (see: :ref:`register-url-maps-method`). Use of the ``url_maps`` method in Tethys 4.0.0 causes long warning messages to be displayed in the terminal to encourage users to migrate as soon as possible. **Don't wait until 4.1.0 to move to the ``controller`` decorator!**

.. _controller-decorator:

Controller Decorator
--------------------
The ``controller`` decorator is used to decorate a function or class (see :ref:`class_based_controllers`) that serves as a controller for a URL endpoint. When Tethys registers a URL mapping, in the background, it uses a :ref:`UrlMap <URL Maps>` object that needs at least three things: a ``controller``, a ``name``, and a ``url``. When you decorate a function with the ``controller`` decorator that provides the first element. The next two elements can either be automatically derived from the decorated function, or you can supply them explicitly. For example, if you register a controller like this::

  @controller
  def my_demo_controller(request):
    ...

Tethys will create a ``UrlMap`` with the following arguments::

  UrlMap(
    name='my_demo_controller',
    url='my-demo-controller/',
    controller='my_first_app.controllers.my_demo_controller',
  )

.. note::
  The full URL endpoint that gets registered will include the hostname of your Tethys Portal and the ``root_url`` that is defined in your ``app.py`` file. So in the case of the ``UrlMap`` above the final endpoint would be something like::

    http://my-tethys-portal.com/apps/my-first-app/my-demo-controller/


In this case Tethys just uses the ``name`` of the function as the name of the ``UrlMap`` and a modified version of the name (just replacing ``_`` with ``-``) for the ``url``.

If you want to customize either the ``name`` or the ``url`` then you can provide them as key-word arguments to the ``controller`` decorator::

  @controller(
    name='demo',
    url='demo/url/',
  )
  def my_demo_controller(request):
    ...

which will result in the following ``UrlMap``::

  UrlMap(
    name='demo',
    url='demo/url/',
    controller='my_first_app.controllers.my_demo_controller',
  )

.. note::
  The ``index`` attribute of your app class (defined in ``app.py``) specifies the name of the URL that should serve as the index route for your app. When the URL whose ``name`` attribute matches the ``index`` is registered, the ``url`` attribute of the ``UrlMap`` is overridden to be the ``root_url`` of your app.

  For example, normally the full URL endpoint for the ``'demo'`` URL above would be::

    http://my-tethys-portal.com/apps/my-first-app/demo/url/

  However, if the ``index`` attribute in ``app.py`` were set to ``'demo'`` then the ``url`` would be overridden and the endpoint would be::

    http://my-tethys-portal.com/apps/my-first-app/


The ``controller`` decorator also accepts many other arguments that modify the behavior of the controller. For example the ``permissions_required`` argument lets you specify permissions that a user is required to have to access the URL. Or the ``app_workspace`` argument will pass in a reference to the app's workspace directory as an argument to the function. The full list of arguments that the ``controller`` decorator accepts are documented below.

.. automodule:: tethys_apps.base.controller
   :members: controller

.. _websockets:

Websockets
----------

Tethys Platform supports WebSocket connections using `Django Channels <https://channels.readthedocs.io/en/latest/>`_. The Websocket protocol provides a persistent connection between the client and the server. In contrast to the traditional HTTP protocol, the websocket protocol allows for bidirectional communication between the client and the server (i.e. the server can trigger a response without the client sending a request). Django Channels uses Consumers to structure code and handle client/server communication in a similar way Controllers are used with the HTTP protocol.

.. note::
    For more information about Django Channels and Consumers visit `the Django Channels docummentation <https://channels.readthedocs.io/en/latest/>`_.

.. note::
    For more information on establishing a WebSocket connection see `the JavaScript WebSocket API <https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/>`_. Alternatively, other existing JavaScript or Python WebSocket clients can be used.

.. tip::
    To create a URL mapping using the WebSocket protocol see the :ref:`consumer-decorator`.

.. tip::
    For an example demonstrating all the necessary components to integrating websockets into your app see :doc:`../tutorials/websockets`.


.. _consumer-decorator:

Consumer Decorator
------------------
The ``consumer`` decorator functions largely the same way as the ``controller`` decorator except that it is used to decorate a consumer class, which must be a subclass of either ``channels.consumer.AsyncConsumer`` or ``channels.consumer.SyncConsumer`` (see the `Channels Consumers Documentation <https://channels.readthedocs.io/en/latest/topics/consumers.html#consumers>`_). Also, when the ``consumer`` decorator is used it will register a URL mapping with the :ref:`websocket <websockets>` protocol.

The ``consumer`` decorator is somewhat more simple than the ``controller`` decorator. It's usage is documented below.

.. automodule:: tethys_apps.base.controller
   :members: consumer
   :noindex:


.. _bokeh_integration:

Bokeh Integration
-----------------

Bokeh Integration in Tethys takes advantage of :ref:`websockets` and ``Django Channels`` to leverage Bokeh's flexible architecture. In particular, the ability to sync model objects to the client allows for a responsive user interface that can receive updates from the server using Python. This is referred to as ``Bokeh Server`` in the `Bokeh Documentation <https://docs.bokeh.org/en/latest/docs/user_guide/server.html>`_.

.. note::

    Interactive ``Bokeh`` visualization tools can be entirely created using only Python with the help of ``Bokeh Server``. However, this usually requires the use of an additional server (``Tornado``). One of the alternatives to ``Tornado`` is using ``Django Channels``, which is already supported with Tethys. Therefore, interactive ``Bokeh`` models along with the all the advantages of using ``Bokeh Server`` can be leveraged in Tethys without the need of an additional server.

Even though Bokeh uses :ref:`websockets`, routing with Bokeh endpoints is handled differently from other :ref:`websockets` that would normally be handled by a ``Consumer`` class and use the :ref:`consumer-decorator`. In contrast, Bokeh endpoints use a ``handler`` function that contains the main logic needed for a Bokeh model to be displayed. It contains the model or group of models as well as the callback functions that will help link them to the client. A ``handler`` function should be registered with the :ref:`handler-decorator`. Note that the :ref:`handler-decorator` supports both synchronous and asynchronous functions.

``Handlers`` are added to the ``Bokeh Document``, the smallest serialization unit in ``Bokeh Server``. This same ``Document`` is retrieved and added to the template variables in a ``controller`` function that is linked to the ``Handler function`` using Bokeh's ``server_document`` function. The ``controller`` function is created and registered automatically with the :ref:`handler-decorator`. However, you can manually create a ``controller`` function if custom logic is needed. In this case the ``controller`` function should not be decorated, but rather passed in as an argument to the :ref:`handler-decorator`.

A ``Bokeh Document`` comes with a ``Bokeh Request``. This request contains most of the common attributes of a normal ``HTTPRequest``, and can be easily converted to an ``HTTPRequest`` using the ``with_request`` argument in the :ref:`handler-decorator`. Similarly, the ``with_workspaces`` argument can be used to add ``user_workspace`` and ``app_workspace`` to the ``Bokeh Document``. This latter argument will also convert the ``Bokeh Request`` of the ``Document`` to an ``HTTPRequest``, meaning it will do the same thing as the ``with_request`` argument in addition to adding workspaces.

.. important::

    To use the ``handler`` decorator you will need the ``bokeh`` and ``bokeh-django`` packages which may not be installed by default. They can be installed with:

    .. code-block:: bash

        conda install -c conda-forge -c erdc/label/dev bokeh bokeh-django

.. tip::
    For more information regarding Bokeh Server and available models visit the `Bokeh Server Documentation <https://docs.bokeh.org/en/latest/docs/user_guide/server.html>`_ and the `Bokeh model widgets reference guide <https://docs.bokeh.org/en/latest/docs/reference/models.html>`_.

.. _handler-decorator:

Handler Decorator
-----------------

.. automodule:: tethys_apps.base.controller
   :members: handler
   :noindex:

.. tip::
    For a more in-depth example of how to use Bokeh with Tethys see the :ref:`bokeh-tutorial`.

.. _controller-search-path:

Search Path
-----------

In a Tethys app the controllers are usually defined in the ``controllers.py`` module. If your app includes consumers then they should be defined in a ``consumers.py`` module. Tethys will automatically search both the ``controllers.py`` and ``consumers.py`` modules to find any functions or classes that have been decorated with the either ``controller`` or the ``consumer`` decorators and register them. If you have many controllers or consumers and want to organize them in multiple modules then you can convert the ``controllers.py`` or the ``consumers.py`` modules into packages with the same name (a directory named either ``controllers`` or ``consumers`` with an ``__init__.py`` and other Python modules in it).

For existing apps with controllers located in modules with different names than these defaults, it is recommended to move the modules into a package named either ``controllers`` or ``consumers`` as described above. However, you may also use the ``controller_modules`` property of the :term:`app class` to define addtiional controller search locations. For example:

.. code-block:: python

    class App(TethysAppBase):
        ...
        controller_modules = [
            'custom_controllers',  # For a module named custom_controller.py in the same directory as app.py
            'rest',  # For a package named "rest" in the same directory as app.py containing modules with controllers
        ]

.. _class_based_controllers:

Class-Based Controllers
-----------------------

.. automodule:: tethys_apps.base.controller
   :members: TethysController
   :noindex:

.. _URL Maps:

URL Maps
--------
Under the hood, Tethys creates a ``UrlMap`` object that maps the URL endpoint to the controller or consumer that will handle the request. When using the ``controller`` or ``consumer`` decorators the ``UrlMap`` objects are created automatically. However, if you have a need to manually modify the list of registered ``UrlMap`` objects for your app then you can do so by overriding the :ref:`register_url_maps <register-url-maps-method>` method in the ``app.py`` file.

Tethys usually manages ``url_maps`` from the ``app.py`` file of each individual app using a ``UrlMap`` constructor. This constructor normally accepts a ``name``, a ``url``, and a ``controller``. However, there are other parameters such as ``protocol``, ``regex``, ``handler``, and ``handler_type``. This section provides information on how to use the ``url_maps`` API.

URL Maps Contructor
-------------------

.. autoclass:: tethys_apps.base.url_map.UrlMapBase
   :members:

   .. automethod:: __init__

.. _register-url-maps-method:

Register URL Maps Method
------------------------

The ``register_url_maps`` method is tightly related to the App Base Class API.

.. automethod:: tethys_apps.base.app_base.TethysBase.register_url_maps
   :noindex:

Register Controllers
--------------------

.. automodule:: tethys_apps.base.controller
   :members: register_controllers
   :noindex:
