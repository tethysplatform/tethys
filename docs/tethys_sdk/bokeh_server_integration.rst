****************************
Bokeh Server Integration API
****************************

**Last Updated:** September 2019

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

The ``url_maps`` documentation below provides more detail regarding the use of ``Bokeh handlers`` as well as other
related functionality.

.. automethod:: tethys_apps.base.app_base.TethysBase.url_maps
   :noindex:

.. tip::
    For more information regarding Bokeh Server and available widgets visit the `Bokeh Server Documentation
    <https://bokeh.pydata.org/en/latest/docs/user_guide/server.html>`_ and the `Bokeh model widgets reference guide
    <https://bokeh.pydata.org/en/latest/docs/reference/models.html#bokeh-models>`_.
