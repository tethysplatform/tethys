.. _add_rest_api_recipe :

**************
Add a REST API
**************

**Last Updated:** March 2026

In this recipe, you'll learn how to add a REST API endpoint to your Tethys application. 
The REST API will provide an access point to your data. This can be used in your front end to access the data in your backend.

For this, we'll be creating special `controllers` that are referred to as 'endpoints'. These endpoints can be accessed by 
making a request to the URL that is associated with the endpoint. Instead of returning HTML, endpoints return data in the form of JSON or XML. 
For this example, your endpoints will return JSON data. 

Endpoints can also serve as an access point for your data to be edited or updated. 
This is done by making a POST request to the endpoint with the data that you want to update or edit.

In this recipe, you'll learn how to create a GET endpoint. The GET endpoint will return some data in JSON format, and the POST endpoint will allow you to update that data.

1. Install the Django REST framework package
Before you can begin adding a REST API, you'll need to install the Django REST framework package. 

You can install this package using either conda or pip as follows:

.. code-block:: bash

    # conda: conda-forge channel strongly recommended
    conda install -c conda-forge djangorestframework

    # pip
    pip install djangorestframework

You can add this package to your app's dependencies in the install.yml file like so:

.. code-block:: yaml

    # This file should be committed to your app code.
    version: 1.0
    # This should be greater or equal to your tethys-platform in your environment
    tethys_version: ">=4.0.0"
    # This should match the app - package name in your setup.py
    name: rest_api_app

    requirements:
        # Putting in a skip true param will skip the entire section. Ignoring the option will assume it be set to False
        skip: false
        conda:
            channels:
            - conda-forge
            packages: 
            - djangorestframework
        pip:

        npm:

    post:
 
2. Create a REST API endpoint

Next, you'll need to create a REST API endpoint. This is done by creating a new controller function. 
Common practice is to create a new file called `api.py` in your app's controllers directory to hold all of your REST API endpoints. 
If you would like to do so, create a new folder called :file:`controllers` inside your app directory with the following new empty Python modules in it:

* :file:`controllers/`
    * :file:`__init__.py`
    * :file:`controllers.py`
    * :file:`api.py`

Move your existing controller functions to the :file:`controllers.py` module. 

Next, create a folder called :file:`data` and add this :download:`example data file<./resources/daily_data.json>` to it. 
This file will be used in the REST API endpoint that you'll create in the next step to provide data.


Then, add the following code to the :file:`api.py` module to create a new REST API endpoint:

.. code-block:: python

    from django.http import HttpResponseBadRequest, JsonResponse
    from tethys_sdk.routing import controller
    from rest_framework.authentication import TokenAuthentication
    from rest_framework.decorators import api_view, authentication_classes

    DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "daily_data.json"

    @controller(url='api/daily-data', login_required=False)
    @api_view(['GET'])
    @authentication_classes((TokenAuthentication,))
    def daily_data(request):
        """
        Controller for the daily-data REST endpoint.
        """
        if request.method == 'GET':
            request_params = request.GET.copy()
            date = request_params.get("date", None)
            
            with DATA_FILE.open("r", encoding="utf-8") as f:
                date_data = json.load(f)
            available_dates = date_data.keys()

            response_data = date_data[date]
            
            return JsonResponse(response_data)

This code creates a new REST API endpoint at the URL :code:`/api/daily-data`.

3. Test the REST API Endpoint

To more easily test your new API endpoint, you can use a tool like Postman. Follow the following instructions to get started with testing your API with Postman:

1. If you have not done so already, `download and install the Postman app <https://www.postman.com/>`_ and then launch it.

2. In Postman click on the **New** button and select **Collection**.

3. Name the collection "My REST API" and press the **Create** button.

4. Right-click on the new *My REST API* collection or click on it's "**...**" button and select **Add Request**.

5. Name the new request "get-daily-data" and press the **Save to My REST API** button.

6. From the menu on the left, expand the *My REST API* collection and click on the *get-daily-data* request to open it in a new tab.

7. Select **GET** as the method and enter "http://localhost:8000/apps/rest-api-app/api/daily-data/" in the URL field.

8. Click on the **Params** button just under the URL field and add a new key-value pair with "date" as the key and "02-16-2026" as the value. 
This will add a query parameter to your request that specifies the date for which you want to retrieve data.

9. Press the **Save** button to save changes. This will save the url and any details, like the date param that you send with 
this request as a configuration so you can easily send the same request again in the future.

10. Press the **Send** button. You should see a response similar to this:

.. code-block:: json

    {"detail":"Authentication credentials were not provided."}

This is because the endpoint you created requires authentication. To authenticate, you'll need to retreive your account's API token and include that token in the request header.

To retrieve your API token, follow these steps:

1. Navigate to `<http://localhost:8000/apps/>`_ and sign in if necessary.

2. Click on the button with your username on it in the top-right-hand corner of the page to access your user profile.

3. Copy the value of the API Key.

4. In Postman, click on the Authorization tab, just under the URL field.

5. Select "API Key" as the **TYPE** and enter "Authorization" for the **Key** and "Token <your token>" for the value (replace ``<your token>`` with the token you copied).

6. Press the **Send** button again. This time the request should be sent with the proper authorization token. 
You should see a response object with the data corresponding to the date you provided in the request.

7. Press the **Save** button to save your changes to the Postman request.

That's it! You've now created a functioning REST API endpoint and tested it using Postman. You can now use this endpoint in your front end to access the data in your backend.

To learn more about how to use REST API endpoints in your front end, check out the :ref:`use_rest_api_javascript_recipe` recipe.

To learn how to create a POST endpoint that allows you to update data, check out the :ref:`post_rest_api_recipe` recipe.

