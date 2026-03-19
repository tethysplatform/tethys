.. _add_post_api_recipe :

**********************
Add POST API Endpoint
**********************

**Last Updated:** March 2026

.. codeblock:: python

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


    else:
        return HttpResponseBadRequest('Only GET and POST requests are allowed.')