.. _use_rest_api_javascript :

********************************
Accessing an API with JavaScript
********************************

**Last Updated:** July 2026

Prerequisite: :ref:`Add a REST API<add_rest_api_recipe>`

Now that you've created a REST API, you can make use of it in your application's JavaScript code by making requests to the API.

Accessing the GET Endpoint
##########################

First, let's add a way for the user to select which date they'd like to access data from.

We'll use a DatePicker gizmo for this. Inside `controllers.py` your home controller add the following:

.. code-block:: python
        
    @controller
    def home(request):
        """
        Controller for the app home page.
        """

        day_picker = DatePicker(name='day_picker', display_text='Select a Date', autoclose=True, format='mm-dd-yyyy')
        context = {
            'day_picker': day_picker
        }

        return App.render(request, 'home.html', context)

Next, place this gizmo in your page inside `home.html` with a label we'll be using soon:

.. code-block:: html+django

    {% block app_content %}
        {% gizmo day_picker %}
        <p id="daily-data-display">Select a date to view daily data</p>
    {% endblock %}

Now we'll begin retreiving data from the API to display in your application dynamically using JavaScript.
Start by adding a file inside public/js named `daily_data.js` with the following code:

.. code-block:: javascript

    function getDailyData(date) {
    }

    function setDailyDataLabel(text) {
    } 

    $(document).ready(function() {
    });

Now you'll need to link to that JavaScript file inside your `home.html`:

.. code-block:: html+django

    {% block scripts %}
        {{ block.super }}
        <script type="text/javascript" src="{% static tethys_app|public:'js/daily_data.js' %}"></script>
    {% endblock %}

Now go back to `daily_data.js`. Before we start accessing the API let's test everything we've added so far:

.. code-block:: javascript

    function getDailyData(date) {
    }

    function setDailyDataLabel(text) {
    } 

    $(document).ready(function() {
        $("#day_picker").change(function() {
            let selectedDate = $(this).val();
            console.log(selectedDate);
        )
    });

Open your app and refresh the page and open your browser console. Each time you change the selected date in the date picker, you should see that date show up in the console.  

Next, we'll send a request to the API with the selected date. Begin by adding the following to your `getDailyData` function in `daily_data.js`

.. code-block:: javascript
    :emphasize-lines: 2-8

    function getDailyData(date) {
        return $.ajax({
            url: 'api/daily-data',
            type: 'GET',
            data: {
                date: date
            }
        });
    }

This function will now return a GET request to the API with a provided date as a parameter. However, now we need to specify what to do with the response form that request. 

Edit your JavaScript with the following changes:

.. code-block:: javascript
    :emphasize-lines: 4-14

    $(document).ready(function() {
        $("#day_picker").change(function() {
            let selectedDate = $(this).val();
            getDailyData(selectedDate)
                .done(function(data) {
                    console.log(data);
                })
                .fail(function(xhr) {
                    if (xhr.status === 404) {
                        console.log("No data available for ", selectedDate);
                    } else {
                        console.log("There was an issue retreiving data: ", xhr.statusText);
                    }
                })
        })
    })

Open your app and refresh the page again. Now instead of the date showing up in the console when you change the date picker, you should see the JSON response being displayed. 
If you select a date without data, you should see a message explaining that there is no data available for that date. 

Now that you have requests to the API working, let's make this output available to the user. For that, we'll add some functionality to setDailyDataLabel to show text on the page:

.. code-block:: javascript

    function setDailyDataLabel(text) {
        $("#daily-data-display").text(text);
    } 

Now, update your API call handling to use this function instead of logging to the console:

.. code-block:: javascript

    $(document).ready(function() {
        $("#day_picker").change(function() {
            let selectedDate = $(this).val();
            getDailyData(selectedDate)
                .done(function(data) {
                    setDailyDataLabel("Data for " + selectedDate + " - Count:  " + data.count + ", Value: " + data.value);
                })
                .fail(function(xhr) {
                    if (xhr.status === 404) {
                        setDailyDataLabel("No data available for " + selectedDate);
                    } else {
                        setDailyDataLabel("There was an issue retreiving data: " + xhr.statusText);
                    }
                })
        })
    });  

That's it! Open your app and refresh the page one more time. Now each time you change the date you should see text below showing either the data pulled from your API endpoint or an error message.

