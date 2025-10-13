.. _user_media_recipe :

User Media
**********

**Last Updated:** September 2025

This recipe shows how to access the User Media Path using the Tethys Paths API.

The User Media Path is generally used for reading and writing publicly accessible information.

For more information on other types of paths that can be used and more info on using the User Media Path, see the :ref:`Paths API documentation <tethys_paths_api>`.

Writing to the User Media Path
##############################

.. code-block:: python

    from tethys_sdk.routing import controller
    
    @controller(name='profile_view', url='profile_view', user_media=True)
    def profile_view(request, user_media)
        if request.method == "POST":
            profile_pic = request.FILES.get("profile_picture")

            destination = user_media.path / "profile_picture.png"
            with destination.open("wb") as destination_file:
                for chunk in profile_pic.chunks():
                    destination_file.write(chunk)


Reading from the User Media Path
################################

.. code-block:: python

    from django.http import FileResponse
    from tethys_sdk.routing import controller

    @controller(name='profile_picture', url='profile_picture', user_media=True)
    def get_profile_picture(request, user_media):
        file_path = user_media.path / "profile_picture.png"
        return FileResponse(open(file_path, "rb"), content_type="image/png")



Other Methods for Accessing the User Media Path
***************************************************

You can also access the User Media Path using the following functions:

.. code-block:: python

    from .app import App
    from django.contrib.auth.models import User 

    user_media_path = App.get_user_media(user).path

.. code-block:: python
    
    from tethys_sdk.paths import get_user_media
    from .app import App
    
    def some_function(user):
        user_media_path = get_user_media(App, user).path

    def some_controller(request):
        user_media_path = get_user_media(App, request.user).path