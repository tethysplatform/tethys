************
URL Maps API
************

**Last Updated:** September 2019

Tethys usually manages url maps from the ``app.py`` file of each individual app using a url map constructor. This
constructor normally accepts a ``name``, a ``url``, and a ``controller``. However, there are other parameters such as
``protocol``, ``regex``, ``handler``, and ``handler_type``. This section provides information on how to use the url
maps API.

URL Maps Contructor
-------------------

.. autoclass:: tethys_apps.base.url_map.UrlMapBase
   :members:

   .. automethod:: __init__

URL Maps Function
-----------------

The ``url_maps`` function is tightly related to the App Base Class API.

.. automethod:: tethys_apps.base.app_base.TethysBase.url_maps
   :noindex:

Websockets
----------

Tethys Platform supports WebSocket connections using `Django Channels
<https://channels.readthedocs.io/en/latest/index.html/>`_. The WebSocket protocol provides as persistent connection
between client and server. In contrast to the traditional HTTP protocol, the webscoket protocol allows for
bidirectional communication between client and server (i.e. the server can trigger a response without the client
sending a request). Django Channels uses Consumers to structure code and handle client/server communication in a s
imilar way Controllers are used with the HTTP protocol.

.. note::
    For more information about Django Channels and Consumers visit
    `the Django Channels docummentation <https://channels.readthedocs.io/en/latest/>`_.

.. note::
    For more information on establishing a WebSocket connection see
    `the JavaScript WebSocket API <https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/>`_. Alternatively, other existing JavaScript or Python WebSocket clients can we used.

.. tip::
    To create a URL mapping using the WebSocket protocol see the example provided in the
    `App Base Class API documentation <./tethys_sdk/url_maps.html#url-maps-function>`_.

.. tip::
    For an example demonstrating all the necessary components to integrating websockets into you app see `This
    Websockets Tutorial <./tutorials/getting_started/websockets.html>`_.

Bokeh Server Integration
------------------------

Bokeh Server Integration in Tethys takes advantage of ``Websockets`` and ``Django Channels`` to leverage Bokeh's
flexible architecture. In particular, the ability to sync model objects to the client allows for a responsive user
interface that can receive updates from the server using Python.

Tethys facilitates the use of ``Bokeh Server`` by taking care of creating the routings necessary to link the models
and the front end bokeh widgets. This is done by providing a ``handler`` in addition that the other common parameters
in a ``UrlMap``.

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

A handler in this context represents a function that contains the main logic needed for a Bokeh widget to be displayed.
It contains the widget or group of widgets as well as the callback functions that will help link them to the client.

The example below adds a column layout containing a slider and a plot widget. A callback function linked to the
slider value change event is also included.

.. code-block:: python

    def home_handler(doc):
        data = {'x': [0, 1, 2, 3], 'y': [0, 10, 20, 30]}
        source = ColumnDataSource(data=data)

        plot = figure(x_axis_type="linear", y_range=(0, 30), title="Bokeh Plot")
        plot.line(x="x", y="y", source=source)

        def callback(attr: str, old: Any, new: Any) -> None:
            if new == 1:
                data['y'] = [0, 10, 20, 30]
            else:
                data['y'] = [i * new for i in [0, 10, 20, 30]]
            source.data = ColumnDataSource(data=data).data
            plot.y_range.end = max(data['y'])

        slider = Slider(start=1, end=5, value=1, step=1, title="Bokeh Slider")
        slider.on_change("value", callback)

        doc.add_root(column(slider, plot))

The ``controller`` from the same ``UrlMap`` where the ``handler`` is defined needs to provide a mechanism to load the
``Bokeh`` widgets to the client.

.. code-block:: python

    def home(request):

        ...

        script = server_document(request.build_absolute_uri())

        context = {
            'script': script
        }

        return render(request, 'test_app/home.html', context)

.. tip::
    For more information regarding Bokeh Server and available widgets visit the `Bokeh Server Documentation
    <https://bokeh.pydata.org/en/latest/docs/user_guide/server.html>`_ and the `Bokeh model widgets reference guide
    <https://bokeh.pydata.org/en/latest/docs/reference/models.html#bokeh-models>`_.
