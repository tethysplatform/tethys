.. _add_post_api_recipe:

*********************
Add POST API Endpoint
*********************

**Last Updated:** March 2026

Prerequisite: :ref:`Add a REST API<add_rest_api_recipe>`

Now that you've added a GET endpoint to access and retreive your data, let's add some POST functionality.

While a GET endpoint allows you to access or retreive data, a POST endpoint allows you to add to your data.

For this example, we'll add POST functionality that allows users to submit data for new dates. 

Begin by adding on to the daily_data controller/endpoint as such:

.. code-block:: python

    @controller(url='api/daily-data', login_required=False)
    @api_view(['GET', 'POST'])
    @authentication_classes((TokenAuthentication,))
    def daily_data(request):
        ...
        elif request.method == 'POST':
            request_params = request.POST.copy()
            date = request_params.get("date", None)
            value = request_params.get("value", None)
            count = request_params.get("count", None)
            if not date or not value or not count:
                return HttpResponseBadRequest('Missing required parameters: date, value, and count are required.')
            try:
                count = int(count)
            except ValueError:
                return HttpResponseBadRequest('Invalid parameter: count must be an integer.')
            
            try:
                value = float(value)
            except ValueError:
                return HttpResponseBadRequest('Invalid parameter: value must be a number.')
            
            with DATA_FILE.open("r", encoding="utf-8") as f:
                date_data = json.load(f)
            available_dates = date_data.keys()

            if date in available_dates:
                return HttpResponseBadRequest(f'Data for date {date} already exists. Use a different date.')

            date_data[date] = {"value": value, "count": count}
            with DATA_FILE.open("w", encoding="utf-8") as f:
                json.dump(date_data, f, indent=4)

            return JsonResponse({"message": f"Data for date {date} has been added successfully."}, status=201)


Now, let's test your POST endpoint. We can do so using Postman again by following these steps:

1. Right-click on the *My REST API* collection or click on it's "**...**" button and select **Add Request**.

2. Name the new request "post-daily-data" and press the **Save to My REST API** button.

3. From the menu on the left, expand the *My REST API* collection and click on the *post-daily-data* request to open it in a new tab.

4. Selct **POST** as the method and enter the folloing URL in the URL field:

   ::

      http://localhost:8000/apps/rest-api-app/api/daily-data/  
      
    

5. Click on the **Body** button just under the URL field and then select "form-data" add the following key/value pairs:

    - date: 3-14-2026
    - value: 29.23
    - count: 162

This will add parameters to your request that specify the date for which you're adding data, along with the values you'd like assigned to that date.

6. Navigate to `<http://localhost:8000/apps/>`_ and sign in if necessary.

7. Click on the button with your username on it in the top-right-hand corner of the page to access your user profile.

8.  Copy the value of the API Key.

9. In Postman, click on the Authorization tab, just under the URL field.

10. Select "API Key" as the **TYPE** and enter:
    * **Key:** Authorization 
    * **Value:** "Token <your token>" (
        
    Replace ``<your token>`` with the API key you copied from your profile.

11. Press the **Send** button. The request should be sent with the proper authorization and with the data you've added to the body. You should see a response with the following message: 

.. code-block:: json
    
    {
        "message": "Data for date 3-14-2026 has been added successfully."
    }

You've now learned how to create a functioning POST endpoint and tested it using Postman. You can now use this endpoint in your app to add new data.

To learn more about how to use REST API endpoints in your frontend, check out the :ref:`use_rest_api_javascript_recipe` recipe.

To learn how to create a PUT endpoint that allows you to update data, check out the :ref:`add_put_api_recipe` recipe.
