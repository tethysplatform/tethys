"""
********************************************************************************
* Name: gen_commands.py
* Author: Nathan Swain
* Created On: 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
"""

import os
import string
import random

from django.template import Template, Context
from django.conf import settings

__all__ = ['GEN_APACHE_OPTION', 'GEN_APACHE_OPTION', 'generate_command']

# Initialize settings
settings.configure()
import django
django.setup()


GEN_SETTINGS_OPTION = 'settings'
GEN_APACHE_OPTION = 'apache'


def generate_command(args):
    """
    Generate a settings file for a new installation.
    """
    # Setup variables
    template = None
    context = Context()

    # Determine template path
    gen_templates_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'gen_templates')
    template_path = os.path.join(gen_templates_dir, args.type)

    # Determine destination file name (defaults to type)
    destination_file = args.type

    # Settings file setup
    if args.type == GEN_SETTINGS_OPTION:
        # Desitnation filename
        destination_file = '{0}.py'.format(args.type)

        # Parse template
        template = Template(open(template_path).read())

        # Generate context variables
        secret_key = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(50)])
        context.update({'secret_key': secret_key})
        print('Generating new settings.py file...')

    if args.type == GEN_APACHE_OPTION:
        # Destination filename
        destination_file = 'tethys-default.conf'

        # Parse template
        template = Template(open(template_path).read())

    # Default destination path is the current working directory
    destination_dir = os.getcwd()

    if args.directory:
        if os.path.isdir(args.directory):
            destination_dir = args.directory
        else:
            print('ERROR: "{0}" is not a valid directory.'.format(destination_dir))
            exit(1)

    destination_path = os.path.join(destination_dir, destination_file)

    # Check for pre-existing file
    if os.path.isfile(destination_path):
        valid_inputs = ('y', 'n', 'yes', 'no')
        no_inputs = ('n', 'no')

        overwrite_input = raw_input('WARNING: "{0}" already exists. '
                                    'Overwrite? (y/n): '.format(destination_file)).lower()

        while overwrite_input not in valid_inputs:
            overwrite_input = raw_input('Invalid option. Overwrite? (y/n): ').lower()

        if overwrite_input in no_inputs:
            print('Generation of "{0}" cancelled.'.format(destination_file))
            exit(0)

    # Render template and write to file
    if template:
        with open(destination_path, 'w') as f:
            f.write(template.render(context))
