*********************************
Bokeh Server Integration Concepts
*********************************

**Last Updated:** September 2019

This tutorial introduces ``Bokeh Server`` integration concepts for Tethys developers. Two ``bokeh`` handlers will be
created to demonstrate how to link Bokeh plots or widgets to Python functions in the brackground using both a plain
Bokeh approach as well as a ``Param`` approach. The topics covered include:

* Bokeh Server
* Handlers
* Param

Create a new Tethys app named bokeh_server_tutorial.

::

    $ tethys scaffold bokeh_server_tutorial

1. Bokeh Server
===============

``Bokeh`` is an interactive visualization library for Python. ``Bokeh Server`` is a component of the ``Bokeh``
architecture. It provides a way to sync model objects from Python to the client. This is done by levering the
``Websocket`` protocol. With the addition of ``Django Channels`` to Tethys, this ability to sync python objects and
frontend plots has also been integrated. This integration facilitates the linking of objects and Bokeh widgets as well
as the creation of the necessary ``websocket`` and ``http`` ``consumers``.

The logic for creating a Bokeh widget along with other related functionality is provided in a ``handler function``.
This handler will be associated to a specific ``controller function`` where the resulting Bokeh widget will be
displayed in a later step.

a. Create a handler function on the ``controller.py`` on top of the default home function.

.. code-block:: Python

    ...

    def home_handler(document):
        pass

Let's use Bokeh's sea temperature sample data to create a time series plot and link it to a slider that will provide
the value to perform a rolling-window analysis on the time series. This a common example use in Bokeh's main
documentation.

b. Add the following imports to ``controller.py`` and logic to the handler created in (a).

.. code-block:: Python

    from bokeh.plotting import figure
    from bokeh.models import ColumnDataSource
    from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature

    ...

    def home_handler(document):
        df = sea_surface_temperature.copy()
        source = ColumnDataSource(data=df)

        plot = figure(x_axis_type="datetime", y_range=(0, 25), y_axis_label="Temperature (Celsius)",
                      title="Sea Surface Temperature at 43.18, -70.43")
        plot.line("time", "temperature", source=source)

        doc.add_root(plot)

c. Clear the default home function in ``controller.py`` and add the following code to it.

.. code-block:: Python
    from bokeh.embed import server_document

    ...

    def home(request):
        script = server_document(request.build_absolute_uri())
        context = {'script': script}
        return render(request, 'bokeh_server_tutorial/home.html', context)

Start Tethys from the terminal and go to the bokeh_server_tutorial app's home page. It should look like this:

.. figure:: ../images/tethys_portal_landing.png
    :width: 650px





.. note::

    The controller parameter of the ``UrlMap`` is pointing to the consumer added in the previous step. A new ``protocol parameter`` with a string value equal to `websocket` has been added to the ``UrlMap``.

2. WebSocket Connections
========================

A ``handshake`` needs to be established between the client and server when creating a ``WebSocket connection``. We will use the standard ``JavaScript WebSocket API`` to do this.

Create a ``WebSocket connection`` by adding the following code to the ``home.html`` template after the ``app_content`` block.

.. code-block:: html+django

    ...

    {% block app_content %}
      {% gizmo dam_inventory_map %}
      <div id="popup"></div>
    {% endblock %}

    {% block after_app_content %}
      <script>
        var notification_ws = new WebSocket('ws://' + window.location.host + '/ws/dam-inventory/dams/notifications/');
      </script>
    {% endblock %}

    ...

A ``WebSocket URL`` follows a pattern similar to tethys app ``HTTP URLs``. The differences being that the URL starts with ``ws://`` instead of ``http(s)://``, and the "apps" part of the URL in between the host and the app name is substituted with a "ws". For example: ws://tethys.host.com/ws/base-app-name/base-ws-url. If the base name of the app is included in the ``WebSocket URL``, it will not be duplicated. This is the same behavior for ``HTTP URLs``.

Upon loading the app home page, the "WebSocket Connected" message will be printed to the terminal. The ``WebSocket connection`` can also be accessed from the browser by right-clicking and selecting inspect, network and filtering by "WS" as displayed in the image below.

.. image:: ../../images/tutorial/advanced/ws-conn-browser.png
   :width: 600px
   :align: center

3. Channel Layers
=================

A ``channel layer`` is needed for two or more app instances to communicate between each other (e.g. two different users interacting with the same app at the same time). A ``channel layer`` provides a backend where ``WebSocket messages`` can be stored and then accessed by the different app instances. The updated ``consumer`` in this step opens a communication link (channel_name) in the "notification" channel group on connect, and closes it on disconnect. A new async function has also been added to handle messages.

a. Update the ``consumer class`` from step (1.a) to look like this.

::

    ...

    import json

    ...

    class notificationsConsumer(AsyncWebsocketConsumer):
        async def connect(self):
            await self.accept()
            await self.channel_layer.group_add("notifications", self.channel_name)
            print(f"Added {self.channel_name} channel to notifications")

        async def disconnect(self, close_code):
            await self.channel_layer.group_discard("notifications", self.channel_name)
            print(f"Removed {self.channel_name} channel from notifications")

        async def dam_notifications(self, event):
            message = event['message']
            await self.send(text_data=json.dumps({'message': message}))
            print(f"Got message {event} at {self.channel_name}")

