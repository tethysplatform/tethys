.. _app_workspace_recipe :

App Workspace
#############

**Last Updated:** September 2025

This recipe shows how to access the App Workspace path using the Tethys Paths API.

The app workspace path is generally used for the app to read and write files at runtime.

For more information on other types of paths that can be used and more info on using the App Workspace path, see the :ref:`Paths API documentation <tethys_paths_api>`.

Writing to the App Workspace Path
**********************************

Here is an example of a controller writing to the app_workspace path:

.. code-block:: python

    from tethys_sdk.routing import controller

    @controller(app_workspace=True)
    def page_controller(request, app_workspace) 
        date = request.POST.get('date')
        temperature_data = request.POST.get('weather_data').split(',')

        file_name = f'temperatures_{date}.txt'
        with open(app_workspace.path / file_name, 'wb') as f:
            hour = 0

            for temp in temperature_data:
                if hour < 10:
                    hour_string = f'0{hour}'
                else: 
                    hour_string = str(hour)
                f.write(f'{hour_string}:00 - {temp}')
                hour += 1
            f.close()

Reading from the App Workspace Path
************************************

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

Other Methods for Accessing the App Workspace Path
***************************************************

You can also access the App Workspace Path using the following functions:

.. code-block:: python

    from .app import App

    app_workspace_path = App.get_app_workspace().path

.. code-block:: python
    
    from tethys_sdk.paths import get_app_workspace
    from .app import App
    
    def some_function():
        app_workspace_path = get_app_workspace(App).path

    def some_controller(request):
        app_workspace_path = get_app_workspace(request).path