.. _user_quotas_recipe:


***********
User Quotas
***********

**Last Updated:** September 2025

This recipe goes over adding and enforcing user quotas.  User workspace quotas can be used to restrict the amout of storage that an individual user has access to in the user workspace and user media locations. For more information on the Quotas API see the :ref:`Quotas API documentation <sdk_quotas_api>`

We'll start by going over how to add a generic user workspace quota:



1. Go to your tethys portal admin settings by clicking on your username in the top right corner, then on "Site Admin"
2. Scroll down until you find "Resource Quotas" and click on it, then open "User Workspace Quota"
3. Here you can set the default amount for user workspace quotas in your tethys portal and the help message that will appear if a user goes over the quota.
4. For the sake of this recipe change the default amount to "1.68e-06". This equates to about 1820 bytes. 
5. Make sure to select "Active" before hitting save on the bottom of the page.
6. App and User workspace quotas only apply to non-admin users, so make sure to create and log into a normal user account before continuing

Now that you've added and activated your quota, let's add a controller to your app to begin writing to the app workspace path. Since this controller is working with a shapefile, we'll be unzipping it in our controller into its individual inner files.

.. code-block:: python
    
    from tethys_sdk.routing import controller 
    import zipfile

    @controller(user_workspace=True)
    def page_controller(request, user_workspace)
        if request.method == 'POST':
            area_name = request.POST.get('area_name')
            shapefile = request.FILES.get('shapefile')

            area_path = user_workspace.path / area_name
            area_path.mkdir(parents=True, exist_ok=True) 

            file_path = area_path / shapefile.name

            with open(file_path 'wb+') as f:
                for chunk in shapefile.chunks():
                    f.write(chunk)

            with zipfile.ZipFile(file_path) as z:
                z.extractall(area_path)

            file_path.unlink(missing_ok=True)
            
        ... 

.. NOTE::
    For more information on geting user inputs like in this controller refer to the recipe :ref:`get_user_input_recipe`

After adding a shapefile to your user workspace, close your app and access your user profile page in the top right corner. Here, you can find the amount of storage currently you are using:

.. image:: ../../images/recipes/user_storage_usage.png
   :width: 100%
   :align: center

Continue adding shapefiles until you see a screen like this: 

.. image:: ../../images/recipes/exceeding_quotas.png
   :width: 100%
   :align: center

You can clear out this workspace by pressing "edit" towards the top of the page and then "Manage Storage" in the "Workspace" row.

.. image:: ../../images/recipes/user_workspace_manage_storage_button.png
   :width: 100%
   :align: center


For more information on using the Paths API to access the user workspace path, check out the :ref:`User Workspace Path Recipe <user_workspace_recipe>`, or the :ref:`Paths API documentation <tethys_paths_api>`