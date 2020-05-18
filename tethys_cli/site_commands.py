import yaml
from subprocess import call
from pathlib import Path

from django.utils import timezone

from tethys_cli.cli_helpers import load_apps
from tethys_cli.cli_colors import write_msg
from tethys_apps.utilities import get_tethys_home_dir


# General Settings
TAB_TITLE = 'tab_title'
FAVICON = 'favicon'
BRAND_TEXT = 'title'
BRAND_IMAGE = 'logo'
BRAND_IMAGE_HEIGHT = 'logo_height'
BRAND_IMAGE_WIDTH = 'logo_wigth'
BRAND_IMAGE_PADDING = 'logo_padding'
APPS_LIBRARY_TITLE = 'library_title'
PRIMARY_COLOR = 'primary_color'
SECONDARY_COLOR = 'secondary_color'
BACKGROUND_COLOR = 'background_color'
TEXT_COLOR = 'text_color'
TEXT_HOVER_COLOR = 'text_hover_color'
SECONDARY_TEXT_COLOR = 'secondary_text_color'
SECONDARY_TEXT_HOVER_COLOR = 'secondary_text_hover_color'
FOOTER_COPYRIGHT = 'footer_copyright'

# Home Page
HERO_TEXT = 'hero_text'
BLURB_TEXT = 'blurb_text'
FEATURE1_HEADING = 'feature1_heading'
FEATURE1_BODY = 'feature1_body'
FEATURE1_IMAGE = 'feature1_image'
FEATURE2_HEADING = 'feature2_heading'
FEATURE2_BODY = 'feature2_body'
FEATURE2_IMAGE = 'feature2_image'
FEATURE3_HEADING = 'feature3_heading'
FEATURE3_BODY = 'feature3_body'
FEATURE3_IMAGE = 'feature3_image'
CALL_TO_ACTION_TEXT = 'action_text'
CALL_TO_ACTION_BUTTON = 'action_button'

# Custom Styles
BASE_CSS = 'base_css'
HOME_CSS = 'home_css'
LIBRARY_CSS = 'library_css'

# Custom Templates
HOME_TEMPLATE = 'home_template'
LIBRARY_TEMPLATE = 'library_template'

arg_filter = {
    TAB_TITLE: 'Site Title',
    FAVICON: 'Favicon',
    BRAND_TEXT: 'Brand Text',
    BRAND_IMAGE: 'Brand Image',
    BRAND_IMAGE_HEIGHT: 'Brand Image Height',
    BRAND_IMAGE_WIDTH: 'Brand Image Width',
    BRAND_IMAGE_PADDING: 'Brand Image Padding',
    APPS_LIBRARY_TITLE: 'Apps Library Title',
    PRIMARY_COLOR: 'Primary Color',
    SECONDARY_COLOR: 'Secondary Color',
    BACKGROUND_COLOR: 'Background Color',
    TEXT_COLOR: 'Primary Text Color',
    TEXT_HOVER_COLOR: 'Primary Text Hover Color',
    SECONDARY_TEXT_COLOR: 'Secondary Text Color',
    SECONDARY_TEXT_HOVER_COLOR: 'Secondary Text Hover Color',
    FOOTER_COPYRIGHT: 'Footer Copyright',
    HERO_TEXT: 'Hero Text',
    BLURB_TEXT: 'Blurb Text',
    FEATURE1_HEADING: 'Feature 1 Heading',
    FEATURE1_BODY: 'Feature 1 Body',
    FEATURE1_IMAGE: 'Feature 1 Image',
    FEATURE2_HEADING: 'Feature 2 Heading',
    FEATURE2_BODY: 'Feature 2 Body',
    FEATURE2_IMAGE: 'Feature 2 Image',
    FEATURE3_HEADING: 'Feature 3 Heading',
    FEATURE3_BODY: 'Feature 3 Body',
    FEATURE3_IMAGE: 'Feature 3 Image',
    CALL_TO_ACTION_TEXT: 'Call to Action',
    CALL_TO_ACTION_BUTTON: 'Call to Action Button',
    BASE_CSS: 'Portal Base CSS',
    HOME_CSS: 'Home Page CSS',
    LIBRARY_CSS: 'Apps Library CSS',
    HOME_TEMPLATE: 'Home Page Template',
    LIBRARY_TEMPLATE: 'Apps Library Template'
}


