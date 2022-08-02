import yaml
from subprocess import call
from pathlib import Path

from django.utils import timezone

from tethys_cli.cli_helpers import load_apps
from tethys_cli.cli_colors import write_msg, write_warning
from tethys_apps.utilities import get_tethys_home_dir


SITE_SETTING_CATEGORIES = ['GENERAL_SETTINGS', 'HOME_PAGE', 'CUSTOM_STYLES', 'CUSTOM_TEMPLATES']


def add_site_parser(subparsers):
    # Setup site command
    site_parser = subparsers.add_parser('site', help='Add/Change the Tethys Portal content and theme.')
    site_parser.add_argument('--site-title', dest='site_title',
                             help='A double quoted string with the title that will display in the browser tab. '
                                  'Default is "Tethys Portal".')
    site_parser.add_argument('--favicon', dest='favicon',
                             help='Local or external path to the icon that will display in the browser tab. '
                                  'We recommend storing the favicon in the static directory of tethys_portal. '
                                  'Default is "tethys_portal/images/default_favicon.png".')
    site_parser.add_argument('--brand-text', dest='brand_text',
                             help='A double quoted string with the title of the portal. Default is "Tethys Portal".')
    site_parser.add_argument('--brand-image', dest='brand_image',
                             help='Local or external path to the portal logo. We recommend storing the logo in the '
                                  'static directory of tethys_portal. '
                                  'Default is "tethys_portal/images/tethys-logo-75.png".')
    site_parser.add_argument('--brand-image-height', dest='brand_image_height', help='The height of the portal logo.')
    site_parser.add_argument('--brand-image-width', dest='brand_image_width', help='The width of the portal logo.')
    site_parser.add_argument('--brand-image-padding', dest='brand_image_padding',
                             help='The padding for the portal logo.')
    site_parser.add_argument('--apps-library-title', dest='apps_library_title',
                             help='A double quoted string with the Title for the Apps library. '
                                  'Default is "Apps Library".')
    site_parser.add_argument('--primary-color', dest='primary_color',
                             help='The primary color for the portal. Default is #0a62a9.')
    site_parser.add_argument('--secondary-color', dest='secondary_color',
                             help='The secondary color for the portal. Default is #7ec1f7.')
    site_parser.add_argument('--background-color', dest='background_color', help='The background color for the portal.')
    site_parser.add_argument('--primary-text-color', dest='primary_text_color',
                             help='The primary text color for the portal.')
    site_parser.add_argument('--primary-text-hover-color', dest='primary_text_hover_color',
                             help='The hover text color for the portal.')
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
    site_parser.add_argument('--feature-1-heading', dest='feature_1_heading',
                             help='A double quoted string with the heading for display feature number 1 out 3.')
    site_parser.add_argument('--feature-1-body', dest='feature_1_body',
                             help='A double quoted string with the content for display feature number 1 out 3.')
    site_parser.add_argument('--feature-1-image', dest='feature_1_image',
                             help='A double quoted string with an image for display feature number 1 out 3.')
    site_parser.add_argument('--feature-2-heading', dest='feature_2_heading',
                             help='A double quoted string with the heading for display feature number 2 out 3.')
    site_parser.add_argument('--feature-2-body', dest='feature_2_body',
                             help='A double quoted string with the content for display feature number 2 out 3.')
    site_parser.add_argument('--feature-2-image', dest='feature_2_image',
                             help='A double quoted string with an image for display feature number 2 out 3.')
    site_parser.add_argument('--feature-3-heading', dest='feature_3_heading',
                             help='A double quoted string with the heading for display feature number 3 out 3.')
    site_parser.add_argument('--feature-3-body', dest='feature_3_body',
                             help='A double quoted string with the content for display feature number 3 out 3.')
    site_parser.add_argument('--feature-3-image', dest='feature_3_image',
                             help='A double quoted string with an image for display feature number 3 out 3.')
    site_parser.add_argument('--call-to-action', dest='call_to_action',
                             help='A double quoted string with the call to action text that will display in the '
                                  'portal. Default is "Ready to get started?".')
    site_parser.add_argument('--call-to-action-button', dest='call_to_action_button',
                             help='A double quoted string for the call to action button. '
                                  'Default is "Start Using Tethys!".')
    site_parser.add_argument('--portal-base-css', dest='portal_base_css',
                             help='CSS code to modify the Tethys Portal Base Page, which extends most of the portal '
                                  'pages (i.e. Home, Login, Developer, Admin, etc.). Takes a file path available '
                                  'through Tethys static files or straight CSS code.')
    site_parser.add_argument('--home-page-css', dest='home_page_css',
                             help='CSS code to modify the Tethys Portal Home Page. Takes a file path available through '
                                  'Tethys static files or straight CSS code.')
    site_parser.add_argument('--apps-library-css', dest='apps_library_css',
                             help='CSS code to modify the Tethys Portal Apps Library. Takes a file path available '
                                  'through Tethys static files or straight CSS code.')
    site_parser.add_argument('--accounts-base-css', dest='accounts_base_css',
                             help='CSS code to modify the base template for all of the accounts pages '
                                  '(e.g. login, register, change password, etc.). Takes a file path available '
                                  'through Tethys static files or straight CSS code.')
    site_parser.add_argument('--login-css', dest='login_css',
                             help='CSS code to modify the Portal Login page. Takes a file path available '
                                  'through Tethys static files or straight CSS code.')
    site_parser.add_argument('--register-css', dest='register_css',
                             help='CSS code to modify the Portal Registration page. Takes a file path available '
                                  'through Tethys static files or straight CSS code.')
    site_parser.add_argument('--user-base-css', dest='user_base_css',
                             help='CSS code to modify the base template for all of the user profile pages '
                                  '(e.g. user, settings, manage storage). Takes a file path available '
                                  'through Tethys static files or straight CSS code.')
    site_parser.add_argument('--home-page-template', dest='home_page_template',
                             help='Django template to modify the Tethys Portal Home Page. Takes a file path available '
                                  'through the Tethys template files system.')
    site_parser.add_argument('--apps-library-template', dest='apps_library_template',
                             help='Django template to modify the Tethys Portal Apps Library. Takes a file path '
                                  'available through the Tethys template files system.')
    site_parser.add_argument('--login-page-template', dest='login_page_template',
                             help='Django template to modify the Portal Login page. Takes a file path '
                                  'available through the Tethys template files system.')
    site_parser.add_argument('--register-page-template', dest='register_page_template',
                             help='Django template to modify the Portal Registration page. Takes a file path '
                                  'available through the Tethys template files system.')
    site_parser.add_argument('--user-page-template', dest='user_page_template',
                             help='Django template to modify the User Profile page. Takes a file path '
                                  'available through the Tethys template files system.')
    site_parser.add_argument('--user-settings-page-template', dest='user_settings_page_template',
                             help='Django template to modify the User Settings (i.e. edit) page. Takes a file path '
                                  'available through the Tethys template files system.')
    site_parser.add_argument('-d', '--restore-defaults', dest='restore_defaults', action='store_true',
                             help='Restores the sites default values.')
    site_parser.add_argument('-f', '--from-file', action='store_true', default=False,
                             help='Load site content from portal_config.yml file.')

    site_parser.set_defaults(func=gen_site_content, restore_defaults=False, from_file=False)


