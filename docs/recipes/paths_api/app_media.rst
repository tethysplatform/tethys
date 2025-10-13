.. _app_media_recipe :

App Media
*********

**Last Updated:** September 2025

This recipe shows how to access the App Media Path using the Tethys Paths API.

The App Media Path is generally used for reading and writing publicly accessible information.

For more information on other types of paths that can be used and more info on using the App Media Path, see the :ref:`Paths API documentation <tethys_paths_api>`

Writing to the App Media Path
#############################

.. code-block:: python

    from tethys_sdk.routing import controller
    
    @controller(name='site_images', url='site_images/', app_media=True)
    def site_images(request, app_media):
        if request.method == "POST":
            image_file = request.FILE.get("image")

            destination = app_media.path / image_file.name
            with destination.open("wb") as f:
                for chunk in image_file.chunks():
                    f.write(chunk)

Reading from the App Media Path
###############################

.. code-block:: python

    from tethys_sdk.routing import controller
    
    @controller(name='site_images', url='site_images/', app_media=True)
    def site_images(request, app_media):
        if request.method == "GET":
            file_name = request.GET.get("file_name")
            
            file_path = app_media.path / file_name

            extension_type = file_path.suffix.lower()
            if extension_type == ".png":
                content_type = "image/png"
            elif extension_type in [".jpg", ".jpeg"]:
                content_type = "image/jpeg"
            elif extension_type == ".gif":
                content_type = "image/gif"
            else:
                content_type = "application/octet-stream"

            return FileResponse(open(file_path, "rb"), content_type=content_type)

Other Methods for Accessing the App Media Path
##############################################

You can also access the App Media Path using the following functions:

.. code-block:: python

    from .app import App

    app_media_path = App.get_app_media().path

.. code-block:: python
    
    from tethys_sdk.paths import get_app_media
    
    def some_controller(request):
        app_media_path = get_app_media(request).path
        
