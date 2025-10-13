.. _user_workspace_recipe :

User Workspace
##############

**Last Updated:** September 2025

This recipe shows how to access the User Workspace Path using the Tethys Paths API.

The User Workspace Path is generally used for reading and writing user files at runtime.

For more information on other types of paths that can be used and more info on using the User Workspace path, see the :ref:`Paths API documentation <tethys_paths_api>`.

Writing to the User Workspace Path
**********************************

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

Reading from the User Workspace Path
************************************

Here is an example of a controller reading from the user_workspace path:

.. code-block:: python

    from tethys_sdk.routing import controller

    @controller(user_workspace=True)
    def page_controller(request, user_workspace):
        observations = {}
        file_name = 'last_observation.txt'
        with open(user_workspace.path / file_name, 'r') as f:
            for line in f:
                hour, value = line.strip().split(" - ")
                observations[hour] = value

        context = {"observations": observations}

        return App.render(request, "page_template.html", context)

Other Methods for Accessing the User Workspace Path
***************************************************

You can also access the User Workspace Path using the following functions:

.. code-block:: python

    from .app import App
    from django.contrib.auth.models import User 

    user_workspace_path = App.get_user_workspace(user).path

.. code-block:: python
    
    from tethys_sdk.paths import get_user_workspace
    from .app import App
    
    def some_function(user):
        user_workspace_path = get_user_workspace(App, user).path

    def some_controller(request):
        user_workspace_path = get_user_workspace(App, request.user).path