def gen_site_content(args):
    load_apps()

    if args.restore_defaults:
        restore_site_setting_defaults()

    if args.from_file:
        portal_yaml = Path(get_tethys_home_dir()) / 'portal_config.yml'
        if portal_yaml.exists():
            with portal_yaml.open() as f:
                site_settings = yaml.safe_load(f).get('site_settings', {})
                for category in SITE_SETTING_CATEGORIES:
                    category_settings = site_settings.pop(category, {})
                    update_site_settings_content(category_settings, warn_if_setting_not_found=True)
                for category in site_settings:
                    write_warning(
                        f'WARNING: the portal_config.yml file contains an invalid category in site_settings.'
                        f'"{category}" is not one of {SITE_SETTING_CATEGORIES}.'
                    )
        else:
            valid_inputs = ('y', 'n', 'yes', 'no')
            no_inputs = ('n', 'no')

            generate_input = input('Would you like to generate a template portal_config.yml file that you can then'
                                   'customize? (y/n): ')

            while generate_input not in valid_inputs:
                generate_input = input('Invalid option. Try again. (y/n): ').lower()

            if generate_input in no_inputs:
                write_msg('Generation of portal_config.yml file cancelled. Please generate one manually or provide '
                          'specific site settings arguments.')
            else:
                call(['tethys', 'gen', 'portal'])
                write_msg('\nRe-run the tethys site command with the --from-file argument.')
                exit(0)

    update_site_settings_content(vars(args))


def restore_site_setting_defaults():
    from tethys_config.models import Setting, SettingsCategory
    from tethys_config.init import setting_defaults

    Setting.objects.all().delete()

    for category in SITE_SETTING_CATEGORIES:
        category_name = uncodify(category)
        category = SettingsCategory.objects.get(name=category_name)
        setting_defaults(category)


def update_site_settings_content(settings_dict, warn_if_setting_not_found=False):
    from tethys_config.models import Setting

    for arg, content in settings_dict.items():
        setting_name = uncodify(arg)
        obj = Setting.objects.filter(name=setting_name)
        if not obj and warn_if_setting_not_found:
            write_warning(f'WARNING: "{arg}" is not a valid site setting.')
        if content and obj:
            content = content.replace('\\n', '\n')
            obj.update(content=content, date_modified=timezone.now())


def uncodify(code_name):
    setting_name = code_name.replace('_', ' ').title()
    setting_name = setting_name.replace('Css', 'CSS').replace('To ', 'to ')
    return setting_name
