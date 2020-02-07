****************************
Plot Time Series at Location
****************************

**Last Updated:** December 2019

In this tutorial you will add a tool for querying the active THREDDS dataset for time series data at a location and display it on a plot. Topics covered in this tutorial include:

* :ref:`plotly_view_gizmo`
* `Leaflet Plugins <https://leafletjs.com/plugins.html>`_: `Leaflet.Draw <http://leaflet.github.io/Leaflet.draw/docs/leaflet-draw-latest.html>`_
* `THREDDS NetCDF Subset Service (NCSS) <https://www.unidata.ucar.edu/software/tds/current/reference/NetcdfSubsetServiceReference.html>`_
* `JQuery Load <https://api.jquery.com/load/>`_

.. figure:: ./resources/plot_at_location_solution.png
    :width: 800px
    :align: center


0. Start From Previous Solution (Optional)
==========================================

If you wish to use the previous solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-thredds_tutorial.git
    cd tethysapp-thredds_tutorial
    git checkout -b visualize-leaflet-solution visualize-leaflet-solution-|version|

1. Add Drawing Tool to Map
==========================

In this step you'll learn to use another Leaflet plugin: `Leaflet.Draw <http://leaflet.github.io/Leaflet.draw/docs/leaflet-draw-latest.html>`_. This plugin adds a toolbar of controls for drawing different shapes on the map, including a point/marker tool. You'll implement the plot at location tool using the marker tool and bind to its on-draw event to load the plot for that location.

1. Include Leaflet Draw scripts and stylesheets in :file:`templates/thredds_tutorial/home.html`:

.. code-block:: html+django

    {% block styles %}
      {{ block.super }}
      <link rel="stylesheet" href="https://unpkg.com/leaflet@1.6.0/dist/leaflet.css"
       integrity="sha512-xwE/Az9zrjBIphAcBb3F6JVqxf46+CDLwfLMHloNu6KEQCAWi6HcDUbeOfBIptF7tcCzusKFjFw2yuvEpDL9wQ=="
       crossorigin=""/>
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet-timedimension@1.1.1/dist/leaflet.timedimension.control.min.css" />
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/0.4.2/leaflet.draw.css"/>
      <link rel="stylesheet" href="{% static 'thredds_tutorial/css/leaflet_map.css' %}"/>
      <link rel="stylesheet" href="{% static 'thredds_tutorial/css/loader.css' %}" />
    {% endblock %}

    {% block global_scripts %}
      {{ block.super }}
      <script src="https://unpkg.com/leaflet@1.6.0/dist/leaflet.js"
       integrity="sha512-gZwIG9x3wUXg2hdXF6+rVkLF/0Vi9U8D2Ntg4Ga5I5BZpVkVxlJWbSQtXPSiUTtC0TjtGOmxa1AJPuV0CPthew=="
       crossorigin=""></script>
      <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/iso8601-js-period@0.2.1/iso8601.min.js"></script>
      <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/leaflet-timedimension@1.1.1/dist/leaflet.timedimension.min.js"></script>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/0.4.2/leaflet.draw.js"></script>
    {% endblock %}

2. Declare the following variables in :file:`public/js/leaflet_map.js`:

.. code-block:: javascript

    /************************************************************************
    *                      MODULE LEVEL / GLOBAL VARIABLES
    *************************************************************************/
    var public_interface,    // Object returned by the module
        m_map,               // The Leaflet Map
        m_layer,             // The layer
        m_layer_meta,        // Map of layer metadata indexed by variable
        m_td_layer,          // The time dimension layer
        m_curr_dataset,      // The current selected dataset
        m_curr_variable,     // The current selected variable/layer
        m_curr_style,        // The current selected style
        m_curr_wms_url,      // The current WMS url
        m_drawn_features;    // Layer for drawn items

    /************************************************************************
    *                    PRIVATE FUNCTION DECLARATIONS
    *************************************************************************/
    // Map Methods
    var init_map, update_layer;

    // Control Methods
    var init_controls, update_variable_control, update_style_control;

    // Legend Methods
    var update_legend, clear_legend;

    // Loader Methods
    var show_loader, hide_loader;

    // Plot Methods
    var init_plot_at_location;

