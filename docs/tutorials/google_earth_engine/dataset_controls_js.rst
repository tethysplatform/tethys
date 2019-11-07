*******************************************
Add JavaScript for Dynamic Control Behavior
*******************************************

**Last Updated:** November 2019

1. Stub out new JavaScript file
===============================

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

2. Include the new :file:`gee_datasets.js` script in the :file:`templates/earth_engine/home.html` template:

.. code-block:: html+django

    {% block scripts %}
      {{ block.super }}
      <script src="{% static 'earth_engine/js/gee_datasets.js' %}" type="text/javascript"></script>
    {% endblock %}

2. Implement Methods
====================

1. Implement the `bind_controls` method as follows:

.. code-block:: javascript

    bind_controls = function() {
        $('#platform').on('change', function() {
            let platform = $('#platform').val();

            if (platform !== m_platform) {
                m_platform = platform;
                console.log(`Platform Changed to: ${m_platform}`);
                // TODO: Update the sensor options when platform changes
            }
        });

        $('#sensor').on('change', function() {
            let sensor = $('#sensor').val();

            if (sensor !== m_sensor) {
                m_sensor = sensor;
                console.log(`Sensor Changed to: ${m_sensor}`);
                // TODO: Update the product options when sensor changes
            }
        });

        $('#product').on('change', function() {
            let product = $('#product').val();

            if (product !== m_product) {
                m_product = product;
                console.log(`Product Changed to: ${m_product}`);
                // TODO: Update the valid date range when product changes
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




2. Implement the `update_sensor_options` method as follows:

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

3. Implement the `update_product_options` method as follows:

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

4. Implement the `update_date_bounds` method as follows:

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

5. Add the new methods to the appropriate change events in the `bind_controls` method as follows:

.. code-block:: javascript

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

6. Implement the `collect_data` method as follows:

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

7. Bind to the click event of the `load_map` button by adding the following to the bottom of the `bind_controls` method:

.. code-block:: javascript

    $('#load_map').on('click', function() {
        let data = collect_data();
        console.log(data);
    });

