from tethys_sdk.base import TethysExtensionBase, url_map_maker


class TestExtension(TethysExtensionBase):
    """
    Tethys extension class for Test Extension.
    """

    name = 'Test Extension'
    package = 'test_extension'
    root_url = 'test-extension'
    description = 'Place a brief description of your extension here.'

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='test-extension/{var1}/{var2}',
                controller='test_extension.controllers.home'
            ),
        )

        return url_maps
