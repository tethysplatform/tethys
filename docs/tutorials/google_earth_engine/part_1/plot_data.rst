***********************
Plot Data at a Location
***********************

**Last Updated:** July 2024

In the final tutorial you will add the ability for users to drop a point or draw a polygon and generate a time series of the selected dataset at that location. The following topics will be reviewed in this tutorial:

* Tethys MapView Gizmo Drawing API
* JQuery Load + Gizmo Strategy
* GEE Geoprocessing
* Adding New App Dependencies

.. figure:: ../../../images/tutorial/gee/plot_data.png
    :width: 800px
    :align: center

0. Start From Previous Solution (Optional)
==========================================

If you wish to use the previous solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine
    cd tethysapp-earth_engine
    git checkout -b vis-gee-layers-solution vis-gee-layers-solution-|version|

1. Create New GEE Function to Extract Time Series
=================================================

In this step you'll expand the GEE functions to include a function that can extract time series at one or more points or polygons.

1. Install new dependency, ``geojson``, ``simplejson``, ``pandas`` in Tethys environment:

.. code-block:: bash

    conda install -c conda-forge geojson simplejson pandas

2. Add ``geojson``, ``simplejson``, ``pandas``, as dependencies in the :file:`install.yml`:

.. code-block:: yaml
    :emphasize-lines: 17-19

    # This file should be committed to your app code.
    version: 1.0
    # This should be greater or equal to your tethys-platform in your environment
    tethys_version: ">=4.0.0"
    # This should match the app - package name in your setup.py
    name: earth_engine

    requirements:
      # Putting in a skip true param will skip the entire section. Ignoring the option will assume it be set to False
      skip: false
      conda:
        channels:
          - conda-forge
        packages:
          - earthengine-api
          - oauth2client
          - geojson
          - simplejson
          - pandas
      pip:

      npm:

    post:

3. Add ``get_time_series_from_image_collection`` function to the :file:`gee/methods.py` module:

.. code-block:: python

    import geojson
    import pandas as pd

.. code-block:: python

    def get_time_series_from_image_collection(platform, sensor, product, index_name, scale=30, geometry=None,
                                          date_from=None, date_to=None, reducer='median'):
        """
        Derive time series at given geometry.
        """
        time_series = []
        ee_product = EE_PRODUCTS[platform][sensor][product]
        collection_name = ee_product['collection']

        if not isinstance(geometry, geojson.GeometryCollection):
            raise ValueError('Geometry must be a valid geojson.GeometryCollection')

        for geom in geometry.geometries:
            log.debug(f'Computing Time Series for Geometry of Type: {geom.type}')

            try:
                ee_geometry = None
                if isinstance(geom, geojson.Polygon):
                    ee_geometry = ee.Geometry.Polygon(geom.coordinates)
                elif isinstance(geom, geojson.Point):
                    ee_geometry = ee.Geometry.Point(geom.coordinates)
                else:
                    raise ValueError('Only Points and Polygons are supported.')

                if date_from is not None:
                    if index_name is not None:
                        indexCollection = ee.ImageCollection(collection_name) \
                            .filterDate(date_from, date_to) \
                            .select(index_name)
                    else:
                        indexCollection = ee.ImageCollection(collection_name) \
                            .filterDate(date_from, date_to)
                else:
                    indexCollection = ee.ImageCollection(collection_name)

                def get_index(image):
                    if reducer:
                        the_reducer = getattr(ee.Reducer, reducer)()

                    if index_name is not None:
                        index_value = image.reduceRegion(the_reducer, ee_geometry, scale).get(index_name)
                    else:
                        index_value = image.reduceRegion(the_reducer, ee_geometry, scale)

                    date = image.get('system:time_start')
                    index_image = ee.Image().set('indexValue', [ee.Number(date), index_value])
                    return index_image

                index_collection = indexCollection.map(get_index)
                index_collection_agg = index_collection.aggregate_array('indexValue')
                values = index_collection_agg.getInfo()
                log.debug('Values acquired.')
                df = pd.DataFrame(values, columns=['Time', index_name.replace("_", " ")])
                time_series.append(df)

            except EEException:
                log.exception('An error occurred while attempting to retrieve the time series.')

        log.debug(f'Time Series: {time_series}')
        return time_series

This function uses a `Pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_ to store each time series. The DataFrame consists of two columns: Time and the name of the index. The column names will be used for the plot axes.

2. Create Endpoint for Extracting Time Series
=============================================

The technique that will be demonstrated in this step will leverage the `jQuery.load() <https://api.jquery.com/load/>`_ method, which calls a URL and inserts the HTML returned into a target element. You'll create an endpoint that will call the ``get_time_series_from_image_collection`` function to get the times series and then render a plot using the Tethys ``PlotlyView`` gizmo. Then simply call the endpoint with ``jQuery.load()`` and target the content area of the plot modal to load the plot into the modal.

