.. _bokeh-tutorial:

**************************
Bokeh Integration Concepts
**************************

**Last Updated:** July 2024

This tutorial introduces ``Bokeh Server`` integration concepts for Tethys developers. Two ``bokeh`` handlers will be created to demonstrate how to link Bokeh plots or widgets to Python functions in the brackground using both a plain Bokeh approach as well as a ``Param`` approach. The topics covered include:

* Bokeh Server
* Handler functions using Bokeh Widgets
* Handler functions using Param and Panel

Create and install a new Tethys app named bokeh_tutorial in your :ref:`virtual_environment`.

::

    tethys scaffold bokeh_tutorial
    cd tethysapp-bokeh_tutorial
    tethys install -d

1. Bokeh Server
===============

``Bokeh`` is an interactive visualization library for Python. ``Bokeh Server`` is a component of the ``Bokeh`` architecture. It provides a way to sync model objects in Python on the backend to JavaScript model objects on the client. This is done by leveraging the ``Websocket`` protocol. With the addition of ``Django Channels`` to Tethys, this ability to sync backend python objects and frontend plots has also been integrated without the need of other components such as a ``Tornado`` server (see the Tethys Bokeh Integration documentation :ref:`bokeh_integration`). This integration facilitates the linking of objects and ``Bokeh`` widgets as well as the creation of the necessary ``websocket`` and ``http`` ``consumers``.

To leverage the Bokeh integration with Tethys you will need the ``bokeh`` and ``bokeh-django`` libraries.

1. Install the ``bokeh`` and ``bokeh-django`` libraries by running one of the following commands with your Tethys environment activated:

.. code-block:: bash

    # conda: conda-forge channel strongly recommended for bokeh (the erdc/label/dev channel is currently needed for bokeh-django)
    conda install -c conda-forge -c erdc/label/dev bokeh bokeh-django bokeh_sampledata

    # pip
    pip install bokeh bokeh-django bokeh_sampledata

2. Add the new dependencies to your :file:`install.yml` as follows so that the app will work when installed in a new environment:

.. code-block:: yaml

    # This file should be committed to your app code.
    version: 1.0
    # This should match the app - package name in your setup.py
    name: bokeh_tutorial

    requirements:
      # Putting in a skip true param will skip the entire section. Ignoring the option will assume it be set to False
      skip: false
      conda:
        channels:
          - conda-forge
        packages:
          - bokeh
          - bokeh-django
          - bokeh_sampledata

      pip:

    post:

The logic for creating a Bokeh widget along with other related functionality is provided in a ``handler function``. This handler will be associated to a specific ``controller function`` where the resulting Bokeh widget will be displayed in a later step.

2. Handler Functions Using Bokeh Widgets
========================================

Let's use Bokeh's sea temperature sample data to create a time series plot and link it to a slider that will provide the value to perform a rolling-window analysis on the time series. This example is based on a similar example in Bokeh's main documentation.

1. Create a ``handler function`` by adding the following imports and logic to ``handlers.py``.

.. code-block:: Python

    from bokeh.plotting import figure
    from bokeh.models import ColumnDataSource
    from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature

    from tethys_sdk.routing import handler

    from .app import App


    @handler(
        template=f"{App.package}/home.html",
    )
    def home(document):
        df = sea_surface_temperature.copy()
        source = ColumnDataSource(data=df)

        plot = figure(x_axis_type="datetime", y_range=(0, 25), y_axis_label="Temperature (Celsius)",
                      height=500, width=800, title="Sea Surface Temperature at 43.18, -70.43")
        plot.line("time", "temperature", source=source)

        document.add_root(plot)

This simple handler contains the logic for a time series plot of the sea surface temperature sample data provided by ``Bokeh``. The ``handler`` decorator marks this function as a handler. It auto generates a default ``controller function`` that is linked to the handler. A default template can also be used, but we specified a custom template using the ``template`` argument to the ``handler`` decorator. The ``handler`` decorator also sets up the routing. By default the route name and the URL are derived from the ``handler function`` name (in this case ``home``). For more information about the ``handler`` decorator and additional arguments that can be passed see :ref:`handler-decorator`. Since this default controller is sufficient, we don't need to create a custom controller and can just delete the ``controller.py`` file.