3. The Leaflet.Draw toolbar can be customized to show or hide controls as desired. Since the plot at location tool will use the draw toolbar, you'll initialize it as part of the intialization of the plot at location tool. Implement the ``init_plot_at_location`` method in :file:`public/js/leaflet_map.js`:

.. code-block:: javascript

    // Plot Methods
    init_plot_at_location = function() {
        // Initialize layer for drawn features
        m_drawn_features = new L.FeatureGroup();
        m_map.addLayer(m_drawn_features);

        // Initialize draw controls
        let draw_control = new L.Control.Draw({
            draw: {
                polyline: false,
                polygon: false,
                circle: false,
                rectangle: false,
            }
        });

        m_map.addControl(draw_control);

        // Bind to draw event
        m_map.on(L.Draw.Event.CREATED, function(e) {
            // Remove all layers (only show one location at a time)
            m_drawn_features.clearLayers();

            // Add layer with the new features
            let new_features_layer = e.layer;
            m_drawn_features.addLayer(new_features_layer);
        });
    };

4. Call ``init_plot_at_location`` during initialization of :file:`public/js/leaflet_map.js`:

.. code-block:: javascript

    /************************************************************************
    *                  INITIALIZATION / CONSTRUCTOR
    *************************************************************************/

    // Initialization: jQuery function that gets called when
    // the DOM tree finishes loading
    $(function() {
        init_map();
        init_controls();
        init_plot_at_location();
    });

5. Verify that the drawing tool has been added to the map. Browse to `<http://localhost:8000/apps/thredds-tutorial>`_ in a web browser and login if necessary. A single tool for drawing markers/points should appear near the top left-hand corner of the map, just below the zoom controls.

2. Create New Plot Controller
=============================

In this step you will create a new controller that will query the dataset at the given location using the NCSS service and then build a plotly plot with the results.

1. Add two new methods to the :file:`thredds_methods.py` module:


.. code-block:: python

    from datetime import datetime, timedelta

.. code-block:: python

    def find_dataset(catalog, dataset):
        """
        Recursively search a TDSCatalog for a dataset with the given name.

        Args:
            catalog(siphon.catalog.TDSCatalog): A Siphon catalog object bound to a valid THREDDS service.
            dataset(str): The name of the dataset to find.

        Returns:
            siphon.catalog.Dataset: The catalog dataset object or None if not found.
        """
        if dataset in catalog.datasets:
            return catalog.datasets[dataset]

        for catalog_name, catalog_obj in catalog.catalog_refs.items():
            d = find_dataset(catalog_obj.follow(), dataset)
            if d is not None:
                return d

        return None

.. code-block:: python

    def extract_time_series_at_location(catalog, geometry, dataset, variable, start_time=None, end_time=None,
                                        vertical_level=None):
        """
        Extract a time series from a THREDDS dataset at the given location.

        Args:
            catalog(siphon.catalog.TDSCatalog): a Siphon catalog object bound to a valid THREDDS service.
            geometry(geojson): A geojson object representing the location.
            dataset(str): Name of the dataset to query.
            variable(str): Name of the variable to query.
            start_time(datetime): Start of time range to query. Defaults to datetime.utcnow().
            end_time(datetime): End of time range to query. Defaults to 7 days after start_time.
            vertical_level(number): The vertical level to query. Defaults to 100000.

        Returns:
            netCDF5.Dataset: The data from the NCSS query.
        """
        try:
            d = find_dataset(catalog, dataset)
            ncss = d.subset()
            query = ncss.query()

            # Filter by location
            coordinates = geometry.geometry.coordinates
            query.lonlat_point(coordinates[0], coordinates[1])

            # Filter by time
            if start_time is None:
                start_time = datetime.utcnow()

            if end_time is None:
                end_time = start_time + timedelta(days=7)

            query.time_range(start_time, end_time)

            # Filter by variable
            query.variables(variable).accept('netcdf')

            # Filter by vertical level
            if vertical_level is not None:
                query.vertical_level(vertical_level)
            else:
                query.vertical_level(100000)

            # Get the data
            data = ncss.get_data(query)

        except OSError as e:
            if 'NetCDF: Unknown file format' in str(e):
                raise ValueError("We're sorry, but we don't support querying this type of dataset at this time. "
                                 "Please try another dataset.")
            else:
                raise e

        return data