1. The ``generate_figure`` helper function creates a Plotly figure object from the given time series. Create a new module called :file:`helpers.py` in the :file:`earth_engine` package with the following contents:

.. code-block:: python

    import pandas as pd
    from plotly import graph_objs as go


    def generate_figure(figure_title, time_series):
        """
        Generate a figure from a list of time series Pandas DataFrames.

        Args:
            figure_title(str): Title of the figure.
            time_series(list<pandas.DataFrame>): list of time series Pandas DataFrames.
        """
        data = []
        yaxis_title = 'No Data'

        for index, df in enumerate(time_series):
            column_name = df.columns[1]
            yaxis_title = column_name
            series_name = f'{column_name} {index + 1}' if len(time_series) > 1 else column_name
            series_plot = go.Scatter(
                x=pd.to_datetime(df.iloc[:, 0], unit='ms'),
                y=df.iloc[:, 1],
                name=series_name,
                mode='lines'
            )

            data.append(series_plot)

        figure = {
            'data': data,
            'layout': {
                'title': {
                    'text': figure_title,
                    'pad': {
                        'b': 5,
                    },
                },
                'yaxis': {'title': yaxis_title},
                'legend': {
                    'orientation': 'h'
                },
                'margin': {
                    'l': 40,
                    'r': 10,
                    't': 80,
                    'b': 10
                }
            }
        }

        return figure

2. The ``get_time_series_plot`` function will call the ``get_time_series_from_image_collection`` function with the parameters given and render a ``PlotlyView`` gizmo from the results. Add a new controller called ``get_time_series_plot`` to :file:`controllers.py`:

.. code-block:: python

    import geojson
    from simplejson.errors import JSONDecodeError
    from tethys_sdk.gizmos import PlotlyView
    from .helpers import generate_figure
    from .gee.methods import get_time_series_from_image_collection

.. code-block:: python

    @controller
    def get_time_series_plot(request):
        context = {'success': False}

        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])

        try:
            log.debug(f'POST: {request.POST}')

            platform = request.POST.get('platform', None)
            sensor = request.POST.get('sensor', None)
            product = request.POST.get('product', None)
            start_date = request.POST.get('start_date', None)
            end_date = request.POST.get('end_date', None)
            reducer = request.POST.get('reducer', None)
            index_name = request.POST.get('index_name', None)
            scale = float(request.POST.get('scale', 250))
            geometry_str = request.POST.get('geometry', None)

            # Derived parameters
            ee_product = EE_PRODUCTS[platform][sensor][product]
            display_name = ee_product['display']

            if not index_name:
                index_name = ee_product['index']

            try:
                geometry = geojson.loads(geometry_str)
            except JSONDecodeError:
                raise ValueError('Please draw an area of interest.')

            if index_name is None:
                raise ValueError(f"We're sorry, but plotting {display_name} is not supported at this time. Please select "
                                 f"a different product.")

            time_series = get_time_series_from_image_collection(
                platform=platform,
                sensor=sensor,
                product=product,
                index_name=index_name,
                scale=scale,
                geometry=geometry,
                date_from=start_date,
                date_to=end_date,
                reducer=reducer
            )

            log.debug(f'Time Series: {time_series}')

            figure = generate_figure(
                figure_title=display_name,
                time_series=time_series
            )

            plot_view = PlotlyView(figure, height='200px', width='100%')

            context.update({
                'success': True,
                'plot_view': plot_view
            })

        except ValueError as e:
            context['error'] = str(e)

        except Exception:
            context['error'] = f'An unexpected error has occurred. Please try again.'
            log.exception('An unexpected error occurred.')

        return App.render(request, 'plot.html', context)

3. Create a new template called :file:`templates/earth_engine/plot.html` with the following contents:

.. code-block:: html+django

    {% load tethys %}

    {% if plot_view %}
      {% gizmo plot_view %}
    {% endif %}

    {% if error %}
      <div class="alert alert-danger" role="alert">
        <span>{{ error }}</span>
      </div>
    {% endif %}

.. important::

    Notice that this template **does not** extend from any template like other Tethys templates. It should contain only the HTML that will be inserted into the modal.

    Notice also that the template will render an error message instead of the plot if an error is provided in the context.

3. Create a Modal for the Plot
==============================

In this step you'll add a Plot button and the modal for the plot to the controller and template.

1. Add **Plot AOI** button to ``home`` controller in :file:`controllers.py`:

.. code-block:: python

    plot_button = Button(
        name='load_plot',
        display_text='Plot AOI',
        style='outline-secondary',
        attributes={'id': 'load_plot'},
    )

    context = {
        'platform_select': platform_select,
        'sensor_select': sensor_select,
        'product_select': product_select,
        'start_date': start_date,
        'end_date': end_date,
        'reducer_select': reducer_select,
        'load_button': load_button,
        'clear_button': clear_button,
        'plot_button': plot_button,
        'ee_products': EE_PRODUCTS,
        'map_view': map_view
    }

2. Add **Plot AOI** button to the ``app_navigation_items`` block of the :file:`templates/earth_engine/home.html` template:

.. code-block:: html+django

    {% block app_navigation_items %}
      <li class="title">Select Dataset</li>
      {% gizmo platform_select %}
      {% gizmo sensor_select %}
      {% gizmo product_select %}
      {% gizmo start_date %}
      {% gizmo end_date %}
      {% gizmo reducer_select %}
      <p class="help">Change variables to select a data product, then press "Load" to add that product to the map.</p>
      {% gizmo load_button %}
      {% gizmo clear_button %}
      <p class="help mt-2">Draw an area of interest or drop a point, the press "Plot AOI" to view a plot of the data.</p>
      {% gizmo plot_button %}
    {% endblock %}

3. Add a new `Bootstrap Modal <https://getbootstrap.com/docs/5.2/components/modal/>`_ for displaying the plot to the ``after_app_content`` block of the :file:`templates/earth_engine/home.html` template:

.. code-block:: html+django

    {% block after_app_content %}
      <!-- Plot Modal -->
      <div class="modal fade" id="plot-modal" tabindex="-1" role="dialog" aria-labelledby="plot-modal-label">
        <div class="modal-dialog" role="document">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="plot-modal-label">Area of Interest Plot</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <div id="plot-container"></div>
            </div>
          </div>
        </div>
      </div>
      <!-- End Plot Modal -->
      <div id="ee-products" data-ee-products="{{ ee_products|jsonify }}"></div>
      <div id="loader">
        <img src="{% static tethys_app|public:'images/map-loader.gif' %}">
      </div>
    {% endblock %}

4. Temporarily bind the ``click`` event of the **Plot AOI** button to the show modal action (in the ``bind_controls`` method of :file:`public/js/gee_datasets.js`):

.. code-block:: javascript

    $('#load_plot').on('click', function() {
        $('#plot-modal').modal('show');
    });

4. Stub Out the Plot JavaScript Methods
=======================================

1. Add the following module function declarations to the *PRIVATE FUNCTION DECLARATIONS* section of :file:`public/js/gee_datasets.js`:

.. code-block:: javascript

    // Time Series Plot Methods
    var get_geometry, update_plot, show_plot_modal;

2. Add the following module function stubs to the *PRIVATE FUNCTION IMPLEMENTATIONS* section of :file:`public/js/gee_datasets.js`, just below the ``clear_map`` method:

.. code-block:: javascript

    // Time Series Plot Methods
    get_geometry = function() {};

    update_plot = function() {};

    show_plot_modal = function() {};

.. note::

    The lines that define empty functions (e.g.: ``update_plot = function() {};``) are method stubs that will be implemented in future steps.

5. Add a Loading GIF for the Plot Modal
=======================================

In this step you'll add a loading image to the modal whenever it is shown, replacing whatever contents was there previously. This will be replaced by the loaded plot once it is finished loading. Launching the modal again, will replace the previous plot with the loading image and so on.

1. Download this :download:`animated plot loading image <./resources/plot-loader.gif>` or find one that you like and save it to the :file:`public/images` directory.

2. Create a new stylesheet called :file:`plot.css` in :file:`public/css` with the following contents:

.. code-block:: css

    #plot-loader {
        display: flex;
        align-items: center;
        width: 100%;
        justify-content: center;
        flex-direction: column;
    }

    #plot-loader p {
        text-align: center;
    }

    #plot-modal .modal-body {
        min-height: 480px;
    }

    .modal-dialog {
        max-width: 70vw;
        margin: 1.75rem auto;
    }

3. Include the :file:`plot.css` stylesheet in the :file:`home.html` template:

.. code-block:: html+django

    {% block content_dependent_styles %}
        {{ block.super }}
        <link rel="stylesheet" href="{% static tethys_app|public:'css/map.css' %}" />
        <link rel="stylesheet" href="{% static tethys_app|public:'css/loader.css' %}" />
        <link rel="stylesheet" href="{% static tethys_app|public:'css/plot.css' %}" />
    {% endblock %}

.. tip::

    Click on the **Plot AOI** button to open the modal *before* and *after* adding the ``plot.css`` styles to see how the styles change the position of the loading GIF in the modal.

4. **Replace** the ``show_plot_modal`` method stub in :file:`public/js/gee_datasets.js` with the following implementation:

.. code-block:: javascript

    show_plot_modal = function() {
        $('#plot-container').html(
            '<div id="plot-loader">' +
                '<img src="/static/earth_engine/images/plot-loader.gif">' +
                '<p>Loading... This may take up to 5 minutes. Please wait.</p>' +
            '</div>'
        );
        $('#plot-modal').modal('show');
    };

5. To allow us to verify that the loading GIF appears in the modal when we update it, add a ``click`` event on the ``load_plot`` button to temporarily call the new ``show_plot_modal`` method. **Add** the following to the bottom of the ``bind_controls`` method of :file:`public/js/gee_datasets.js`:

.. code-block:: javascript

    $('#load_plot').on('click', function() {
        show_plot_modal();
    });

6. Verify that the loading GIF appears in the modal when it is opened. Browse to `<http://localhost:8000/apps/earth-engine>`_ in a web browser and login if necessary. Click on the **Plot AOI** button to open the modal. The modal should show the loading GIF and it should be centered in the modal.

6. Implement Plotting Capability
================================

In this step you'll use the native drawing capabilities of the Tethys ``MapView`` to allow the user to draw points and polygons on the map. Then you'll retrieve the drawn geometry in our JavaScript and send it with the other control values to the ``jQuery.load()`` call to the ``get-time-series-plot`` endpoint.

1. Enable the drawing controls in the ``MapView`` definition in the ``home`` controller in :file:`controllers.py`:

.. code-block:: python

    from tethys_sdk.gizmos import MVDraw

.. code-block:: python

    map_view = MapView(
        height='100%',
        width='100%',
        controls=[
            'ZoomSlider', 'Rotate', 'FullScreen',
            {'ZoomToExtent': {
                'projection': 'EPSG:4326',
                'extent': [29.25, -4.75, 46.25, 5.2]
            }}
        ],
        basemap=[
            'CartoDB',
            {'CartoDB': {'style': 'dark'}},
            'OpenStreetMap',
            'ESRI'
        ],
        view=MVView(
            projection='EPSG:4326',
            center=[37.880859, 0.219726],
            zoom=7,
            maxZoom=18,
            minZoom=2
        ),
        draw=MVDraw(
            controls=['Pan', 'Modify', 'Delete', 'Move', 'Point', 'Polygon', 'Box'],
            initial='Pan',
            output_format='GeoJSON'
        )
    )

2. Include the ``PlotlyView`` Gizmo dependencies in the :file:`templates/earth_engine/home.html` template:

.. code-block:: html+django

    {% block import_gizmos %}
      {% import_gizmo_dependency plotly_view %}
    {% endblock %}

3. Update the ``click`` event on the ``load_plot`` button to call the new ``update_plot`` method (in the ``bind_controls`` method):

.. code-block:: javascript

    $('#load_plot').on('click', function() {
        update_plot();
    });

4. **Replace** the ``get_geometry`` method stub in :file:`public/js/gee_datasets.js` with the following implementation:

.. code-block:: javascript

    get_geometry = function() {
        // Get drawn geometry from embedded textarea of Tethys Map View
        let geometry_json = $('#map_view_geometry').val() || null;
        return geometry_json;
    };

5. Update the ``collect_data`` method in :file:`public/js/gee_datasets.js` to call ``get_geometry`` and return its result with the other data it collects:

.. code-block:: javascript

    collect_data = function() {
        let data = {
            platform: m_platform,
            sensor: m_sensor,
            product: m_product,
            start_date: m_start_date,
            end_date: m_end_date,
            reducer: m_reducer,
            geometry: get_geometry()
        };
        return data;
    };

6. **Replace** the ``update_plot`` method in :file:`public/js/gee_datasets.js` with the following implementation:

.. code-block:: javascript

    update_plot = function() {
        let data = collect_data();

        show_plot_modal();

        $('#plot-container').load('get-time-series-plot/', data);
    };

7. Test and Verify
==================

Browse to `<http://localhost:8000/apps/earth-engine>`_ in a web browser and login if necessary. Verify the following:

1. Load approximately one year of the the *MODIS TERRA Land Servica Temperature and Emissivity* dataset on the map.
2. Use the **Point** drawing tool to add a point to the map.
3. Press the **Plot AOI** button to initiate the time series query and plotting.
4. The plot should show a single time series of temperatures. The gaps in the time series indicate where data is missing, usually due to cloud cover.
5. Repeat the process using one of the polygon tools to verify that the data is being aggregated properly.

8. Solution
===========

This concludes this portion of the GEE Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-earth_engine/tree/plot-data-solution-3.0>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine
    cd tethysapp-earth_engine
    git checkout -b plot-data-solution plot-data-solution-|version|