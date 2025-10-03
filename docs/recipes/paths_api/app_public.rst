.. _app_public_recipe :

App Public
##########

**Last Updated:** September 2025

This recipe shows how to access the App Public Path using the Tethys Paths API.

The App Public Path is generally used for reading static files for the app. This will generally mean things like public images used in the app, but can even include assets like CSS or JavaScript files.

For more information on other types of paths that can be used and more info on using the App Public path, see the :ref:`Paths API documentation <tethys_paths_api>`

Reading from the App Public Path
********************************

Here is an example of a controller reading from the App Public Path


.. code-block:: python

    from tethys_sdk.routing import controller
    
    @controller(name='get_app_icon', 'app_icon', app_public=True)
    def get_app_icon_image(request, app_public):
        if request.method == "GET":
            file_path = app_public.path / "app_icon.jpg"

            return FileResponse(open(file_path), "rb", content_type="image/jpeg")

Other Methods for Accessing the App Public Path
***************************************************

You can also access the App Public Path using the following functions/properties:

.. code-block:: python

    from .app import App 

    app_public_path = App().public_path.path

.. code-block:: python
    
    from tethys_sdk.paths import get_app_public
    from .app import App

    def some_controller(request):
        app_public_path = get_app_public(request).path