.. note::

    The ``find_dataset`` method is another recursive function similar to the ``parse_datasets`` function, except that it searches for and returns a single dataset with the name given.

    The ``extract_time_series_at_location`` method uses the NetCDF Subset Service (NCSS) to subset the dataset, in this case at a specific location over a period of time.

2. Create a new function that will generate the Plotly figure in a new Python module, :file:`figure.py`:

.. code-block:: python

    from plotly import graph_objs as go
    from netCDF4 import num2date


    def generate_figure(time_series, dataset, variable):
        """
        Generate a figure from a netCDF4.Dataset.

        Args:
            time_series(netCDF4.Dataset): A time series NetCDF4 Dataset.
            dataset(str): The name of the time series dataset.
            variable(str): The name of the variable to plot.
        """
        figure_data = []
        figure_title = dataset

        column_name = variable.replace('_', ' ').title()

        yaxis_title = column_name
        series_name = column_name

        # Add units to yaxis title
        variable_units = time_series.variables[variable].units
        if variable_units:
            yaxis_title += f' ({variable_units})'

        # Extract needed arrays for plot from NetCDF4 Dataset
        variable_array = time_series.variables[variable][:].squeeze()
        time = time_series.variables['time']
        time_array = num2date(time[:].squeeze(), time.units)

        series_plot = go.Scatter(
            x=time_array,
            y=variable_array,
            name=series_name,
            mode='lines'
        )

        figure_data.append(series_plot)

        figure = {
            'data': figure_data,
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

3. Create a new controller, ``get_time_series_plot``, to handle plot requests. Add the following to :file:`controllers.py`:

.. code-block:: python

    import geojson
    from datetime import datetime
    from simplejson.errors import JSONDecodeError
    from tethys_sdk.gizmos import SelectInput, PlotlyView
    from .figure import generate_figure
    from .thredds_methods import parse_datasets, get_layers_for_wms, extract_time_series_at_location

.. code-block:: python

    @login_required()
    def get_time_series_plot(request):
        context = {'success': False}

        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])

        try:
            log.debug(f'POST: {request.POST}')

            geojson_str = str(request.POST.get('geometry', None))
            dataset = request.POST.get('dataset', None)
            variable = request.POST.get('variable', None)
            start_time = request.POST.get('start_time', None)
            end_time = request.POST.get('end_time', None)
            vertical_level = request.POST.get('vertical_level', None)

            # Deserialize GeoJSON string into Python objects
            try:
                geometry = geojson.loads(geojson_str)
            except JSONDecodeError:
                raise ValueError('Please draw an area of interest.')

            # Convert milliseconds from epoch to date time
            if start_time is not None:
                s = int(start_time) / 1000.0
                start_time = datetime.fromtimestamp(s)

            if end_time is not None:
                e = int(end_time) / 1000.0
                end_time = datetime.fromtimestamp(e)

            # Retrieve the connection to the THREDDS server
            catalog = app.get_spatial_dataset_service(app.THREDDS_SERVICE_NAME, as_engine=True)

            time_series = extract_time_series_at_location(
                catalog=catalog,
                geometry=geometry,
                dataset=dataset,
                variable=variable,
                start_time=start_time,
                end_time=end_time,
                vertical_level=vertical_level
            )

            log.debug(f'Time Series: {time_series}')

            figure = generate_figure(
                time_series=time_series,
                dataset=dataset,
                variable=variable
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

        return render(request, 'thredds_tutorial/plot.html', context)

4. Create a new template for the ``get_time_series_plot`` controller, :file:`templates/thredds_tutorial/plot.html`, with the following contents:

.. code-block:: html+django

    {% load tethys_gizmos %}

    {% if plot_view %}
      {% gizmo plot_view %}
    {% endif %}

    {% if error %}
      <div class="alert alert-danger" role="alert">
        <span>{{ error }}</span>
      </div>
    {% endif %}

5. Add a ``UrlMap`` for the ``get_time_series_plot`` controller in :file:`app.py`:

.. code-block:: python

    UrlMap(
        name='get_time_series_plot',
        url='thredds-tutorial/get-time-series-plot',
        controller='thredds_tutorial.controllers.get_time_series_plot'
    ),

3. Load Plot Using JQuery Load
==============================

The `JQuery.load() <https://api.jquery.com/load/>`_ method is used to call a URL and load the returned HTML into the target element. In this step, you'll use ``jQuery.load()`` to call the ``get-time-series-plot`` endpoint and load the markup for the plot that is returned into a modal for display to the user. This pattern allows you to render the plot dynamically, while still defining it using Python and the Plotly gizmo.

1. Download this :download:`animated plot loading image <./resources/plot-loader.gif>` or find one that you like and save it to the :file:`public/images` directory.

2. Create a new stylesheet, :file:`public/css/plot.css`, with the following contents:

.. code-block:: css

    #plot-loader {
        margin: 65px 84px;
    }

    #plot-loader p {
        text-align: center;
    }

    #plot-modal .modal-body {
        min-height: 480px;
    }

