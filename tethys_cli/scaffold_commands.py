import os
import re
import logging
import random
import shutil

from jinja2 import Template
from tethys_cli.cli_colors import write_pretty_output, FG_RED, FG_YELLOW, FG_WHITE

# Constants
APP_PREFIX = 'tethysapp'
EXTENSION_PREFIX = 'tethysext'
SCAFFOLD_TEMPLATES_DIR = 'scaffold_templates'
EXTENSION_TEMPLATES_DIR = 'extension_templates'
APP_TEMPLATES_DIR = 'app_templates'
TEMPLATE_SUFFIX = '_tmpl'
APP_PATH = os.path.join(os.path.dirname(__file__), SCAFFOLD_TEMPLATES_DIR, APP_TEMPLATES_DIR)
EXTENSION_PATH = os.path.join(os.path.dirname(__file__), SCAFFOLD_TEMPLATES_DIR, EXTENSION_TEMPLATES_DIR)


def add_scaffold_parser(subparsers):
    # Setup scaffold command
    scaffold_parser = subparsers.add_parser('scaffold', help='Create a new Tethys app project from a scaffold.')
    scaffold_parser.add_argument('name', help='The name of the new Tethys app project to create. Only lowercase '
                                              'letters, numbers, and underscores allowed.')
    scaffold_parser.add_argument('-t', '--template', dest='template', help="Name of template to use.")
    scaffold_parser.add_argument('-e', '--extension', dest='extension', action="store_true")
    scaffold_parser.add_argument('-d', '--defaults', dest='use_defaults', action='store_true',
                                 help="Run command, accepting default values automatically.")
    scaffold_parser.add_argument('-o', '--overwrite', dest='overwrite', action="store_true",
                                 help="Attempt to overwrite project automatically if it already exists.")
    scaffold_parser.set_defaults(func=scaffold_command, template='default', extension=False)


def proper_name_validator(value, default):
    """
    Validate proper_name user input.
    """
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
            write_pretty_output(
                'Warning: Illegal characters were detected in proper name "{0}". They have been replaced or '
                'removed with valid characters: "{1}"'.format(before, value), FG_YELLOW
            )
        # Otherwise, throw error
        else:
            write_pretty_output('Error: Proper name can only contain letters and numbers and spaces.', FG_RED)
            return False, value
    return True, value


def get_random_color():
    """
    Generate a random color.
    """
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

    return random.choice(default_colors)


def theme_color_validator(value, default):
    """
    Validate theme_color user input.
    """
    # Generate random color if default option provided
    if value == default:
        return True, get_random_color()

    # Validate hexadecimal if provided
    try:
        if len(value) > 0 and '#' in value:
            value = value[1:]

        int(value, 16)
        value = '#' + value
        return True, value
    except ValueError:
        write_pretty_output("Error: Value given is not a valid hexadecimal color.", FG_RED)
        return False, value


def render_path(path, context):
    """
    Replace variables in path with values.
    """
    # Check for tokens delineated by "+" (e.g.: +variable+)
    if '+' not in path:
        return path

    for token, value in context.items():
        path = path.replace('+' + token + '+', value)
    return path