2. Delete the ``controllers.py`` file.

3. Clear the default ``home.html`` template and add the following code to it.

.. code-block:: html+django

    {% extends tethys_app.package|add:"/base.html" %}

    {% block app_content %}
      <h1>Bokeh Integration Example</h1>
      {{ script|safe }}
    {% endblock %}

As you can see, a ``script`` context variable has been added to the app_content block. The default ``controller function`` defines this script which handles loading the content specified in the ``handler function``. We customized the template by adding in a heading which will render above the content from the ``handler function``.

If you start tethys and go to the home page of this app you should see something like this:

.. figure:: ../images/tutorial/bokeh_integration/bokeh_integration_1.png
    :width: 650px

This is a simple Bokeh plot. We will now add the rest of the logic to make it an interactive plot. We will add a ``Slider`` widget. Then, we will create a callback function to modify the time-series plot based on the slider. Finally, we will add both our plot and slider to the document tree using a ``Column`` layout.

5. Modify the ``handler function`` from ``handlers.py`` to look like this.

.. code-block:: python
    :emphasize-lines: 1-2, 17-28

    from bokeh.models import ColumnDataSource, Slider
    from bokeh.layouts import column

    ...

    @handler(
        template=f"{App.package}/home.html",
    )
    def home(document):
        df = sea_surface_temperature.copy()
        source = ColumnDataSource(data=df)

        plot = figure(x_axis_type="datetime", y_range=(0, 25), y_axis_label="Temperature (Celsius)",
                      height=500, width=800, title="Sea Surface Temperature at 43.18, -70.43")
        plot.line("time", "temperature", source=source)

        slider = Slider(start=0, end=30, value=0, step=1, title="Smoothing by N Days")

        def callback(attr, old, new):
            if new == 0:
                data = df
            else:
                data = df.rolling(f'{new}D').mean()
            source.data = dict(ColumnDataSource(data=data).data)

        slider.on_change("value", callback)

        document.add_root(column(slider, plot))

If you start tethys and go to the home page of this app you should see something like this:

.. figure:: ../images/tutorial/bokeh_integration/bokeh_integration_2.png
    :width: 650px

The ``Slider`` and ``Plot`` will appear in the order they were added to the ``Column`` layout. If the value of the ``Slider`` changes, the data in the ``Plot`` will reflect this change based on this expression: `data = df.rolling(f'{new}D').mean()`. Where `df` is the sample data and `new` is the new ``Slider`` value.


3. Handler Functions Using Param and Panel
==========================================

``Param`` is a Python library for providing parameters with dynamically generated values. One of the main advantages of ``Param`` is that parameters are provided using declarative programming. ``Panel``, on the other hand, is a visualization library for creating custom dashboards that rely on the use of widgets to render plots, images, and tables. These libraries can be used in combination with ``Bokeh Server`` to attain the same result of creating interactive tools within an app that are connected to Python objects. Given the depth of these libraries, the resulting code structure, and the level of difficulty for creating complex visualizations may be simplified.

In this example we will build on top of the ``bokeh_tutorial`` app to demonstrate how to use ``Param`` and ``Panel`` in combination with ``bokeh Server``. This same example can be found in `Panel's documentation <https://panel.holoviz.org/how_to/param/examples/subobjects.html#param-subobjects>`_.

1. Install the ``param`` and ``panel`` libraries by running the following with your Tethys environment activated:

.. code-block:: bash

    conda install -c conda-forge panel param

2. Add the new dependencies to your :file:`install.yml` as follows so that the app will work when installed in a new environment:

.. code-block:: yaml

    packages:
      ...
      - panel
      - param


.. warning::

    The current versions of ``panel`` and ``param`` may not function properly with the following sections of this tutorial. If you encounter issues,
    consider installing specific versions using one of the following commands:

    .. code-block:: bash

        conda install -c conda-forge panel=1.3.8 param=2.0.2 bokeh=3.3.4

    .. code-block:: bash

        pip install panel==1.3.8 param==2.0.2 bokeh==3.3.4

    For best results, make sure your python version is 3.12 or lower.

3. Add the following objects to a new file called ``param_model.py``.