3. Include the Plotly gizmo dependencies and the new stylesheet in :file:`templates/thredds_tutorial/home.html`:

.. code-block:: html+django

    {% block import_gizmos %}
      {% import_gizmo_dependency plotly_view %}
    {% endblock %}

    {% block styles %}
      {{ block.super }}
      <link rel="stylesheet" href="https://unpkg.com/leaflet@1.6.0/dist/leaflet.css"
       integrity="sha512-xwE/Az9zrjBIphAcBb3F6JVqxf46+CDLwfLMHloNu6KEQCAWi6HcDUbeOfBIptF7tcCzusKFjFw2yuvEpDL9wQ=="
       crossorigin=""/>
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet-timedimension@1.1.1/dist/leaflet.timedimension.control.min.css" />
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/0.4.2/leaflet.draw.css"/>
      <link rel="stylesheet" href="{% static 'thredds_tutorial/css/leaflet_map.css' %}"/>
      <link rel="stylesheet" href="{% static 'thredds_tutorial/css/loader.css' %}" />
      <link rel="stylesheet" href="{% static 'thredds_tutorial/css/plot.css' %}" />
    {% endblock %}

4. Add a modal to :file:`templates/thredds_tutorial/home.html` for displaying the plot:

.. code-block:: html+django

    {% block after_app_content %}
      <div id="loader">
        <img src="{% static 'thredds_tutorial/images/map-loader.gif' %}">
      </div>
      <!-- Plot Modal -->
      <div class="modal fade" id="plot-modal" tabindex="-1" role="dialog" aria-labelledby="plot-modal-label">
        <div class="modal-dialog" role="document">
          <div class="modal-content">
            <div class="modal-header">
              <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
              <h5 class="modal-title" id="plot-modal-label">Area of Interest Plot</h5>
            </div>
            <div class="modal-body">
              <div id="plot-container"></div>
            </div>
          </div>
        </div>
      </div>
    {% endblock %}

.. note::

    The empty **#plot-container** ``div`` is the element that you will target with the ``jQuery.load()`` method and thus where the plot will be rendered.

5. Declare two new plot methods in :file:`public/js/leaflet_map.js`:

.. code-block:: javascript

    // Plot Methods
    var init_plot_at_location, show_plot_modal, update_plot;

6. The ``show_plot_modal`` will reset the modal with the loading gif and show the modal if it is not already showing. Implement the ``show_plot_modal`` method in :file:`public/js/leaflet_map.js`:

.. code-block:: javascript

    show_plot_modal = function() {
        // Replace last plot with animated loading image
        $('#plot-container').html(
            '<div id="plot-loader">' +
                '<img src="/static/thredds_tutorial/images/plot-loader.gif">' +
                '<p>Loading... Please wait.</p>' +
            '</div>'
        );

        // Show the modal
        $('#plot-modal').modal('show');
    };

