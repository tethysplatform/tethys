'''
********************************************************************************
* Name: New App Paste Template/Scaffold
* Author: Nathan Swain
* Copyright: (c) Brigham Young University 2013
* License: BSD 2-Clause
********************************************************************************
'''

import sys
import random
import re

from paste.script.templates import Template, var
from paste.util.template import paste_script_template_renderer
from paste.script.create_distro import Command

# Horrible hack to change the behaviour of Paste itself
# Since this module is only imported when commands are
# run, this will not affect any other paster commands.
Command._bad_chars_re = re.compile('[^a-zA-Z0-9_-]')


class TethysAppTemplate(Template):

    """
    Template to build a skeleton Tethys Apps package
    """

    _template_dir = 'tethysapp_template/'
    summary = 'Create a new Tethys app project using this scaffold.'
    template_renderer = staticmethod(paste_script_template_renderer)

    vars = [
        var('proper_name', 'e.g.: "My First App" for project name "my_first_app"'),
        var('version', 'e.g.: 0.0.1'),
        var('description', 'One-line description of the app'),
        var('author', 'Author name'),
        var('author_email', 'Author email'),
        var('url', 'URL of homepage'),
        var('license_name', 'License name'),
    ]

    # Default colors from flatuicolors.com
    default_colors = ('#2ecc71',    # Emerald
                      '#3498db',    # Peter River
                      '#34495e',    # Wet Asphalt
                      '#9b59b6',    # Amethyst
                      '#e67e22',    # Carrot
                      '#f1c40f',    # Sun Flower
                      '#e74c3c',    # Alizarin
                      '#1abc9c',    # Turquoise
    )

    def check_vars(self, vars, cmd):
        vars = Template.check_vars(self, vars, cmd)
        PREFIX = 'tethysapp-'
        PREFIX_NO_DASH = 'tethysapp'

        if not vars['project'].startswith(PREFIX):
            print('\nError: Expected the project name to start with "{0}". Please add the "{0}" '
                  'as a prefix and try again'.format(PREFIX))
            sys.exit(1)

        # Validate project name
        project_error_regex = re.compile(r'^[a-zA-Z0-9_]+$')
        project_warning_regex = re.compile(r'^[a-zA-Z0-9_-]+$')
        project = vars['project'][len(PREFIX):]

        # Only letters, numbers and underscores allowed in app names
        if not project_error_regex.match(project):

            # If the only offending character is a dash, replace dashes with underscores and notify user
            if project_warning_regex.match(project):
                before = project
                project = project.replace('-', '_')
                print('\nWarning: Dashes in project name "{0}" have been replaced ' \
                      'with underscores "{1}"'.format(before, project))

            # Otherwise, throw error
            else:
                print('\nError: Invalid characters in project name "{0}". Only letters, numbers, and underscores ' \
                      '(no dashes) allowed after the "tethysapp-" prefix.'.format(project))
                sys.exit(1)

        vars['project'] = project

        # Derive the project_url from the project name
        vars['project_url'] = project.replace('_', '-').lower()

        # Derive proper_name if not provided by user
        if not vars['proper_name']:
            vars['proper_name'] = project.replace('_', ' ').title()

        # Derive the proper_no_spaces variable (used for the name of the App class)
        vars['proper_no_spaces'] = ''.join(vars['proper_name'].split())

        # Add the color variable to vars
        vars['color'] = random.choice(self.default_colors)

        return vars
