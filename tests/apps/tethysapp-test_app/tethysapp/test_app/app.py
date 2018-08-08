from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.app_settings import CustomSetting


class TestApp(TethysAppBase):
    """
    Tethys app class for Test App.
    """

    name = 'Test App'
    index = 'test_app:home'
    icon = 'test_app/images/icon.gif'
    package = 'test_app'
    root_url = 'test-app'
    color = '#2c3e50'
    description = 'Place a brief description of your app here.'
    tags = ''
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='test-app',
                controller='test_app.controllers.home'
            ),
        )

        return url_maps

    def custom_settings(self):
        """
        Example custom_settings method.
        """
        custom_settings = (
          CustomSetting(
              name='default_name',
              type=CustomSetting.TYPE_STRING,
              description='Default model name.',
              required=True,
          ),
          CustomSetting(
              name='max_count',
              type=CustomSetting.TYPE_INTEGER,
              description='Maximum allowed count in a method.',
              required=False
          ),
          CustomSetting(
              name='change_factor',
              type=CustomSetting.TYPE_FLOAT,
              description='Change factor that is applied to some process.',
              required=True
          ),
          CustomSetting(
              name='enable_feature',
              type=CustomSetting.TYPE_BOOLEAN,
              description='Enable this feature when True.',
              required=True
          )
        )

        return custom_settings