7. The ``update_plot`` method will gather the needed parameters for the ``get-time-series-plot`` endpoint and call it with ``jQuery.load()``. Implement the ``update_plot`` method in :file:`public/js/leaflet_map.js`:

.. code-block:: javascript

    update_plot = function(location_layer) {
        // Reset and show plot modal
        show_plot_modal();

        // Serialize geometry for request
        let geometry = location_layer.toGeoJSON();
        let geometry_str = JSON.stringify(geometry);

        // Build data packet
        let data = {
            geometry: geometry_str,
            variable: m_curr_variable,
            dataset: m_curr_dataset,
        };

        // Get available time range from time control on map (if any)
        let available_times = m_map.timeDimension.getAvailableTimes()
        if (available_times && available_times.length) {
            data.start_time = available_times[0]
            data.end_time = available_times[available_times.length - 1]
        }

        // Get vertical level
        let vertical_level = $('#vertical_level').val();
        if (vertical_level) {
            data.vertical_level = vertical_level;
        }

        // Call load
        $('#plot-container').load('get-time-series-plot/', data);
    };

.. note::

    ``$`` is shorthand for ``jQuery``.

8. When ``jQuery.load()`` is called with the data parameter, as it is in this case, the request is submitted using the ``POST`` method. You must include the CSRF token with any POST request for Django to accept the request. Add the following to :file:`public/js/main.js` to allow ``jQuery.load()`` to use the ``POST`` method:

.. code-block:: javascript

    // Get a cookie
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // find if method is csrf safe
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    // add csrf token to appropriate ajax requests
    $(function() {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
                }
            }
        });
    }); //document ready;

9. Call ``update_plot`` in the on-draw handler at the bottom of ``init_plot_at_location`` in :file:`public/js/leaflet_map.js`:

.. code-block:: javascript

    m_map.on(L.Draw.Event.CREATED, function(e) {
        // Remove all layers (only show one location at a time)
        m_drawn_features.clearLayers();

        // Add layer with the new features
        let new_features_layer = e.layer;
        m_drawn_features.addLayer(new_features_layer);

        // Load the plot
        update_plot(new_features_layer);
    });

10. Clear the drawn features whenever the layer updates:

.. code-block:: javascript

    update_layer = function() {
        if (m_td_layer) {
            m_map.removeLayer(m_td_layer);
        }

        // Clear the legend
        clear_legend();

        // Clear drawn features
        if (m_drawn_features) {
            m_drawn_features.clearLayers();
        }

        // Layer
        m_layer = L.tileLayer.wms(m_curr_wms_url, {
            layers: m_curr_variable,
            format: 'image/png',
            transparent: true,
            colorscalerange: '250,350',  // Hard-coded color scale range won't work for all layers
            abovemaxcolor: "extend",
            belowmincolor: "extend",
            numcolorbands: 100,
            styles: m_curr_style
        });

        // Wrap WMS layer in Time Dimension Layer
        m_td_layer = L.timeDimension.layer.wms(m_layer, {
            updateTimeDimension: true
        });

        // Add events for loading
        m_layer.on('loading', function() {
            show_loader();
        });

        m_layer.on('load', function() {
            hide_loader();
        });

        // Add Time-Dimension-Wrapped WMS layer to the Map
        m_td_layer.addTo(m_map);

        // Update the legend graphic
        update_legend();
    };

4. Test and Verify
==================

Browse to `<http://localhost:8000/apps/thredds-tutorial>`_ in a web browser and login if necessary. Verify the following:

1. Select the "Best GFS Half Degree Forecast Time Series" dataset using the **Dataset** control to test a time-varying layer.
2. Click on the **Draw a Marker** button, located just below the zoom controls on the map.
3. Drop a marker somewhere on the map.
4. Verify that the plot dialog appears automatically after dropping the marker with the loading image showing.
5. Verify that the plot appears after the data has been queried.

5. Solution
===========

This concludes the New App Project portion of the THREDDS Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-thredds_tutorial/tree/thredds-service-solution-3.0>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-thredds_tutorial.git
    cd tethysapp-thredds_tutorial
    git checkout -b plot-at-location-solution plot-at-location-solution-|version|