def scaffold_command(args):
    """
    Create a new Tethys app projects in the current directory.
    """
    # Log
    log = logging.getLogger('tethys')
    # log.setLevel(logging.DEBUG)
    log.debug('Command args: {}'.format(args))

    # Get template dirs
    log.debug('APP_PATH: {}'.format(APP_PATH))
    log.debug('EXTENSION_PATH: {}'.format(EXTENSION_PATH))

    # Get template root directory
    is_extension = False

    if args.extension:
        is_extension = True
        template_name = args.template
        template_root = os.path.join(EXTENSION_PATH, args.template)
    else:
        template_name = args.template
        template_root = os.path.join(APP_PATH, args.template)

    log.debug('Template root directory: {}'.format(template_root))

    # Validate template
    if not os.path.isdir(template_root):
        write_pretty_output('Error: "{}" is not a valid template.'.format(template_name), FG_WHITE)
        exit(1)

    # Validate project name
    project_name = args.name

    # Only lowercase
    contains_uppers = False
    for letter in project_name:
        if letter.isupper():
            contains_uppers = True
            break

    if contains_uppers:
        before = project_name
        project_name = project_name.lower()
        write_pretty_output('Warning: Uppercase characters in project name "{0}" '
                            'changed to lowercase: "{1}".'.format(before, project_name), FG_YELLOW)

    # Check for valid characters name
    project_error_regex = re.compile(r'^[a-zA-Z0-9_]+$')
    project_warning_regex = re.compile(r'^[a-zA-Z0-9_-]+$')

    # Only letters, numbers and underscores allowed in app names
    if not project_error_regex.match(project_name):
        # If the only offending character is a dash, replace dashes with underscores and notify user
        if project_warning_regex.match(project_name):
            before = project_name
            project_name = project_name.replace('-', '_')
            write_pretty_output('Warning: Dashes in project name "{0}" have been replaced '
                                'with underscores "{1}"'.format(before, project_name), FG_YELLOW)
        # Otherwise, throw error
        else:
            write_pretty_output('Error: Invalid characters in project name "{0}". '
                                'Only letters, numbers, and underscores.'.format(project_name), FG_YELLOW)
            exit(1)

    # Project name derivatives
    project_dir = '{0}-{1}'.format(EXTENSION_PREFIX if is_extension else APP_PREFIX, project_name)
    split_project_name = project_name.split('_')
    title_case_project_name = [x.title() for x in split_project_name]
    default_proper_name = ' '.join(title_case_project_name)
    class_name = ''.join(title_case_project_name)
    default_theme_color = get_random_color()

    write_pretty_output('Creating new Tethys project named "{0}".'.format(project_dir), FG_WHITE)

    # Get metadata from user
    if not is_extension:
        metadata_input = (
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
                'name': 'color',
                'prompt': 'App theme color (e.g.: "#27AE60")',
                'default': default_theme_color,
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
    else:
        metadata_input = (
            {
                'name': 'proper_name',
                'prompt': 'Proper name for the extension (e.g.: "My First Extension")',
                'default': default_proper_name,
                'validator': proper_name_validator
            },
            {
                'name': 'description',
                'prompt': 'Brief description of the extension',
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
    context = {
        'project': project_name,
        'project_dir': project_dir,
        'project_url': project_name.replace('_', '-'),
        'class_name': class_name,
        'proper_name': default_proper_name,
        'description': '',
        'color': default_theme_color,
        'tags': '',
        'author': '',
        'author_email': '',
        'license_name': ''
    }

    if not args.use_defaults:
        # Collect metadata input from user
        for item in metadata_input:
            valid = False
            response = item['default']

            while not valid:
                try:
                    response = input('{0} ["{1}"]: '.format(item['prompt'], item['default'])) or item['default']
                except (KeyboardInterrupt, SystemExit):
                    write_pretty_output('\nScaffolding cancelled.', FG_YELLOW)
                    exit(1)

                if callable(item['validator']):
                    valid, response = item['validator'](response, item['default'])
                else:
                    valid = True

                if not valid:
                    write_pretty_output('Invalid response: {}'.format(response), FG_RED)

            context[item['name']] = response

    log.debug('Template context: {}'.format(context))

    # Create root directory
    project_root = os.path.join(os.getcwd(), project_dir)
    log.debug('Project root path: {}'.format(project_root))

    if os.path.isdir(project_root):
        if not args.overwrite:
            valid = False
            negative_choices = ['n', 'no', '']
            valid_choices = ['y', 'n', 'yes', 'no']
            default = 'y'
            response = ''

            while not valid:
                try:
                    response = input('Directory "{}" already exists. '
                                     'Would you like to overwrite it? [Y/n]: '.format(project_root)) or default
                except (KeyboardInterrupt, SystemExit):
                    write_pretty_output('\nScaffolding cancelled.', FG_YELLOW)
                    exit(1)

                if response.lower() in valid_choices:
                    valid = True

            if response.lower() in negative_choices:
                write_pretty_output('Scaffolding cancelled.', FG_YELLOW)
                exit(0)

        try:
            shutil.rmtree(project_root)
        except OSError:
            write_pretty_output('Error: Unable to overwrite "{}". '
                                'Please remove the directory and try again.'.format(project_root), FG_YELLOW)
            exit(1)

    # Walk the template directory, creating the templates and directories in the new project as we go
    for curr_template_root, dirs, template_files in os.walk(template_root):
        curr_project_root = curr_template_root.replace(template_root, project_root)
        curr_project_root = render_path(curr_project_root, context)

        # Create Root Directory
        os.makedirs(curr_project_root)
        write_pretty_output('Created: "{}"'.format(curr_project_root), FG_WHITE)

        # Create Files
        for template_file in template_files:
            template_file_path = os.path.join(curr_template_root, template_file)
            project_file = template_file.replace(TEMPLATE_SUFFIX, '')
            project_file_path = os.path.join(curr_project_root, project_file)

            # Load the template
            log.debug('Loading template: "{}"'.format(template_file_path))

            try:
                with open(template_file_path, 'r') as tfp:
                    template = Template(tfp.read())
            except UnicodeDecodeError:
                with open(template_file_path, 'br') as tfp:
                    with open(project_file_path, 'bw') as pfp:
                        pfp.write(tfp.read())
                continue

            # Render template if loaded
            log.debug('Rendering template: "{}"'.format(template_file_path))
            if template:
                with open(project_file_path, 'w') as pfp:
                    pfp.write(template.render(context))
                write_pretty_output('Created: "{}"'.format(project_file_path), FG_WHITE)

    write_pretty_output('Successfully scaffolded new project "{}"'.format(project_name), FG_WHITE)
