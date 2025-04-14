*******************************************
Add JavaScript for Dynamic Control Behavior
*******************************************

**Last Updated:** July 2024

In this tutorial you will add dynamic behavior to the dataset controls created in the previous step using JavaScript. The following topics will be reviewed in this tutorial:

* JavaScript Fundamentals
* JavaScript Closure Module Method
* Using JavaScript with Tethys Gizmos

.. figure:: ../../../images/tutorial/gee/dataset_controls_js.png
    :width: 800px
    :align: center

0. Start From Previous Solution (Optional)
==========================================

If you wish to use the previous solution as a starting point:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine
    cd tethysapp-earth_engine
    git checkout -b dataset-controls-solution dataset-controls-solution-|version|

1. Stub out new JavaScript file
===============================

In this step you'll learn how to create a JavaScript module using the closure method. For more on JavaScript closures see: `JavaScript Closures - MDN <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures>`_. The basic module developed in this step will contain variables for storing the current value of each control and it will also read in the ``EE_PRODUCTS`` data you embedded in the template in the previous tutorial.

1. Create a new JavaScript file at :file:`public/js/gee_datasets.js` with the following contents:

.. code-block:: javascript

    var GEE_DATASETS = (function() {
        // Wrap the library in a package function
        "use strict"; // And enable strict mode for this library

        /************************************************************************
        *                      MODULE LEVEL / GLOBAL VARIABLES
        *************************************************************************/
        var MODIS = 'modis',
            SENTINEL = 'sentinel',
            LANDSAT = 'landsat',
            INITIAL_START_DATE,
            INITIAL_END_DATE,
            EE_PRODUCTS;

        var public_interface;

        // Selector Variables
        var m_platform,
            m_sensor,
            m_product,
            m_start_date,
            m_end_date,
            m_reducer;

        /************************************************************************
        *                    PRIVATE FUNCTION DECLARATIONS
        *************************************************************************/
        // Dataset Select Methods
        var bind_controls, update_product_options, update_sensor_options, update_date_bounds, collect_data;

        /************************************************************************
        *                    PRIVATE FUNCTION IMPLEMENTATIONS
        *************************************************************************/
        // Dataset Select Methods
        bind_controls = function() {};

        update_sensor_options = function() {};

        update_product_options = function() {};

        update_date_bounds = function() {};

        collect_data = function() {};

        /************************************************************************
        *                            PUBLIC INTERFACE
        *************************************************************************/
        public_interface = {};

        /************************************************************************
        *                  INITIALIZATION / CONSTRUCTOR
        *************************************************************************/
        $(function() {
            // Initialize Global Variables
            bind_controls();

            // Initialize Constants
            EE_PRODUCTS = $('#ee-products').data('ee-products');
            INITIAL_START_DATE = m_start_date = $('#start_date').val();
            INITIAL_END_DATE = m_end_date = $('#end_date').val();

            // Initialize members
            m_platform = $('#platform').val();
            m_sensor = $('#sensor').val();
            m_product = $('#product').val();
            m_reducer = $('#reducer').val();
        });

        return public_interface;

    }()); // End of package wrapper


.. note::

    The lines that define empty functions (e.g.: ``bind_controls = function() {};``) are method stubs that will be implemented in the following steps.

2. Include the new :file:`gee_datasets.js` script in the :file:`templates/earth_engine/home.html` template:

.. code-block:: html+django

    {% block scripts %}
      {{ block.super }}
      <script src="{% static tethys_app|public:'js/gee_datasets.js' %}" type="text/javascript"></script>
    {% endblock %}

2. Implement Methods
====================

In this step you'll implement the methods in the :file:`public/js/gee_datasets.js` file that will update the options in the dataset controls dynamically. For example when the user selects a new Satellite Platform, the options of the Sensor select box will be updated to the sensors for that platform. The general approach will be to:

* Create functions that update the controls with the currently saved values.
* Save the value of a control anytime it changes.
* Call the appropriate update functions when a control's value changes.

Here is a brief explanation of each method that will be implemented in this step:

* **update_sensor_options**: updates the options of the sensor select box with options that correspond with the current satellite platform.
* **update_product_options**: updates the options of the product select box with options that correspond with the current satellite platform and sensor.
* **update_date_bounds**: updates the date range that is selectable for both date pickers based on the current product. The value of each date picker is also reset to fit within the new range if necessary.
* **bind_controls**: used to bind the update methods to the ``change`` event of each control. Called when the module initializes after page load.
* **collect_data**: used to collect the current values of all of the controls, as stored in our module, for use in our request for the map imagery later on.

1. **Replace** the ``update_sensor_options`` method stub in :file:`public/js/gee_datasets.js` with the following implementation:

.. code-block:: javascript

    update_sensor_options = function() {
        if (!m_platform in EE_PRODUCTS) {
            alert('Unknown platform selected.');
        }

        // Clear sensor options
        $('#sensor').select2().empty();

        // Set the Sensor Options
        let first_option = true;
        for (var sensor in EE_PRODUCTS[m_platform]) {
            let sensor_display_name = sensor.toUpperCase();
            let new_option = new Option(sensor_display_name, sensor, first_option, first_option);
            $('#sensor').append(new_option);
            first_option = false;
        }

        // Trigger a sensor change event to update select box
        $('#sensor').trigger('change');
        update_date_bounds();
    };

2. **Replace** the ``update_product_options`` method stub in :file:`public/js/gee_datasets.js` with the following implementation:

.. code-block:: javascript

    update_product_options = function() {
        if (!m_platform in EE_PRODUCTS || !m_sensor in EE_PRODUCTS[m_platform]) {
            alert('Unknown platform or sensor selected.');
        }

        // Clear product options
        $('#product').select2().empty();

        let first_option = true;

        // Set the Product Options
        for (var product in EE_PRODUCTS[m_platform][m_sensor]) {
            let product_display_name = EE_PRODUCTS[m_platform][m_sensor][product]['display'];
            let new_option = new Option(product_display_name, product, first_option, first_option);
            $('#product').append(new_option);
            first_option = false;
        }

        // Trigger a product change event to update select box
        $('#product').trigger('change');
        update_date_bounds();
    };

3. **Replace** the ``update_date_bounds`` method stub in :file:`public/js/gee_datasets.js` with the following implementation:

.. code-block:: javascript

    update_date_bounds = function() {
        // Get new date picker bounds for the current product
        let earliest_valid_date = EE_PRODUCTS[m_platform][m_sensor][m_product]['start_date'];
        let latest_valid_date = EE_PRODUCTS[m_platform][m_sensor][m_product]['end_date'];

        // Get current values of date pickers
        let current_start_date = $('#start_date').val();
        let current_end_date = $('#end_date').val();

        // Convert to Dates objects for comparison
        let date_evd = Date.parse(earliest_valid_date);
        let date_lvd = Date.parse(latest_valid_date) ? (latest_valid_date) : Date.now();
        let date_csd = Date.parse(current_start_date);
        let date_ced = Date.parse(current_end_date);

        // Don't reset currently selected dates if they fall within the new date range
        let reset_current_dates = true;

        if (date_csd >= date_evd && date_csd <= date_lvd && date_ced >= date_evd && date_ced <= date_lvd) {
            reset_current_dates = false;
        }

        // Update start date datepicker bounds
        $('#start_date').datepicker('setStartDate', earliest_valid_date);
        $('#start_date').datepicker('setEndDate', latest_valid_date);
        if (reset_current_dates) {
            $('#start_date').datepicker('update', INITIAL_START_DATE);
            m_start_date = INITIAL_START_DATE;
        }

        // Update end date datepicker bounds
        $('#end_date').datepicker('setStartDate', earliest_valid_date);
        $('#end_date').datepicker('setEndDate', latest_valid_date);
        if (reset_current_dates) {
            $('#end_date').datepicker('update', INITIAL_END_DATE);
            m_end_date = INITIAL_END_DATE;
        }

        console.log('Date Bounds Changed To: ' + earliest_valid_date + ' - ' + latest_valid_date);
    };

