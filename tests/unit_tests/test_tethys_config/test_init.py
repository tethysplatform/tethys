import unittest
from unittest import mock

from django.utils import timezone

from tethys_config.init import initial_settings, reverse_init, setting_defaults


class TestInit(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('tethys_config.init.setting_defaults')
    @mock.patch('tethys_config.init.SettingsCategory')
    def test_initial_settings(self, mock_settings, mock_defaults):
        mock_apps = mock.MagicMock()
        mock_schema_editor = mock.MagicMock()

        initial_settings(apps=mock_apps, schema_editor=mock_schema_editor)

        mock_settings.assert_any_call(name='General Settings')
        mock_settings(name='General Settings').save.assert_called()

        mock_settings.assert_any_call(name='Home Page')
        mock_settings(name='Home Page').save.assert_called()

        self.assertEqual(mock_defaults.call_count, 4)

    @mock.patch('tethys_config.init.SettingsCategory')
    def test_reverse_init(self, mock_categories):
        mock_apps = mock.MagicMock
        mock_schema_editor = mock.MagicMock()
        mock_cat = mock.MagicMock()
        mock_categories.objects.get.return_value = mock_cat

        reverse_init(apps=mock_apps, schema_editor=mock_schema_editor)

        self.assertEqual(mock_cat.delete.call_count, 4)

    @mock.patch('tethys_config.init.timezone')
    @mock.patch('tethys_config.init.SettingsCategory')
    def test_setting_defaults(self, mock_settings, mock_timezone):
        # Set known now
        now = timezone.now()
        mock_timezone.now.return_value = now

        # General settings
        type(mock_settings()).name = mock.PropertyMock(return_value="General Settings")
        setting_defaults(category=mock_settings())

        mock_settings().setting_set.create.assert_any_call(name="Site Title",
                                                           content="Tethys Portal",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Favicon",
                                                           content="/tethys_portal/images/"
                                                                   "default_favicon.png",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Brand Text",
                                                           content="Tethys Portal",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Brand Image",
                                                           content="/tethys_portal/images/"
                                                                   "tethys-logo-25.png",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Brand Image Height", content="",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Brand Image Width", content="",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Brand Image Padding",
                                                           content="",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Apps Library Title",
                                                           content="Apps",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Primary Color",
                                                           content="#0a62a9",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Secondary Color",
                                                           content="#7ec1f7",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Background Color", content="",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Primary Text Color", content="",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Primary Text Hover Color",
                                                           content="",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Secondary Text Color",
                                                           content="",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Secondary Text Hover Color",
                                                           content="",
                                                           date_modified=now)

        mock_settings().save.assert_called()

        # Home page settings
        type(mock_settings()).name = mock.PropertyMock(return_value="Home Page")
        setting_defaults(category=mock_settings())

        mock_settings().setting_set.create.assert_any_call(name="Hero Text",
                                                           content="Welcome to Tethys Portal,\nthe hub "
                                                                   "for your apps.",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Blurb Text",
                                                           content="Tethys Portal is designed to be "
                                                                   "customizable, so that you can host "
                                                                   "apps for your\norganization. You "
                                                                   "can change everything on this page "
                                                                   "from the Home Page settings.",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Feature 1 Heading",
                                                           content="Feature 1",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Feature 1 Body",
                                                           content="Use these features to brag about "
                                                                   "all of the things users can do "
                                                                   "with your instance of Tethys "
                                                                   "Portal.",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Feature 1 Image",
                                                           content="/tethys_portal/images/"
                                                                   "placeholder.gif",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Feature 2 Heading",
                                                           content="Feature 2",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Feature 2 Body",
                                                           content="Describe the apps and tools that "
                                                                   "your Tethys Portal provides and "
                                                                   "add custom pictures to each "
                                                                   "feature as a finishing touch.",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Feature 2 Image",
                                                           content="/tethys_portal/images/"
                                                                   "placeholder.gif",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Feature 3 Heading",
                                                           content="Feature 3",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Feature 3 Body",
                                                           content="You can change the color theme and "
                                                                   "branding of your Tethys Portal in "
                                                                   "a jiffy. Visit the Site Admin "
                                                                   "settings from the user menu and "
                                                                   "select General Settings.",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Feature 3 Image",
                                                           content="/tethys_portal/images/"
                                                                   "placeholder.gif",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Call to Action",
                                                           content="Ready to get started?",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Call to Action Button",
                                                           content="Start Using Tethys!",
                                                           date_modified=now)

        mock_settings().save.assert_called()

        # Custom Styles
        type(mock_settings()).name = mock.PropertyMock(return_value="Custom Styles")
        setting_defaults(category=mock_settings())

        mock_settings().setting_set.create.assert_any_call(name="Portal Base CSS",
                                                           content="",
                                                           date_modified=now)

        mock_settings().setting_set.create.assert_any_call(name="Home Page CSS",
                                                           content="",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Apps Library CSS",
                                                           content="",
                                                           date_modified=now)

        mock_settings().save.assert_called()

        # Custom Templates
        type(mock_settings()).name = mock.PropertyMock(return_value="Custom Templates")
        setting_defaults(category=mock_settings())

        mock_settings().setting_set.create.assert_any_call(name="Home Page Template",
                                                           content="",
                                                           date_modified=now)
        mock_settings().setting_set.create.assert_any_call(name="Apps Library Template",
                                                           content="",
                                                           date_modified=now)

        mock_settings().save.assert_called()
