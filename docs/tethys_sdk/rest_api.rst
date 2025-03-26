.. _tethys_rest_api:

********
REST API
********

.. important::

    This feature requires the ``djangorestframework`` library to be installed. Starting with Tethys 5.0 or if you are using ``micro-tethys-platform``, you will need to install ``djangorestframework`` using conda or pip as follows:

    .. code-block:: bash

        # conda: conda-forge channel strongly recommended
        conda install -c conda-forge djangorestframework

        # pip
        pip install djangorestframework

    **Don't Forget**: If you end up using this feature in your app, add ``djangorestframework`` as a requirement to your :file:`install.yml`.

REST API's in Tethys Platform use token authentication (see: https://www.django-rest-framework.org/api-guide/authentication/).

You can find the API token for your user on the user management page (http://[HOST_Portal]/user/[username]/).

Example API Controller (api.py):

.. code-block:: python

    from django.http import JsonResponse
    from rest_framework.authentication import TokenAuthentication
    from rest_framework.decorators import api_view, authentication_classes
    from tethys_sdk.routing import controller

    @controller(url='api/get-data')
    @api_view(['GET', 'POST'])
    @authentication_classes((TokenAuthentication,))
    def get_time_series(request):
        """
        Controller for the get-time-series REST endpoint.
        """
        name = request.GET.get('name', None)
        response_data = {'name': name}
        return JsonResponse(response_data)

Example Accessing Data:

.. code-block:: python

    >>> import requests
    >>> res = requests.get('http://[HOST_Portal]/apps/[your_app_name]/api/get-data?name=oscar',
                           headers={'Authorization': 'Token asdfqwer1234'})
    >>> da.text
    '{"name": "oscar"}'
