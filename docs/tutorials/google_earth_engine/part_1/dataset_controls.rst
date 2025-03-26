********************************
Build Dataset Selection Controls
********************************

**Last Updated:** July 2024

In this tutorial you will add controls to the app that will eventually be used to select various Google Earth Engine datasets to display. The following topics will be reviewed in this tutorial:

* Tethys Gizmos API
* Tethys Templating API

.. figure:: ../../../images/tutorial/gee/dataset_controls.png
    :width: 800px
    :align: center


0. Start From Previous Solution (Optional)
==========================================

If you wish to use the previous solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine
    cd tethysapp-earth_engine
    git checkout -b new-app-project-solution new-app-project-solution-|version|


1. Define Target GEE Products
=============================

Google Earth Engine hosts a huge offering of remote sensing datasets (see: `Earth Engine Data Catalog <https://developers.google.com/earth-engine/datasets>`_). For the purposes of this tutorial, you'll only expose a few of the datasets in the app.

In this step, you'll define a variable that will effectively contain a list of all of the datasets you plan to support with some metadata for each that you will need in the interface and for processing. The data is organized in nested dictionaries with the following structure:

.. code-block:: python

    EE_PRODUCTS = {
        '<SATELLITE_PLATFORM>': {
            '<SENSOR>': {
                '<PRODUCT>': {
                    'display': 'Display name of the product',
                    'collection': 'Image collection name.',
                    'index': 'Index(es) of the image collection to render, if applicable.',
                    'vis_params': 'A dictionary of visualization parameters to use when rendering the index.',
                    'start_date': 'The valid start date of the dataset.'
                    'end_date': 'The valid end date of the dataset or None if current.'
                }
            }
        }
    }

The metadata parameters for each dataset were derived from the examples of each dataset that can be found in the `Earth Engine Data Catalog <https://developers.google.com/earth-engine/datasets>`_ or the `Earth Engine Code Editor <https://code.earthengine.google.com/>`_ example scripts. Additional datasets can be easily added to the app by following this pattern.

Create a new package (a folder with an empty :file:`__init__.py`) called :file:`gee` to house Google Earth Engine related logic in the :file:`earth_engine` directory. Add a Python module called :file:`products.py` to this package with the following contents:

.. code-block:: python

    EE_PRODUCTS = {
        'modis': {
            'terra': {
                'snow': {
                    'display': 'Snow Cover Daily Global 500m',
                    'collection': 'MODIS/061/MOD10A1',
                    'index': 'NDSI_Snow_Cover',
                    'vis_params': {
                        'min': 0.0,
                        'max': 100.0,
                        'palette': ['black', '0dffff', '0524ff', 'ffffff'],
                    },
                    'start_date': '2000-02-24',
                    'end_date': None  # to present
                },
                'temperature': {
                    'display': 'Land Surface Temperature and Emissivity Daily Global 1km',
                    'collection': 'MODIS/061/MOD11A1',
                    'index': 'LST_Day_1km',
                    'vis_params': {
                        'min': 13000.0,
                        'max': 16500.0,
                        'palette': [
                            '040274', '040281', '0502a3', '0502b8', '0502ce', '0502e6',
                            '0602ff', '235cb1', '307ef3', '269db1', '30c8e2', '32d3ef',
                            '3be285', '3ff38f', '86e26f', '3ae237', 'b5e22e', 'd6e21f',
                            'fff705', 'ffd611', 'ffb613', 'ff8b13', 'ff6e08', 'ff500d',
                            'ff0000', 'de0101', 'c21301', 'a71001', '911003'
                        ],
                    },
                    'start_date': '2000-03-05',
                    'end_date': None  # to present
                }
            },
        },
        'sentinel': {
            '5': {
                'cloud': {
                    'display': 'Cloud',
                    'collection': 'COPERNICUS/S5P/OFFL/L3_CLOUD',
                    'index': 'cloud_fraction',
                    'vis_params': {
                        'min': 0,
                        'max': 0.95,
                        'palette': ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red']
                    },
                    'start_date': '2018-07-04',
                    'end_date': None  # to present
                },
                'co': {
                    'display': 'Carbon Monoxide',
                    'collection': 'COPERNICUS/S5P/OFFL/L3_CO',
                    'index': 'CO_column_number_density',
                    'vis_params': {
                        'min': 0,
                        'max': 0.05,
                        'palette': ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red']
                    },
                    'start_date': '2018-06-28',
                    'end_date': None  # to present
                },
                'ozone': {
                    'display': 'Ozone',
                    'collection': 'COPERNICUS/S5P/OFFL/L3_O3',
                    'index': 'O3_column_number_density',
                    'vis_params': {
                        'min': 0.12,
                        'max': 0.15,
                        'palette': ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red']
                    },
                    'start_date': '2018-09-08',
                    'end_date': None  # to present
                },
                'so2': {
                    'display': 'Sulphur Dioxide',
                    'collection': 'COPERNICUS/S5P/OFFL/L3_SO2',
                    'index': 'SO2_column_number_density',
                    'vis_params': {
                        'min': 0.0,
                        'max': 0.0005,
                        'palette': ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red']
                    },
                    'start_date': '2018-12-05',
                    'end_date': None  # to present
                },
                'ch4': {
                    'display': 'Methane',
                    'collection': 'COPERNICUS/S5P/OFFL/L3_CH4',
                    'index': 'CH4_column_volume_mixing_ratio_dry_air',
                    'vis_params': {
                        'min': 1750,
                        'max': 1900,
                        'palette': ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red']
                    },
                    'start_date': '2019-02-08',
                    'end_date': None  # to present
                },
            }
        },
        'landsat': {
            '8': {
                'surface': {
                    'display': 'Surface Reflectance',
                    'collection': 'LANDSAT/LC08/C02/T1_L2',
                    'index': None,
                    'vis_params': {
                        'bands': ['SR_B4', 'SR_B3', 'SR_B2'],
                        'min': 0,
                        'max': 3000,
                        'gamma': 1.4,
                    },
                    'cloud_mask': 'mask_l8_sr',
                    'start_date': '2013-04-01',
                    'end_date': None  # to present
                },
                'toa': {
                    'display': 'Top-of-Atmosphere(TOA) Reflectance',
                    'collection': 'LANDSAT/LC08/C02/T1_TOA', 
                    'index': None,
                    'vis_params': {
                        'bands': ['B4', 'B3', 'B2'],
                        'min': 0,
                        'max': 3000,
                        'gamma': 1.4,
                    },
                    'start_date': '2013-04-01',
                    'end_date': None  # to present
                },
            },
            '9': {
                'surface': {
                    'display': 'Surface Reflectance',
                    'collection': 'LANDSAT/LC09/C02/T1_L2',
                    'index': None,
                    'vis_params': {
                        'bands': ['SR_B4', 'SR_B3', 'SR_B2'],
                        'min': 0,
                        'max': 3000,
                        'gamma': 1.4,
                    },
                    'cloud_mask': 'mask_l8_sr',
                    'start_date': '2021-10-31',
                    'end_date': None  # to present
                },
                'toa': {
                    'display': 'Top-of-Atmosphere(TOA) Reflectance',
                    'collection': 'LANDSAT/LC09/C02/T1_TOA', 
                    'index': None,
                    'vis_params': {
                        'bands': ['B4', 'B3', 'B2'],
                        'min': 0,
                        'max': 3000,
                        'gamma': 1.4,
                    },
                    'start_date': '2021-10-31',
                    'end_date': None  # to present
                },
            }
        }
    }


2. Add Controls to Home Controller and Template
===============================================

The datasets are organized based on the satellite platform and sensor they were captured with. The controls will allow users to drill down to the subset of the dataset product they want to see and include the following controls:

* Satellite Platform
* Sensor
* Product
* Start Date
* End Date

In this step, you'll create controls using Tethys Gizmos with their initial values. You'll also pass the ``EE_PRODUCTS`` dictionary to the template so that it can be used by JavaScript in future steps.

1. Modify the ``home`` controller in :file:`controllers.py` as follows:

.. code-block:: python

    import datetime as dt
    from tethys_sdk.routing import controller
    from tethys_sdk.gizmos import SelectInput, DatePicker, Button
    from .gee.products import EE_PRODUCTS


    @controller
    def home(request):
        """
        Controller for the app home page.
        """
        default_platform = 'modis'
        default_sensors = EE_PRODUCTS[default_platform]
        first_sensor_key = next(iter(default_sensors.keys()))
        default_products = default_sensors[first_sensor_key]
        first_product_key = next(iter(default_products.keys()))
        first_product = default_products[first_product_key]

        # Build initial platform control
        platform_select = SelectInput(
            name='platform',
            display_text='Satellite Platform',
            options=(
                ('MODIS', 'modis'),
                ('Sentinel', 'sentinel'),
                ('Landsat', 'landsat')
            )
        )

        # Build initial sensor control
        sensor_options = []

        for sensor in default_sensors:
            sensor_options.append((sensor.upper(), sensor))

        sensor_select = SelectInput(
            name='sensor',
            display_text='Sensor',
            options=sensor_options
        )

        # Build initial product control
        product_options = []
        for product, info in default_products.items():
            product_options.append((info['display'], product))

        product_select = SelectInput(
            name='product',
            display_text='Product',
            options=product_options
        )

        # Hardcode initial end date to today (since all of our datasets extend to present)
        today = dt.datetime.today()
        initial_end_date = today.strftime('%Y-%m-%d')

        # Initial start date will a set number of days before the end date
        # NOTE: This assumes the start date of the dataset is at least 30+ days prior to today
        initial_end_date_dt = dt.datetime.strptime(initial_end_date, '%Y-%m-%d')
        initial_start_date_dt = initial_end_date_dt - dt.timedelta(days=30)
        initial_start_date = initial_start_date_dt.strftime('%Y-%m-%d')

        # Build date controls
        first_product_start_date = first_product.get('start_date', None)
        first_product_end_date = first_product.get('end_date', None) or initial_end_date

        start_date = DatePicker(
            name='start_date',
            display_text='Start Date',
            format='yyyy-mm-dd',
            start_view='decade',
            today_button=True,
            today_highlight=True,
            start_date=first_product_start_date,
            end_date=first_product_end_date,
            initial=initial_start_date,
            autoclose=True
        )

        end_date = DatePicker(
            name='end_date',
            display_text='End Date',
            format='yyyy-mm-dd',
            start_view='decade',
            today_button=True,
            today_highlight=True,
            start_date=first_product_start_date,
            end_date=first_product_end_date,
            initial=initial_end_date,
            autoclose=True
        )

        # Build reducer method control
        reducer_select = SelectInput(
            name='reducer',
            display_text='Reduction Method',
            options=(
                ('Median', 'median'),
                ('Mosaic', 'mosaic'),
                ('Mode', 'mode'),
                ('Mean', 'mean'),
                ('Minimum', 'min'),
                ('Maximum', 'max'),
                ('Sum', 'sum'),
                ('Count', 'count'),
                ('Product', 'product'),
            )
        )

        # Build Buttons
        load_button = Button(
            name='load_map',
            display_text='Load',
            style='outline-secondary',
            attributes={'id': 'load_map'}
        )

        context = {
            'platform_select': platform_select,
            'sensor_select': sensor_select,
            'product_select': product_select,
            'start_date': start_date,
            'end_date': end_date,
            'reducer_select': reducer_select,
            'ee_products': EE_PRODUCTS,
            'load_button': load_button,
        }

        return App.render(request, 'home.html', context)

2. Replace the contents of the `templates/earth_engine/home.html` template with the following:

.. code-block:: html+django

    {% extends tethys_app.package|add:"/base.html" %}
    {% load static tethys %}

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
    {% endblock %}

    {% block app_content %}
    {% endblock %}

    {# Use the after_app_content block for modals #}
    {% block after_app_content %}
      <div id="ee-products" data-ee-products="{{ ee_products|jsonify }}"></div>
    {% endblock %}

3. Test and Verify
==================

Browse to `<http://localhost:8000/apps/earth-engine>`_ in a web browser and login if necessary. Verify the following:

1. The content area should be blank and the controls should be located in the navigation pane on the left. If the navigation pane is not open, press the hamburger button to the left of the app logo and name to open it.
2. There should be six controls: **Satellite Platform**, **Sensor**, **Product**, **Start Date**, **End Date**, and **Reduction Method**.
3. Confirm that each control is being rendered with the values you expect.
4. Verify that the controls function properly (i.e. select controls display options in drop down when selected and the date picker appears when you select one of the date controls.
5. Notice that if you select a different satellite platform, the sensor options do not update. This is because we have not implemented the dynamic behaviour of the controls yet. We have used Tethys Gizmos to create the controls with their initial state, but we'll need to write some JavaScript to update the controls when the state of one changes. We'll do that in the next tutorial.

4. Solution
===========

This concludes this portion of the GEE Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-earth_engine/tree/dataset-controls-solution-3.0>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine
    cd tethysapp-earth_engine
    git checkout -b dataset-controls-solution dataset-controls-solution-|version|