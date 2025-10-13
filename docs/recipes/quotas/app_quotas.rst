.. _app_quotas_reicpe:


**********
App Quotas
**********

**Last Updated:** September 2025

This recipe goes over adding and enforcing an app workspace quota. An app workspace quota will make sure that users cannot use too much storage space in the app workspace and app media locations. For more information on the Quotas API see the  :ref:`Quotas API documentation <sdk_quotas_api>`


We'll start by going over how to add a generic app workspace quota:

1. Go to your tethys portal admin settings by clicking on your username in the top right corner, then on "Site Admin"
2. Scroll down until you find "Resource Quotas" and click on it, then open "TethysApp Workspace Quota"
3. Here you can set the default amount for app workspace quotas in your tethys portal and the help message that will appear if a user goes over the quota.
4. For the sake of this recipe change the default amount to "2e-07". This equates to about 214 bytes. 
5. Make sure to select "Active" before hitting save on the bottom of the page.
6.  App and User workspace quotas only apply to non-admin users, so make sure to create and log into a normal user account before continuing

Now that you've added and activated your quota, let's add a controller to your app to begin writing to the app workspace path

.. code-block:: python

    from tethys_sdk.routing import controller
    
    @controller(app_workspace=True)
    def page_controller(request, app_workspace) 
        if request.method == 'POST':
            date = request.POST.get('date')
            temperature_file = request.files.get('temperature_file')
            
            temperature_contents = temperature_file.read().decode('utf-8')
            temperature_data = temperate_data.strip().split(',')

            file_name = f'temperatures_{date}.txt'
            with open(app_workspace.path / file_name, 'w') as f:
                hour = 0

                for temp in temperature_data:
                    if hour < 10:
                        hour_string = f'0{hour}'
                    else: 
                        hour_string = str(hour)
                    f.write(f'{hour_string}:00 - {temp}')
                    hour += 1
                f.close()
                
        ...

.. NOTE:: 
    For more information on getting user inputs like in this controller refer to the :ref:`Get User Input Recipe<get_user_input_recipe>`

After adding some data to your app workspace directory, go back to your site admin page. Scroll down until you find "Installed Apps" and click on it. 

Select your app name and find the total storage you've used here

.. image:: ../../images/recipes/quotas-amount-screenshot.png
   :width: 100%
   :align: center

Continue adding data until you see a screen like this:

.. image:: ../../images/recipes/exceeding_quotas.png
   :width: 100%
   :align: center

You can clear out this workspace by logging back into your admin account and accessing the site admin page. Scroll down to "Installed Apps", and click on your app's name. Then just click "Clear Workspace".

.. image:: ../../images/recipes/app_workspace_clear_button.png
   :width: 100%
   :align: center


For more information on using the Paths API to access the app workspace path, check out the :ref:`App Workspace Path Recipe <app_workspace_recipe>`
, or the :ref:`Paths API documentation <tethys_paths_api>`