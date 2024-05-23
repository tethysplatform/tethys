***********************
UrlMaps and Controllers
***********************

**Last Updated:** February 22, 2018

Although ``UrlMaps`` and controllers defined in extensions are loaded, it is not recommended that you use them to load normal html pages. Rather, use ``UrlMaps`` in extensions to define REST endpoints that handle any dynamic calls used by your custom gizmos and templates. ``UrlMaps`` are defined in extensions in the ``ext.py`` in the same way that they are defined in apps:

::

    from tethys_sdk.base import TethysExtensionBase
    from tethys_sdk.routing import url_map_maker


    class Extension(TethysExtensionBase):
        """
        Tethys extension class for My First Extension.
        """
        name = 'My First Extension'
        package = 'my_first_extension'
        root_url = 'my-first-extension'
        description = 'This is my first extension.'

        def url_maps(self):
            """
            Map controllers to URLs.
            """
            UrlMap = url_map_maker(self.root_url)

            return (
                UrlMap(
                    name='get_data',
                    url='my-first-extension/rest/get-data',
                    controller='my_first_extension.controllers.get_data
                ),
            )

