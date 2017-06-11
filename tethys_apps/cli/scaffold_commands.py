import os
import re
import logging
import random
from builtins import *

APP_PREFIX = 'tethysapp'
EXTENSION_PREFIX = 'tethysext'


def proper_name_validator(value, default):
    # Check for default
    if value == default:
        return True, value

    # Validate and sanitize user input
    proper_name_error_regex = re.compile(r'^[a-zA-Z0-9\s]+$')
    proper_name_warn_regex = re.compile(r'^[a-zA-Z0-9-\s_\"\']+$')

    if not proper_name_error_regex.match(value):
        # If offending characters are dashes, underscores or quotes, replace and notify user
        if proper_name_warn_regex.match(value):
            before = value
            value = value.replace('_', ' ')
            value = value.replace('-', ' ')
            value = value.replace('"', '')
            value = value.replace("'", "")
            print('Warning: Illegal characters were detected in proper name "{0}". They have been replaced or '
                  'removed with valid characters: "{1}"'.format(before, value))
        # Otherwise, throw error
        else:
            print('Error: Proper name can only contain letters and numbers and spaces.')
            return False, value
    return True, value


def theme_color_validator(value, default):
    # Default colors from flatuicolors.com
    default_colors = (
        '#27ae60',  # Nephritis
        '#2980b9',  # Belize Hole
        '#2c3e50',  # Midnight Blue
        '#8e44ad',  # Wisteria
        '#d35400',  # Pumpkin
        '#f39c12',  # Orange
        '#c0392b',  # Pomegranate
        '#16a085',  # Green Sea
    )

    # Generate random color if default option provided
    if value == default:
        return True, random.choice(default_colors)

    # Validate hexadecimal if provided
    try:
        if len(value) > 0 and '#' in value:
            value = value[1:]

        int(value, 16)
        value = '#' + value
        return True, value
    except ValueError:
        print("Error: Value given is not a valid hexadecimal color.")
        return False, value


def scaffold_command(args):
    """
    Create a new Tethys app projects in the current directory.
    """
    # Log
    log = logging.getLogger('tethys')
    log.setLevel(logging.DEBUG)
    log.debug('Command args: {}'.format(args))

    # Constants
    SCAFFOLD_TEMPLATES_DIR = 'scaffold_templates'
    EXTENSION_TEMPLATES_DIR = 'extension_templates'
    APP_TEMPLATES_DIR = 'app_templates'
    APP_PATH = os.path.join(os.path.dirname(__file__), SCAFFOLD_TEMPLATES_DIR, APP_TEMPLATES_DIR)
    EXTENSION_PATH = os.path.join(os.path.dirname(__file__), SCAFFOLD_TEMPLATES_DIR, EXTENSION_TEMPLATES_DIR)

    # Get template dirs
    log.debug('APP_PATH: {}'.format(APP_PATH))
    log.debug('EXTENSION_PATH: {}'.format(EXTENSION_PATH))

    # Get template root directory
    is_extension = False

    if args.extension:
        is_extension = True
        template_name = args.extension
        template_root = os.path.join(EXTENSION_PATH, args.extension)
    else:
        template_name = args.template
        template_root = os.path.join(APP_PATH, args.template)

    log.debug('Template root directory: {}'.format(template_root))

    # Validate template
    if not os.path.isdir(template_root):
        print('Error: "{}" is not a valid template.'.format(template_name))
        exit(1)

    # Validate project name
    project_name = args.name

    # Only underscores
    if '-' in project_name:
        before = project_name
        project_name = project_name.replace('-', '_')
        log.info('Dash ("-") characters changed to underscores ("_").')

    # Only lowercase
    contains_uppers = False
    for letter in project_name:
        if letter.isupper():
            contains_uppers = True
            break

    if contains_uppers:
        before = project_name
        project_name = project_name.lower()
        log.info('Uppercase characters changed to lowercase.')

    # Check for valid characters name
    project_error_regex = re.compile(r'^[a-zA-Z0-9_]+$')
    project_warning_regex = re.compile(r'^[a-zA-Z0-9_-]+$')

    # Only letters, numbers and underscores allowed in app names
    if not project_error_regex.match(project_name):
        # If the only offending character is a dash, replace dashes with underscores and notify user
        if project_warning_regex.match(project_name):
            before = project_name
            project_name = project_name.replace('-', '_')
            print('Warning: Dashes in project name "{0}" have been replaced '
                  'with underscores "{1}"'.format(before, project_name))
        # Otherwise, throw error
        else:
            print('Error: Invalid characters in project name "{0}". '
                  'Only letters, numbers, and underscores.'.format(project_name))
            exit(1)

    # Project name derivatives
    if is_extension:
        project_dir = '{0}-{1}'.format(EXTENSION_PREFIX, project_name)
    else:
        project_dir = '{0}-{1}'.format(APP_PREFIX, project_name)

    split_project_name = project_name.split('_')
    title_case_project_name = [x.title() for x in split_project_name]
    default_proper_name = ' '.join(title_case_project_name)
    app_class_name = ''.join(title_case_project_name)

    print('Initializing tethys app project with name "{0}".'.format(project_dir))

    # Get metadata from user
    metadata = (
        {
            'name': 'proper_name',
            'prompt': 'Proper name for the app (e.g.: "My First App")',
            'default': default_proper_name,
            'validator': proper_name_validator
        },
        {
            'name': 'description',
            'prompt': 'Brief description of the app',
            'default': '',
            'validator': None
        },
        {
            'name': 'theme_color',
            'prompt': 'App theme color (e.g.: "#27AE60")',
            'default': 'random',
            'validator': theme_color_validator
        },
        {
            'name': 'tags',
            'prompt': 'Tags: Use commas to delineate tags and '
                      'quotes around each tag (e.g.: "Hydrology","Reference Timeseries")',
            'default': '',
            'validator': None
        },
        {
            'name': 'author',
            'prompt': 'Author name',
            'default': '',
            'validator': None
        },
        {
            'name': 'author_email',
            'prompt': 'Author email',
            'default': '',
            'validator': None
        },
        {
            'name': 'license_name',
            'prompt': 'License name',
            'default': '',
            'validator': None
        },
    )

    # Build up template context
    template_context = dict(
        project=project_name,
        project_dir=project_dir,
        project_url=project_name.replace('_', '-'),
        app_class_name=app_class_name
    )

    for item in metadata:
        valid = False
        value = item['default']

        while not valid:
            try:
                value = input('{0} ["{1}"]: '.format(item['prompt'], item['default'])) or item['default']
            except (KeyboardInterrupt, SystemExit):
                print('\nScaffolding cancelled.')
                exit(1)

            if callable(item['validator']):
                valid, value = item['validator'](value, item['default'])
            else:
                valid = True

            if not valid:
                print('Invalid value: {0}'.format(value))

        template_context[item['name']] = value

    log.debug('Template context: {0}'.format(template_context))


    # TODO: Create Context
    # TODO: Create Root Directory in CWD
    # TODO: Copy Directories and Files into Root Directory
    # TODO: Check for directory template tags and rename accordingly from context
    # TODO: Create all files passing through template engine