The respective print messages set on connect and disconnect will appear in the terminal when the app home is opened or closed.

b. ``Channel layers`` require a backend to store the ``WebSocket messages`` coming from different app instances. These messages can be stored in memory. Add the following peace of code to tethys' ``settings.py``.

::

    ...

    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer'
        },
    }

.. note::

    ``Django Channels`` recommends the use of an external backend store for production environments. The ``channels-redis`` python package plus ``Redis Server`` are the default recommendation. For more information see ``Django Channels`` `channel layers <https://channels.readthedocs.io/en/latest/topics/channel_layers.html>`_ and `deploying <https://channels.readthedocs.io/en/latest/deploying.html>`_ sections.

.. tip::
    A ``Channel layer`` can be added to the settings.py using the ``tethys gen settings --channel-layer`` followed by the python dot-formatted path of the channel layer. See ``tethys gen settings --help`` for details.

Channel Layer Definitions
-------------------------

+---------------+-----------------------------------------------+
| Term          | Simplified definition                         |
+===============+===============================================+
| channel name  | Communication link unique to an app instance. |
+---------------+-----------------------------------------------+
| channel group | Communication link for different app          |
|               | instances to talk to each other.              |
+---------------+-----------------------------------------------+
| channel layer | The mechanism that enables communication      |
|               | between different app instances.              |
+---------------+-----------------------------------------------+
| channel layer | A backend database to store group messages.   |
| backend       |                                               |
+---------------+-----------------------------------------------+

4. New Dam Notification
=======================

Now that we have a working ``WebSocket connection`` and a communication backend is set, let's add the programming logic.

a. Add the following code to the ``add_dam controller`` in ``controllers.py``.

::

    ...

    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    ...

    def add_dam(request):

    ...

        new_num_dams = session.query(Dam).count()

        if new_num_dams > num_dams:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "notifications", {
                    "type": "dam_notifications",
                    "message": "New Dam"
                }
            )

        return redirect(reverse('dam_inventory:home'))

    messages.error(request, "Please fix errors.")

This piece of code checks to see if a new dam has been added and if so it sends a message to the notification group. Notice that the type of the group message is ``dam_notifications``; this is the same consumer function defined in step (3.a) and therefore the print message assigned to this function will appear on the terminal when the condition is triggered and the message is sent.

.. note::

    ``Channel layers`` can easily be accessed from within a consumer by calling ``self.channel_layer``. From outside the ``consumer`` they can be called with ``channels.layers.get_channel_layer``.

.. note::

    ``Channel layers`` are purely ``asynchronous`` so they need to be wrapped in a converter like ``async_to_sync`` to be used from synchronous code.

b. Let's create a message box to display our notification when a new app is added. Add the following code to the ``home controller`` in ``controllers.py``.

::

    ...

    from tethys_sdk.gizmos import (MapView, Button, TextInput, DatePicker, SelectInput, DataTableView, MVDraw, MVView,
                                   MVLayer, MessageBox)

    ...

    def home(request):

    ...

        message_box = MessageBox(name='notification',
                                 title='',
                                 dismiss_button='Nevermind',
                                 affirmative_button='Refresh',
                                 affirmative_attributes='onClick=window.location.href=window.location.href;')

        context = {
            'dam_inventory_map': dam_inventory_map,
            'message_box': message_box,
            'add_dam_button': add_dam_button,
            'can_add_dams': has_permission(request, 'add_dams')
        }

        return render(request, 'dam_inventory/home.html', context)

    ...


This ``gizmo`` creates an empty message box with a current page refresh. It will be populated in the next step based on our ``WebSocket connection``.

c. Now that the logic has been added, lets add the tethys ``message box gizmo`` and modify the ``WebSocket connection`` from step (2) to listen for any ``New Dam`` messages and populate our message box accordingly. Update the code in home.html as follows.

.. code-block:: html+django

    ...

    {% block app_content %}
      {% gizmo dam_inventory_map %}
      <div id="popup"></div>
    {% endblock %}

    {% block after_app_content %}
    {% gizmo message_box %}
      <script>
        var notification_ws = new WebSocket('ws://' + window.location.host + '/ws/dam-inventory/dams/notifications/');
        var n_div = $("#notification");
        var n_title = $("#notificationLabel");
        var n_content = $('#notification .lead');

        notification_ws.onmessage = function (e) {
          var data = JSON.parse(e.data);
          if (data["message"] = "New Dam") {
            n_title.html('Dam Notification');
            n_content.html('A new dam has been added. Refresh this page to load it.');
            n_div.modal();
          }
        };
      </script>
    {% endblock %}

Besides the ``message_box gizmo``, a simple ``JavaScript`` conditional has been added to display and populate the message box if the message our ``WebSocket connection`` listened for is equal to ``New Dam``.

Test the ``WebSocket communication`` by opening two instances of the dam inventory app at the same time. Add a dam in one instance, a message box will display on the home of the other instance suggesting a refresh to display the newly added dam.

.. note::

    Other ``WebSockets`` could be added to the app as a way of practice. For example: another message box when a hydrograph has been added to a dam.

5. Solution
===========

This concludes the WebSockets tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-dam_inventory>`_ or clone it as follows:

::

    $ git clone https://github.com/tethysplatform/tethysapp-dam_inventory.git
    $ cd tethysapp-dam_inventory
    $ git checkout websocket-solution
