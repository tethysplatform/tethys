.. _custom_settings_recipe :

***************
Custom Settings
***************

**Last Updated:** February 2026

This recipe will show you how to create custom settings for your app.  You can create custom settings for your app that can be configured on the app settings page in Tethys Portal.  You can utilize the values of these custom settings inside your app.

Open the :file:`app.py` file, import custom settings, and add the ``custom_settings`` method to your app class.

.. code-block:: python

    from tethys_sdk.app_settings import CustomSetting

    class MyApp(TethysAppBase):
        ...
        def custom_settings(self):
            """
            Example custom settings.
            """
            default_map_context_setting = CustomSetting(
                name='default_map_extent',
                type=CustomSetting.TYPE_STRING,
                description='Default Map Extent',
                required=False,
                default='-125,25,-66,49',
            )

            return (default_map_context_setting)



