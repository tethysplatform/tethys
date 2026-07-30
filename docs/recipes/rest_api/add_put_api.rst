.. _add_put_api_recipe:

**********************
Add a PUT API Endpoint
**********************

**Last Updated:** June 2026

Prerequisite: :ref:`Add a REST API<add_rest_api_recipe>`

Now that you've added a GET endpoint to access and retrieve your data, let's add some PUT functionality.

While a GET endpoint allows you to retrieve data and a POST endpoint allows you to create new data, a PUT endpoint allows you to update existing data.

For this example, we'll add PUT functionality that allows users to update the value and count associated with an existing date.

Begin by adding on to the ``daily_data`` controller/endpoint as such:

.. code-block:: python

    @controller(url='api/daily-data', login_required=False)
    @api_view(['GET', 'PUT'])
    @authentication_classes((TokenAuthentication,))
    def daily_data(request):
        ...
        elif request.method == 'PUT':
            request_params = request.data
            date = request_params.get("date", None)
            value = request_params.get("value", None)
            count = request_params.get("count", None)

            if not date or value is None or count is None:
                return HttpResponseBadRequest(
                    'Missing required parameters: date, value, and count are required.'
                )

            try:
                count = int(count)
            except ValueError:
                return HttpResponseBadRequest(
                    'Invalid parameter: count must be an integer.'
                )

            try:
                value = float(value)
            except ValueError:
                return HttpResponseBadRequest(
                    'Invalid parameter: value must be a number.'
                )

            with DATA_FILE.open("r", encoding="utf-8") as f:
                date_data = json.load(f)

            if date not in date_data:
                return HttpResponseBadRequest(
                    f'Data for date {date} does not exist.'
                )

            date_data[date] = {
                "value": value,
                "count": count
            }

            with DATA_FILE.open("w", encoding="utf-8") as f:
                json.dump(date_data, f, indent=4)

            return JsonResponse(
                {
                    "message": f"Data for date {date} has been updated successfully."
                },
                status=200
            )

Now, let's test your PUT endpoint. We can do so using Postman again by following these steps:

1. Right-click on the *My REST API* collection or click on its "**...**" button and select **Add Request**.

2. Name the new request "put-daily-data" and press the **Save to My REST API** button.

3. From the menu on the left, expand the *My REST API* collection and click on the *put-daily-data* request to open it in a new tab.

4. Select **PUT** as the method and enter:

   ::

      http://localhost:8000/apps/rest-api-app/api/daily-data/

   in the URL field.

5. Click on the **Body** tab, select **raw**, and choose **JSON** from the dropdown menu. Enter the following JSON:

.. code-block:: json

    {
        "date": "3-11-2026",
        "value": 32.65,
        "count": 129
    }

This request specifies the existing date you would like to update, along with the new values that should be stored for that date.

6. Navigate to ``http://localhost:8000/apps/`` and sign in if necessary.

7. Click on the button with your username in the top-right-hand corner of the page to access your user profile.

8. Copy the value of the API Key.

9. In Postman, click on the **Authorization** tab just under the URL field.

10. Select **API Key** as the **Type** and enter:

    * **Key:** Authorization
    * **Value:** Token <your token>

    Replace ``<your token>`` with the API key you copied from your profile.

11. Press the **Send** button. The request should be sent with the proper authorization and the JSON body you created. You should receive a response similar to:

.. code-block:: json

    {
        "message": "Data for date 3-11-2026 has been updated successfully."
    }

If you inspect the ``daily_data.json`` file, you should see that the values associated with the specified date have been updated.

You've now learned how to create a functioning PUT endpoint and tested it using Postman. You can now use this endpoint in your app to update existing data.

To learn more about how to use REST API endpoints in your frontend, check out the :ref:`use_rest_api_javascript_recipe` recipe.

To learn how to create a POST endpoint that allows you to create new data, check out the :ref:`add_post_api_recipe` recipe.