def add_site_parser(subparsers):
    # Setup site command
    site_parser = subparsers.add_parser('site', help='Add/Change the Tethys Portal content and theme.')
    site_parser.add_argument('--tab-title', dest='tab_title',
                             help='A double quoted string with the title that will display in the browser tab. '
                                  'Default is "Tethys Portal".')
    site_parser.add_argument('--favicon', dest='favicon',
                             help='Local or external path to the icon that will display in the browser tab. '
                                  'We recommend storing the favicon in the static directory of tethys_portal. '
                                  'Default is "tethys_portal/images/default_favicon.png".')
    site_parser.add_argument('--title', dest='title',
                             help='A double quoted string with the title of the portal. Default is "Tethys Portal".')
    site_parser.add_argument('--logo', dest='logo',
                             help='Local or external path to the portal logo. We recommend storing the logo in the '
                                  'static directory of tethys_portal. '
                                  'Default is "tethys_portal/images/tethys-logo-75.png".')
    site_parser.add_argument('--logo-height', dest='logo_height', help='The height of the portal logo.')
    site_parser.add_argument('--logo-width', dest='logo_width', help='The width of the portal logo.')
    site_parser.add_argument('--logo-padding', dest='logo_padding', help='The padding for the portal logo.')
    site_parser.add_argument('--library-title', dest='library_title',
                             help='A double quoted string with the Title for the Apps library. '
                                  'Default is "Apps Library".')
    site_parser.add_argument('--primary-color', dest='primary_color',
                             help='The primary color for the portal. Default is #0a62a9.')
    site_parser.add_argument('--secondary-color', dest='secondary_color',
                             help='The secondary color for the portal. Default is #1b95dc.')
    site_parser.add_argument('--background-color', dest='background_color', help='The background color for the portal.')
    site_parser.add_argument('--text-color', dest='text_color', help='The primary text color for the portal.')
    site_parser.add_argument('--text-hover-color', dest='text_hover_color', help='The hover text color for the portal.')
    site_parser.add_argument('--secondary-text-color', dest='secondary_text_color',
                             help='The secondary text color for the portal.')
    site_parser.add_argument('--secondary-text-hover-color', dest='secondary_text_hover_color',
                             help='The secondary hover text color for the portal.')
    site_parser.add_argument('--copyright', dest='footer_copyright',
                             help='A double quoted string with the Footer copyright for the portal. '
                                  'Default is "Copyright © 2019 Your Organization".')
    site_parser.add_argument('--hero-text', dest='hero_text',
                             help='A double quoted string with the hero text to display in the portal home. '
                                  'Default is "Welcome to Tethys Portal,\nthe hub for your apps.".')
    site_parser.add_argument('--blurb-text', dest='blurb_text',
                             help='A double quoted string with the blurb text to display in the portal home. '
                                  'Default is "Tethys Portal is designed to be customizable, so that you can host apps '
                                  'for your\norganization. You can change everything on this page from the Home Page '
                                  'settings.".')
    site_parser.add_argument('--feature1-heading', dest='feature1_heading',
                             help='A double quoted string with the heading for display feature number 1 out 3.')
    site_parser.add_argument('--feature1-body', dest='feature1_body',
                             help='A double quoted string with the content for display feature number 1 out 3.')
    site_parser.add_argument('--feature1-image', dest='feature1_image',
                             help='A double quoted string with an image for display feature number 1 out 3.')
    site_parser.add_argument('--feature2-heading', dest='feature2_heading',
                             help='A double quoted string with the heading for display feature number 2 out 3.')
    site_parser.add_argument('--feature2-body', dest='feature2_body',
                             help='A double quoted string with the content for display feature number 2 out 3.')
    site_parser.add_argument('--feature2-image', dest='feature2_image',
                             help='A double quoted string with an image for display feature number 2 out 3.')
    site_parser.add_argument('--feature3-heading', dest='feature3_heading',
                             help='A double quoted string with the heading for display feature number 3 out 3.')
    site_parser.add_argument('--feature3-body', dest='feature3_body',
                             help='A double quoted string with the content for display feature number 3 out 3.')
    site_parser.add_argument('--feature3-image', dest='feature3_image',
                             help='A double quoted string with an image for display feature number 3 out 3.')
    site_parser.add_argument('--action-text', dest='action_text',
                             help='A double quoted string with the call to action text that will display in the '
                                  'portal. Default is "Ready to get started?".')
    site_parser.add_argument('--action-button', dest='action_button',
                             help='A double quoted string for the call to action button. '
                                  'Default is "Start Using Tethys!".')
    site_parser.add_argument('--base-css', dest='base_css',
                             help='CSS code to modify the Tethys Portal Base Page, which extends most of the portal '
                                  'pages (i.e. Home, Login, Developer, Admin, etc.). Takes a file path available '
                                  'through Tethys static files or straight CSS code.')
    site_parser.add_argument('--home-css', dest='home_css',
                             help='CSS code to modify the Tethys Portal Home Page. Takes a file path available through '
                                  'Tethys static files or straight CSS code.')
    site_parser.add_argument('--library-css', dest='library_css',
                             help='CSS code to modify the Tethys Portal Apps Library. Takes a file path available '
                                  'through Tethys static files or straight CSS code.')
    site_parser.add_argument('--home-template', dest='home_template',
                             help='Django template to modify the Tethys Portal Home Page. Takes a file path available '
                                  'through the Tethys template files system.')
    site_parser.add_argument('--library-template', dest='library_template',
                             help='Django template to modify the Tethys Portal Apps Library. Takes a file path '
                                  'available through the Tethys template files system.')
    site_parser.add_argument('--restore-defaults', dest='restore_defaults', action='store_true',
                             help='Restores the sites default values.')
    site_parser.add_argument('-f', '--from-file', type=str, help='Load site content from portal_config.yml file.')

    site_parser.set_defaults(func=gen_site_content, restore_defaults=False, from_file=True)


