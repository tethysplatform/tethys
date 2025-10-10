.. _paths_api_recipe :


*********
Paths API
*********

**Last Updated:** September 2025

This recipe shows how to make use of the Tethys Paths API.

With the Paths API you can provide controllers and handlers access to different paths within your app storage.

For more information on each type of path see the :ref:`Paths API documentation <tethys_paths_api>`.

The Tethys paths can easily be accessed by specifying arguments to the various routing decorators. You'll also need to specify the argument in the controller function itself in order for it to be passed into the controller function

Writing to Paths
################

Here is an example of a controller writing to the user_workspace path:

.. code-block:: python

    from tethys_sdk.routing import controller

    @controller(user_workspace=True)
    def page_controller(request, user_workspace) 
        date = request.POST.get('date')
        temperature_data = request.POST.get('weather_data').split(',')

        file_name = f'temperatures_{date}.txt'
        with open(user_workspace.path / file_name, 'wb') as f:
            hour = 0

            for temp in temperature_data:
                if hour < 10:
                    hour_string = f'0{hour}'
                else: 
                    hour_string = str(hour)
                f.write(f'{hour_string}:00 - {temp}')
                hour += 1
            f.close()

Reading from Paths
##################

Here is an example of a controller reading from the app_workspace path:

.. code-block:: python

    from tethys_sdk.routing import controller
    
    @controller(app_workspace=True)
    def page_controller(request, app_workspace):
        observations = {}
        file_name = 'last_observation.txt'
        with open(app_workspace.path / file_name, 'r') as f:
            for line in f:
                hour, value = line.strip().split(" - ")
                observations[hour] = value

        context = {"observations": observations}

        return App.render(request, "page_template.html", context)

You can use this or similar code to access the other types of Paths as well.


Other Methods for Accessing Paths
#################################

You can also access these paths using the following functions:

.. code-block:: python

    from .app import App
    from django.contrib.auth.models import User 

    user = User.objects.get(id=1)
    app_workspace = App.get_app_workspace()
    user_workspace = App.get_user_workspace(user)
    app_media = App.get_app_media()
    user_media = App.get_user_media(user)
    app_public = App.public_path
    app_resources = App.resources_path





