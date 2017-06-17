********
REST API
********

REST API's in Tethys Platform use token authentication
(see: http://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication).

You can find the API token for your user on the user management page
(http://[HOST_Portal]/user/[username]/).

Example Url Map (app.py)::

    UrlMap(name='api_get_data',
           url='[your_app_name]/api/get_data',
           controller='[your_app_name].api.get_data')


Example API Controller (api.py)::

    from django.http import JsonResponse
    from rest_framework.authentication import TokenAuthentication
    from rest_framework.decorators import api_view, authentication_classes

    @api_view(['GET'])
    @authentication_classes((TokenAuthentication,))
    def get_data(request):
        '''
        API Controller for getting data
        '''
        name = request.GET.get('name')
        data = {"name": name}
        return JsonResponse(data)


Example Accessing Data::

    >>> import requests
    >>> res = requests.get('http://[HOST_Portal]/apps/[your_app_name]/api/get_data?name=oscar',
                           headers={'Authorization': 'Token asdfqwer1234'})
   >>> da.text
   '{"name": "oscar"}'