4. **Replace** the ``bind_controls`` method stub in :file:`public/js/gee_datasets.js` with the following implementation :

.. code-block:: javascript

    bind_controls = function() {
        $('#platform').on('change', function() {
            let platform = $('#platform').val();

            if (platform !== m_platform) {
                m_platform = platform;
                console.log(`Platform Changed to: ${m_platform}`);
                // Update the sensor options when platform changes
                update_sensor_options();
            }
        });

        $('#sensor').on('change', function() {
            let sensor = $('#sensor').val();

            if (sensor !== m_sensor) {
                m_sensor = sensor;
                console.log(`Sensor Changed to: ${m_sensor}`);
                // Update the product options when sensor changes
                update_product_options();
            }
        });

        $('#product').on('change', function() {
            let product = $('#product').val();

            if (product !== m_product) {
                m_product = product;
                console.log(`Product Changed to: ${m_product}`);
                // Update the valid date range when product changes
                update_date_bounds();
            }
        });

        $('#start_date').on('change', function() {
            let start_date = $('#start_date').val();

            if (start_date !== m_start_date) {
                m_start_date = start_date;
                console.log(`Start Date Changed to: ${m_start_date}`);
            }
        });

        $('#end_date').on('change', function() {
            let end_date = $('#end_date').val();

            if (end_date !== m_end_date) {
                m_end_date = end_date;
                console.log(`End Date Changed to: ${m_end_date}`);
            }
        });

        $('#reducer').on('change', function() {
            let reducer = $('#reducer').val();

            if (reducer !== m_reducer) {
                m_reducer = reducer;
                console.log(`Reducer Changed to: ${m_reducer}`);
            }
        });
    };

5. **Replace** the ``collect_data`` method stub in :file:`public/js/gee_datasets.js` with the following implementation:

.. code-block:: javascript

    collect_data = function() {
        let data = {
            platform: m_platform,
            sensor: m_sensor,
            product: m_product,
            start_date: m_start_date,
            end_date: m_end_date,
            reducer: m_reducer
        };
        return data;
    };

6. Temporarily log the result of ``collect_data`` when the user clicks on the **Load** button to verify that everything is working correctly. Add the following to the bottom of the ``bind_controls`` method in :file:`public/js/gee_datasets.js`:

.. code-block:: javascript

    $('#load_map').on('click', function() {
        let data = collect_data();
        console.log(data);
    });

3. Test and Verify
==================

Browse to `<http://localhost:8000/apps/earth-engine>`_ in a web browser and login if necessary. Verify the following:

1. Open a JavaScript console in your web browser (in Chrome press :kbd:`CTRL-SHIFT-i`  or :kbd:`F12` and select the **Console** tab).
2. Change the values of each control and note the output being logged to the console.
3. The value of the each control that changes should be logged. For example, when the **Satellite Platform** control is changed, the **Sensor**, **Product**, and date controls should be updated.
4. The **Start Date** control should not allow users to select dates before the beginning date of the selected dataset.
5. Press the **Load** button and inspect the object that is logged to the JavaScript console. It should display the currently selected values of each control.

4. Solution
===========

This concludes this portion of the GEE Tutorial. You can view the solution on GitHub at `<https://github.com/tethysplatform/tethysapp-earth_engine/tree/dataset-controls-js-solution-3.0>`_ or clone it as follows:

.. parsed-literal::

    git clone https://github.com/tethysplatform/tethysapp-earth_engine
    cd tethysapp-earth_engine
    git checkout -b dataset-controls-js-solution dataset-controls-js-solution-|version|