def gen_site_content(args):
    load_apps()

    from tethys_config.models import Setting, SettingsCategory

    if args.restore_defaults:
        from tethys_config.init import setting_defaults

        Setting.objects.all().delete()

        general_category = SettingsCategory.objects.get(name="General Settings")
        setting_defaults(general_category)

        home_category = SettingsCategory.objects.get(name="Home Page")
        setting_defaults(home_category)

    if args.from_file:
        portal_yaml = Path(get_tethys_home_dir()) / 'portal_config.yml'
        if portal_yaml.exists():
            with portal_yaml.open() as f:
                site_content_settings = yaml.safe_load(f).get('site_content', {})
                for arg in site_content_settings:
                    if site_content_settings[arg]:
                        content = site_content_settings[arg]
                        obj = Setting.objects.filter(name=arg_filter[arg.lower()])
                        obj.update(content=content, date_modified=timezone.now())
        else:
            valid_inputs = ('y', 'n', 'yes', 'no')
            no_inputs = ('n', 'no')

            generate_input = input('Would you like to generate a template portal_config.yml file that you can then'
                                   'customize? (y/n): ')

            while generate_input not in valid_inputs:
                generate_input = input('Invalid option. Try again. (y/n): ').lower()

            if generate_input in no_inputs:
                write_msg('Generation of portal_config.yml file cancelled. Please generate one manually or provide '
                          'specific site content arguments.')
            else:
                call(['tethys', 'gen', 'portal'])
                write_msg('\nRe-run the tethys site command with the --from-file argument.')
                exit(0)

    for arg in vars(args):
        if vars(args)[arg] and arg in arg_filter:
            content = vars(args)[arg].replace('\\n', '\n')
            obj = Setting.objects.filter(name=arg_filter[arg])
            obj.update(content=content, date_modified=timezone.now())
