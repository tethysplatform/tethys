import unittest
from unittest import mock

from tethys_config.init import initial_settings, reverse_init, setting_defaults, custom_settings, \
    reverse_custom


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

        self.assertEqual(mock_defaults.call_count, 2)

    @mock.patch('tethys_config.init.initial_settings')
    @mock.patch('tethys_config.init.setting_defaults')
    @mock.patch('tethys_config.init.SettingsCategory')
    def test_custom_settings(self, mock_settings, mock_defaults, mock_init_settings):
        mock_apps = mock.MagicMock()
        mock_schema_editor = mock.MagicMock()
        mock_settings.objects.all.return_value = False

        custom_settings(apps=mock_apps, schema_editor=mock_schema_editor)

        mock_init_settings.called_with(mock_apps, mock_schema_editor)
        mock_settings.assert_has_calls([mock.call(name='Custom Styles'), mock.call(name='Custom Templates')],
                                       any_order=True)
        mock_settings(name='Custom Styles').save.assert_called()
        mock_settings(name='Custom Templates').save.assert_called()

        self.assertEqual(mock_defaults.call_count, 2)

    @mock.patch('tethys_config.init.Setting')
    @mock.patch('tethys_config.init.SettingsCategory')
    def test_reverse_init(self, mock_categories, mock_settings):
        mock_apps = mock.MagicMock
        mock_schema_editor = mock.MagicMock()
        mock_cat = mock.MagicMock()
        mock_set = mock.MagicMock()
        mock_categories.objects.all.return_value = [mock_cat]
        mock_settings.objects.all.return_value = [mock_set]

        reverse_init(apps=mock_apps, schema_editor=mock_schema_editor)

        mock_categories.objects.all.assert_called_once()
        mock_settings.objects.all.assert_called_once()
        mock_cat.delete.assert_called_once()
        mock_set.delete.assert_called_once()

    @mock.patch('tethys_config.init.Setting')
    @mock.patch('tethys_config.init.SettingsCategory')
    def test_reverse_custom(self, mock_categories, mock_settings):
        mock_apps = mock.MagicMock
        mock_schema_editor = mock.MagicMock()
        mock_cat = mock.MagicMock()
        mock_cat.name = 'Custom Styles'
        mock_set = mock.MagicMock()
        mock_set.name = 'Home Page Template'
        mock_categories.objects.all.return_value = [mock_cat]
        mock_settings.objects.all.return_value = [mock_set]

        reverse_custom(apps=mock_apps, schema_editor=mock_schema_editor)

        mock_categories.objects.all.assert_called_once()
        mock_settings.objects.all.assert_called_once()
        mock_cat.delete.assert_called_once()
        mock_set.delete.assert_called_once()

    @mock.patch('tethys_config.init.timezone.now')
    @mock.patch('tethys_config.init.SettingsCategory')
    def test_setting_defaults(self, mock_settings, mock_now):

        # General settings
        type(mock_settings()).name = mock.PropertyMock(return_value="General Settings")
        setting_defaults(category=mock_settings())

        mock_settings().setting_set.create.assert_any_call(name="Site Title",
                                                           content="Tethys Portal",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Favicon",
                                                           content="/tethys_portal/images/"
                                                                   "default_favicon.png",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Brand Text",
                                                           content="Tethys Portal",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Brand Image",
                                                           content="/tethys_portal/images/"
                                                                   "tethys-logo-75.png",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Brand Image Height", content="",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Brand Image Width", content="",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Brand Image Padding",
                                                           content="",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Apps Library Title",
                                                           content="Apps Library",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Primary Color",
                                                           content="#0a62a9",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Secondary Color",
                                                           content="#1b95dc",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Background Color", content="",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Primary Text Color", content="",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Primary Text Hover Color",
                                                           content="",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Secondary Text Color",
                                                           content="",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Secondary Text Hover Color",
                                                           content="",
                                                           date_modified=mock_now.return_value)

        mock_settings().save.assert_called()

        # Home page settings
        type(mock_settings()).name = mock.PropertyMock(return_value="Home Page")
        setting_defaults(category=mock_settings())

        mock_settings().setting_set.create.assert_any_call(name="Hero Text",
                                                           content="Welcome to Tethys Portal,\nthe hub "
                                                                   "for your apps.",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Blurb Text",
                                                           content="Tethys Portal is designed to be "
                                                                   "customizable, so that you can host "
                                                                   "apps for your\norganization. You "
                                                                   "can change everything on this page "
                                                                   "from the Home Page settings.",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Feature 1 Heading",
                                                           content="Feature 1",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Feature 1 Body",
                                                           content="Use these features to brag about "
                                                                   "all of the things users can do "
                                                                   "with your instance of Tethys "
                                                                   "Portal.",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Feature 1 Image",
                                                           content="/tethys_portal/images/"
                                                                   "placeholder.gif",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Feature 2 Heading",
                                                           content="Feature 2",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Feature 2 Body",
                                                           content="Describe the apps and tools that "
                                                                   "your Tethys Portal provides and "
                                                                   "add custom pictures to each "
                                                                   "feature as a finishing touch.",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Feature 2 Image",
                                                           content="/tethys_portal/images/"
                                                                   "placeholder.gif",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Feature 3 Heading",
                                                           content="Feature 3",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Feature 3 Body",
                                                           content="You can change the color theme and "
                                                                   "branding of your Tethys Portal in "
                                                                   "a jiffy. Visit the Site Admin "
                                                                   "settings from the user menu and "
                                                                   "select General Settings.",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Feature 3 Image",
                                                           content="/tethys_portal/images/"
                                                                   "placeholder.gif",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Call to Action",
                                                           content="Ready to get started?",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Call to Action Button",
                                                           content="Start Using Tethys!",
                                                           date_modified=mock_now.return_value)

        mock_settings().save.assert_called()

        # Custom Styles
        type(mock_settings()).name = mock.PropertyMock(return_value="Custom Styles")
        setting_defaults(category=mock_settings())

        mock_settings().setting_set.create.assert_any_call(name="Portal Base CSS",
                                                           content="",
                                                           date_modified=mock_now.return_value)

        mock_settings().setting_set.create.assert_any_call(name="Home Page CSS",
                                                           content="",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Apps Library CSS",
                                                           content="",
                                                           date_modified=mock_now.return_value)

        mock_settings().save.assert_called()

        # Custom Templates
        type(mock_settings()).name = mock.PropertyMock(return_value="Custom Templates")
        setting_defaults(category=mock_settings())

        mock_settings().setting_set.create.assert_any_call(name="Home Page Template",
                                                           content="",
                                                           date_modified=mock_now.return_value)
        mock_settings().setting_set.create.assert_any_call(name="Apps Library Template",
                                                           content="",
                                                           date_modified=mock_now.return_value)

        mock_settings().save.assert_called()
