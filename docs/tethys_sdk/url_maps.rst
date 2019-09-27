************
URL Maps API
************

**Last Updated:** September 2019

A ``UrlMap`` is a mapping between a URL and a function or class that is responsible for handling a request. When a request is submitted to Tethys, it matches the URL of that request against a list of ``UrlMaps`` and calls the function or class that the matching ``UrlMap`` points to.

Tethys usually manages ``url_maps`` from the ``app.py`` file of each individual app using a ``UrlMap`` constructor. This constructor normally accepts a ``name``, a ``url``, and a ``controller``. However, there are other parameters such as ``protocol``, ``regex``, ``handler``, and ``handler_type``. This section provides information on how to use the ``url_maps`` API.

URL Maps Contructor
-------------------

.. autoclass:: tethys_apps.base.url_map.UrlMapBase
   :members:

   .. automethod:: __init__

URL Maps Methods
----------------

The ``url_maps`` methods is tightly related to the App Base Class API.

.. automethod:: tethys_apps.base.app_base.TethysBase.url_maps
   :noindex:

Websockets
----------

Tethys Platform supports WebSocket connections using `Django Channels <https://channels.readthedocs.io/en/latest/>`_. The WebSocket protocol provides a persistent connection between the client and the server. In contrast to the traditional HTTP protocol, the webscoket protocol allows for bidirectional communication between the client and the server (i.e. the server can trigger a response without the client sending a request). Django Channels uses Consumers to structure code and handle client/server communication in a similar way Controllers are used with the HTTP protocol.

.. note::
    For more information about Django Channels and Consumers visit `the Django Channels docummentation <https://channels.readthedocs.io/en/latest/>`_.

.. note::
    For more information on establishing a WebSocket connection see `the JavaScript WebSocket API <https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/>`_. Alternatively, other existing JavaScript or Python WebSocket clients can we used.

.. tip::
    To create a URL mapping using the WebSocket protocol see the example provided in the `App Base Class API documentation <./tethys_sdk/url_maps.html#url-maps-method>`_.

.. tip::
    For an example demonstrating all the necessary components to integrating websockets into your app see `This Websockets Tutorial <./tutorials/getting_started/websockets.html>`_.

.. _bokeh_integration:

Bokeh Integration
-----------------

Bokeh Integration in Tethys takes advantage of ``Websockets`` and ``Django Channels`` to leverage Bokeh's flexible architecture. In particular, the ability to sync model objects to the client allows for a responsive user interface that can receive updates from the server using Python. This is referred to as ``Bokeh Server`` in the `Bokeh Documentation <https://bokeh.pydata.org/en/latest/docs/user_guide/server.html>`_.

Tethys facilitates the use of the ``Bokeh Server`` component of ``Bokeh`` by taking care of creating the routings necessary to link the models and the front end bokeh models. This is done by providing a ``handler`` in addition that the other common parameters in a ``UrlMap``.

.. note::

    Interactive ``Bokeh`` visualization tools can be entirely created using only Python with the help of ``Bokeh Server``. However, this usually requires the use of an additional server (``Tornado``). One of the alternatives to ``Tornado`` is using ``Django Channels``, which is already supported with Tethys. Therefore, interactive ``Bokeh`` models along with the all the advantages of using ``Bokeh Server`` can be leveraged in Tethys without the need of an additional server.

.. code-block:: python

    class MyFirstApp(TethysAppBase):

        def url_maps(self):
            """
            Example url_maps method.
            """
            # Create UrlMap class that is bound to the root url.
            UrlMap = url_map_maker(self.root_url)

            url_maps = (

                ...

                UrlMap(name='bokeh_handler',
                    url='my-first-app/bokeh-example',
                    controller='my_first_app.controllers.bokeh_example',
                    handler='my_first_app.controllers.bokeh_example_handler',
                    handler_type='bokeh'
                ),
            )

            return url_maps

A ``Handler`` in this context represents a function that contains the main logic needed for a Bokeh model to be displayed. It contains the model or group of models as well as the callback functions that will help link them to the client. ``Handlers`` are added to the ``Bokeh Document``, the smallest serialization unit in ``Bokeh Server``. This same ``Document`` is later retrieved and added to the template variables in the ``Controller`` that will be linked to the ``Handler function`` using Bokeh's `server_document` function.

A ``Bokeh Document comes with a ``Bokeh Request``. This request contains most of the common attibutes of a normal ``HTTPRequest``, and can be easily converted to HTTP using the ``with_request`` decorator from ``tethys_sdk.base``. A second handler decorator named ``with_workspaces`` can be used to add ``user_workspace`` and ``app_workspace`` to the ``Bokeh Document``. This latter decorator will also convert the ``Bokeh Request`` of the ``Document`` to an ``HTTPRequest, meaning it will do the same thing as the ``with_request`` decorator besides adding workspaces.

The example below adds a column layout containing a slider and a plot. A callback function linked to the slider value change event and a demonstration of how to use the ``with_workspaces`` decorator are also included.

.. code-block:: python

    from tethys_sdk.base import with_workspaces

    ...

    @with_workspaces
    def home_handler(doc):
        # create data source for plot
        data = {'x': [0, 1, 2, 3], 'y': [0, 10, 20, 30]}
        source = ColumnDataSource(data=data)

        # create plot
        plot = figure(x_axis_type="linear", y_range=(0, 30), title="Bokeh Plot")
        plot.line(x="x", y="y", source=source)

        # callback function
        def callback(attr: str, old: Any, new: Any) -> None:
            if new == 1:
                data['y'] = [0, 10, 20, 30]
            else:
                data['y'] = [i * new for i in [0, 10, 20, 30]]
            source.data = ColumnDataSource(data=data).data
            plot.y_range.end = max(data['y'])

        # create slider and add callback to it
        slider = Slider(start=1, end=5, value=1, step=1, title="Bokeh Slider")
        slider.on_change("value", callback)

        # attributes available when using "with_workspaces" decorator
        request = doc.request
        user_workspace = doc.user_workspace
        app_workspace = doc.app_workspace

        # add layout with bokeh models to document
        doc.add_root(column(slider, plot))

The ``controller`` from the same ``UrlMap`` where the ``handler`` is defined needs to provide a mechanism to load the ``Bokeh`` models to the client.

.. code-block:: python

    def home(request):

        ...

        script = server_document(request.build_absolute_uri())

        context = {
            'script': script
        }

        return render(request, 'test_app/home.html', context)

.. tip::
    For more information regarding Bokeh Server and available models visit the `Bokeh Server Documentation <https://bokeh.pydata.org/en/latest/docs/user_guide/server.html>`_ and the `Bokeh model widgets reference guide <https://bokeh.pydata.org/en/latest/docs/reference/models.html#bokeh-models>`_.