.. code-block:: python

    import param
    import panel as pn
    import numpy as np
    from bokeh.plotting import figure


    class Shape(param.Parameterized):
        radius = param.Number(default=1, bounds=(0, 1))

        def __init__(self, **params):
            super(Shape, self).__init__(**params)
            self.figure = figure(x_range=(-1, 1), y_range=(-1, 1), width=500, height=500)
            self.renderer = self.figure.line(*self._get_coords())

        def _get_coords(self):
            return [], []

        def view(self):
            if not self.figure.renderers:
                self.__init__(name=self.name)
            return self.figure


    class Circle(Shape):
        n = param.Integer(default=100, precedence=-1)

        def __init__(self, **params):
            super(Circle, self).__init__(**params)

        def _get_coords(self):
            angles = np.linspace(0, 2 * np.pi, self.n + 1)
            return (self.radius * np.sin(angles),
                    self.radius * np.cos(angles))

        @param.depends('radius', watch=True)
        def update(self):
            xs, ys = self._get_coords()
            self.renderer.data_source.data.update({'x': xs, 'y': ys})


    class NGon(Circle):
        n = param.Integer(default=3, bounds=(3, 10), precedence=1)

        @param.depends('radius', 'n', watch=True)
        def update(self):
            xs, ys = self._get_coords()
            self.renderer.data_source.data.update({'x': xs, 'y': ys})


    shapes = [NGon(name='NGon'), Circle(name='Circle')]


    class ShapeViewer(param.Parameterized):
        shape = param.ObjectSelector(default=shapes[0], objects=shapes)

        @param.depends('shape')
        def view(self):
            return self.shape.view()

        @param.depends('shape', 'shape.radius')
        def title(self):
            return '## %s (radius=%.1f)' % (type(self.shape).__name__, self.shape.radius)

        @param.depends('shape')
        def controls(self):
            return pn.Param(self.shape)

        def panel(self):
            expand_layout = pn.Column()

            return pn.Column(
                pn.pane.HTML('<h1>Bokeh Integration Example using Param and Panel</h1>'),
                pn.Row(
                    pn.Column(
                        pn.panel(self.param, expand_button=False, expand=True, expand_layout=expand_layout),
                        "#### Subobject parameters:",
                        expand_layout),
                    pn.Column(self.title, self.view)
                ),
                sizing_mode='stretch_width',
            )

The added classes depend on ``Bokeh``.  The `Circle` and `NGon` classes depend on the `Shape` class, while the `ShapeViewer` allows the user to pick one of the two available shapes.

4. Add a ``handler function`` that uses the classes created in the previous step by adding the following code to ``handlers.py``.

.. code-block:: python
    :emphasize-lines: 3, 7-12

    ...

    from .param_model import ShapeViewer

    ...

    @handler(
        app_package=App.package,
    )
    def shapes(document):
        viewer = ShapeViewer().panel()
        viewer.server_doc(document)

Note that in this case we are not using a custom template, but we add the ``app_package`` argument to the the ``handler`` decorator so that the default template that Tethys uses will inherit from the ``base.html`` template from our app.

5. To add the new endpoint to the app navigation bar, go to the ``base.html`` template and replace the ``app_navigation`` block content with the code below.

.. code-block:: html+django

    {% block app_navigation_items %}
      {% url tethys_app|url:'home' as home_url %}
      {% url tethys_app|url:'shapes' as shapes_url %}
      <li class="nav-item title">Examples</li>
      <li class="nav-item"><a class="nav-link {% if request.path == home_url %}active{% endif %}" href="{{ home_url }}">Sea Surface</a></li>
      <li class="nav-item"><a class="nav-link {% if request.path == shapes_url %}active{% endif %}" href="{{ shapes_url }}">Shapes</a></li>
    {% endblock %}

If you start tethys and go to the shapes endpoint of this app you should see something like this:

.. figure:: ../images/tutorial/bokeh_integration/bokeh_integration_3.png
    :width: 650px

4. Solution
===========

This concludes the ``Bokeh Integration`` tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-bokeh_tutorial>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-bokeh_tutorial
    cd tethysapp-bokeh_tutorial
    git checkout -b solution solution-|version|
